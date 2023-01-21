# Selenium Tags
RUN_GAME_CLASS_NAME = "load_iframe_btn"
GAME_ID = "game_drop"

# Constants
WIDTH = 1280
HEIGHT = 720
ACTION_DELAY = 10
GOLD_PIXEL_COLOR = (255, 171, 50, 255)

# Crop coordinates
NEWS_CROP = (0,0,WIDTH,100)

GOLD_CROP = (56,21,107,60)
LIVES_CROP = (168,21,212,60)
ROUNDS_CROP = (424,21,492,60)

GOLD_PIXEL = (30, 40)

RESULTS_CROP = (0, 450, WIDTH, 520)
PLAY_PAUSE_CROP = (460, 0, 575, 50)

ANIMAL_SLOTS_START = (300, 130)
ANIMAL_SLOTS_SIZE = (96, 225)

SHOP_SLOTS_START = (303, 380)
SHOP_SLOTS_SIZE = (96, 170)

FOOD_SLOTS_START = (783, 380)

# Click Locations

END_ROUND_BUTTON = (600, 300)
ROLL_BUTTON = (-600, 300)
FREEZE_SELL_BUTTON = (100, 300)

LATER_BUTTON = (-100, 300)

SETTINGS = [(600, -300),
            (-600, -250),
            (0, -300),
            (0, -100),
            (-600, -100),
            (0, -300),
            (-600, 0),
            (0, -300),
            (0, -200), 
            (0, -100), 
            (0, 0), 
            (0, 100), 
            (-600, 300),
            (-500, -200),
            (0, -250),
            (0, 0)]

ROUND_SETTINGS = [(0, -300), (100, -300)]

# Configs
TESSERACT_CONFIG_NUM = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
TESSERACT_CONFIG_CHAR = '--psm 11 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm '
URL = "https://teamwood.itch.io/super-auto-pets"