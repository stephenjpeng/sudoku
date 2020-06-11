import os


SCROT_PATH = '/tmp/scrot.png'
TESSDATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', 'training')
TRAIN_SIZE = (28, 28)
CONTENT_CUTOFF = 5
SOLVER_SLEEP = 0.00

ROWS = 9
COLUMNS = 9
BLOCKS = 9
CELL_WIDTH = 50
CORNER_SIZE = 8
CENTER_SIZE = 11
POPUP_SIZE = 14
INFO_SIZE = 9
ANSWER_SIZE = 28
ICON_SIZE = 38

FILL_COLOR = '#1c2337'
PROGRESS_FILL_COLOR = '#2980b9'
OUTLINE_COLOR = '#ccccdd'
ANSWER_COLOR = '#54859e'
SOLVER_COLOR = '#99D0F2'
WRONG_ANSWER_COLOR = '#E74C3C'
GIVEN_COLOR = OUTLINE_COLOR
ACTIVE_COLOR = '#eec65f'
ACTIVE_OUTLINE_COLOR = '#aaaabb'
BUTTON_COLOR = FILL_COLOR
ACTIVE_BUTTON_COLOR = '#3c556e'
BUTTON_TEXT_COLOR = OUTLINE_COLOR
TEXT_COLOR = FILL_COLOR

ANSWER_FONT = ("texgyreheros", ANSWER_SIZE, "bold")
POPUP_FONT = ("texgyreheros", POPUP_SIZE)
INFO_FONT = ("texgyreheros", INFO_SIZE)
ICON_FONT = ("texgyreheros", ICON_SIZE, "bold")

UP = "Up"
LEFT = "Left"
DOWN = "Down"
RIGHT = "Right"
DIRECTION_KEYS = [ UP, LEFT, DOWN, RIGHT ]

SYMBOLS = ["exclam", "at", "numbersign", "dollar", "percent", "asciicircum", "ampersand", "asterisk", "parenleft"]
DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
SYMBOLS_TO_DIGITS = dict(zip(SYMBOLS, DIGITS))

INITIAL_BOARD = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
]

USER_BOARD = [
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1],
]

USER_CORNERS = [
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
]

USER_CENTERS = [
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
    [set(), set(), set(), set(), set(), set(), set(), set(), set()],
]
