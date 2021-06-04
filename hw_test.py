from libraries.hardware_interfacer import MotorShield
import tweaking, gpiozero, time

motor = MotorShield()
servo = gpiozero.AngularServo(tweaking.servo_pin)

servo.angle = tweaking.servo_left

while True:
    for i in range(0, 10):
        print(float(i) / 10)
        motor.drive_forwards(float(i) / 100)
        servo.angle = 1.0 - servo.angle
        time.sleep(1)