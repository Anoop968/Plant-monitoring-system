import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
import threading
import serial
import smtplib
from email.message import EmailMessage
import time

# --- CONFIGURATION (UPDATE THESE) ---
SERIAL_PORT = 'COM3'      # Your ESP8266 COM port
EMAIL_ID = "your-email@gmail.com"
EMAIL_PASS = "your-app-password" # Get this from Google App Passwords
RECEIVER_EMAIL = "target-email@gmail.com"

# --- GLOBAL STATES ---
is_scanning = False
last_email_time = 0

# Initialize Serial for Pump
try:
    ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
except:
    ser = None
    print("Warning: ESP8266 not found. Pump logic disabled.")

# --- LOGIC FUNCTIONS ---

def send_alert_email():
    global last_email_time
    # Cooldown: Only send one email every 2 minutes so you don't get blocked
    if time.time() - last_email_time < 120:
        return
    
    try:
        msg = EmailMessage()
        msg.set_content("AgriScan AI Alert: A ripe fruit has been detected. The automated irrigation system has been triggered.")
        msg['Subject'] = "🌱 AgriScan AI: Fruit Detection Report"
        msg['From'] = EMAIL_ID
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ID, EMAIL_PASS)
            server.send_message(msg)
        
        last_email_time = time.time()
        print("Report Emailed Successfully.")
    except Exception as e:
        print(f"Email Error: {e}")

def detect_health_loop():
    global is_scanning
    cap = cv2.VideoCapture(0)
    
    while True:
        if is_scanning:
            ret, frame = cap.read()
            if not ret: break

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Color Masks
            r_low, r_up = np.array([0, 120, 70]), np.array([10, 255, 255])
            g_low, g_up = np.array([35, 40, 40]), np.array([85, 255, 255])
            b_low, b_up = np.array([10, 40, 20]), np.array([30, 255, 100])

            mask_red = cv2.inRange(hsv, r_low, r_up)
            mask_green = cv2.inRange(hsv, g_low, g_up)
            mask_brown = cv2.inRange(hsv, b_low, b_up)

            current_status = "System: Scanning..."
            status_color = (255, 255, 255)

            # Analyze Objects
            for mask, label, box_color in [(mask_red, "FRUIT", (0, 0, 255)), 
                                           (mask_green, "LEAF", (0, 255, 0)), 
                                           (mask_brown, "DEFECT", (0, 75, 150))]:
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    if cv2.contourArea(cnt) > 2000:
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)
                        
                        if label == "FRUIT":
                            current_status = "FRUIT DETECTED - PUMPING"
                            # 1. Trigger Pump via ESP8266
                            if ser: ser.write(b'P') 
                            # 2. Trigger Email in separate thread
                            threading.Thread(target=send_alert_email, daemon=True).start()
                        
                        if label == "DEFECT":
                            current_status = "DEFECT DETECTED - ALERT"
                            status_color = (0, 0, 255)

            # Update the GUI Dashboard Text
            update_ui_report(current_status)
            
            # Top Banner for Camera Window
            cv2.rectangle(frame, (0, 0), (640, 40), (0, 0, 0), -1)
            cv2.putText(frame, current_status, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.imshow("AgriScan AI Live Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# --- UI WRAPPER ---

def update_ui_report(msg):
    report_label.config(text=msg)
    if "ALERT" in msg or "DETECTED" in msg:
        report_label.config(fg="red")
    else:
        report_label.config(fg="green")

def start_btn_clicked():
    global is_scanning
    is_scanning = True
    print("Scan Started.")

def schedule_scan():
    try:
        delay = int(timer_entry.get())
        messagebox.showinfo("Scheduler", f"Scanning will begin in {delay} seconds.")
        root.after(delay * 1000, start_btn_clicked)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of seconds.")

# --- TKINTER MAIN WINDOW ---

root = tk.Tk()
root.title("AgriScan AI Control Center")
root.geometry("400x450")
root.configure(bg="#f0f0f0")

tk.Label(root, text="AGRISCAN AI DASHBOARD", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(pady=20)

report_label = tk.Label(root, text="STATUS: SYSTEM IDLE", font=("Helvetica", 12), fg="gray", bg="#f0f0f0")
report_label.pack(pady=10)

tk.Frame(root, height=2, bd=1, relief="sunken").pack(fill="x", padx=20, pady=10)

tk.Label(root, text="Schedule Scan (seconds):", bg="#f0f0f0").pack()
timer_entry = tk.Entry(root, justify='center')
timer_entry.insert(0, "5")
timer_entry.pack(pady=5)

tk.Button(root, text="Start Scheduled Scan", command=schedule_scan, bg="#FF9800", fg="white", width=25, height=2).pack(pady=10)
tk.Button(root, text="Manual Start", command=start_btn_clicked, bg="#4CAF50", fg="white", width=25, height=2).pack(pady=5)
tk.Button(root, text="Emergency Stop / Quit", command=root.destroy, bg="#f44336", fg="white", width=25).pack(pady=20)

# Run OpenCV in a background thread so the GUI stays responsive
threading.Thread(target=detect_health_loop, daemon=True).start()

root.mainloop()