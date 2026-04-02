"""TERPRESS DPDUv3L 的命令行入口。

这个文件是整个项目的“上层编排层”，主要负责三件事：
1. 解析命令行参数，例如 `device realtime`、`outlet on --sock 1`
2. 按照命令选择合适的 OID，并调用 `pdusnmp.py` 发起 SNMP 请求
3. 把设备返回的原始数值转换成更适合命令行阅读的文本

如果未来需要继续扩展功能，通常按下面的顺序修改：
1. 先去 `pdu_oid_catalog.py` 确认目标功能对应的 OID 是否已经存在
2. 如果没有，就把新的 OID 记录补进目录
3. 在本文件的 `OID_KEYS` 中声明“业务键名 -> OID 目录键名”的映射
4. 根据是否需要单位换算，补充读取函数或指标配置
5. 在 `build_parser()` 中增加新的命令行子命令

这样做的原因是：
- OID 目录和命令行逻辑解耦，便于维护
- 同一个 OID 可以被多个命令复用
- 后续让其他 AI 或开发者接手时，更容易定位该改哪个文件
"""

import asyncio
import argparse

import pdusnmp
from pdu_oid_catalog import OID_CATALOG, get_oid_entry, resolve_oid, search_oid_entries


# 统一配置设备 IP，默认优先使用这里。
# 如果命令行没有传入 `--ip`，就会使用这个值。
DEVICE_IP = '192.168.0.166'

# 当前代码默认按 8 个插口处理。
# 如果后续设备型号变化，这里是第一处需要确认的配置。
OUTLET_COUNT = 8

# `OID_KEYS` 是“命令行业务名称”和“OID 目录键名”之间的中间层。
# 这样命令层不需要直接依赖具体 OID 字符串，只依赖稳定的业务名称。
# 后面如果 OID 调整，通常只需要改这里或 `pdu_oid_catalog.py`。
OID_KEYS = {
    'device_name': 'deviceStatusModelNumber',
    'device_voltage': 'phaseStatusVoltage',
    'device_current': 'phaseStatusCurrent',
    'device_active_power': 'deviceStatusActivePower',
    'device_power_factor': 'deviceStatusPowerFactor',
    'device_active_energy': 'deviceStatusActiveEnergy',
    'device_frequency': 'deviceStatusFrequency',
    'device_carbon_emission': 'deviceStatusCarbonEmission',
    'outlet_status': 'outletStatusState',
    'outlet_voltage': 'outletStatusVoltage',
    'outlet_current': 'outletStatusCurrent',
    'outlet_energy': 'outletStatusActiveEnergy',
    'outlet_control': 'outletControlCommand',
    'temperature': 'sensorStatusTemperature',
    'humidity': 'sensorStatusHumidity',
}

# 设备返回的“状态值语义”和“控制写入值语义”不是同一套。
# 这里定义的是状态读取时的语义：
# - 读到 1 表示关闭
# - 读到 2 表示开启
STATUS_ON_VALUE = '2'
STATUS_OFF_VALUE = '1'

# 用于把状态原始值翻译为命令行输出文本。
STATUS_LABELS = {
    STATUS_OFF_VALUE: '关闭',
    STATUS_ON_VALUE: '开启',
}

# `REALTIME_METRICS` 定义了“设备实时数据”命令要输出哪些指标。
# 元组格式说明：
# (显示名称, OID_KEYS 中的键名, 索引, 除数, 单位, 小数位)
#
# 例如电压的原始值如果是 2278，除以 10 后显示为 227.8V。
# 大多数整机指标都属于这种“读原始整数值 -> 按倍率换算”的模式。
REALTIME_METRICS = [
    ('电压', 'device_voltage', 1, 10, 'V', 1),
    ('有功功率', 'device_active_power', 1, 1000, 'kW', 3),
    ('有功电能量', 'device_active_energy', 1, 1000, 'kWh', 3),
    ('碳排放量', 'device_carbon_emission', 1, 1000, 'Kg', 3),
    ('电流', 'device_current', 1, 100, 'A', 3),
    ('功率因数', 'device_power_factor', 1, 1000, '', 3),
    ('频率', 'device_frequency', 1, 1000, 'Hz', 3),
]

# `OUTLET_METRICS` 是分插口测量项的换算规则。
# 这里单独拆出来，是因为分插口指标和整机指标经常不是同一组 OID，
# 并且有些设备可能只支持状态，不支持分插口电流/电压/电能。
OUTLET_METRICS = {
    'voltage': ('outlet_voltage', 10, 'V', 1),
    'current': ('outlet_current', 100, 'A', 2),
    'energy': ('outlet_energy', 1, 'Wh', 0),
}


def parse_sock(value):
    """把命令行传入的插口号转换为整数，并做范围校验。"""
    sock = int(value)
    if sock < 1 or sock > OUTLET_COUNT:
        raise argparse.ArgumentTypeError(f'插口号必须在 1 到 {OUTLET_COUNT} 之间')
    return sock


def build_engine(ip, oid, sock=None):
    """创建底层 SNMP 引擎实例，并把本次请求所需参数灌进去。

    这里统一封装的好处是：
    - 避免每个读取函数都重复写 `MySnmpEngine()` 初始化代码
    - 后续如果要加 community、端口、超时之类的公共配置，也只改这里
    """
    snmp = pdusnmp.MySnmpEngine()
    snmp.dev_ip = ip
    snmp.oid = oid
    if sock is not None:
        snmp.n_sock = sock
    return snmp


def resolve_cli_oid(key, sock=None):
    """把命令层的业务键名解析成最终可访问的 OID 字符串。

    调用链是：
    命令行逻辑 -> OID_KEYS -> pdu_oid_catalog.resolve_oid()

    这样本文件不直接持有大量 OID 字符串，而是通过 OID 目录模块统一管理。
    """
    catalog_key = OID_KEYS.get(key)
    if catalog_key is None:
        return None
    return resolve_oid(catalog_key, sock)


def get_device_name(ip):
    """读取设备型号。"""
    snmp = build_engine(ip, resolve_cli_oid('device_name'))
    return snmp.get_device_name()


def get_raw_value(ip, key, index=None):
    """读取某个业务键名对应 OID 的原始返回值。

    这里返回的是“设备原始值”，不做单位换算。
    适合给后续的通用换算函数复用，也适合以后扩展 raw/debug 命令。
    """
    oid = resolve_cli_oid(key, index)
    if oid is None:
        return None
    snmp = build_engine(ip, oid)
    return asyncio.run(snmp.get_value())


def read_metric_value(ip, key, index=None, divisor=1):
    """读取数值型指标，并按倍率做换算。

    约定：
    - 设备返回 `-1` 时，表示“不支持”或“无该功能”，这里统一转成 `None`
    - 返回文本或异常值时，也统一转成 `None`

    这样上层输出层就不需要知道设备各种异常语义，只需要处理：
    - 有值：正常显示
    - None：显示“不支持”
    """
    raw_value = get_raw_value(ip, key, index)
    if raw_value is None:
        return None

    try:
        numeric = float(raw_value)
    except (TypeError, ValueError):
        return None

    if numeric < 0:
        return None

    return numeric / divisor


def format_metric_value(value, decimals, unit):
    """把数值格式化成适合 CLI 输出的字符串。"""
    if value is None:
        return '不支持'
    return f'{value:.{decimals}f}{unit}'


def collect_realtime_metrics(ip):
    """收集 `device realtime` 命令需要展示的整机实时数据。"""
    metrics = []
    for label, key, index, divisor, unit, decimals in REALTIME_METRICS:
        value = read_metric_value(ip, key, index=index, divisor=divisor)
        metrics.append((label, format_metric_value(value, decimals, unit)))
    return metrics


def get_outlet_metric_value(ip, sock, metric_name):
    """读取某个分插口测量项，并返回“原始数值 + 已格式化文本”。

    返回二元组的目的是兼顾两类场景：
    - 某些命令只想直接打印给用户看，用格式化后的文本即可
    - 某些后续扩展功能如果还要继续计算，可以拿原始浮点值
    """
    key, divisor, unit, decimals = OUTLET_METRICS[metric_name]
    value = read_metric_value(ip, key, index=sock, divisor=divisor)
    return value, format_metric_value(value, decimals, unit)


def get_outlet_status(ip, sock):
    """读取单个插口的开关状态原始值。"""
    snmp = build_engine(ip, resolve_cli_oid('outlet_status', sock), sock)
    return snmp.get_status()


def get_outlet_voltage(ip, sock):
    """读取单个插口电压。"""
    value, display = get_outlet_metric_value(ip, sock, 'voltage')
    return value, display


def get_outlet_current(ip, sock):
    """读取单个插口电流。"""
    value, display = get_outlet_metric_value(ip, sock, 'current')
    return value, display


def get_outlet_name(ip, sock):
    """读取单个插口名称。

    当前设备的插口名称 OID 默认没有接入 `OID_KEYS`，所以这里通常会返回 `None`。
    如果以后补了插口名称 OID，这个函数会自动开始生效。
    """
    oid = resolve_cli_oid('outlet_name', sock)
    if oid is None:
        return None
    snmp = build_engine(ip, oid, sock)
    return snmp.get_sock_name()


def get_outlet_energy(ip, sock):
    """读取单个插口电能。"""
    oid = resolve_cli_oid('outlet_energy', sock)
    if oid is None:
        return None
    value, display = get_outlet_metric_value(ip, sock, 'energy')
    return value, display


def set_outlet_state(ip, sock, turn_on):
    """控制单个插口开关。

    这里不直接处理状态值映射，而是交给 `pdusnmp.turn_on_off()`，
    因为“写入 1/2 分别代表什么”属于设备控制语义，应放在底层封装里统一维护。
    """
    snmp = build_engine(ip, resolve_cli_oid('outlet_control', sock), sock)
    return snmp.turn_on_off(turn_on)


def format_status(raw_status):
    """把设备返回的插口状态值翻译成中文文本。"""
    raw_text = str(raw_status)
    return STATUS_LABELS.get(raw_text, f'未知状态({raw_text})')


def collect_outlet_info(ip, sock):
    """汇总单个插口的完整信息。

    这个函数是后续扩展“插口详情页”或“批量导出”的核心入口。
    如果要新增分插口维度的字段，优先从这里扩展。
    """
    _, voltage_display = get_outlet_voltage(ip, sock)
    _, current_display = get_outlet_current(ip, sock)
    info = {
        '插口号': sock,
        '状态': format_status(get_outlet_status(ip, sock)),
        '电压(V)': voltage_display,
        '电流(A)': current_display,
    }

    outlet_name = get_outlet_name(ip, sock)
    if outlet_name is not None:
        info['名称'] = outlet_name

    outlet_energy = get_outlet_energy(ip, sock)
    if outlet_energy is not None:
        _, energy_display = outlet_energy
        info['电能(Wh)'] = energy_display

    return info


def print_outlet_info(ip, sock):
    """把 `collect_outlet_info()` 的结果按 CLI 友好的形式打印出来。"""
    info = collect_outlet_info(ip, sock)
    print(f'设备 IP: {ip}')
    for key, value in info.items():
        print(f'{key}: {value}')


# 下面这组 `handle_*` 函数是 argparse 的命令处理器。
# 它们的职责应该尽量保持简单：
# - 读取参数
# - 调用业务函数
# - 打印结果
# 不建议在这里堆积复杂业务逻辑，复杂逻辑优先下沉到上面的 helper 函数。
def handle_device_name(args):
    """处理 `device-name` / `device name` 命令。"""
    device_name = get_device_name(args.ip)
    if device_name is None:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'设备型号: {device_name}')
    return 0


def handle_device_realtime(args):
    """处理 `device realtime` 命令。"""
    print(f'设备 IP: {args.ip}')
    for label, value in collect_realtime_metrics(args.ip):
        print(f'{label}: {value}')
    return 0


def handle_outlet_info(args):
    """处理 `outlet info --sock N` 命令。"""
    print_outlet_info(args.ip, args.sock)
    return 0


def handle_outlet_list(args):
    """处理 `outlet list` 命令，遍历展示所有插口的摘要。"""
    print(f'设备 IP: {args.ip}')
    for sock in range(1, OUTLET_COUNT + 1):
        info = collect_outlet_info(args.ip, sock)
        print(
            f'插口 {sock}: '
            f'状态={info["状态"]}, '
            f'电压={info["电压(V)"]}, '
            f'电流={info["电流(A)"]}'
        )
    return 0


def handle_outlet_status(args):
    """处理 `outlet status --sock N` 命令。"""
    status = get_outlet_status(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'状态: {format_status(status)}')
    return 0


def handle_outlet_voltage(args):
    """处理 `outlet voltage --sock N` 命令。"""
    _, voltage = get_outlet_voltage(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'电压(V): {voltage}')
    return 0


def handle_outlet_current(args):
    """处理 `outlet current --sock N` 命令。"""
    _, current = get_outlet_current(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'电流(A): {current}')
    return 0


def handle_outlet_on(args):
    """处理 `outlet on --sock N` 命令。"""
    success = set_outlet_state(args.ip, args.sock, True)
    if not success:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'插口 {args.sock} 已开启')
    return 0


def handle_outlet_off(args):
    """处理 `outlet off --sock N` 命令。"""
    success = set_outlet_state(args.ip, args.sock, False)
    if not success:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'插口 {args.sock} 已关闭')
    return 0


def print_oid_entry(entry):
    """打印单条 OID 目录记录的详细信息。"""
    print(f'键名: {entry["key"]}')
    if entry.get("name"):
        print(f'原始名称: {entry["name"]}')
    print(f'OID: {entry["oid"]}')
    print(f'类型: {entry["type"] or "-"}')
    print(f'读写: {entry["access"] or "-"}')
    print(f'含义: {entry["meaning"] or "-"}')
    print(f'备注: {entry["remark"] or "-"}')


def handle_oid_list(args):
    """处理 `oid list` 命令。

    这个命令主要是给维护者和其他 AI 用的，方便快速搜索现有 OID，
    避免重复翻 Excel 或重复定义节点。
    """
    entries = search_oid_entries(args.keyword)
    if not entries:
        print('未找到匹配的 OID')
        return 1

    print(f'共找到 {len(entries)} 条 OID 记录')
    for entry in entries:
        print(f'{entry["key"]}: {entry["oid"]} | {entry["meaning"]}')
    return 0


def handle_oid_show(args):
    """处理 `oid show --key xxx` 命令。"""
    entry = get_oid_entry(args.key)
    print_oid_entry(entry)
    return 0


def build_parser():
    """构建 argparse 命令树。

    当前命令大致分三类：
    - device: 设备级别信息
    - outlet: 插口级别信息与控制
    - oid: OID 目录查询

    后续新增命令时，建议继续按这个分层扩展，避免所有命令都堆在顶层。
    """
    parser = argparse.ArgumentParser(
        description='PDU SNMP 命令行工具，可在 Windows 和 Ubuntu 命令行中使用'
    )
    parser.add_argument(
        '--ip',
        default=DEVICE_IP,
        help=f'设备 IP 地址，默认值为 {DEVICE_IP}',
    )

    subparsers = parser.add_subparsers(dest='command')

    parser_device_name = subparsers.add_parser('device-name', help='读取设备型号')
    parser_device_name.set_defaults(handler=handle_device_name)

    parser_device = subparsers.add_parser('device', help='读取设备信息')
    device_subparsers = parser_device.add_subparsers(dest='device_command')

    parser_device_info = device_subparsers.add_parser('name', help='读取设备型号')
    parser_device_info.set_defaults(handler=handle_device_name)

    parser_device_realtime = device_subparsers.add_parser('realtime', help='读取设备实时数据')
    parser_device_realtime.set_defaults(handler=handle_device_realtime)

    parser_outlet = subparsers.add_parser('outlet', help='查询或控制插口')
    outlet_subparsers = parser_outlet.add_subparsers(dest='outlet_command')

    parser_outlet_info = outlet_subparsers.add_parser('info', help='读取单个插口完整信息')
    parser_outlet_info.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_info.set_defaults(handler=handle_outlet_info)

    parser_outlet_list = outlet_subparsers.add_parser('list', help='读取全部插口简要信息')
    parser_outlet_list.set_defaults(handler=handle_outlet_list)

    parser_outlet_status = outlet_subparsers.add_parser('status', help='读取单个插口状态')
    parser_outlet_status.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_status.set_defaults(handler=handle_outlet_status)

    parser_outlet_voltage = outlet_subparsers.add_parser('voltage', help='读取单个插口电压')
    parser_outlet_voltage.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_voltage.set_defaults(handler=handle_outlet_voltage)

    parser_outlet_current = outlet_subparsers.add_parser('current', help='读取单个插口电流')
    parser_outlet_current.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_current.set_defaults(handler=handle_outlet_current)

    parser_outlet_on = outlet_subparsers.add_parser('on', help='打开单个插口')
    parser_outlet_on.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_on.set_defaults(handler=handle_outlet_on)

    parser_outlet_off = outlet_subparsers.add_parser('off', help='关闭单个插口')
    parser_outlet_off.add_argument('--sock', required=True, type=parse_sock, help='插口号，范围 1-8')
    parser_outlet_off.set_defaults(handler=handle_outlet_off)

    parser_oid = subparsers.add_parser('oid', help='查看内置 OID 目录')
    oid_subparsers = parser_oid.add_subparsers(dest='oid_command')

    parser_oid_list = oid_subparsers.add_parser('list', help='列出全部或按关键字筛选 OID')
    parser_oid_list.add_argument('--keyword', help='按键名、OID、含义或备注筛选')
    parser_oid_list.set_defaults(handler=handle_oid_list)

    parser_oid_show = oid_subparsers.add_parser('show', help='查看单条 OID 详细说明')
    parser_oid_show.add_argument('--key', required=True, choices=sorted(entry['key'] for entry in OID_CATALOG), help='OID 键名')
    parser_oid_show.set_defaults(handler=handle_oid_show)

    return parser


def main():
    """CLI 主入口。

    如果没有传入子命令，就打印帮助；
    如果传入了子命令，就调用对应 handler。
    """
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, 'handler'):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == '__main__':
    raise SystemExit(main())
