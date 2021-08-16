from config import *
import numpy as np
import pytesseract
import threading
import pyautogui as pg
import keyboard
import time
import math
import cv2


def mouse_click(pos: tuple) -> None:
    pg.moveTo(*pos, 0.2, pg.easeOutQuad)
    pg.click()


def is_captcha_on_screen() -> bool:
    # TODO: Pixel Matching
    return pg.locateOnScreen('captcha.png', region=CAPTCHA_REGION, grayscale=True, confidence=0.8) is not None and \
    pg.locateOnScreen('captcha_vknext.png', region=CAPTCHA_REGION, grayscale=True, confidence=0.8) is not None


def input_captcha() -> None:
    print('Waitng for captcha...')
    captcha = pg.prompt(title='Captcha')
    if captcha:
        mouse_click(CAPTCHA_INPUT_POS)
        pg.hotkey('ctrl', 'a')
        pg.press('backspace')
        pg.write(captcha)
        pg.press('enter')


def click(pos: tuple[int, int]) -> None:
    while is_captcha_on_screen():
        input_captcha()
        time.sleep(0.5)
    mouse_click(pos)


def exit_handler() -> None:
    pause.set()
    while True:
        if keyboard.wait('q') is None:
            pause.clear()
            print('Stopped.')


def number_from_screenshot(number_region: tuple[int, int , int, int]) -> int:
    image = cv2.cvtColor(np.array(pg.screenshot(region=number_region)), cv2.COLOR_RGB2BGR)
    return int(pytesseract.image_to_string(image, lang='eng', config=TESSERACT_CONFIG).strip())


def bot_handler() -> None:
    click(FOCUS_POS)
    click(PLAY_POS)
    time.sleep(0.5)
    count = 0
    while pause.wait():
        count += 1
        print(f'>----- Attempt #{count} -----<')
        click(LEVEL12_POS)
        time.sleep(1.5)
        try:
            e1 = number_from_screenshot(N_REG[0] + N_REG_SIZE) # Числитель числа #1
            d1 = number_from_screenshot(N_REG[1] + N_REG_SIZE) # Знаменатель числа #1
            e2 = number_from_screenshot(N_REG[2] + N_REG_SIZE) # Числитель числа #2
            d2 = number_from_screenshot(N_REG[3] + N_REG_SIZE) # Знаменатель числа #2
        except ValueError:
            print('Numbers are not recognized.')
            continue
        if pg.locateOnScreen('mult.png', region=OPER_REG, grayscale=True, confidence=0.8) is not None:
            oper = '*'
        else:
            oper = '/'
        print(f'Expression: ({e1}/{d1}) {oper} ({e2}/{d2})')
        if oper == '/':
            e2, d2 = d2, e2
        gcd = math.gcd(e1 * e2, d1 * d2)
        re = int(e1 * e2 / gcd)
        rd = int(d1 * d2 / gcd)
        if rd == 1:
            result = str(re)
        else:
            result = f'{re}/{rd}'
        print(f'Result: {result}')
        click(INPUT_POS)
        pg.hotkey('ctrl', 'a')
        pg.press('backspace')
        pg.write(result)
        pg.press('enter')
        time.sleep(1)


def main() -> None:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print('Go to menu in the game and press enter to start...')
    input('(To interrupt the process press Q)')
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
