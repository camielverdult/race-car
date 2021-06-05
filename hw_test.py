from libraries.hardware_interfacer import MotorShield
import tweaking, gpiozero, time

motor = MotorShield()
servo = gpiozero.AngularServo(tweaking.servo_pin)

servo.angle = tweaking.servo_middle

motor.drive_forwards(0.03)
time.sleep(100)