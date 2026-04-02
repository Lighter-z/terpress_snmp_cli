import asyncio
import argparse

import pdusnmp
from pdu_oid_catalog import OID_CATALOG, get_oid_entry, resolve_oid, search_oid_entries


# 统一配置设备 IP，默认优先使用这里
DEVICE_IP = '192.168.0.166'
OUTLET_COUNT = 8

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

STATUS_ON_VALUE = '2'
STATUS_OFF_VALUE = '1'

STATUS_LABELS = {
    STATUS_OFF_VALUE: '关闭',
    STATUS_ON_VALUE: '开启',
}

REALTIME_METRICS = [
    ('电压', 'device_voltage', 1, 10, 'V', 1),
    ('有功功率', 'device_active_power', 1, 1000, 'kW', 3),
    ('有功电能量', 'device_active_energy', 1, 1000, 'kWh', 3),
    ('碳排放量', 'device_carbon_emission', 1, 1000, 'Kg', 3),
    ('电流', 'device_current', 1, 100, 'A', 3),
    ('功率因数', 'device_power_factor', 1, 1000, '', 3),
    ('频率', 'device_frequency', 1, 1000, 'Hz', 3),
]

OUTLET_METRICS = {
    'voltage': ('outlet_voltage', 10, 'V', 1),
    'current': ('outlet_current', 100, 'A', 2),
    'energy': ('outlet_energy', 1, 'Wh', 0),
}


def parse_sock(value):
    sock = int(value)
    if sock < 1 or sock > OUTLET_COUNT:
        raise argparse.ArgumentTypeError(f'插口号必须在 1 到 {OUTLET_COUNT} 之间')
    return sock


def build_engine(ip, oid, sock=None):
    snmp = pdusnmp.MySnmpEngine()
    snmp.dev_ip = ip
    snmp.oid = oid
    if sock is not None:
        snmp.n_sock = sock
    return snmp


def resolve_cli_oid(key, sock=None):
    catalog_key = OID_KEYS.get(key)
    if catalog_key is None:
        return None
    return resolve_oid(catalog_key, sock)


def get_device_name(ip):
    snmp = build_engine(ip, resolve_cli_oid('device_name'))
    return snmp.get_device_name()


def get_raw_value(ip, key, index=None):
    oid = resolve_cli_oid(key, index)
    if oid is None:
        return None
    snmp = build_engine(ip, oid)
    return asyncio.run(snmp.get_value())


def read_metric_value(ip, key, index=None, divisor=1):
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
    if value is None:
        return '不支持'
    return f'{value:.{decimals}f}{unit}'


def collect_realtime_metrics(ip):
    metrics = []
    for label, key, index, divisor, unit, decimals in REALTIME_METRICS:
        value = read_metric_value(ip, key, index=index, divisor=divisor)
        metrics.append((label, format_metric_value(value, decimals, unit)))
    return metrics


def get_outlet_metric_value(ip, sock, metric_name):
    key, divisor, unit, decimals = OUTLET_METRICS[metric_name]
    value = read_metric_value(ip, key, index=sock, divisor=divisor)
    return value, format_metric_value(value, decimals, unit)


def get_outlet_status(ip, sock):
    snmp = build_engine(ip, resolve_cli_oid('outlet_status', sock), sock)
    return snmp.get_status()


def get_outlet_voltage(ip, sock):
    value, display = get_outlet_metric_value(ip, sock, 'voltage')
    return value, display


def get_outlet_current(ip, sock):
    value, display = get_outlet_metric_value(ip, sock, 'current')
    return value, display


def get_outlet_name(ip, sock):
    oid = resolve_cli_oid('outlet_name', sock)
    if oid is None:
        return None
    snmp = build_engine(ip, oid, sock)
    return snmp.get_sock_name()


def get_outlet_energy(ip, sock):
    oid = resolve_cli_oid('outlet_energy', sock)
    if oid is None:
        return None
    value, display = get_outlet_metric_value(ip, sock, 'energy')
    return value, display


def set_outlet_state(ip, sock, turn_on):
    snmp = build_engine(ip, resolve_cli_oid('outlet_control', sock), sock)
    return snmp.turn_on_off(turn_on)


def format_status(raw_status):
    raw_text = str(raw_status)
    return STATUS_LABELS.get(raw_text, f'未知状态({raw_text})')


def collect_outlet_info(ip, sock):
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
    info = collect_outlet_info(ip, sock)
    print(f'设备 IP: {ip}')
    for key, value in info.items():
        print(f'{key}: {value}')


def handle_device_name(args):
    device_name = get_device_name(args.ip)
    if device_name is None:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'设备型号: {device_name}')
    return 0


def handle_device_realtime(args):
    print(f'设备 IP: {args.ip}')
    for label, value in collect_realtime_metrics(args.ip):
        print(f'{label}: {value}')
    return 0


def handle_outlet_info(args):
    print_outlet_info(args.ip, args.sock)
    return 0


def handle_outlet_list(args):
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
    status = get_outlet_status(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'状态: {format_status(status)}')
    return 0


def handle_outlet_voltage(args):
    _, voltage = get_outlet_voltage(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'电压(V): {voltage}')
    return 0


def handle_outlet_current(args):
    _, current = get_outlet_current(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'电流(A): {current}')
    return 0


def handle_outlet_on(args):
    success = set_outlet_state(args.ip, args.sock, True)
    if not success:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'插口 {args.sock} 已开启')
    return 0


def handle_outlet_off(args):
    success = set_outlet_state(args.ip, args.sock, False)
    if not success:
        return 1
    print(f'设备 IP: {args.ip}')
    print(f'插口 {args.sock} 已关闭')
    return 0


def print_oid_entry(entry):
    print(f'键名: {entry["key"]}')
    if entry.get("name"):
        print(f'原始名称: {entry["name"]}')
    print(f'OID: {entry["oid"]}')
    print(f'类型: {entry["type"] or "-"}')
    print(f'读写: {entry["access"] or "-"}')
    print(f'含义: {entry["meaning"] or "-"}')
    print(f'备注: {entry["remark"] or "-"}')


def handle_oid_list(args):
    entries = search_oid_entries(args.keyword)
    if not entries:
        print('未找到匹配的 OID')
        return 1

    print(f'共找到 {len(entries)} 条 OID 记录')
    for entry in entries:
        print(f'{entry["key"]}: {entry["oid"]} | {entry["meaning"]}')
    return 0


def handle_oid_show(args):
    entry = get_oid_entry(args.key)
    print_oid_entry(entry)
    return 0


def build_parser():
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
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, 'handler'):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == '__main__':
    raise SystemExit(main())
