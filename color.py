import serial, time

class Color(object):
    def __init__(self, r = 0, g = 0, b = 0):
        self.r = r
        self.g = g
        self.b = b
    def toBytes(self):
        return [
            chr(self.g),
            chr(self.r),
            chr(self.b)
        ]

    def __repr__(self):
        return "<Color: ({0}, {1}, {2})>".format(self.r, self.g, self.b)

class LedStrip(object):
    MSG_SETRANGE = 0x1
    MSG_LERPRANGE = 0x2
    MSG_SETVALUES = 0x3
    def __init__(self, numLEDs, ser):
        self.numLEDs = numLEDs
        self.ser = ser
    def start(self):
        print "Waiting for serial device"
        while(not self.ser.inWaiting()):
            self.ser.write(chr(self.numLEDs))
            time.sleep(0.1)
        print ser.readline()
    def SetValues(self, colors):
        msg = [chr(LedStrip.MSG_SETVALUES)]
        msg += sum([color.toBytes() for color in colors], [])
        self.ser.write(msg)
        return int(ord(self.ser.read()))
    def SetRange(self, color, start, end):
        msg = [chr(LedStrip.MSG_SETRANGE)]
        msg += color.toBytes()
        msg += chr(start)
        msg += chr(end)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    def LerpRange(self, color, start, end, steps, delay):
        msg = [chr(LedStrip.MSG_LERPRANGE)]
        msg += color.toBytes()
        msg += chr(start)
        msg += chr(end)
        msg += chr(steps)
        msg += chr(delay)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    def close(self):
        self.ser.close()


ser = serial.Serial(
    port='COM4',
    baudrate=115200,
    timeout = 5
)

leds = LedStrip(24, ser)

try:
    leds.start()
    time.sleep(0.5)
    leds.SetRange(Color(100,100,100), 0, 23)
    c = Color(0, 0, 0)
    colors = [Color(i * 5, i * 5, i * 5) for i in range(24)]
    leds.SetValues(colors)
    time.sleep(5)
    leds.SetRange(Color(255,0,0), 0, 10)
    leds.SetRange(Color(0,255,0), 11, 23)
    leds.LerpRange(Color(255, 255, 255), 0, 23, 10, 100)
    leds.LerpRange(Color(0, 0, 0), 0, 23, 10, 100)
finally:
    leds.close()