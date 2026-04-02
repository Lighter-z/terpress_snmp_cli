import asyncio
import time

import pdusnmp


# 统一配置设备 IP，后续只需要修改这里
DEVICE_IP = '192.168.0.166'


# 获取设备型号
def get_device_name():
    # 创建 SNMP 实例
    snmp = pdusnmp.MySnmpEngine()
    # 设置设备地址
    snmp.dev_ip = DEVICE_IP
    # 设置要读取的 OID
    snmp.oid = '1.3.6.1.4.1.23280.2.1.3.1'
    # 发送 SNMP 请求
    device_name = snmp.get_device_name()
    # 打印结果
    print("设备型号：", device_name)


# 获取各插口电压
def get_relay_voltage():
    # 创建 SNMP 实例
    snmp = pdusnmp.MySnmpEngine()
    # 设置设备地址
    snmp.dev_ip = DEVICE_IP
    # 遍历 1 到 8 号插口
    for i in range(1, 9):
        snmp.n_sock = i
        snmp.oid = '1.3.6.1.4.1.23280.8.1.3.' + i.__str__()
        # 发送 SNMP 请求
        relay_voltage = snmp.get_relay_voltage()
        # 打印结果
        print("第", i, "个插口电压：", relay_voltage, "V")


# 切换各插口开关状态
def set_relay_state():
    # set_value = 0
    # 创建 SNMP 实例
    snmp = pdusnmp.MySnmpEngine()
    # 设置设备地址
    snmp.dev_ip = DEVICE_IP
    # 依次读取并切换 1 到 8 号插口状态
    for i in range(1, 9):
        snmp.n_sock = i
        time.sleep(2)
        # 读取当前插口状态
        snmp.oid = '1.3.6.1.4.1.23280.8.1.2.' + i.__str__()
        relay_state = snmp.get_status()
        if relay_state == str(2):
            set_value = f'2'
        else:
            set_value = f'1'
            time.sleep(1)
        print("第", i, "个插口状态：", relay_state, set_value)
        snmp.oid = '1.3.6.1.4.1.23280.9.1.2.' + i.__str__()
        # TODO: 异步发送 SNMP 请求设置继电器状态
        asyncio.run(snmp.set_value(set_value))
        # 打印结果
        if set_value == '2':
            print("第", i, "个插口状态：已关闭")
        else:
            print("第", i, "个插口状态：已开启")


# 示例入口
if __name__ == '__main__':
    get_device_name()
    get_relay_voltage()
    set_relay_state()
