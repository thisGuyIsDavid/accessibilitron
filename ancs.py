import serial



class ANCSiousReader:
    serial = None

    def __init__(self):
        self.is_running = True

    def set_serial(self):
        self.serial = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def process_read_line(self, read_line):
        read_line = read_line.decode('utf-8')
        message_array = read_line.split('OK+ANCS')
        for message in message_array:
            # messages must be nine characters long to analyze.
            if len(message) == 9:
                self.process_ancs_message(message)

    def process_ancs_message(self, message):
        print(message)

        if message[1:2] != "0":
            return

        message_type = message[2:3]

        if message_type == '1': # phone call
            print('phone call')
        elif message_type == '4': # text message
            print('text')

        elif message_type == '9': # slack
            print('slack')

        else:
            print(message_type)

    def process(self):
        self.set_serial()

        # start up command to check if HM-10 is working.
        print("SENDING \"AT\" to HM-10")
        self.serial.write("AT".encode())

        print("STARTING SERIAL READ")

        while True:
            message = self.serial.readline()
            if message == "":
                continue
            self.process_read_line(message)

    def shutdown(self):
        pass

    def run(self):
        try:
            self.process()
        except KeyboardInterrupt as ki:
            pass
        except Exception as e:
            with open('errorlog.txt', 'w') as error_log:
                error_log.write(str(e))
        finally:
            self.serial.close()
            self.shutdown()

ANCSiousReader().run()
