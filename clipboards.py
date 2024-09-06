"""
clipboards functionality
"""
# pylint: disable=global-statement

import re
import pyperclip
from pynput import keyboard
import pyautogui

COPYCOMBO = {keyboard.Key.ctrl_l, keyboard.Key.shift}
PASTECOMBO = {keyboard.Key.ctrl_l, keyboard.Key.alt_l}
VALUENUMS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 0}
copyact, pasteact = False, False
NUMBA = ''
activenums = set()
CB = ['', '', '', '', '', '', '', '', '', '', '']

mods = {
    keyboard.Key.ctrl_l: False,
    keyboard.Key.shift: False,
    keyboard.Key.alt_l: False
}

numz = {
    "<49>": 1,
    "'\\x00'": 2,
    "<50>": 2,
    "<51>": 3,
    "<52>": 4,
    "<53>": 5,
    "<54>": 6,
    "'\\x1e'": 6,
    "<55>": 7,
    "<56>": 8,
    "<57>": 9,
    "<48>": 0
}

numzz = ["'1'", "'2'", "'3'", "'4'", "'5'", "'6'", "'7'", "'8'", "'9'", "'0'"]


def load_saves(cb):
    """
    Loads clipboards from text file
    """
    try:
        with open(r'cbsaves.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            cb_dict = {}
            for i in range(1, 11):
                if i * 2 - 2 < len(lines):
                    key = lines[i * 2 - 2].strip()
                    value = lines[i * 2 - 1].strip()
                    if key.startswith('CB') and key[2:].isdigit():
                        index = int(key[2:])
                        if 1 <= index <= 10:
                            cb_dict[index] = value
            for index, value in cb_dict.items():
                cb[index] = value
    except FileNotFoundError:
        pass


def is_zoom_invitation(text):
    """
    Checks if copied value is a zoom invite
    """
    return 'Meeting ID:' in text and 'Passcode:' in text


def extract_zoom_info(text):
    """
    Extracts Zoom meeting info from invitation
    """
    meeting_id_match = re.search(r'Meeting ID:\s*([\d\s]+)', text)
    passcode_match = re.search(r'Passcode:\s*(\d+)', text)

    meeting_id = meeting_id_match.group(1).replace(' ', '') if meeting_id_match else 'Not Found'
    passcode = passcode_match.group(1) if passcode_match else 'Not Found'

    return f"Meeting ID: {meeting_id} Password: {passcode}"


def copy(nb, cb):
    """
    Copies to clipboard slot
    """
    pyautogui.hotkey('ctrl', 'c')
    cb[nb] = pyperclip.paste()
    if cb[nb] != '':
        if 'Meeting ID:' in cb[nb] and 'Passcode:' in cb[nb]:
            cb[nb] = extract_zoom_info(cb[nb])
        pyperclip.copy('')
        print(f'Saved {cb[nb]} to CB{nb}.')
        update_save()


def paste(nb, cb):
    """
    Pastes from clipboard slot
    """
    if CB[nb] != '':
        pyperclip.copy(cb[nb])
        pyautogui.hotkey('ctrl', 'v')
        print(f'Pasted {cb[nb]} from CB{nb}.')
    else:
        print(f'No value stored at CB{nb}.')


def on_press(key):
    """
    Checks if pressed key is part of a hotkey.
    If all parts of hotkey are pressed, toggles copy/paste
    """
    global copyact, pasteact, NUMBA

    key_str = str(key)

    if key in mods:
        mods[key] = True
    elif key_str in numz:
        activenums.add(numz[key_str])
        NUMBA = numz[key_str]

    mods_values = list(mods.values())

    if NUMBA:
        if mods_values == [True, True, False]:
            copyact = True
        elif mods_values == [True, False, True]:
            pasteact = True


def on_release(key):
    """
    Checks if clipboard hotkey was pressed and released, triggering action
    """
    global copyact, pasteact, NUMBA

    if key in mods:
        mods[key] = False
    elif str(key) in numz:
        activenums.discard(numz[str(key)])
    elif str(key) in numzz:
        activenums.discard(int(str(key).strip("'")))

    modsrel = bool(list(mods.values()) == [False, False, False])
    if (copyact or pasteact) and modsrel and NUMBA not in activenums:
        if copyact:
            copy(NUMBA, CB)
            copyact = False
        elif pasteact:
            paste(NUMBA, CB)
            pasteact = False
        NUMBA = ''


def keyboard_listener_thread():
    """
    Main listener
    """
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def update_save():
    """
    Saves clipboard to text file
    """
    with open(r'cbsaves.txt', 'w', encoding='utf-8') as f:
        for i in range(1, 11):
            if CB[i] != '':
                f.write(f"CB{i}\n{CB[i]}\n")


load_saves(CB)
