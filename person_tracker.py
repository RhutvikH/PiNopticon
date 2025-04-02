import cv2
import time
import requests
from ultralytics import YOLO

# ------ Configuration ------
PI_SERVER_URL = 'http://192.168.240.71:5000'  # Raspberry Pi's IP address
VIDEO_STREAM_URL = f'{PI_SERVER_URL}/video_feed'
MODEL_PATH = 'models/yolov8n.pt'  # YOLOv8 nano model for person detection

# YOLO model initialization
model = YOLO(MODEL_PATH)
PERSON_CLASS_ID = 0  # Class 0 is 'person'

# Servo angle settings
BASE_ANGLE = 90              # Servo's neutral position
MAX_OFFSET_ANGLE = 30        # Maximum angle change from center
SERVO_UPDATE_INTERVAL = 0.5  # Minimum interval between updates (so that it doesnt rapidly move)
ALPHA = 0.1                  # Smoothing factor (0 < alpha <= 1) (to smoothen out the movement)
ANGLE_CHANGE_THRESHOLD = 2.0 # Minimum angle change to trigger update (degrees)

def compute_servo_angle(frame_width, bbox_center_x):
    """
    Map the horizontal position of a bounding box's center to a servo angle.
    """
    center_x = frame_width / 2 ## center of screen
    offset = -bbox_center_x + center_x
    norm_offset = offset / center_x  # Normalized offset in [-1, 1]
    angle_adjustment = norm_offset * MAX_OFFSET_ANGLE # to move the camera accordingly
    servo_angle = BASE_ANGLE + angle_adjustment
    return max(0, min(180, servo_angle))  # Clamp to [0, 180]

def send_servo_angle(angle):
    """
    Send a new target servo angle to the Pi.
    """
    try:
        angle = float(angle)
        response = requests.post(f"{PI_SERVER_URL}/servo", json={'angle': angle}) ## send requests to change the angle
        if response.status_code == 200:
            print(f"Servo angle updated to {angle:.2f}")
        else:
            print("Failed to update servo angle:", response.text)
            
    except Exception as e:
        print("Error sending servo angle:", e)

# ------ Video Stream Setup ------
cap = cv2.VideoCapture(VIDEO_STREAM_URL)
if not cap.isOpened():
    print("Error: Unable to open video stream!")
    exit()

# Initialize variables
last_servo_update = time.time()
smoothed_angle = BASE_ANGLE  # Start at neutral position
last_sent_angle = BASE_ANGLE # Track the last angle sent to the servo

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from stream.")
        break

    frame_height, frame_width = frame.shape[:2]

    # Run YOLOv8 detection
    results = model(frame, verbose=False)[0]
    persons = [r for r in results.boxes.data.cpu().numpy() if int(r[5]) == PERSON_CLASS_ID]

    # Calculate target angle
    target_angle = BASE_ANGLE  # Default if no person detected
    if persons:
        chosen_bbox = max(persons, key=lambda x: (x[2]-x[0]) * (x[3]-x[1]))
        x1, y1, x2, y2, conf, cls = chosen_bbox
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"Person: {conf:.2f}", (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        bbox_center_x = (x1 + x2) / 2
        target_angle = compute_servo_angle(frame_width, x1)

    # Smooth the target angle
    smoothed_angle = ALPHA * target_angle + (1 - ALPHA) * smoothed_angle

    # Send update if interval has passed and angle change is significant
    current_time = time.time()
    if current_time - last_servo_update >= SERVO_UPDATE_INTERVAL:
        if abs(smoothed_angle - last_sent_angle) > ANGLE_CHANGE_THRESHOLD:
            send_servo_angle(smoothed_angle)
            last_sent_angle = smoothed_angle
            last_servo_update = current_time

    # Display frame for debugging
    cv2.imshow("Live Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()