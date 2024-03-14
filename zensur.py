def censor_highscore_name(highscore_name):
    highscore_name = highscore_name.replace(" ","").replace("!","")
    if highscore_name in ["ASS"]: return "LOL"
    return highscore_name
