import cv2
import numpy as np

# Initialize Webcam
cap = cv2.VideoCapture(0)

def detect_health():
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Image Pre-processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. Define Color Masks (Fine-tuned for Expo Lighting)
        # Red (Fruit)
        r_low, r_up = np.array([0, 120, 70]), np.array([10, 255, 255])
        # Green (Leaves)
        g_low, g_up = np.array([35, 40, 40]), np.array([85, 255, 255])
        # Brown/Black (Defects)
        b_low, b_up = np.array([10, 40, 20]), np.array([30, 255, 100])

        mask_red = cv2.inRange(hsv, r_low, r_up)
        mask_green = cv2.inRange(hsv, g_low, g_up)
        mask_brown = cv2.inRange(hsv, b_low, b_up)

        # 3. Analyze Results
        status = "System: Scanning..."
        color = (255, 255, 255)

        # Detect Contours and draw boxes
        for mask, label, box_color in [(mask_red, "HEALTHY FRUIT", (0, 0, 255)), 
                                       (mask_green, "HEALTHY LEAF", (0, 255, 0)), 
                                       (mask_brown, "DEFECT DETECTED", (0, 75, 150))]:
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 1500: # Filter noise
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
                    
                    if label == "DEFECT DETECTED":
                        status = "ALERT: FUNGAL/DISEASE DETECTED"
                        color = (0, 0, 255)

        # 4. Display Dashboard
        cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
        cv2.putText(frame, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.imshow("AgriScan AI - Fixed Station", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

detect_health()