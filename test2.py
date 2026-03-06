import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import serial
import smtplib
from email.message import EmailMessage
import time

# --- CONFIGURATION ---
SERIAL_PORT = 'COM3' 
EMAIL_ID = "your-email@gmail.com"
EMAIL_PASS = "your-app-password"
RECEIVER_EMAIL = "target-email@gmail.com"

class AgriScanApp:
    def __init__(self, window):
        self.window = window
        self.window.title("AgriScan AI - Integrated Dashboard")
        self.window.geometry("1000x650")
        self.window.configure(bg="#f4f4f4")

        # --- Variables ---
        self.is_running = False
        self.last_email_time = 0
        try:
            self.ser = serial.Serial(SERIAL_PORT, 115200, timeout=1)
        except:
            self.ser = None

        # --- UI LAYOUT ---
        # Video on Left
        self.video_label = tk.Label(window, bg="black")
        self.video_label.pack(side="left", padx=20, pady=20)

        # Controls on Right
        self.control_frame = tk.Frame(window, padx=20, bg="#f4f4f4")
        self.control_frame.pack(side="right", fill="y")

        tk.Label(self.control_frame, text="AGRISCAN CONTROL", font=("Arial", 16, "bold"), bg="#f4f4f4").pack(pady=20)
        
        self.status_label = tk.Label(self.control_frame, text="SYSTEM IDLE", fg="gray", font=("Arial", 12, "bold"), bg="#f4f4f4")
        self.status_label.pack(pady=10)

        # Timer/Auto-Scan Section
        tk.Label(self.control_frame, text="Auto-Scan Delay (sec):", bg="#f4f4f4").pack(pady=(20,0))
        self.timer_entry = tk.Entry(self.control_frame, justify='center')
        self.timer_entry.insert(0, "5")
        self.timer_entry.pack(pady=5)

        tk.Button(self.control_frame, text="SCHEDULE AUTO-SCAN", command=self.schedule_scan, bg="#FF9800", fg="white", width=25, height=2).pack(pady=10)
        tk.Button(self.control_frame, text="MANUAL START", command=self.start_scan, bg="#4CAF50", fg="white", width=25, height=2).pack(pady=5)
        tk.Button(self.control_frame, text="STOP SYSTEM", command=self.stop_scan, bg="#f44336", fg="white", width=25).pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    # --- LOGIC ---
    def start_scan(self):
        self.is_running = True
        self.status_label.config(text="SCANNING...", fg="blue")

    def stop_scan(self):
        self.is_running = False
        self.status_label.config(text="IDLE", fg="gray")

    def schedule_scan(self):
        try:
            delay = int(self.timer_entry.get())
            self.status_label.config(text=f"STARTING IN {delay}s", fg="orange")
            self.window.after(delay * 1000, self.start_scan)
        except:
            messagebox.showerror("Error", "Enter valid seconds")

    def send_alert(self):
        if time.time() - self.last_email_time < 60: return # Cooldown
        try:
            msg = EmailMessage()
            msg.set_content("Ripe Fruit Detected! Pump Activated.")
            msg['Subject'] = "AgriScan Alert"
            msg['From'] = EMAIL_ID
            msg['To'] = RECEIVER_EMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_ID, EMAIL_PASS)
                server.send_message(msg)
            self.last_email_time = time.time()
        except: pass

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            if self.is_running:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Masks
                masks = [
                    (cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255])), "FRUIT", (0, 0, 255)),
                    (cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255])), "LEAF", (0, 255, 0)),
                    (cv2.inRange(hsv, np.array([10, 40, 20]), np.array([30, 255, 100])), "DEFECT", (0, 75, 150))
                ]

                detected_status = "Scanning: No targets"
                for mask, label, color in masks:
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for cnt in contours:
                        if cv2.contourArea(cnt) > 2000:
                            x, y, w, h = cv2.boundingRect(cnt)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            
                            if label == "FRUIT":
                                detected_status = "FRUIT DETECTED"
                                if self.ser: self.ser.write(b'P')
                                threading.Thread(target=self.send_alert, daemon=True).start()
                            elif label == "DEFECT":
                                detected_status = "DEFECT ALERT!"

                self.status_label.config(text=detected_status)

            # Convert to Tkinter Format
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update_frame)

# --- RUN ---
root = tk.Tk()
app = AgriScanApp(root)
root.mainloop()