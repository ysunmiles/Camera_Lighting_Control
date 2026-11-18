import serial

def serialSend(str):
    with serial.Serial("COM4", baudrate=19200, timeout=1) as ser:
        ser.write(str.encode("utf-8"))

serialSend("SB0000#")

def LEDSet(LEDNub, Lightness):
    