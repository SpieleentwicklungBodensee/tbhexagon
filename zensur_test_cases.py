import zensur
from highscore import CHARS

print("testing:")
highscore_names_censored = 0
highscore_names_uncensored = 0
for char0 in CHARS:
    print(char0, end="")
    for char1 in CHARS:
        for char2 in CHARS:
            highscore_name0 = char0 + char1 + char2
            highscore_name1 = zensur.censor_highscore_name(highscore_name0)
            if highscore_name0 != highscore_name1:
                print(" ["+highscore_name0+"]>["+highscore_name1, end="]")
                highscore_names_censored+=1
            else:
                highscore_names_uncensored+=1
    print("")
print("highscore names censored: " + str(highscore_names_censored))
print("highscore names uncensored: " + str(highscore_names_uncensored))
