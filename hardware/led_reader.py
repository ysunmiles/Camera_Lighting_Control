"""
DPS1024-4T-125 数字光源控制器：读取指定通道当前亮度。

本模块只负责“读取当前亮度值”这一任务，自包含串口处理，
不依赖队友的 LED_control.py，两份代码可在同一程序中分别导入、协同运行。

协议（说明书 3.3 节）：
- 串口：RS232，19200 波特率，8 数据位，1 停止位，无校验（8N1）。
- 查询帧：S + 通道(A~D) + #，例如 SA#。
- 应答：小写通道字母 + 4 位亮度值，例如 a0168。

待真机核对（以控制器手册 3.3 节为准）：
- 应答帧末尾是否带结束符（\\r\\n、# 等）；当前正则允许可选的
  尾随换行/井号，若手册规定固定结束符，请收紧 RESPONSE_PATTERN。
- 亮度值是否固定 4 位补零；若设备回 3 位数字，需调整正则位数。

协同用法示例：
    from hardware import LED_control   # 队友：开灯 / 调光
    from hardware import led_reader     # 本模块：回读亮度

    LED_control.initCOM("COM4")
    led_reader.initCOM("COM4")

    LED_control.setLightness(1, 168)
    value = led_reader.readLightness(1)
"""

import re

import serial

# RS232 串口参数（与说明书一致）
BAUDRATE = 19200
BYTESIZE = serial.EIGHTBITS
STOPBITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
READ_TIMEOUT = 1.0

# 应答整帧格式：小写通道字母 + 4 位十进制亮度，末尾允许可选的换行 / 井号结束符。
# 使用 fullmatch 校验整帧，回包前后夹有杂质、串入其他通道数据都会被拒绝。
# 注意：若手册规定固定结束符（如必须以 \r\n 结尾），请在此收紧。
RESPONSE_PATTERN = re.compile(r"[a-d](\d{4})[\r\n#]*")

# 模块级串口号，由 initCOM 设置；readLightness 也可直接传入 port 覆盖
_port = ""


def initCOM(com_str: str) -> None:
    """
    初始化串口号。
    Args:
        com_str: 串口名称，例如 "COM4"。
    """
    global _port
    _port = com_str


def _led_char(led_number: int) -> str:
    """LED 编号 1~4 -> 控制器通道字母 A~D（读取应答中通道回显为小写 a~d）。"""
    mapping = {1: "A", 2: "B", 3: "C", 4: "D"}
    if led_number not in mapping:
        raise ValueError(f"LED 编号需为 1~4，收到: {led_number}")
    return mapping[led_number]


def _open(port: str) -> serial.Serial:
    """按手册参数（19200, 8N1）打开串口，并清掉残留缓冲。"""
    if not port:
        raise serial.SerialException(
            "串口号未初始化，请先调用 initCOM(\"COMx\")，或在 readLightness 中传入 port"
        )
    ser = serial.Serial(
        port,
        baudrate=BAUDRATE,
        bytesize=BYTESIZE,
        stopbits=STOPBITS,
        parity=PARITY,
        timeout=READ_TIMEOUT,
    )
    # 清掉上一条命令残留在输入缓冲里的应答，避免污染本次读取
    ser.reset_input_buffer()
    return ser


def _query(message_str: str, port: str) -> str:
    """发送查询指令并读取应答文本（严格 UTF-8 解码，去除首尾空白）。

    解码失败（含非法字节）时直接抛出 UnicodeDecodeError，不静默丢弃字节。
    """
    with _open(port) as ser:
        ser.write(message_str.encode("utf-8"))
        ser.flush()
        # 优先按行读取；若设备不回换行符，再把缓冲内剩余字节一次性读出
        raw = ser.readline()
        if not raw and ser.in_waiting:
            raw = ser.read(ser.in_waiting)
    # 严格解码：无法解码的字节必须显式报错，不能 errors="ignore" 静默丢弃
    return raw.decode("utf-8", errors="strict").strip()


def readLightness(led_number: int, port: str = "") -> int:
    """
    读取指定 LED 当前亮度值。
    Args:
        led_number: LED 编号 1~4。
        port: 可选串口号（如 "COM4"）；为空时使用 initCOM 设置的端口。
    Returns:
        亮度值 0~255。
    Raises:
        ValueError: 编号非法、应答超时/格式异常或亮度越界时抛出。
        serial.SerialException: 串口未找到、无法打开或通信失败时抛出。
    """
    use_port = port or _port
    led_char = _led_char(led_number)
    query = f"S{led_char}#"
    response = _query(query, use_port)

    if not response:
        raise ValueError(f"通道 {led_number} 读取超时，未收到控制器应答（查询帧: {query}）")

    # 整帧校验：通道小写字母 + 4 位亮度；fullmatch 拒绝前后杂质、串道数据。
    match = RESPONSE_PATTERN.fullmatch(response)
    if not match:
        raise ValueError(f"通道 {led_number} 应答格式异常: {response!r}（查询帧: {query}）")

    # 校验回显通道与请求通道一致，防止串错通道的回包被误读。
    if response[0] != led_char.lower():
        raise ValueError(
            f"通道 {led_number} 应答串道: 回包首字母为 {response[0]!r}（查询帧: {query}，应答: {response!r}）"
        )

    lightness_value = int(match.group(1))
    if not 0 <= lightness_value <= 255:
        raise ValueError(f"通道 {led_number} 亮度值越界: {lightness_value}（应为 0~255）")
    return lightness_value
