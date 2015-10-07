import serial, time
import jrpc

def colortoBytes(color):
    return [
        chr(color['g']),
        chr(color['r']),
        chr(color['b'])
    ]

class LedStrip(jrpc.service.SocketObject):
    MSG_SETRANGE = 0x1
    MSG_LERPRANGE = 0x2
    MSG_SETVALUES = 0x3
    def __init__(self, numLEDs, ser):
        jrpc.service.SocketObject.__init__(self, 50001, debug = True)
        self.numLEDs = numLEDs
        self.ser = ser
    def pre_run(self):
        jrpc.service.SocketObject.pre_run(self)
        print "Waiting for serial device"
        while(not self.ser.inWaiting()):
            self.ser.write(chr(self.numLEDs))
            time.sleep(0.1)
        print ser.readline()
    def SetValues(self, colors):
        msg = [chr(LedStrip.MSG_SETVALUES)]
        msg += sum([colortoBytes(color) for color in colors], [])
        self.ser.write(msg)
        return int(ord(self.ser.read()))
    @jrpc.service.method
    def SetRange(self, color, start, end):
        msg = [chr(LedStrip.MSG_SETRANGE)]
        msg += colortoBytes(color)
        msg += chr(start)
        msg += chr(end)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    def LerpRange(self, color, start, end, steps, delay):
        msg = [chr(LedStrip.MSG_LERPRANGE)]
        msg += colortoBytes(color)
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
leds.pre_run()
leds.running = True
leds.run()

#try:
#    leds.start()
#    time.sleep(0.5)
#    leds.SetRange(Color(255,255,255), 0, 23)
#    exit()
#    while(True):
#        leds.SetRange(Color(100,100,100), 0, 23)
#        leds.LerpRange(Color(0, 0, 0), 10, 23, 100, 4)
#        leds.LerpRange(Color(100,100,100), 10, 23, 100, 4)
#
#    c = Color(0, 0, 0)
#    colors = [Color(i * 5, i * 5, i * 5) for i in range(24)]
#    leds.SetValues(colors)
#    time.sleep(5)
#    leds.SetRange(Color(255,0,0), 0, 10)
#    leds.SetRange(Color(0,255,0), 11, 23)
#    leds.LerpRange(Color(255, 255, 255), 0, 23, 10, 100)
#    leds.LerpRange(Color(0, 0, 0), 0, 23, 10, 100)
#finally:
#    leds.close()