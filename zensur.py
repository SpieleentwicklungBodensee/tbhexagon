from highscore import CHARS

censored_words = ["AH","BH","HJ","HH","SD","SS","SA","NS","KZ","IS", # verbotene kfz kennzeichen
                  "SRP","KPD", # verbotene parteien
                  "SPD","CDU","CSU","FDP","AFD","BSW","NPD", # parteien
                  "ASS","FAG","KKK","SEX","TIT"] # other

spaces = ["!"," "]

def remove_spaces(string):
    for space in spaces:
        string = string.replace(space,"")
    return string

def censor_highscore_name(highscore_name):
    if remove_spaces(highscore_name) in censored_words:
        last_char = highscore_name[2]
        chars_no_spaces = remove_spaces(CHARS)
        if last_char in spaces:
            last_char = chars_no_spaces[0]
        elif last_char in chars_no_spaces:
            last_char = (chars_no_spaces+chars_no_spaces[0])[ chars_no_spaces.find(last_char)+1 ]
        highscore_name = highscore_name[0] + highscore_name[1] + last_char
        if remove_spaces(highscore_name) in censored_words:
            highscore_name = "ERR"
    return highscore_name
