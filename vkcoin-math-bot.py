from dotenv import load_dotenv
import pyautogui as pg
from os import environ
from config import *
import pytesseract
import threading
import keyboard
import telebot
import time
import math


load_dotenv()
bot = telebot.TeleBot(environ.get('TOKEN'))
CHAT_ID = environ.get('CHAT_ID')


def is_captcha_on_screen() -> bool:
    return pg.locateOnScreen('captcha.png', region=CAPTCHA_REGION, grayscale=True, confidence=0.8) is not None and \
    pg.locateOnScreen('captcha_vknext.png', region=CAPTCHA_REGION, grayscale=True, confidence=0.8) is not None


def click(pos: tuple[int, int]) -> None:
    pg.moveTo(*pos, 0.2, pg.easeOutQuad)
    pg.click()


def input_captcha() -> None:
    print('Waitng for captcha...')
    pg.screenshot('captcha_temp.png', region=CAPTCHA_IMAGE_REGION)
    bot.send_photo(chat_id=CHAT_ID, photo=open('captcha_temp.png', 'rb'))
    captcha = pg.prompt(title='Captcha')
    click(CAPTCHA_INPUT_POS)
    pg.hotkey('ctrl', 'a')
    pg.press('backspace')
    pg.write(captcha)
    pg.press('enter')
    bot.send_message(chat_id=CHAT_ID, text='Каптча введена')


def exit_handler() -> None:
    pause.set()
    while True:
        if keyboard.wait('tab') is None:
            pause.clear()
            print('Stopped.')


def number_from_screenshot(number_region: tuple[int, int , int, int]) -> int:
    screenshot = pg.screenshot(region=number_region)
    return int(pytesseract.image_to_string(screenshot, config=TESSERACT_CONFIG).strip())


def bot_handler() -> None:
    bot.send_message(chat_id=CHAT_ID, text='Бот начал работу')
    click(FOCUS_POS)
    click(PLAY_POS)
    time.sleep(0.5)
    count = 0
    while pause.wait():
        while is_captcha_on_screen():
            input_captcha()
            time.sleep(1)

        count += 1
        print(f'>----- Attempt #{count} -----<')
        click(LEVEL12_POS)
        time.sleep(1)
        try:
            e1 = number_from_screenshot(N_REG[0] + N_REG_SIZE) # Числитель числа #1
            print(e1, end='')
            d1 = number_from_screenshot(N_REG[1] + N_REG_SIZE) # Знаменатель числа #1
            print(f', {d1}', end='')
            e2 = number_from_screenshot(N_REG[2] + N_REG_SIZE) # Числитель числа #2
            print(f', {e2}', end='')
            d2 = number_from_screenshot(N_REG[3] + N_REG_SIZE) # Знаменатель числа #2
            print(f', {d2}')
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


@bot.message_handler(func=lambda m: True)
def telegram_input(message):
    if is_captcha_on_screen():
        print(f'Telegram input: "{message.text}"')
        pg.hotkey('ctrl', 'a')
        pg.press('backspace')
        pg.write(message.text)
        pg.press('enter')


def telegram_handler():
    bot.polling(none_stop=True)


def main() -> None:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print('Go to menu in the game and press enter to start...')
    input('(To interrupt the process press Q)')
    global pause
    pause = threading.Event()
    bot_thread = threading.Thread(target=bot_handler)
    exit_thread = threading.Thread(target=exit_handler)
    telegram_thread = threading.Thread(target=telegram_handler)
    bot_thread.start()
    exit_thread.start()
    telegram_thread.start()
    bot_thread.join()
    exit_thread.join()
    telegram_thread.join()


if __name__ == '__main__':
    main()
