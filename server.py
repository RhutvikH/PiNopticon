### On the Raspberry Pi

import threading
import time
import cv2
import RPi.GPIO as GPIO
from flask import Flask, Response, request
from picamera2 import Picamera2

app = Flask(__name__)

# ----- Servo Setup -----
SERVO_PIN = 11  # GPIO pin (using BOARD numbering)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Global variables for smooth servo motion
current_servo_angle = 90.0  # starting at the center (90°)
servo_lock = threading.Lock()

def smooth_set_servo_angle(target_angle, step=1.0, delay=0.02):
    """
    Gradually update the servo angle from the current angle to target_angle.
    step: the increment (or decrement) for each update.
    delay: time (in seconds) to wait between updates.
    """
    global current_servo_angle
    with servo_lock:
        # Determine direction and smoothly update
        while abs(current_servo_angle - target_angle) > 0.5:
            if current_servo_angle < target_angle:
                current_servo_angle = min(current_servo_angle + step, target_angle)
            else:
                current_servo_angle = max(current_servo_angle - step, target_angle)
            duty = (current_servo_angle / 18.0) + 2
            pwm.ChangeDutyCycle(duty)
            time.sleep(delay)
        # Ensure the final angle is reached
        duty = (target_angle / 18.0) + 2
        pwm.ChangeDutyCycle(duty)
        time.sleep(delay)
        current_servo_angle = target_angle
        pwm.ChangeDutyCycle(0)

# ----- Camera Setup -----
picam2 = Picamera2()
picam2.start()

def generate_frames():
    """Continuously capture frames from the camera and yield JPEG-encoded images."""
    while True:
        frame = picam2.capture_array()
        # Convert RGB to BGR for proper color display in OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ----- Flask Routes -----
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Returns a multipart response with JPEG frames."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to update servo status
@app.route('/servo', methods=['POST'])
def servo():
    """
    Servo control route. Expects a JSON payload with an 'angle' field.
    The angle should be between 0 and 180.
    """
    data = request.get_json()
    if not data or 'angle' not in data:
        return 'Angle not provided', 400

    try:
        target_angle = float(data['angle'])
        if target_angle < 0 or target_angle > 180:
            return 'Invalid angle. Must be between 0 and 180.', 400
        # Run the servo update in a separate thread to avoid blocking the stream.
        threading.Thread(target=smooth_set_servo_angle, args=(target_angle,)).start()
        return f'Servo angle set to {target_angle}', 200
    except Exception as e:
        return f'Error: {e}', 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        pwm.stop()
        GPIO.cleanup()
