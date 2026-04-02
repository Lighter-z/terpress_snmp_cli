# TERPRESS DPDUv3L PDU SNMP 命令行工具

一个通过 SNMP 协议读取和控制 PDU 插口的命令行工具，适合在 Windows 或 Ubuntu 终端里直接查询插口信息、控制单个插口开关。

设备信息：

- 厂家中文名：特普瑞斯
- 厂家英文名：`TERPRESS`
- 设备型号：`DPDUv3L`

运行环境：

- Python 版本：`Python 3.13`

## 文件作用

### `pdusnmp.py`

底层 SNMP 封装，负责：

- 校验设备 IP 地址和插口号
- 发送 SNMP `GET` 和 `SET` 请求
- 提供设备名称、插口状态、电压、电流等读取方法
- 提供插口开关控制方法

### `pdu_snmp_cli.py`

命令行入口，负责：

- 解析命令参数
- 调用 `pdusnmp.py`
- 查询单个插口或全部插口信息
- 控制单个插口开启或关闭
- 查询内置 OID 目录

### `pdu_oid_catalog.py`

根据 `PDU的OID节点一览表v0.6.xlsx` 整理出的完整 OID 目录，包含：

- OID 键名
- OID 节点
- 数据类型
- 读写属性
- 含义
- 备注

## 文件关系

`pdu_snmp_cli.py` 调用 `pdusnmp.py` 进行设备通信，同时调用 `pdu_oid_catalog.py` 提供完整 OID 目录查询能力。

## 依赖安装

```bash
pip install -r requirements.txt
```

如果你的系统里有多个 Python 版本：

- Windows 可以用 `py -3.13`
- Ubuntu 可以用 `python3`

## 默认配置

在 `pdu_snmp_cli.py` 顶部修改默认设备地址：

```python
DEVICE_IP = '192.168.0.166'
```

也可以执行时临时指定：

```bash
python pdu_snmp_cli.py --ip 192.168.0.166 device-name
```

## 常用命令

查看帮助：

```bash
python pdu_snmp_cli.py -h
```

读取设备型号：

```bash
python pdu_snmp_cli.py device-name
```

或者：

```bash
python pdu_snmp_cli.py device name
```

读取设备实时数据：

```bash
python pdu_snmp_cli.py device realtime
```

读取 1 号插口完整信息：

```bash
python pdu_snmp_cli.py outlet info --sock 1
```

读取全部插口简要信息：

```bash
python pdu_snmp_cli.py outlet list
```

读取单个插口状态：

```bash
python pdu_snmp_cli.py outlet status --sock 1
```

读取单个插口电压：

```bash
python pdu_snmp_cli.py outlet voltage --sock 1
```

读取单个插口电流：

```bash
python pdu_snmp_cli.py outlet current --sock 1
```

打开 1 号插口：

```bash
python pdu_snmp_cli.py outlet on --sock 1
```

关闭 1 号插口：

```bash
python pdu_snmp_cli.py outlet off --sock 1
```

按关键字搜索 OID：

```bash
python pdu_snmp_cli.py oid list --keyword 电流
```

查看某个 OID 的详细说明：

```bash
python pdu_snmp_cli.py oid show --key outletControlCommand
```

在 Ubuntu 下执行时，把上面的 `python` 换成 `python3` 即可。

## 当前支持的插口信息

- 状态
- 电压
- 电流

设备实时数据命令当前会读取这些指标：

- 电压
- 电流
- 有功功率
- 有功电能量
- 功率因数
- 频率
- 碳排放量

如果你的设备支持插口名称，并且你已经确认对应 OID，可以在 `pdu_snmp_cli.py` 的 `OID_KEYS` 里补充：

- `outlet_name`

## OID 说明

完整 OID 已经整理进代码，不需要再单独翻 Excel。可以直接使用：

```bash
python pdu_snmp_cli.py oid list
```

或按关键字搜索：

```bash
python pdu_snmp_cli.py oid list --keyword 温度
```

当前插口控制和查询默认使用这些 OID：

- `deviceStatusModelNumber`：设备型号
- `phaseStatusVoltage`：设备电压
- `phaseStatusCurrent`：设备电流
- `deviceStatusActivePower`：总有功功率
- `deviceStatusPowerFactor`：总功率因数
- `deviceStatusActiveEnergy`：总有功电能量
- `deviceStatusFrequency`：频率
- `deviceStatusCarbonEmission`：碳排放量
- `outletStatusState`：插口状态
- `outletStatusVoltage`：插口电压
- `outletStatusCurrent`：插口电流
- `outletStatusActiveEnergy`：插口电能
- `outletControlCommand`：插口开关控制

如果设备对某些分插口测量项不支持，设备会返回 `-1`。命令行会显示为 `不支持`，而不是负数。

## 开关状态值说明

这个设备的“控制写入值”和“状态返回值”不是同一套定义。

控制写入值：

- `1`：开启
- `2`：关闭

命令行里：

- `outlet on --sock N` 会写入 `1`
- `outlet off --sock N` 会写入 `2`

状态返回值：

- `1`：关闭
- `2`：开启

## 说明

当前版本更偏向设备联调工具，仍有这些特点：

- 社区字符串写死为 `public` 和 `private`
- 默认设备 IP 写在代码里，但可以通过 `--ip` 临时覆盖
- 全部插口信息查询是串行执行
- 插口名称的 OID 默认未配置
