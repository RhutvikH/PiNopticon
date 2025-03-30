import cv2
import numpy as np

# Initialize MobileNet-SSD (fast for laptops)
# net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt', 'MobileNetSSD_deploy.caffemodel')
# classes = ["background", "person", "car", "dog", ...]  # COCO classes

cap = cv2.VideoCapture('http://<Pi_IP>:5000/video_feed')

while True:
    ret, frame = cap.read()
    if not ret: break
    
    # Object detection
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    # Draw bounding boxes
    for i in range(detections.shape[2]):
        confidence = detections[0,0,i,2]
        if confidence > 0.5:  # Threshold
            class_id = int(detections[0,0,i,1])
            box = detections[0,0,i,3:7] * np.array([frame.shape[1], frame.shape[0]]*2)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)
            cv2.putText(frame, f"{classes[class_id]}: {confidence:.2f}", 
                        (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    cv2.imshow('Pi Stream Detection', frame)
    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()