import argparse

import pdusnmp


# 统一配置设备 IP，默认优先使用这里
DEVICE_IP = '192.168.0.166'
OUTLET_COUNT = 8

OID_TEMPLATES = {
    'device_name': '1.3.6.1.4.1.23280.2.1.3.1',
    'outlet_status': '1.3.6.1.4.1.23280.8.1.2.{sock}',
    'outlet_voltage': '1.3.6.1.4.1.23280.8.1.3.{sock}',
    'outlet_current': '1.3.6.1.4.1.23280.8.1.4.{sock}',
    'outlet_control': '1.3.6.1.4.1.23280.9.1.2.{sock}',
    # 如果你的设备支持插口名称或电能，请按实际 MIB/OID 补充模板
    'outlet_name': None,
    'outlet_energy': None,
}

STATUS_ON_VALUE = '2'
STATUS_OFF_VALUE = '1'

STATUS_LABELS = {
    STATUS_OFF_VALUE: '关闭',
    STATUS_ON_VALUE: '开启',
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


def resolve_oid(key, sock=None):
    template = OID_TEMPLATES[key]
    if template is None:
        return None
    if '{sock}' in template:
        return template.format(sock=sock)
    return template


def get_device_name(ip):
    snmp = build_engine(ip, resolve_oid('device_name'))
    return snmp.get_device_name()


def get_outlet_status(ip, sock):
    snmp = build_engine(ip, resolve_oid('outlet_status', sock), sock)
    return snmp.get_status()


def get_outlet_voltage(ip, sock):
    snmp = build_engine(ip, resolve_oid('outlet_voltage', sock), sock)
    return snmp.get_relay_voltage()


def get_outlet_current(ip, sock):
    snmp = build_engine(ip, resolve_oid('outlet_current', sock), sock)
    return snmp.get_current()


def get_outlet_name(ip, sock):
    oid = resolve_oid('outlet_name', sock)
    if oid is None:
        return None
    snmp = build_engine(ip, oid, sock)
    return snmp.get_sock_name()


def get_outlet_energy(ip, sock):
    oid = resolve_oid('outlet_energy', sock)
    if oid is None:
        return None
    snmp = build_engine(ip, oid, sock)
    return snmp.get_energy()


def set_outlet_state(ip, sock, turn_on):
    snmp = build_engine(ip, resolve_oid('outlet_control', sock), sock)
    return snmp.turn_on_off(turn_on)


def format_status(raw_status):
    raw_text = str(raw_status)
    return STATUS_LABELS.get(raw_text, f'未知状态({raw_text})')


def collect_outlet_info(ip, sock):
    info = {
        '插口号': sock,
        '状态': format_status(get_outlet_status(ip, sock)),
        '电压(V)': get_outlet_voltage(ip, sock),
        '电流(A)': get_outlet_current(ip, sock),
    }

    outlet_name = get_outlet_name(ip, sock)
    if outlet_name is not None:
        info['名称'] = outlet_name

    outlet_energy = get_outlet_energy(ip, sock)
    if outlet_energy is not None:
        info['电能'] = outlet_energy

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
            f'电压={info["电压(V)"]}V, '
            f'电流={info["电流(A)"]}A'
        )
    return 0


def handle_outlet_status(args):
    status = get_outlet_status(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'状态: {format_status(status)}')
    return 0


def handle_outlet_voltage(args):
    voltage = get_outlet_voltage(args.ip, args.sock)
    print(f'设备 IP: {args.ip}')
    print(f'插口号: {args.sock}')
    print(f'电压(V): {voltage}')
    return 0


def handle_outlet_current(args):
    current = get_outlet_current(args.ip, args.sock)
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
