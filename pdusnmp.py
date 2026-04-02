"""底层 SNMP 通信封装。

这个文件尽量只做“和设备通信直接相关”的事情，不处理命令行、不维护 OID 目录。

职责边界：
- 负责发起 SNMP GET / SET
- 负责最基础的 IP、插口号校验
- 负责把某些常见数值型 OID 转成 Python 数字

不建议在这里做的事情：
- 不建议写命令行解析
- 不建议维护整套 OID 目录
- 不建议堆积太多设备业务逻辑

如果未来要支持新的设备控制语义，例如更多插口动作、更多 community 配置，
优先在这个文件扩展，然后让上层 `pdu_snmp_cli.py` 调用。
"""

# _*_ coding:utf-8 _*_
# 依赖 pysnmp，请先执行：pip install pysnmp
import asyncio
from pysnmp.hlapi.asyncio import *

# 这个设备的插口控制写入值语义如下：
# - 1: 开启
# - 2: 关闭
# 这里集中定义后，上层无须关心具体写入哪个整数。
CONTROL_ON_VALUE = 1
CONTROL_OFF_VALUE = 2


# 定义 SNMP 引擎
class MySnmpEngine:
    """针对当前 PDU 设备的最小 SNMP 访问对象。

    使用方式通常是：
    1. 上层先创建实例
    2. 填入 `dev_ip`、`oid`
    3. 如果是分插口命令，再填 `n_sock`
    4. 调用本类的读取/写入方法

    这里保留了很多“按具体业务命名”的方法，是为了让上层代码更直观。
    例如 `get_device_name()` 比直接写 `get_value()` 更容易理解。
    """
    dev_ip = ''
    oid = ''
    n_sock = 0

    # 验证 IP 地址
    def verify_ip(self):
        """校验 `dev_ip` 是否是合法 IPv4 地址字符串。"""
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
        """校验当前插口号是否在设备支持范围内。"""
        if self.n_sock <= 0 or self.n_sock > 8:
            return False
        return True

    # 获取指定 OID 的值
    async def get_value(self):
        """发起一次 SNMP GET 请求，并返回 OID 原始值。

        返回值统一转成字符串，便于上层自己决定如何做数值换算。
        这样底层通信层不需要知道每个 OID 的业务单位。
        """
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
        """发起一次 SNMP SET 请求。

        当前默认把写入值当成整数，因为现有开关控制和大部分控制项都走整数写入。
        如果以后遇到字符串型写入命令，可以在这里继续扩展类型分支。
        """
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
        """读取设备名称/型号类字符串值。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        dev_name = asyncio.run(self.get_value())
        return dev_name

    # 获取总电压
    def get_total_voltage(self):
        """读取总电压，并按 0.1V 倍率做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取总电流
    def get_total_current(self):
        """读取总电流，并按 0.01A 倍率做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 100
        return rt_value

    # 获取总功率
    def get_total_power(self):
        """读取总功率，并按 0.001kW 的显示需求做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 1000
        return rt_value

    # 获取总电能
    def get_total_energy(self):
        """读取总电能，并按上层当前使用方式做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 1000
        return rt_value

    # 获取温度
    def get_temperature(self):
        """读取温度，并按 0.1℃ 倍率做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取湿度
    def get_humidity(self):
        """读取湿度，并按 0.1 单位做换算。"""
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        value = asyncio.run(self.get_value())
        rt_value = float(value) / 10
        return rt_value

    # 获取指定插口状态
    def get_status(self):
        """读取插口状态原始值。

        注意：状态值的语义由设备定义，上层需要自己解释 1/2 代表什么。
        当前项目已经确认：
        - 1 表示关闭
        - 2 表示开启
        """
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
        """读取插口电压，并按 0.1V 倍率做换算。"""
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
        """读取插口电流，并按 0.01A 倍率做换算。"""
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
        """读取插口电能。

        这个方法是早期封装保留下来的接口。
        当前项目的新命令行逻辑优先使用 `pdu_snmp_cli.py` 中基于 OID 表的换算规则，
        因为不同 OID 的单位说明以 OID 表为准。
        """
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
        """读取插口名称字符串。"""
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
        """控制单个插口开关。

        参数：
        - on_off=True  -> 开启
        - on_off=False -> 关闭

        这里把布尔语义转换为设备实际需要的整数写入值，
        上层调用者不需要记忆 1/2 分别代表什么。
        """
        if not self.verify_ip():
            print('无效的 IP 地址')
            return None
        if not self.verify_sock():
            print('无效的插口号')
            return None
        if on_off:
            state = CONTROL_ON_VALUE
        else:
            state = CONTROL_OFF_VALUE
        return asyncio.run(self.set_value(state))

