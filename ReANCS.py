import serial
import time



with serial.Serial(
        port='/dev/serial0', baudrate=9600, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1) as ser:
    ser.write("WAKEUP".encode())
    for i in range(2):
        ser.readline()
        time.sleep(0.5)
    ser.write("AT".encode())
    while True:
        x = ser.readline()
        print(x)
        time.sleep(0.5)



    print(f"Serial port {ser.name} opened successfully.")

