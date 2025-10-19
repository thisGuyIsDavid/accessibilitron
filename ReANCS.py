import serial
import time



with serial.Serial(
        port='/dev/serial0', baudrate=9600, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0) as ser:
    ser.write("AT+ADDR?\r\n".encode('utf-8'))
    while True:
        x = ser.read()
        print(x)
        time.sleep(0.5)



    print(f"Serial port {ser.name} opened successfully.")

