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

