TESSERACT_PATH  = 'D:\\Tesseract-OCR\\tesseract.exe'
TESSERACT_CONFIG = r'-c tessedit_char_whitelist=01234567890()*+-/=? --psm 6'

KEEP_TEMP_FILES = False # Нужно ли сохранять временные скриншоты
PLAY_POS        = (1105, 858) # Кнопка "Играть"
FOCUS_POS       = (1800, 500) # Пустое пространство для фокуса на окне
INPUT_FIELD_POS = (1037, 910) # Поле ввода "Напишите сообщение..."
LEVEL1_POS      = (1024, 800) # Кнопка "Ур. 1"
BACK_POS        = (1096, 980) # Кнопка "Вернуться назад"

CAPTCHA_INPUT_FIELD_POS = (934, 493)  # Поле ввода в окне капчи
CAPTCHA_SEND_POS        = (1054, 562) # Кнопка "Отправить" в окне капчи

REPLACEMENTS = {
    '=?': '',
    '–': '-',
    '—': '-',
    'n': '11',
    'l': '1',
    'H': '11',
    'o': '0',
    'O': '0',
    '’': '',
    ':': '',
    '`': ''
}

DEFAULT_LEVEL = 6 # Уровень игры