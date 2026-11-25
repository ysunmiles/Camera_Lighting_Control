import serial

COM = ""

def initCOM(com_str: str) -> None:
    """
    初始化串口号。
    Args:
        com_str: 串口名称，例如 "COM4"。
    """
    global COM
    COM = com_str

# initCOM("COM4")

def serialSend(message_str: str) -> None:
    """
    向已初始化的串口发送一条 UTF-8 编码的文本数据。
    Args:
        message_str: 要发送的串口字符串，例如 "SA0255#"。
    Raises:
        serial.SerialException: 串口未找到、无法打开或通信失败时抛出。
    """
    with serial.Serial(COM, baudrate=19200, timeout=1) as ser:
        ser.write(message_str.encode("utf-8"))

# serialSend("S_CTRL:XXXX#")

def setControlMode(mode: str) -> None:
    """
    设置控制器的常亮常灭模式。
    Args:
        mode: "0001" 表示常亮，"0000" 表示常灭。
    Raises:
        ValueError: mode 不是说明书规定的模式时抛出。
        serial.SerialException: 串口未找到、无法打开或通信失败时抛出。
    """
    if mode not in ("0000", "0001"):
        raise ValueError("mode 只能是 '0000'（常灭）或 '0001'（常亮）")

    serialSend(f"S_CTRL:{mode}#")


def turnOn() -> None:
    """设置控制器为常亮模式。"""
    setControlMode("0001")


def turnOff() -> None:
    """设置控制器为常灭模式。"""
    setControlMode("0000")


def readControlMode() -> str:
    """
    读取控制器的常亮常灭模式。
    Returns:
        "0001" 表示常亮，"0000" 表示常灭。
    Raises:
        serial.SerialException: 串口未找到、无法打开或通信失败时抛出。
        ValueError: 未收到应答或应答格式异常时抛出。
    """
    with serial.Serial(COM, baudrate=19200, timeout=1) as ser:
        ser.write(b"S_CTRL:#")
        response = ser.readline().decode("utf-8", errors="ignore").strip()

    if not response:
        raise ValueError("读取常亮常灭模式超时，未收到控制器应答")

    if response.startswith("_ctrl:"):
        mode = response.split(":", 1)[1]
        if mode in ("0000", "0001"):
            return mode

    raise ValueError(f"控制器应答格式异常: {response!r}")

def setLightness(led_number: int, lightness_value: int):
    """
    设定
    Args:
        led_number: 指定LED编号如，1~4。
        lightness_value: 设定亮度值，0~255。
    Raises:
        serial.SerialException: 串口未找到、无法打开或通信失败时抛出。
    """
    if led_number == 1:
        led_number_str = "A"
    elif led_number == 2:
        led_number_str = "B"
    elif led_number == 3:
        led_number_str = "C"
    elif led_number == 4:
        led_number_str = "D"
    
    lightness_value_str = f"{lightness_value:04d}"
    
    message = f"S{led_number_str}{lightness_value_str}#"

    serialSend(message)

