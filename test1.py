import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import threading
import serial
import smtplib
from email.message import EmailMessage

# --- CONFIGURATION ---
SERIAL_PORT = 'COM3' 
# Set your Email info here if needed

class AgriScanApp:
    def __init__(self, window):
        self.window = window
        self.window.title("AgriScan AI - Integrated Dashboard")
        self.window.geometry("900x600")

        # 1. Layout: Left side for Video, Right side for Controls
        self.video_label = tk.Label(window, bg="black")
        self.video_label.pack(side="left", padx=10, pady=10)

        self.control_frame = tk.Frame(window, padx=20)
        self.control_frame.pack(side="right", fill="y")

        # 2. UI Elements
        tk.Label(self.control_frame, text="SYSTEM STATUS", font=("Arial", 14, "bold")).pack(pady=10)
        self.status_label = tk.Label(self.control_frame, text="IDLE", fg="gray", font=("Arial", 12))
        self.status_label.pack(pady=5)

        tk.Button(self.control_frame, text="START SCAN", command=self.start_scan, bg="green", fg="white", width=20).pack(pady=20)
        tk.Button(self.control_frame, text="STOP", command=self.stop_scan, bg="red", fg="white", width=20).pack(pady=5)

        # 3. OpenCV Setup
        self.cap = cv2.VideoCapture(0)
        self.is_running = False
        
        # Start the update loop
        self.update_frame()

    def start_scan(self):
        self.is_running = True
        self.status_label.config(text="SCANNING...", fg="blue")

    def stop_scan(self):
        self.is_running = False
        self.status_label.config(text="IDLE", fg="gray")

    def update_frame(self):
        # This function runs every 10ms to update the video
        ret, frame = self.cap.read()
        
        if ret:
            if self.is_running:
                # --- YOUR OPENCV LOGIC HERE ---
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # (Add your red/brown mask logic here to draw boxes on 'frame')
                # Example:
                # if detected: self.status_label.config(text="FRUIT DETECTED", fg="red")
                pass

            # Convert BGR (OpenCV) to RGB (Tkinter)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Put the image on the label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Repeat this function after 10 milliseconds
        self.window.after(10, self.update_frame)

# --- MAIN ---
root = tk.Tk()
app = AgriScanApp(root)
root.mainloop()