# Original code from Alessandro Serrapica 
# https://github.com/Zeph1990/LSM6DS3-for-Raspberry-Pi/blob/master/LSM6DS3.py

import math
import Adafruit_GPIO.I2C as I2C


# Calibration voltage at 0g
zero_x = 1.569
zero_y = 1.569
zero_z = 1.569

# Standard sensitivity – 0.3 V/g
sensitivity_x = 0.3
sensitivity_y = 0.3
sensitivity_z = 0.3

class LSM6DS3:

    def __init__(self, address = 0x6a, debug = 0, pause = 0.8, adc_voltage = 5.0):
        # Default I2C address is 0x6a
        self.i2c = I2C.get_i2c_device(address)
        self.address = address

        # ADC reference voltage
        self.adc_voltage = adc_voltage

        # Setup I2C device
        dataToWrite = 0
        dataToWrite |= 0x03
        dataToWrite |= 0x00
        dataToWrite |= 0x10
        self.i2c.write8(0X10, dataToWrite)

        self.accel_center_x = self.i2c.readS16(0X28)
        self.accel_center_y = self.i2c.readS16(0x2A)
        self.accel_center_z = self.i2c.readS16(0x2C)


    def readRawAccelX(self):
    	output = self.i2c.readS16(0X28)
    	return output

    def readRawAccelY(self):
    	output = self.i2c.readS16(0x2A)
    	return output

    def readRawAccelZ(self):
    	output = self.i2c.readS16(0x2C)
    	return output


    def getXRotation(self):
        value_y = self.readRawAccelY()
        value_z = self.readRawAccelZ()

        yv=(value_y/1024.0*self.adc_voltage-zero_y)/sensitivity_y
        zv=(value_z/1024.0*self.adc_voltage-zero_z)/sensitivity_z
        # Calculates the angle between the Y and Z vectors. 
        # * 57.2957795 is for the conversion from radians to degrees. +180 is the offset
        angle_x =math.atan2(-yv,-zv)*57.2957795+180

        return angle_x

    def getYRotation(self):
        value_x = self.readRawAccelX()
        value_z = self.readRawAccelZ()

        xv=(value_x/1024.0*self.adc_voltage-zero_x)/sensitivity_x
        zv=(value_z/1024.0*self.adc_voltage-zero_z)/sensitivity_z
        # Calculates the angle between the X and Z vectors. 
        # * 57.2957795 is for the conversion from radians to degrees. +180 is the offset
        angle_y =math.atan2(-xv,-zv)*57.2957795+180

        return angle_y

    def getZRotation(self):
        value_x = self.readRawAccelX()
        value_y = self.readRawAccelY()

        xv=(value_x/1024.0*self.adc_voltage-zero_x)/sensitivity_x
        yv=(value_y/1024.0*self.adc_voltage-zero_y)/sensitivity_y
        # Calculates the angle between the Y and X vectors. 
        # * 57.2957795 is for the conversion from radians to degrees. +180 is the offset
        angle_z =math.atan2(-yv,-xv)*57.2957795+180

        return angle_z

    def readRawGyroX(self):
        output = self.i2c.readS16(0X22)
        return output

    def readFloatGyroX(self):
        output = self.calcGyro(self.readRawGyroX())
        return output