"""
read_demo.py — 读取 DPS1024-4T 四路通道当前亮度并打印到终端。

独立于队友的 LED_control.py，只做“读取亮度”这一件事。

用法（在仓库根目录 D:\\GitHub\\Camera_Lighting_Control 下运行）：
    python read_demo.py --list          # 先列出本机可用串口
    python read_demo.py --port COM3     # 指定控制器对应的串口号读取四路亮度

运行前确认：控制器已上电、RS232 接线（TXD / RXD / GND）接好、pyserial 已安装。
"""

import argparse
import sys
from pathlib import Path

# 无论从哪个目录启动，都把脚本所在目录加入路径，确保能找到 hardware 包
sys.path.insert(0, str(Path(__file__).resolve().parent))

from hardware import led_reader

# 不硬编码默认串口号：本机 COM3/COM4 当前均为蓝牙串口，控制器端口需接线后用 --list 确认。
# 未通过 --port 指定时，程序先列出可用串口并退出，避免误连蓝牙设备。
DEFAULT_PORT = ""
CHANNELS = (1, 2, 3, 4)


def list_ports() -> None:
    """列出本机可用串口，方便确认串口号。"""
    try:
        from serial.tools import list_ports
    except ImportError:
        print("未找到 pyserial，请先运行: pip install pyserial")
        return

    ports = list_ports.comports()
    if not ports:
        print("未发现串口设备。")
        return

    print("可用串口：")
    for port in ports:
        print(f"  {port.device}  {port.description}")


def main() -> int:
    parser = argparse.ArgumentParser(description="读取 DPS1024-4T 四路通道亮度")
    parser.add_argument("--port", default=DEFAULT_PORT, help="串口号，如 COM3；不确定时先加 --list 查看")
    parser.add_argument("--list", action="store_true", help="列出可用串口后退出")
    args = parser.parse_args()

    if args.list:
        list_ports()
        return 0

    if not args.port:
        print("未指定串口号。请先运行 python read_demo.py --list 确认控制器对应的 COM 口，")
        print("再用 python read_demo.py --port COMx 指定。")
        return 1

    led_reader.initCOM(args.port)
    print(f"串口 {args.port} 已初始化，开始读取四路亮度...\n")

    failed = 0
    for channel in CHANNELS:
        try:
            value = led_reader.readLightness(channel)
            print(f"CH{channel} 亮度: {value}")
        except Exception as exc:  # 单路失败不影响其余通道读取
            failed += 1
            print(f"CH{channel} 读取失败: {exc}")

    if failed == 0:
        print("\n四路亮度读取完成。")
    else:
        print(f"\n{failed} 路读取失败，请检查接线、串口号和控制器状态。")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
