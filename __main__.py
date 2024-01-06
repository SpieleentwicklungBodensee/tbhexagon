import pygame
from bitmapfont import BitmapFont

SCR_W, SCR_H = 256, 256

pygame.display.init()

class Game():
    def __init__(self):
        self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)
        self.running = False

        self.font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H)


    def render(self):
        self.window.fill((0, 0, 0))

        self.font.centerText(self.window, 'TB HEXAGON', y=2)

        pygame.display.flip()


    def controls(self):
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False


    def update(self):
        pass


    def start(self):
        self.running = True

        while self.running:
            self.render()
            self.controls()
            self.update()


    def quit(self):
        pygame.quit()



try:
    game = Game()
    game.start()
except KeyboardInterrupt:
    pass
finally:
    game.quit()
