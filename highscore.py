
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
