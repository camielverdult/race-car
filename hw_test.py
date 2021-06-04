from libraries.hardware_interfacer import MotorShield
import tweaking, gpiozero, time

motor = MotorShield()
servo = gpiozero.AngularServo(tweaking.servo_pin)

for i in range(0, 1.0, 0.01):
    print(i)
    motor.drive_forwards(i)
    time.sleep(0.1)