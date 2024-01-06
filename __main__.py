import pygame


SCR_W, SCR_H = 256, 256

pygame.display.init()

window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)


class Game():
    def __init__(self):
        pass

    def render(self):
        pass

    def controls(self):
        pass

    def update(self):
        pass

    def quit(self):
        pygame.quit()




try:
    game = Game()
    game.start()
except KeyboardInterrupt:
    pass
finally:
    game.quit()
