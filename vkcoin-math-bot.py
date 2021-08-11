from datetime import datetime
import win32api, win32con
from config import *
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


def click(pos: tuple):
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print(f'Left click at {pos}')


def exit_handler():
    pause.set()
    while True:
        if keyboard.wait('escape') is None:
            pause.clear()
            print('Stopped.')


def bot_handler():
    click(FOCUS_POS)
    click(PLAY_POS)
    time.sleep(1)
    while pause.wait():
        if pyautogui.locateOnScreen('captcha.png'):
            print('Waitng for captcha...')
            captcha = pyautogui.prompt('Captcha')
            if captcha:
                click(CAPTCHA_INPUT_FIELD_POS)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(captcha)
                click(CAPTCHA_SEND_POS)
                time.sleep(2)
            continue
        print('>----- Start -----<')
        click(get_level_pos(level))
        time.sleep(1)
        filename = f'temp/{datetime.timestamp(datetime.now())}.png'
        pyautogui.screenshot(filename, region=(1039, 580, 352, 132))
        print(f'Screenshot "{filename}" taken')
        img = cv2.imread(filename)
        expression = replace_all(str(pytesseract.image_to_string(img, lang='eng', config=TESSERACT_CONFIG)).strip(), REPLACEMENTS)
        if not KEEP_TEMP_FILES:
            os.remove(filename)
        print(f'Expression: {expression}')
        try:
            result = str(int(numexpr.evaluate(expression)))
            print(f'Result: {result}')
            click(INPUT_FIELD_POS)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(result)
            pyautogui.press('enter')
            time.sleep(1)
        except SyntaxError:
            click(BACK_POS)
            time.sleep(1)
            click(PLAY_POS)
            time.sleep(1)


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
