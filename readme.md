# Camera_Lighting_Control

本项目属于 TUB EMK MSMA 项目，主要用于构建基于工业相机SDK、OpenCV和RS232串口通信的图像采集、图像处理及亮度自动调节软件系统，并提供图形用户界面（GUI）。

## 软件架构

```text
Camera_Lighting_Control/
│
├── main.py                  # 程序入口（当前为占位）
│
├── read_demo.py             # 四路亮度读取演示脚本
├── requirements.txt
├── requirements_test.py
│
├── hardware/
│   ├── LED_control.py       # 调光、常亮/常灭（队友维护）
│   └── led_reader.py        # 亮度回读
│
├── gui/                     # GUI 占位，待补充
├── control/                 # 控制逻辑占位，待补充
└── data/                    # 数据存储占位，待补充
```

## 开发环境

项目使用 Python 3.12，依赖位于 `requirements.txt`。

在 Windows PowerShell 中初始化环境：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

VS Code 中选择解释器：

```text
.venv\Scripts\python.exe
```

依赖包括 OpenCV、pyserial、PySide6 和 Vimba X Python API (`vmbpy`)。
使用相机前还需要安装 Allied Vision Vimba X SDK，并确认相机的 USB/GigE
传输层驱动已安装。`vmbpy` 只提供 Python API，不能替代系统级 SDK 和驱动。

## 串口发送示例

调光与常亮/常灭由 `hardware/LED_control.py` 提供，串口参数为 19200 / 8N1。
安装依赖并连接串口设备后，可在程序中调用：

```python
from hardware import LED_control

LED_control.initCOM("COMx")   # 替换为实际串口号
LED_control.setLightness(1, 168)   # 第一通道亮度 168
```

具体命令帧格式见下一节「串口亮度回读」与 `hardware/LED_control.py` 内注释。

## 检查依赖

安装依赖后，可以运行以下命令检查每个包是否已安装、版本是否符合要求并且能够正常导入：

```powershell
python requirements_test.py
```

程序会输出每个依赖的版本和检查结果；所有依赖正常时返回退出码 `0`，
否则返回退出码 `1`。如果 `vmbpy` 导入失败，请同时确认 Vimba X SDK
及其传输层驱动已经安装并且可用。

## 串口亮度回读（hardware/led_reader.py）

- 查询帧：`S` + 通道(A~D) + `#`，例如 `SA#` / `SB#` / `SC#` / `SD#`。
- 应答：小写通道字母 + 4 位十进制亮度，例如 `a0168`，范围 `0000`–`0255`。
- 串口参数：19200，8 数据位，1 停止位，无校验（8N1）。
- 运行四路亮度演示：先 `python read_demo.py --list` 确认控制器对应的 COM 口（描述含 FTDI / Prolific / USB-to-Serial，不要连蓝牙 SPP 口），再 `python read_demo.py --port COMx`。
- 模块分工：`LED_control.py` 由队友维护（调光、常亮/常灭）；`led_reader.py` 为亮度回读，两者可在同一程序中分别导入。

## 当前待办（接入真机前需完成）

1. **真机回包结束符待确认**：手册未给亮度应答定义 `#` 或换行结束符。当前解析先 `strip()` 首尾空白，正则仅容忍尾随 `\r\n`、不接受井号。控制器接线后需抓一次原始回包字节，确认是否带固定结束符；若回包实际以 `#` 结尾，需在 `hardware/led_reader.py` 的 `RESPONSE_PATTERN` 中补回井号。
2. **真机读取验证**：目前回读逻辑仅通过离线模拟回包测试；接线、上电后需实测四路亮度读取是否正常。本机 COM3/COM4 当前为蓝牙串口（BTHENUM），不是控制器端口。
3. **Python 环境与依赖**：项目约定 Python 3.12，建议在仓库根目录建 `.venv` 后按 `requirements.txt` 安装依赖；若在其他 Python 版本（如 3.13/3.15）上出现 OpenCV、vmbpy 导入失败，通常是 NumPy 编译版本与解释器不匹配，切换到 3.12 虚拟环境重装即可。

## 已知模块状态

- `main.py` 目前仍是入口占位，尚未把相机、调光、亮度回读串联起来；`gui/`、`control/`、`data/` 目录为占位，后续集成时补充。
- 频闪模式（帧内加 `P` 标识，如 `SPA0168#`，时间范围 `0000`–`0999`）当前未实现回读。
