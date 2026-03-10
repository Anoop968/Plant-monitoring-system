import cv2
import numpy as np
import requests  # Replaces 'serial'
import smtplib
import time
from email.message import EmailMessage

# --- CONFIGURATION ---
# Replace this with the IP address displayed in your Arduino Serial Monitor
ESP_IP = "172.31.172.7 " 
PUMP_URL = f"http://{ESP_IP}/pump"

EMAIL_ID = "an2177287@gmail.com"
EMAIL_PASS = "kknu lwci fsxc"
RECEIVER_EMAIL = "target-email@gmail.com"

# Initialize Webcam
cap = cv2.VideoCapture(0)

# Cooldown variables
last_email_time = 0
last_pump_time = 0

def trigger_pump_wifi():
    """Sends a WiFi command to the ESP8266 to trigger the pump."""
    try:
        # Use a short timeout so the video feed doesn't lag if WiFi is slow
        response = requests.get(PUMP_URL, timeout=2)
        if response.status_code == 200:
            print("WiFi Command Sent: Pump Activated!")
        else:
            print(f"Server reached but error returned: {response.status_code}")
    except Exception as e:
        print(f"WiFi Connection Failed: {e}")

def send_photo_email(frame):
    try:
        msg = EmailMessage()
        msg['Subject'] = "AgriScan AI: Healthy Fruit Detected"
        msg['From'] = EMAIL_ID
        msg['To'] = RECEIVER_EMAIL
        msg.set_content("A healthy fruit has been detected. See attached image.")

        _, buffer = cv2.imencode('.jpg', frame)
        msg.add_attachment(buffer.tobytes(), maintype='image', subtype='jpeg', filename='detected_fruit.jpg')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ID, EMAIL_PASS)
            smtp.send_message(msg)
        print("Email Sent!")
    except Exception as e:
        print(f"Email failed: {e}")

def detect_health():
    global last_email_time, last_pump_time
    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Image Pre-processing
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. Define Color Masks
        r_low, r_up = np.array([0, 120, 70]), np.array([10, 255, 255])
        g_low, g_up = np.array([35, 40, 40]), np.array([85, 255, 255])
        b_low, b_up = np.array([10, 40, 20]), np.array([30, 255, 100])

        mask_red = cv2.inRange(hsv, r_low, r_up)
        mask_green = cv2.inRange(hsv, g_low, g_up)
        mask_brown = cv2.inRange(hsv, b_low, b_up)

        # 3. Analyze Results
        status = "System: Scanning..."
        color = (255, 255, 255)

        for mask, label, box_color in [(mask_red, "HEALTHY FRUIT", (0, 0, 255)), 
                                       (mask_green, "HEALTHY LEAF", (0, 255, 0)), 
                                       (mask_brown, "DEFECT DETECTED", (0, 75, 150))]:
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                if cv2.contourArea(cnt) > 1500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
                    
                    # --- WIFI TRIGGER ON DEFECT ---
                    if label == "DEFECT DETECTED":
                        status = "ALERT: FUNGAL/DISEASE DETECTED"
                        color = (0, 0, 255)
                        if (time.time() - last_pump_time > 8): # Slightly higher cooldown for WiFi
                            trigger_pump_wifi()
                            last_pump_time = time.time()

                    # --- EMAIL PHOTO ON FRUIT ---
                    if label == "HEALTHY FRUIT":
                        if time.time() - last_email_time > 60:
                            send_photo_email(frame)
                            last_email_time = time.time()

        # 4. Display Dashboard
        cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
        cv2.putText(frame, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.imshow("AgriScan AI - WiFi Edition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_health()