# Camera_Lighting_Control

本项目属于 TUB EMK MSMA 项目，主要用于构建基于工业相机SDK、OpenCV和RS232串口通信的图像采集、图像处理及亮度自动调节软件系统，并提供图形用户界面（GUI）。

## 软件架构

```text
Camera_Lighting_Control/
│
├── main.py
│
├── gui/
│   ├── main_window.py
│   ├── camera_panel.py
│   ├── led_panel.py
│   └── experiment_panel.py
│
├── hardware/
│   ├── camera.py
│   ├── led_controller.py
│   └── trigger.py
│
├── control/
│   ├── exposure_control.py
│   └── brightness_control.py
│
├── data/
│   ├── image_storage.py
│   └── metadata.py
│
└── config/
	└── settings.json
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

## 检查依赖

安装依赖后，可以运行以下命令检查每个包是否已安装、版本是否符合要求并且能够正常导入：

```powershell
python requirements_test.py
```

程序会输出每个依赖的版本和检查结果；所有依赖正常时返回退出码 `0`，
否则返回退出码 `1`。如果 `vmbpy` 导入失败，请同时确认 Vimba X SDK
及其传输层驱动已经安装并且可用。
