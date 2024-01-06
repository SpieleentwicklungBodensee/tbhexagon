import pygame
import time

from bitmapfont import BitmapFont


SCR_W, SCR_H = 256, 256

COLORS = {'red': (255, 0, 0),
          'white': (255, 255, 255),
          }

pygame.display.init()


class Game():
    def __init__(self):
        self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED|pygame.FULLSCREEN)
        self.running = False

        self.font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_big = BitmapFont('gfx/heimatfont.png', zoom=2, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_huge = BitmapFont('gfx/heimatfont.png', zoom=3, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())

        self.logo = pygame.image.load('gfx/tb-logo-1.png')

        self.tick = 0


    def render(self):
        self.window.fill((0, 0, 0))

        for i in range(4):
            scale_f = ((4.0 / SCR_W) * ((self.tick + 32 * i) % 128)) ** 2
            #scale_f = 1
            scaled = pygame.transform.scale(self.logo, (SCR_W * scale_f, SCR_H * scale_f))
            scaled.set_alpha(scale_f / 2 * 255)
            scaled = pygame.transform.rotate(scaled, self.tick)
            self.window.blit(scaled, ((SCR_W - scaled.get_width()) / 2, (SCR_H - scaled.get_height()) / 2))

        if int(time.time() * 1000) % 500 < 250:
            title_color = COLORS['red']
        else:
            title_color = COLORS['white']

        self.font_huge.centerText(self.window, 'TOOLBOX', y=2, fgcolor=title_color)
        self.font_huge.centerText(self.window, 'HEXAGON', y=3, fgcolor=title_color)

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

        clock = pygame.time.Clock()

        while self.running:
            self.render()
            self.controls()
            self.update()

            self.tick += 1

            clock.tick(60)


    def quit(self):
        pygame.quit()



try:
    game = Game()
    game.start()
except KeyboardInterrupt:
    pass
finally:
    game.quit()
