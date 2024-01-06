import pygame
import time
import random

from bitmapfont import BitmapFont

WIN_W, WIN_H = 1024, 1024
SCR_W, SCR_H = 256, 256

COLORS = {'red': (255, 0, 0),
          'white': (255, 255, 255),
          'black': (0, 0, 0),
          }

DISTANCE = 64
SPEED = 1.0 / 128

RENDER_MODE = 'plain'     # 'plain', 'led'

pygame.display.init()


class Game():
    def __init__(self):
        if RENDER_MODE == 'plain':
            self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)
            self.output = self.window
        elif RENDER_MODE == 'led':
            self.window = pygame.display.set_mode((WIN_W, WIN_H))
            self.output = pygame.Surface((SCR_W, SCR_H))
            self.overlay = pygame.Surface((WIN_W, WIN_H), flags=pygame.SRCALPHA)

            stepx = int(WIN_W / SCR_H)
            stepy = int(WIN_W / SCR_H)
            gridcolor = (0, 0, 0, 64)
            for y in range(0, WIN_H, stepy):
                for x in range(0, WIN_W, stepx):
                    pygame.draw.line(self.overlay, gridcolor, (x, 0), (x, WIN_H))
                    pygame.draw.line(self.overlay, gridcolor, (x+1, 0), (x+1, WIN_H))
                    pygame.draw.line(self.overlay, gridcolor, (0, y), (WIN_W, y))
                    pygame.draw.line(self.overlay, gridcolor, (0, y+1), (WIN_W, y+1))

            for y in range(0, WIN_H, stepy):
                if y % stepy == 0:
                    for i in range(int(stepy/2)):
                        pygame.draw.line(self.overlay, (0, 0, 0, 255), (0, y+i), (WIN_W, y+i))

            #self.overlay = pygame.image.load('gfx/raster1792.png')

        self.running = False

        self.font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_big = BitmapFont('gfx/heimatfont.png', zoom=2, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_huge = BitmapFont('gfx/heimatfont.png', zoom=3, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())

        self.logo = pygame.image.load('gfx/tb-logo-pure-1.png')
        self.logo_filled = pygame.image.load('gfx/tb-logo-pure-2.png')

        self.tick = 0

        self.logos = [(3, 40),
                      (2, 20),
                      (1, 0),]   # distance, rotation


    def render(self):
        self.output.fill((0, 0, 0))

        for dist, rot in self.logos:
            size = 1.0 / dist * DISTANCE
            alpha = size / 128 * 255 + 64
            rot = rot

            if size <= 1:
                size = 1
            if size >= SCR_W * 4:
                self.output.fill((0,0,0))
                continue

            size = int(size)

            logo_sprite = self.logo

            #if dist < 0.3 and dist > 0.2:
            #    logo_sprite = self.logo_filled

            if size > 250 and size < 300:
                logo_sprite = self.logo_filled

            if size > 300:
                alpha = 255 - (size / (SCR_W * 4)) * 255
                #alpha = 128

            scaled = pygame.transform.scale(logo_sprite, (size, size))
            scaled.set_alpha(alpha)
            scaled = pygame.transform.rotate(scaled, rot)

            x = (SCR_W - scaled.get_width()) / 2
            y = (SCR_H - scaled.get_height()) / 2

            self.output.blit(scaled, (x, y))

        if int(time.time() * 1000) % 500 < 250:
            title_color = COLORS['red']
        else:
            title_color = COLORS['white']

        #self.font_huge.centerText(self.output, 'TOOLBOX', y=2, fgcolor=title_color)
        #self.font_huge.centerText(self.output, 'HEXAGON', y=3, fgcolor=title_color)

        self.font.drawText(self.output, 'HI', x=1, y=SCR_H/8-2, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '00000', x=1, y=SCR_H/8-1, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '1UP', x=SCR_W/8-4, y=SCR_H/8-2, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '00000', x=SCR_W/8-6, y=SCR_H/8-1, fgcolor=COLORS['white'])

        # compose and zoom
        if RENDER_MODE == 'plain':
            pass
        elif RENDER_MODE == 'led':
            pygame.transform.scale(self.output, (WIN_W, WIN_H), self.window)
            self.window.blit(self.overlay, (0, 0))

        pygame.display.flip()


    def controls(self):
        events = pygame.event.get()

        modstate = pygame.key.get_mods()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                if e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

                if e.key == pygame.K_RETURN:
                    if modstate & pygame.KMOD_ALT:
                        pygame.display.toggle_fullscreen()



    def update(self):
        newlogos = []

        for dist, rot in self.logos:
            dist -= SPEED
            if dist <= 0:
                dist = 3
                rot += 60
                rot = int(random.random() * 36) * 10

            newlogos.append((dist, rot))

        self.logos = newlogos


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
