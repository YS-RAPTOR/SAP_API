# Selenium Tags
RUN_GAME_CLASS_NAME = "load_iframe_btn"
GAME_ID = "game_drop"

# Constants
WIDTH = 1280
HEIGHT = 720
ACTION_DELAY = 10
GOLD_PIXEL_COLOR = (228, 131, 0, 255)

# Crop coordinates
NEWS_CROP = (0,0,WIDTH,100)

GOLD_CROP = (56,21,108,60)
LIVES_CROP = (173,21,215,60)
ROUNDS_CROP = (386,21,422,60)

GOLD_PIXEL = (30, 40)

RESULTS_CROP = (0, 450, WIDTH, 520)
PLAY_PAUSE_CROP = (460, 0, 575, 50)

ANIMAL_SLOTS_START = (204, 130)
ANIMAL_SLOTS_SIZE = (96, 225)

SHOP_SLOTS_START = (207, 380)
SHOP_SLOTS_SIZE = (96, 170)

FOOD_SLOTS_START = (879, 380)

# Click Locations

END_ROUND_BUTTON = (600, 300)
ROLL_BUTTON = (-600, 300)
FREEZE_SELL_BUTTON = (100, 300)

LATER_BUTTON = (-100, 300)

SETTINGS = [(610, -330),
            (610, -330),
            (-520, -35), # GamePlay
            (0, -310),
            (0, -10),
            (0, 85),
            (0, 320),
            (-520, 55), # Audio
            (-315, -282),
            (-315, -182),
            (-315, -82),
            (-315, 18),
            (-520, 140), # Display
            (0, -310),
            (0, -210),
            (-520, 225), # Customize
            (0, -310),
            (0, -210),
            (0, -110),
            (-590, -310) # Go Back
            ]

ROUND_SETTINGS = [(0, -300), (100, -300)]

# Configs
TESSERACT_CONFIG_NUM = '--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
TESSERACT_CONFIG_CHAR = '--psm 11 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm '
URL = "https://teamwood.itch.io/super-auto-pets"