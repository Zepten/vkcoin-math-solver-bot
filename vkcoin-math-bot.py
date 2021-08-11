import win32api, win32con
from config import *
import numpy as np
import pytesseract
import threading
import pyautogui
import keyboard
import numexpr
import time
import cv2
import os


def replace_all(text: str, d: dict):
    for i, j in d.items():
        text = text.replace(i, j)
    return text


def get_level_pos(level: int):
    return (
        LEVEL1_POS[0] + (level - 1) % 4 * 156,
        LEVEL1_POS[1] + (level - 1) // 4 * 60
    )


def mouse_click(pos: tuple):
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def input_captcha():
    print('Waitng for captcha...')
    captcha = pyautogui.prompt(title='Captcha')
    if captcha:
        mouse_click(CAPTCHA_INPUT_FIELD_POS)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(captcha)
        pyautogui.press('enter')


def click(pos: tuple):
    while pyautogui.locateOnScreen('captcha.png'):
        input_captcha()
        time.sleep(0.5)
    mouse_click(pos)


def exit_handler():
    pause.set()
    while True:
        if keyboard.wait('escape') is None:
            pause.clear()
            print('Stopped.')


def bot_handler():
    click(FOCUS_POS)
    click(PLAY_POS)
    time.sleep(0.5)
    while pause.wait():
        print('>----- Start -----<')
        click(get_level_pos(level))
        time.sleep(1)
        image = pyautogui.screenshot(region=(1039, 580, 352, 132))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        print(f'Screenshot taken.')
        expression = replace_all(str(pytesseract.image_to_string(image, lang='eng', config=TESSERACT_CONFIG)).strip(), REPLACEMENTS)
        print(f'Expression: {expression}')
        try:
            result = str(int(numexpr.evaluate(expression)))
            print(f'Result: {result}')
            click(INPUT_FIELD_POS)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(result)
            pyautogui.press('enter')
            time.sleep(0.5)
        except (SyntaxError, KeyError):
            click(BACK_POS)
            time.sleep(0.5)
            click(PLAY_POS)
            time.sleep(0.5)


def main():
    if not os.path.exists('temp'):
        os.mkdir('temp')
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    global level
    try:
        level = max(1, int(input('Enter level: ')))
    except:
        level = DEFAULT_LEVEL
    print(f'Your level is {level}')
    global pause
    pause = threading.Event()
    bot_thread = threading.Thread(target=bot_handler)
    exit_thread = threading.Thread(target=exit_handler)
    bot_thread.start()
    exit_thread.start()
    bot_thread.join()
    exit_thread.join()


if __name__ == '__main__':
    main()
