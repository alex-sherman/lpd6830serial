import serial, time
import jrpc
from jrpc.reflection import NUMBER
from threading import Thread
import random

class COLOR(jrpc.reflection.RPCType):
    r = NUMBER(0, 255)
    g = NUMBER(0, 255)
    b = NUMBER(0, 255)

def colortoBytes(color):
    return [
        chr(min(255, max(0, color['g']))),
        chr(min(255, max(0, color['r']))),
        chr(min(255, max(0, color['b'])))
    ]

class Animation(Thread):
    def __init__(self, strip):
        Thread.__init__(self)
        self.strip = strip
        self.init()
        self._lastCall = 0
        self.running = True
    def start(self):
        self._lastCall = time.time()
        Thread.start(self)
    def stop(self):
        self.running = False
    def run(self):
        while(self.running):
            now = time.time()
            diff = now - self._lastCall
            self._lastCall = now
            self.update(diff)
        time.sleep(0.1)

    def init(self):
        pass
    def update(self, dt):
        pass

class GreenGlow(Animation):
    def init(self):
        self.increasing = True
        self.values = [0] * self.strip.numLEDs

    def update(self, dt):
        self.values = [random.randrange(0, 255) if random.random() < 0.1 else 0 for i in range(self.strip.numLEDs)]
        self.strip.LerpValues([{"r": 0, "g": value, "b": 0} for value in self.values], 100, 3)

class FireAnimation(Animation):
    def init(self):
        self.increasing = True
        self.values = [0] * self.strip.numLEDs

    def update(self, dt):
        self.values = [max(random.randrange(0, 285) - 50, 0) for i in range(self.strip.numLEDs)]
        self.strip.LerpValues([{"r": value, "g": value / 10, "b": 0} for value in self.values], 100, 5)
        #time.sleep(0.1)

class LedStrip(jrpc.service.SocketObject):
    MSG_SETRANGE = 0x1
    MSG_LERPRANGE = 0x2
    MSG_SETVALUES = 0x3
    MSG_LERPVALUES = 0x4
    def __init__(self, numLEDs, ser):
        jrpc.service.SocketObject.__init__(self, 50001, debug = True)
        self.numLEDs = numLEDs
        self.ser = ser
        self.animations = {
            "fire": FireAnimation,
            "green": GreenGlow
        }
        self.animation = None
    def pre_run(self):
        jrpc.service.SocketObject.pre_run(self)
        print "Waiting for serial device"
        while(not self.ser.inWaiting()):
            self.ser.write(chr(self.numLEDs))
            time.sleep(0.1)
        print ser.readline()
        self.StartAnimation("green")

    @jrpc.service.method
    def SetValues(self, colors):
        msg = [chr(LedStrip.MSG_SETVALUES)]
        msg += sum([colortoBytes(color) for color in colors], [])
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    @jrpc.service.method
    def LerpValues(self, colors, steps, delay):
        msg = [chr(LedStrip.MSG_LERPVALUES)]
        msg += sum([colortoBytes(color) for color in colors], [])
        msg += chr(steps)
        msg += chr(delay)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    @jrpc.service.method(COLOR(), NUMBER(), NUMBER())
    def SetRange(self, color, start, end):
        msg = [chr(LedStrip.MSG_SETRANGE)]
        msg += colortoBytes(color)
        msg += chr(start)
        msg += chr(end)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    @jrpc.service.method
    def LerpRange(self, color, start, end, steps, delay):
        msg = [chr(LedStrip.MSG_LERPRANGE)]
        msg += colortoBytes(color)
        msg += chr(start)
        msg += chr(end)
        msg += chr(steps)
        msg += chr(delay)
        self.ser.write(msg)
        return int(ord(self.ser.read()))

    @jrpc.service.method
    def GetAnimations(self):
        return self.animations.keys()

    @jrpc.service.method
    def StartAnimation(self, name):
        self.StopAnimation()
        self.animation = self.animations[name](self)
        self.animation.start()
        return name

    @jrpc.service.method
    def StopAnimation(self):
        if self.animation != None:
            self.animation.stop()
            self.animation.join()
            self.animation = None


    def close(self):
        self.ser.close()
        self.StopAnimation()

ser = serial.Serial(
    port='COM4',
    baudrate=115200,
    timeout = 5
)
leds = LedStrip(24, ser)
leds.pre_run()
leds.running = True
try:
    leds.run()
finally:
    leds.close()

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