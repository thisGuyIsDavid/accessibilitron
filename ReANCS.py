import serial

with serial.Serial(
        port='/dev/serial0', baudrate=9600, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1) as ser:
    serial.write("WAKEUP".encode())
    print(serial.readline())

    print(f"Serial port {ser.name} opened successfully.")

