# _*_ coding:utf-8 _*_
# 依赖 pysnmp，请先执行：pip install pysnmp
import asyncio
from pysnmp.hlapi.asyncio import *


# 定义 SNMP 引擎
class MySnmpEngine:
    dev_ip = ''
    oid = ''
    n_sock = 0

    # 验证 IP 地址
    def verify_ip(self):
        sep = self.dev_ip.split('.')
        if len(sep) != 4:
            return False
        for i, x in enumerate(sep):
            try:
                int_x = int(x)
                if int_x < 0 or int_x > 255:
                    return False
            except:
                return False
        return True

    # 验证插口号
    def verify_sock(self):
        if self.n_sock <= 0 or self.n_sock > 8:
            return False
        return True

    # 获取指定 OID 的值
    async def get_value(self):
        iterator = get_cmd(
            SnmpEngine(),
            CommunityData("public", mpModel=0),  # 社区字符串
            await UdpTransportTarget.create((self.dev_ip, 161)),  # SNMP 代理的 IP 和端口
            ContextData(),
            ObjectType(ObjectIdentity(self.oid))  # 添加 OID
        )
        errorIndication, errorStatus, errorIndex, varBinds = await iterator
        if errorIndication:
            print(f"SNMP 请求失败: {errorIndication}")
        elif errorStatus:
            print(f"SNMP 返回错误: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                return f"{varBind[1]}"

    # 设置指定 OID 的值
    async def set_value(self, set_value):
        iterator = set_cmd(
            SnmpEngine(),
            CommunityData("private", mpModel=0),
            await UdpTransportTarget.create((self.dev_ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.oid), Integer(set_value))  # 按整数写入
        )
        errorIndication, errorStatus, errorIndex, varBinds = await iterator

        if errorIndication:
            print(f"SNMP 请求失败: {errorIndication}")
            return False
        elif errorStatus:
            print(f"SNMP 返回错误: {errorStatus.prettyPrint()}")
            return False
        else:
            return True

    # 获取设备名称
    def get_device_name(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        dev_name = asyncio.run(self.get_value())
        return dev_name

    # 获取总电压
    def get_total_voltage(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取总电流
    def get_total_current(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 100
        return rt_value

    # 获取总功率
    def get_total_power(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 1000
        return rt_value

    # 获取总电能
    def get_total_energy(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 1000
        return rt_value

    # 获取温度
    def get_temperature(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取湿度
    def get_humidity(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取指定插口状态
    def get_status(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        sResult = asyncio.run(self.get_value())
        return sResult

    # 获取指定插口电压
    def get_relay_voltage(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        value = asyncio.run(self.get_value())
        return float(value) / 10

    # 获取指定插口电流
    def get_current(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        value = asyncio.run(self.get_value())
        return float(value) / 100

    # 获取指定插口电能
    def get_energy(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        value = asyncio.run(self.get_value())
        return float(value) / 100

    # 获取指定插口名称
    def get_sock_name(self):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        value = asyncio.run(self.get_value())
        return value

    # 打开或关闭指定插口
    def turn_on_off(self, on_off):
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        if on_off:
            state = 1
        else:
            state = 2
        return asyncio.run(self.set_value(state))

