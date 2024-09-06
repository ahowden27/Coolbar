"""
Main loop for the gui
"""

import threading
from clipboards import keyboard_listener_thread
from gui import App

if __name__ == "__main__":
    app = App()
    keyboard_thread = threading.Thread(target=keyboard_listener_thread)
    keyboard_thread.start()
    app.mainloop()
