"""PDU OID 目录模块。

这个文件的核心目标是把 Excel 中的 OID 说明沉淀成结构化 Python 数据，
让代码在不依赖外部表格的情况下也能：
- 查询完整 OID
- 搜索 OID 含义
- 解析带 `~N` 的分路/分插口节点

维护建议：
1. 新增 OID 时，优先往 `OID_CATALOG` 里补记录
2. `key` 字段尽量保持稳定，因为其他模块会按它引用
3. 如果 Excel 原始行名称为空或不适合当键名，可以人工起一个语义明确的 `key`
4. 如果同一个 OID 存在多种备注写法，也可以保留多个条目，但 `key` 不能冲突
"""

OID_CATALOG = [
    {
        "key": "deviceStatusVersion",
        "name": "deviceStatusVersion",
        "oid": "1.3.6.1.4.1.23280.2.1.2.1~N",
        "type": "OCTET STRING",
        "access": "只读",
        "meaning": "版本",
        "remark": "",
    },
    {
        "key": "deviceStatusModelNumber",
        "name": "deviceStatusModelNumber",
        "oid": "1.3.6.1.4.1.23280.2.1.3.1~N",
        "type": "OCTET STRING",
        "access": "只读",
        "meaning": "设备型号",
        "remark": "",
    },
    {
        "key": "deviceStatusSerialNumber",
        "name": "deviceStatusSerialNumber",
        "oid": "1.3.6.1.4.1.23280.2.1.4.1~N",
        "type": "OCTET STRING",
        "access": "只读",
        "meaning": "设备序列号(MAC地址)",
        "remark": "作为设备的序列号对区别不同设备",
    },
    {
        "key": "deviceStatusActivePower",
        "name": "deviceStatusActivePower",
        "oid": "1.3.6.1.4.1.23280.2.1.5.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总有功功率",
        "remark": "单位：1W，不支持则返回-1",
    },
    {
        "key": "deviceStatusReactivePower",
        "name": "deviceStatusReactivePower",
        "oid": "1.3.6.1.4.1.23280.2.1.6.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总无功功率",
        "remark": "单位：1Var，不支持则返回-1",
    },
    {
        "key": "deviceStatusApparentPower",
        "name": "deviceStatusApparentPower",
        "oid": "1.3.6.1.4.1.23280.2.1.7.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总视在功率",
        "remark": "单位：1VA，不支持则返回-1",
    },
    {
        "key": "deviceStatusPowerFactor",
        "name": "deviceStatusPowerFactor",
        "oid": "1.3.6.1.4.1.23280.2.1.8.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总功率因数",
        "remark": "单位：0.1%，不支持则返回-1",
    },
    {
        "key": "deviceStatusActiveEnergy",
        "name": "deviceStatusActiveEnergy",
        "oid": "1.3.6.1.4.1.23280.2.1.9.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总有功耗电量",
        "remark": "单位：1Wh，不支持则返回-1",
    },
    {
        "key": "deviceStatusReactiveEnergy",
        "name": "deviceStatusReactiveEnergy",
        "oid": "1.3.6.1.4.1.23280.2.1.10.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "总无功耗电量",
        "remark": "单位：1Varh，不支持则返回-1",
    },
    {
        "key": "deviceStatusFrequency",
        "name": "deviceStatusFrequency",
        "oid": "1.3.6.1.4.1.23280.2.1.11.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "频率",
        "remark": "单位：0.001HZ，不支持则返回-1",
    },
    {
        "key": "deviceStatusZeroLineCurrent",
        "name": "deviceStatusZeroLineCurrent",
        "oid": "1.3.6.1.4.1.23280.2.1.12.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "零线电流",
        "remark": "单位：0.01A，不支持则返回-1",
    },
    {
        "key": "deviceStatusThreePhaseUnbalance",
        "name": "deviceStatusThreePhaseUnbalance",
        "oid": "1.3.6.1.4.1.23280.2.1.13.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "三相不平衡度",
        "remark": "单位：1%，不支持则返回-1",
    },
    {
        "key": "ipAddress",
        "name": "",
        "oid": "1.3.6.1.2.1.4.20.1.1",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "IP地址",
        "remark": "",
    },
    {
        "key": "sysName",
        "name": "sys Name",
        "oid": "1.3.6.1.2.1.1.5.0",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "设备名称",
        "remark": "",
    },
    {
        "key": "deviceStatusCarbonEmission",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.2.1.15.1",
        "type": "",
        "access": "只读",
        "meaning": "碳排放量",
        "remark": "单位 ：0.001kg  不支持则返回-1",
    },
    {
        "key": "deviceControlReboot",
        "name": "deviceControlReboot",
        "oid": "1.3.6.1.4.1.23280.3.1.2.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "重启",
        "remark": "将数值设置为1重启设备，设置为2初始化设备 设置为2 1.0.61版本之后支持",
    },
    {
        "key": "deviceControlEngeryReset",
        "name": "deviceControlEngeryReset",
        "oid": "1.3.6.1.4.1.23280.3.1.3.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "总电能重置",
        "remark": "将数值设置为1，可清零电能",
    },
    {
        "key": "deviceControlBeepAlarm",
        "name": "deviceControlBeepAlarm",
        "oid": "1.3.6.1.4.1.23280.3.1.4.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "蜂鸣器告警",
        "remark": "1：关闭蜂鸣器模块 2：使能蜂鸣器模块",
    },
    {
        "key": "deviceControlZeroLineCurrentMaxThreshold",
        "name": "deviceControlZeroLineCurrentMaxThreshold",
        "oid": "1.3.6.1.4.1.23280.3.1.5.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "零线电流告警阈值",
        "remark": "单位：0.01A，不支持则返回-1",
    },
    {
        "key": "deviceControlThreePhaseUnbalanceMaxThreshold",
        "name": "deviceControlThreePhaseUnbalanceMaxThreshold",
        "oid": "1.3.6.1.4.1.23280.3.1.6.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "三相不平衡百分之比告警阈值",
        "remark": "单位：1%，不支持则返回-1",
    },
    {
        "key": "phaseConfigOverVoltageThreshold",
        "name": "phaseConfigOverVoltageThreshold",
        "oid": "1.3.6.1.4.1.23280.5.1.2.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "电压上限告警值",
        "remark": "单位：0.1V",
    },
    {
        "key": "phaseConfigLowVoltageThreshold",
        "name": "phaseConfigLowVoltageThreshold",
        "oid": "1.3.6.1.4.1.23280.5.1.3.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "电压下限告警值",
        "remark": "",
    },
    {
        "key": "phaseConfigOverCurrentThreshold",
        "name": "phaseConfigOverCurrentThreshold",
        "oid": "1.3.6.1.4.1.23280.5.1.4.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "电流上限告警值",
        "remark": "单位：0.01A",
    },
    {
        "key": "phaseConfigLowCurrentThreshold",
        "name": "phaseConfigLowCurrentThreshold",
        "oid": "1.3.6.1.4.1.23280.5.1.5.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "电流下限告警值",
        "remark": "",
    },
    {
        "key": "phaseStatusVoltage",
        "name": "phaseStatusVoltage",
        "oid": "1.3.6.1.4.1.23280.6.1.2.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "电压",
        "remark": "单位：0.1V",
    },
    {
        "key": "phaseStatusCurrent",
        "name": "phaseStatusCurrent",
        "oid": "1.3.6.1.4.1.23280.6.1.3.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "电流",
        "remark": "单位：0.01A",
    },
    {
        "key": "phaseStatusActivePower",
        "name": "phaseStatusActivePower",
        "oid": "1.3.6.1.4.1.23280.6.1.4.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "有功功率",
        "remark": "单位：1W",
    },
    {
        "key": "phaseStatusReactivePower",
        "name": "phaseStatusReactivePower",
        "oid": "1.3.6.1.4.1.23280.6.1.5.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "无功功率",
        "remark": "单位：1Var，不支持则返回-1",
    },
    {
        "key": "phaseStatusApparentPower",
        "name": "phaseStatusApparentPower",
        "oid": "1.3.6.1.4.1.23280.6.1.6.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "视在功率",
        "remark": "单位：1VA，不支持则返回-1",
    },
    {
        "key": "phaseStatusPowerFactor",
        "name": "phaseStatusPowerFactor",
        "oid": "1.3.6.1.4.1.23280.6.1.7.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "功率因数",
        "remark": "单位：%0.1",
    },
    {
        "key": "phaseStatusActiveEnergy",
        "name": "phaseStatusActiveEnergy",
        "oid": "1.3.6.1.4.1.23280.6.1.8.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "有功耗电量",
        "remark": "单位：1Wh",
    },
    {
        "key": "phaseStatusReactiveEnergy",
        "name": "phaseStatusReactiveEnergy",
        "oid": "1.3.6.1.4.1.23280.6.1.9.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "无功耗电量",
        "remark": "单位：1Varh，不支持则返回-1",
    },
    {
        "key": "phaseStatusVoltageLimitState",
        "name": "phaseStatusVoltageLimitState",
        "oid": "1.3.6.1.4.1.23280.6.1.10.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "电压告警状态",
        "remark": "1，正常，2，越上限，3，越下限",
    },
    {
        "key": "phaseStatusCurrentLimitState",
        "name": "phaseStatusCurrentLimitState",
        "oid": "1.3.6.1.4.1.23280.6.1.11.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "电流告警状态",
        "remark": "1，正常，2，越上限，3，越下限",
    },
    {
        "key": "outletStatusState",
        "name": "outletStatusState",
        "oid": "1.3.6.1.4.1.23280.8.1.2.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器状态",
        "remark": "1：关闭状态  2：打开状态，不支持则返回-1",
    },
    {
        "key": "outletStatusVoltage",
        "name": "outletStatusVoltage",
        "oid": "1.3.6.1.4.1.23280.8.1.3.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器电压",
        "remark": "单位：0.1V，不支持则返回-1",
    },
    {
        "key": "outletStatusCurrent",
        "name": "outletStatusCurrent",
        "oid": "1.3.6.1.4.1.23280.8.1.4.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器电流",
        "remark": "单位：0.01A，不支持则返回-1",
    },
    {
        "key": "outletStatusActivePower",
        "name": "outletStatusActivePower",
        "oid": "1.3.6.1.4.1.23280.8.1.5.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器有功功率",
        "remark": "单位：1W，不支持则返回-1",
    },
    {
        "key": "outletStatusPowerFactor",
        "name": "outletStatusPowerFactor",
        "oid": "1.3.6.1.4.1.23280.8.1.6.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器功率因数",
        "remark": "单位：%0.1，不支持则返回-1",
    },
    {
        "key": "outletStatusActiveEnergy",
        "name": "outletStatusActiveEnergy",
        "oid": "1.3.6.1.4.1.23280.8.1.7.1~N",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "继电器电能",
        "remark": "单位：1Wh，不支持则返回-1",
    },
    {
        "key": "outletControlCommand",
        "name": "outletControlCommand",
        "oid": "1.3.6.1.4.1.23280.9.1.2.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "继电器动作",
        "remark": "1：闭合继电器  2：断开继电器，3：重启继电器，4.挂锁 5.解锁 不支持则返回-1 挂锁之后本插口命令不执行，需解锁后执行",
    },
    {
        "key": "outletControlEnergyReset",
        "name": "outletControlEnergyReset",
        "oid": "1.3.6.1.4.1.23280.9.1.3.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "继电器电能清空",
        "remark": "1：清空相应的继电器电能，不支持则返回-1",
    },
    {
        "key": "sensorConfigTempMaxThreshold",
        "name": "sensorConfigTempMaxThreshold",
        "oid": "1.3.6.1.4.1.23280.11.1.2.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "温度上限告警值",
        "remark": "单位：0.1℃，不支持则返回-1",
    },
    {
        "key": "sensorConfigTempMinThreshold",
        "name": "sensorConfigTempMinThreshold",
        "oid": "1.3.6.1.4.1.23280.11.1.3.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "温度下限告警值",
        "remark": "",
    },
    {
        "key": "sensorConfigHumidityMaxThreshold",
        "name": "sensorConfigHumidityMaxThreshold",
        "oid": "1.3.6.1.4.1.23280.11.1.4.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "湿度上限告警值",
        "remark": "单位：%0.1RH，不支持则返回-1",
    },
    {
        "key": "sensorConfigHumidityMinThreshold",
        "name": "sensorConfigHumidityMinThreshold",
        "oid": "1.3.6.1.4.1.23280.11.1.5.1~N",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "湿度下限告警值",
        "remark": "",
    },
    {
        "key": "sensorStatusTemperature",
        "name": "sensorStatusTemperature",
        "oid": "1.3.6.1.4.1.23280.12.1.2",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "温度值",
        "remark": "单位：0.1℃",
    },
    {
        "key": "sensorStatusHumidity",
        "name": "sensorStatusHumidity",
        "oid": "1.3.6.1.4.1.23280.12.1.3",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "湿度值",
        "remark": "单位：%0.1RH",
    },
    {
        "key": "sensorStatusTemperatureLimitState",
        "name": "sensorStatusTemperatureLimitState",
        "oid": "1.3.6.1.4.1.23280.12.1.4",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "温度状态",
        "remark": "1，正常，2，越上限，3，越下限",
    },
    {
        "key": "sensorStatusHumidityLimitState",
        "name": "sensorStatusHumidityLimitState",
        "oid": "1.3.6.1.4.1.23280.12.1.5",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "湿度状态",
        "remark": "",
    },
    {
        "key": "sensorStatusIOSensorState",
        "name": "sensorStatusIOSensorState",
        "oid": "1.3.6.1.4.1.23280.12.1.6",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "节点IO状态",
        "remark": "1，正常，2，告警",
    },
    {
        "key": "deviceStatusBatchQuery",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.2.1.14.1",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "设备总数据批量获取",
        "remark": "解释：outletNum=8  代表8个插口 outletState=255 代表8个插口开关状态 二进制方式代表 12345678=1 2 4 8 16 32 64 128 相加的结果：例如1-8全开1+2+4+8+16+32+64+128=255；outletState=3即1口+2口是开启状态；voltage=239.0代表当前主机电压；current=0.000代表当前主机电流；activePower=0.000代表当前主机功率；powerFactor=1.000代表当前主机功率因素，分路设备支持获取分路信息；energy=0.000代表当前主机用电量；temperature=-1,humidity=-1代表没有温湿度模块。",
    },
    {
        "key": "userDefinedRestartCommands",
        "name": "User-defined restart commands",
        "oid": ".1.3.6.1.4.1.23280.3.1.7.1",
        "type": "INTEGER",
        "access": "写",
        "meaning": "自定义重启任务",
        "remark": "ttt",
    },
    {
        "key": "userDefinedRestartCommandsMode2",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.3.1.7.1 第二种控制方式",
        "type": "INTEGER",
        "access": "写",
        "meaning": "自定义重启任务",
        "remark": "",
    },
    {
        "key": "userDefinedDelaySwitch",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.3.1.7.1 第三种控制方式",
        "type": "INTEGER",
        "access": "写",
        "meaning": "自定义延时开关",
        "remark": "snmpset -v1 -c private 192.168.1.55 1.3.6.1.4.1.23280.3.1.7.1 s \"0xFFFF&10&OFF\"，其中0xFFFF使用16进制代表每个插口，10代表收到命令10秒后执行，OFF为关，ON为开。",
    },
    {
        "key": "userDefinedOutletComboControl",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.3.1.7.1 第四种控制方式",
        "type": "INTEGER",
        "access": "写",
        "meaning": "自定义组合插口控制",
        "remark": "snmpset -v1 -c private 192.168.1.55 1.3.6.1.4.1.23280.3.1.7.1 s \"0xFFFF&OFF\"，其中0xFFFF使用16进制代表每个插口。",
    },
    {
        "key": "networkAddressMode",
        "name": "phaseConfigOverVoltageThreshold",
        "oid": ".1.3.6.1.4.1.23280.3.1.8.1",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "动态 静态IP地址切换",
        "remark": "",
    },
    {
        "key": "networkIpv4Address",
        "name": "phaseConfigOverCurrentThreshold",
        "oid": ".1.3.6.1.4.1.23280.3.1.9.1",
        "type": "INTEGER",
        "access": "读写",
        "meaning": "0.0.0.0",
        "remark": "写入IP地址，按照 IPV4 格式写入，例如 192.168.0.163，重启系统生效。",
    },
    {
        "key": "deviceStatusCarbonEmissionAlt",
        "name": "",
        "oid": ".1.3.6.1.4.1.23280.2.1.15.1",
        "type": "INTEGER",
        "access": "只读",
        "meaning": "碳排放量",
        "remark": "单位0.001KG",
    },
]

OID_LOOKUP = {entry["key"]: entry for entry in OID_CATALOG}


def clean_oid_value(raw_oid):
    """清洗 Excel 原始 OID 字符串。

    处理内容：
    - 去掉开头可能存在的点号 `.`
    - 去掉同一单元格里附带的中文说明

    例如：
    `.1.3.6.1.4.1... 第二种控制方式` -> `1.3.6.1.4.1...`
    """
    if not raw_oid:
        return ""
    return raw_oid.split()[0].lstrip(".")


def resolve_oid(key, index=None):
    """根据目录键名解析出最终可访问的 OID。

    Excel 中很多分路节点使用 `~N` 表示“最后一段是可变索引”。
    例如：
    - `1.3.6.1.4.1.23280.8.1.3.1~N`
    - 当 index=1 时，解析成插口 1 的 OID
    - 当 index=8 时，解析成插口 8 的 OID

    这里之所以把解析逻辑集中在目录模块，是为了避免上层业务代码重复拼接 OID。
    """
    entry = OID_LOOKUP[key]
    oid = clean_oid_value(entry["oid"])
    if oid.endswith("~N"):
        if index is None:
            index = 1
        prefix = oid[:-2]
        if prefix.endswith("1"):
            prefix = prefix[:-1]
        oid = f"{prefix}{index}"
    return oid


def get_oid_entry(key):
    """按键名获取单条 OID 目录记录。"""
    return OID_LOOKUP[key]


def search_oid_entries(keyword):
    """按关键字搜索 OID 目录。

    搜索范围包括：
    - key
    - 原始名称
    - OID 字符串
    - 含义
    - 备注

    这个函数主要服务于 `pdu_snmp_cli.py oid list --keyword ...`
    命令，便于维护者和其他 AI 快速定位相关节点。
    """
    if not keyword:
        return OID_CATALOG

    keyword_lower = keyword.lower()
    results = []
    for entry in OID_CATALOG:
        haystack = " ".join(
            [
                entry.get("key", ""),
                entry.get("name", ""),
                entry.get("oid", ""),
                entry.get("meaning", ""),
                entry.get("remark", ""),
            ]
        ).lower()
        if keyword_lower in haystack:
            results.append(entry)
    return results
