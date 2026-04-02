# Python 3.13 PDU SNMP 命令行工具

这个目录提供了一个通过 SNMP 协议读取和控制 PDU 插口的命令行工具，适合在 Windows 或 Ubuntu 终端里直接查询插口信息、控制单个插口开关。

## 文件作用

### `pdusnmp.py`

底层 SNMP 封装，负责：

- 校验设备 IP 地址和插口号
- 发送 SNMP `GET` 和 `SET` 请求
- 提供设备名称、插口状态、电压、电流等读取方法
- 提供插口开关控制方法

### `demo.py`

命令行入口，负责：

- 解析命令参数
- 调用 `pdusnmp.py`
- 查询单个插口或全部插口信息
- 控制单个插口开启或关闭

## 文件关系

`demo.py` 调用 `pdusnmp.py`，`pdusnmp.py` 再通过 `pysnmp` 与 PDU 设备通信。

## 依赖安装

```bash
pip install -r requirements.txt
```

如果你的系统里有多个 Python 版本：

- Windows 可以用 `py -3.13`
- Ubuntu 可以用 `python3`

## 默认配置

在 `demo.py`顶部修改默认设备地址：

```python
DEVICE_IP = '192.168.0.166'
```

也可以执行时临时指定：

```bash
python demo.py --ip 192.168.0.166 device-name
```

## 常用命令

查看帮助：

```bash
python demo.py -h
```

读取设备型号：

```bash
python demo.py device-name
```

读取 1 号插口完整信息：

```bash
python demo.py outlet info --sock 1
```

读取全部插口简要信息：

```bash
python demo.py outlet list
```

读取单个插口状态：

```bash
python demo.py outlet status --sock 1
```

读取单个插口电压：

```bash
python demo.py outlet voltage --sock 1
```

读取单个插口电流：

```bash
python demo.py outlet current --sock 1
```

打开 1 号插口：

```bash
python demo.py outlet on --sock 1
```

关闭 1 号插口：

```bash
python demo.py outlet off --sock 1
```

在 Ubuntu 下执行时，把上面的 `python` 换成 `python3` 即可。

## 当前支持的插口信息

- 状态
- 电压
- 电流

如果你的设备支持插口名称或电能，并且已经确认对应 OID，可以在 `demo.py` 顶部的 `OID_TEMPLATES` 中补充：

- `outlet_name`
- `outlet_energy`

## OID 说明

请根据设备的 MIB/OID 定义确认以下配置：

- `1.3.6.1.4.1.23280.2.1.3.1`：设备名称
- `1.3.6.1.4.1.23280.8.1.2.x`：插口状态
- `1.3.6.1.4.1.23280.8.1.3.x`：插口电压
- `1.3.6.1.4.1.23280.8.1.4.x`：插口电流
- `1.3.6.1.4.1.23280.9.1.2.x`：插口开关控制

其中 `x` 表示插口编号。

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
- 插口名称和电能的 OID 默认未配置
