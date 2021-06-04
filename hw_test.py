from libraries.hardware_interfacer import MotorShield
import tweaking, gpiozero, time

motor = MotorShield()
servo = gpiozero.AngularServo(tweaking.servo_pin)

servo.angle = tweaking.servo_middle

async for i in range(0, 100):
    print(float(i) / 100)
    motor.drive_forwards(float(i) / 100)
    time.sleep(0.1)