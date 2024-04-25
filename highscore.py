import json

MAX_LENGTH = 3
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ !'

char_cursor = 0
name_cursor = 0

name = None


def scroll(amount):
    global char_cursor, name
    char_cursor += amount
    char_cursor %= (len(CHARS))

    name = name[:name_cursor] + CHARS[char_cursor] + name[name_cursor+1:]

def step(amount=1):
    global char_cursor, name_cursor
    name_cursor += amount

    if name_cursor < 0:
        name_cursor = 0

    if name_cursor < MAX_LENGTH:
        char_cursor = CHARS.index(name[name_cursor])
        return True
    else:
        name_cursor = MAX_LENGTH -1
        return False

def reset():
    global char_cursor, name_cursor, name

    if name is None:
        name = 'AAA'

    name_cursor = 0
    char_cursor = CHARS.index(name[name_cursor])



DEFAULT_LIST = [[900, 'TBX'],
                [800, 'TBX'],
                [700, 'TBX'],
                [600, 'TBX'],
                [500, 'TBX'],
                ]

highscorelist = list(DEFAULT_LIST)

def check(score):
    if score > highscorelist[4][0]:
        return True

    return False

def insert(score, name):
    highscorelist.append([score, name])
    highscorelist.sort(reverse=True)

    if [score, name] in highscorelist[:5]:
        return True

    return False

def save(filename='.hsc'):
    with open(filename, 'w') as f:
        f.write(json.dumps(highscorelist))

def load(filename='.hsc'):
    global highscorelist
    with open(filename) as f:
        j = f.read()
        highscorelist = json.loads(j)

def clear():
    global highscorelist, name
    highscorelist = list(DEFAULT_LIST)
    name = None

def gettop(num=5):
    result = []
    names = []

    for score, name in highscorelist:
        if not name in names:
            result.append((score, name))
            names.append(name)

        if len(result) >= num:
            break

    return result
