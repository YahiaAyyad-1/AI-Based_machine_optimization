import cv2
import threading
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ollama import chat
import markdown
from tkhtmlview import HTMLLabel

class VisionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1600x850")
        self.window.configure(bg="#1e1e1e") # Dark theme

        # --- GStreamer Pipeline ---
        self.vid = cv2.VideoCapture(0)  # Use standard webcam for WSL

        # --- Layout Setup ---
        # Left Side: Camera Feed
        self.left_frame = tk.Frame(window, bg="#1e1e1e")
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True)

        self.canvas = tk.Canvas(self.left_frame, width=1100, height=700, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Right Side: Control Panel
        self.right_frame = tk.Frame(window, bg="#2d2d2d", width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Title & Status
        tk.Label(self.right_frame, text="VISION CONTROL", font=("Arial", 16, "bold"), 
                 bg="#2d2d2d", fg="#ffffff").pack(pady=20)
        
        self.status_var = tk.StringVar(value="IDLE")
        self.status_label = tk.Label(self.right_frame, textvariable=self.status_var, 
                                     font=("Courier", 12, "bold"), bg="#2d2d2d", fg="#00ff00")
        self.status_label.pack(pady=5)

        # Markdown Output (The "Brain")
        tk.Label(self.right_frame, text="AI Analysis Output:", bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w", padx=10)
        self.html_pane = HTMLLabel(self.right_frame, html="<h3 style='color:gray;'>Ready to analyze...</h3>", 
                                   width=40, height=20)
        self.html_pane.pack(padx=10, pady=10, fill="both", expand=True)

        # Control Buttons
        self.btn_analyze = tk.Button(self.right_frame, text="FORCE ANALYSIS", 
                                     bg="#007BFF", fg="white", font=("Arial", 12, "bold"),
                                     height=2, command=self.manual_trigger)
        self.btn_analyze.pack(fill=tk.X, padx=20, pady=10)

        # Configuration
        self.is_analyzing = False
        self.analysis_interval = 60 
        self.update_frame()
        self.auto_analyze_loop() 

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def gstreamer_pipeline(self, w=1280, h=720, fps=30, flip=2):
        """Not used on WSL - standard webcam capture via cv2.VideoCapture(0)"""
        return None

    def update_frame(self):
        ret, frame = self.vid.read()
        if ret:
            self.current_frame = frame.copy()
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize for the canvas while maintaining aspect ratio slightly
            img_pil = Image.fromarray(img_rgb).resize((1100, 700))
            self.photo = ImageTk.PhotoImage(image=img_pil)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(15, self.update_frame)

    def manual_trigger(self):
        """Allows user to skip the countdown and analyze immediately"""
        if not self.is_analyzing:
            # Cancel any pending countdowns by setting status to thinking
            self.status_var.set("FORCE TRIGGERING...")
            self.run_ai_thread()

    def auto_analyze_loop(self):
        if not self.is_analyzing:
            self.run_ai_thread()

    def run_ai_thread(self):
        self.is_analyzing = True
        self.status_label.config(fg="#ffcc00") # Warning yellow
        self.status_var.set("🤖 THINKING...")
        thread = threading.Thread(target=self.run_ai_task, daemon=True)
        thread.start()

    def run_ai_task(self):
        try:
            cv2.imwrite('snapshot.jpg', self.current_frame)
            start_time = time.time()
            
            response = chat(
                model='qwen3-vl:2b',
                messages=[{'role': 'user', 'content': 'Analyze this. Use MD bullet points.', 'images': ['snapshot.jpg']}]
            )
            
            duration = time.time() - start_time
            content = response.message.content or response.message.thinking
            
            # Format Markdown
            md_text = f"### ⏱️ Latency: `{duration:.2f}s`  \n\n---\n{content}"
            html_content = markdown.markdown(md_text)
            styled_html = f"<body style='background-color:#ffffff; font-family:sans-serif; font-size:12px;'>{html_content}</body>"

            self.window.after(0, self.update_display, styled_html)
        except Exception as e:
            self.window.after(0, self.update_display, f"<p style='color:red;'>{e}</p>")
        finally:
            self.is_analyzing = False
            self.window.after(0, lambda: self.countdown(self.analysis_interval))

    def countdown(self, remaining):
        if remaining > 0 and not self.is_analyzing:
            self.status_label.config(fg="#00ff00") # Ready green
            self.status_var.set(f"NEXT IN {remaining}s")
            self._timer_job = self.window.after(1000, self.countdown, remaining - 1)
        elif remaining <= 0:
            self.auto_analyze_loop()

    def update_display(self, html_text):
        self.html_pane.set_html(html_text)

    def on_closing(self):
        if self.vid.isOpened(): self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    VisionApp(tk.Tk(), "Qwen3-VL Advanced Monitor")
