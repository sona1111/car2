#!/usr/bin/python

from Adafruit_I2C import Adafruit_I2C
import math
import logging

logr = logging.getLogger('car.Adafruit_LSM303')

# Minimal constants carried over from Arduino library
LSM303_ADDRESS_ACCEL = (0x32 >> 1)  # 0011001x
LSM303_ADDRESS_MAG   = (0x3C >> 1)  # 0011110x
                                         # Default    Type
LSM303_REGISTER_ACCEL_CTRL_REG1_A = 0x20 # 00000111   rw
LSM303_REGISTER_ACCEL_CTRL_REG4_A = 0x23 # 00000000   rw
LSM303_REGISTER_ACCEL_OUT_X_L_A   = 0x28
LSM303_REGISTER_MAG_CRB_REG_M     = 0x01
LSM303_REGISTER_MAG_MR_REG_M      = 0x02
LSM303_REGISTER_MAG_OUT_X_H_M     = 0x03

# Gain settings for setMagGain()
LSM303_MAGGAIN_1_3 = 0x20 # +/- 1.3
LSM303_MAGGAIN_1_9 = 0x40 # +/- 1.9
LSM303_MAGGAIN_2_5 = 0x60 # +/- 2.5
LSM303_MAGGAIN_4_0 = 0x80 # +/- 4.0
LSM303_MAGGAIN_4_7 = 0xA0 # +/- 4.7
LSM303_MAGGAIN_5_6 = 0xC0 # +/- 5.6
LSM303_MAGGAIN_8_1 = 0xE0 # +/- 8.1

class Compass(Adafruit_I2C):

    def __init__(self, busnum=-1, debug=False, hires=False):
    
        self.mag   = Adafruit_I2C(LSM303_ADDRESS_MAG  , busnum, debug)

        # Enable the magnetometer
        self.mag.write8(LSM303_REGISTER_MAG_MR_REG_M, 0x00)
        
        self.accel = Adafruit_I2C(LSM303_ADDRESS_ACCEL, busnum, debug)
        self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG1_A, 0x27)
       
        if hires:
            self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A,
              0b00001000)
        else:
            self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A, 0)

    # Interpret signed 16-bit magnetometer component from list
    def mag16(self, list, idx):
        n = (list[idx] << 8) | list[idx+1]   # High, low bytes
        return n if n < 32768 else n - 65536 # 2's complement signed

    # Interpret signed 12-bit acceleration component from list
    def accel12(self, list, idx):
        n = list[idx] | (list[idx+1] << 8) # Low, high bytes
        if n > 32767: n -= 65536           # 2's complement signed
        return n >> 4     

    def read(self):
        # Read the magnetometer
        l = self.mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
        comp = [abs(self.mag16(l, 0)),abs(self.mag16(l, 2)),self.mag16(l, 4)]
        
        
        
        heading = float(math.atan2(float(comp[1]/57.0) , float(comp[2]/57.0)))
        compassBearing = heading * (float(180.0) / float(math.pi));
        #if compassBearing < 0:
         #   compassBearing += 360
  
        '''
        l = self.accel.readList(LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80, 6)
        gravity = [self.accel12(l, 0), self.accel12(l, 2), self.accel12(l, 4)]
        
        rollAngle = math.atan2(gravity[1], gravity[2])

        pitchAngle = math.atan(-gravity[0] / ((gravity[1] * math.sin(rollAngle)) + (gravity[2] * math.cos(rollAngle))))

        yawAngle = math.atan2(
           (comp[2] * math.sin(rollAngle))
         - (comp[1] * math.cos(rollAngle))
        ,
           (comp[0] * math.cos(pitchAngle))
         + (comp[1] * math.sin(pitchAngle) * math.sin(rollAngle))
         + (comp[2] * math.sin(pitchAngle) * math.cos(rollAngle)))

        compassBearing = yawAngle * (180.0 / math.pi);
        '''

        return compassBearing
        
    def getHeading(self):
        return 0.0
        
    def getHeading3(self):
    
        al = self.accel.readList(LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80, 6)
        ax = float(self.accel12(al, 0))
        ay = float(self.accel12(al, 2))
        az = float(self.accel12(al, 4))
        
        cl = self.mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
        cx = float(self.mag16(cl, 0))
        cy = float(self.mag16(cl, 2))
        cz = float(self.mag16(cl, 4))
        
        ayf = ay/57.0 #why?
        axf = ax/57.0
        
        xh = (cx*math.cos(ayf))+(cy*math.sin(ayf))*(math.sin(axf))-(cz*math.cos(axf))*(math.sin(ayf))
        yh = (cy*math.cos(axf))+(cz*math.sin(axf))

        heading=math.atan2(float(yh),float(xh)) * (180.0 / math.pi) - 90; #angle in degrees
        if heading > 0:
            heading=heading-360
        heading += 360
 
        return heading
        
    def getHeading2(self):
    
        cl = self.mag.readList(LSM303_REGISTER_MAG_OUT_X_H_M, 6)
        cx = self.mag16(cl, 0) * 0.92
        cy = self.mag16(cl, 2) * 0.92
        cz = self.mag16(cl, 4) * 0.92
    
        
        #x_out = read_word_2c(3) * scale
        #y_out = read_word_2c(7) * scale
        #z_out = read_word_2c(5) * scale

        bearing  = math.atan2(cy, cx) 
        if (bearing < 0):
            bearing += 2 * math.pi


        
            
        return (math.degrees(bearing))



    def setMagGain(gain=LSM303_MAGGAIN_1_3):
        self.mag.write8(LSM303_REGISTER_MAG_CRB_REG_M, gain)
        
class Accelerometer(Adafruit_I2C):

    def __init__(self, busnum=-1, debug=False, hires=False):
        
        self.accel = Adafruit_I2C(LSM303_ADDRESS_ACCEL, busnum, debug)
        self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG1_A, 0x27)
       
        if hires:
            self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A,
              0b00001000)
        else:
            self.accel.write8(LSM303_REGISTER_ACCEL_CTRL_REG4_A, 0)

    # Interpret signed 12-bit acceleration component from list
    def accel12(self, list, idx):
        n = list[idx] | (list[idx+1] << 8) # Low, high bytes
        if n > 32767: n -= 65536           # 2's complement signed
        return n >> 4                      # 12-bit resolution

    def read(self):
        # Read the accelerometer
        list = self.accel.readList(
          LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80, 6)
        res = [( self.accel12(list, 0),
                 self.accel12(list, 2),
                 self.accel12(list, 4) )]

        return res


# Simple example prints accel/mag data once per second:
if __name__ == '__main__':

    from time import sleep

    compass = Compass()
    accell = Accelerometer()
    

    print '[(Accelerometer X, Y, Z), (Magnetometer X, Y, Z, orientation)]'
    while True:
        print 'compass',
        print compass.read()
        print 'accell',
        print accell.read()
        sleep(1) # Output is fun to watch if this is commented out
