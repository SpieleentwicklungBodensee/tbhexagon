import pygame
import time
import random
import math

from bitmapfont import BitmapFont


# 'led' = for led wall output
# 'plain' = for pc/laptop or testing
# 'sim' = led simulation for uli
RENDER_MODE = 'plain'

PRINTLOG = []


__oldprint = print
def __newprint(msg):
    PRINTLOG.append(msg)
    __oldprint(msg)
print = __newprint

def cls():
    PRINTLOG.clear()


def draw_lines(surface,rot,size,verts):
    verts_final=[]
    for v in verts:

        # tb logo specific adjustments
        v=[v[0]*1.333333+30,v[1]*-1.333333+100]
        v=[v[0]-130/2,v[1]-130/2]

        # rotate
        v1=rotate((0,0),v,-rot*math.pi/180)

        # scale
        v1=scale(v1,size*0.0087)

        #center on screen
        v1=(v1[0]+SCR_W/2,v1[1]+SCR_H/2)

        verts_final.append(v1)
    color=(max(min(int(0.1*size*size),255),0),0,0)
    pygame.draw.lines(surface,color,True,verts_final,width=max(int(size/80),1))

def scale(vert,scale):
    return (vert[0]*scale,vert[1]*scale)

#stolen from https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


SCR_W, SCR_H = 256, 320     # the 'designed' resolution for the game
WIN_W, WIN_H = 1024, 1280   # window size for led simulation mode

COLORS = {'red': (255, 0, 0),
          'white': (255, 255, 255),
          'black': (0, 0, 0),
          }

DISTANCE = 64
SPEED = 1.0 / 128

pygame.display.init()


class Player():
    def __init__(self, x, y):
        self.xpos = x
        self.ypos = y

        self.xdir = 0
        self.ydir = 0

    def update(self):
        self.xpos += self.xdir
        self.ypos += self.ydir


class Game():
    def __init__(self):
        print('')
        print('welcome to toolbox hexagon\n')

        # surfaces explained:
        # -------------------
        # self.output = the render target
        # self.window = the actual ui window
        # self.scaled = scale surface to distort output
        # self.overlay = overlay for masking or simulating leds

        if RENDER_MODE == 'plain':
            self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED)
            self.output = self.window

        if RENDER_MODE == 'led':
            self.window = pygame.display.set_mode((1920, 1080), flags=pygame.FULLSCREEN)
            self.output = pygame.Surface((SCR_W, SCR_H))
            self.scaled = pygame.Surface((SCR_W * 2, SCR_H))
            self.overlay = pygame.Surface((SCR_W * 2, SCR_H), flags=pygame.SRCALPHA)

            for x in range(SCR_W):
                pygame.draw.line(self.overlay, (0, 0, 0), (x * 2, 0), (x * 2, SCR_H))

        elif RENDER_MODE == 'sim':
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

        print('loading graphics...')

        self.font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_big = BitmapFont('gfx/heimatfont.png', zoom=2, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())
        self.font_huge = BitmapFont('gfx/heimatfont.png', zoom=3, scr_w=SCR_W, scr_h=SCR_H, colors=COLORS.values())

        self.logo = pygame.image.load('gfx/tb-logo-pure-1.png')
        self.logo_filled = pygame.image.load('gfx/tb-logo-pure-2.png')

        self.copter_sprites = (pygame.image.load('gfx/copter1.png'), pygame.image.load('gfx/copter2.png'))

        self.tick = 0

        self.logos = [(3, 40),
                      (2, 20),
                      (1, 0),]   # distance, rotation

        self.player = Player(64, 64)

        self.mode = 'boot'  # 'boot', 'title', 'game'


        print('init joysticks...')
        pygame.joystick.init()
        if not pygame.joystick.get_count():
            print('no joystick detected')
        else:
            print('found joysticks:')
            for i in range(pygame.joystick.get_count()):
                self.joy = pygame.joystick.Joystick(i)
                self.joy.init()
                print(' - ' + self.joy.get_name())

        print('\ninit complete')
        print('press button or key')

    def render(self):
        self.output.fill((0, 0, 0))

        if self.mode == 'game':
            self.drawTunnel()
            self.drawPlayer()
            self.drawScoreboard()

        elif self.mode == 'title':
            self.drawTunnel()
            self.drawScoreboard()
            self.drawTitle()

        self.drawPrintlog()

        # compose and zoom
        if RENDER_MODE == 'plain':
            pass
        if RENDER_MODE == 'led':
            pygame.transform.scale(self.output, (SCR_W * 2, SCR_H), self.scaled)
            self.window.blit(self.scaled, (0, 0))
            self.window.blit(self.overlay, (0, 0))
        elif RENDER_MODE == 'sim':
            pygame.transform.scale(self.output, (WIN_W, WIN_H), self.window)
            self.window.blit(self.overlay, (0, 0))

        pygame.display.flip()


    def drawTunnel(self):
        for dist, rot in sorted(self.logos,key=lambda x: -x[0]):
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

            if logo_sprite == self.logo_filled: self.output.blit(scaled, (x, y))

            draw_lines(self.output,rot,size,[[26.261813, -13.008806], [26.249923, -13.001606], [26.237643, -13.008806], [26.225762999999997, -12.987656], [-7.500179600000006, 6.467753700000001], [-7.5574196000000065, 6.467753700000001], [-7.5465796000000065, 46.014574], [26.26750099999999, 65.508813], [60.05742099999999, 46.016152000000005], [60.05742099999999, 30.444071], [59.99233099999999, 30.444071], [60.05742099999999, 30.331587000000003], [53.08590099999999, 26.310009], [60.05742099999999, 22.288034], [60.05532099999999, 22.284334], [60.05742099999999, 22.283234], [60.05742099999999, 6.5575257], [60.02442099999999, 6.5575257], [60.05742099999999, 6.5007557], [26.27370599999999, -12.987662], [26.26182599999999, -13.008812]])
            draw_lines(self.output,rot,size,[[29.62222799999999, 28.488001000000004], [29.62222799999999, 28.488001000000004], [29.67740799999999, -2.853285299999996], [53.05539799999999, 10.545036000000003], [53.05539799999999, 18.243743000000002], [46.07939099999999, 22.267830000000004], [38.97228299999999, 18.167961000000005], [38.97228299999999, 26.251254000000003], [53.05539799999999, 34.375341000000006], [53.05539799999999, 41.971861000000004], [26.256672, 57.431595], [-0.55549667, 41.96421], [-0.55549667, 10.545041], [22.62034, -2.8120226], [22.62034, 24.438571], [17.035071, 21.20808], [10.032657999999998, 25.247745], [30.968867999999997, 37.359877999999995], [37.974318, 33.318099999999994], [29.622223999999996, 28.488006999999996]])


    def drawPlayer(self):
        anim = (self.tick // 3) % 2
        sprite = self.copter_sprites[anim]
        self.output.blit(sprite, (self.player.xpos, self.player.ypos))


    def drawTitle(self):
        if int(time.time() * 1000) % 500 < 250:
            title_color = COLORS['red']
        else:
            title_color = COLORS['white']

        self.font_huge.centerText(self.output, 'TOOLBOX', y=2, fgcolor=title_color)
        self.font_huge.centerText(self.output, 'HEXAGON', y=3, fgcolor=title_color)


    def drawScoreboard(self):
        #y = SCR_H/8 -2
        y = 0

        self.font.drawText(self.output, 'HI', x=1, y=y, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '00000', x=1, y=y+1, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '1UP', x=SCR_W/8-4, y=y, fgcolor=COLORS['white'])
        self.font.drawText(self.output, '00000', x=SCR_W/8-6, y=y+1, fgcolor=COLORS['white'])


    def drawPrintlog(self):
        self.font.locate(0, 0)

        outlines = []
        maxlines = SCR_H // 8

        for msg in PRINTLOG[-maxlines:]:
            for s in str(msg).split('\n'):
                outlines.append(s)

        for line in outlines[-maxlines:]:
            self.font.drawText(self.output, line.upper(), x=1, fgcolor=COLORS['white'])


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

                if e.key == pygame.K_LEFT:
                    self.player.xdir = -1
                elif e.key == pygame.K_RIGHT:
                    self.player.xdir = 1
                elif e.key == pygame.K_UP:
                    self.player.ydir = -1
                elif e.key == pygame.K_DOWN:
                    self.player.ydir = 1

                if self.mode == 'boot':
                    self.setMode('title')
                elif self.mode == 'title':
                    self.setMode('game')

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT:
                    if self.player.xdir < 0:
                        self.player.xdir = 0
                elif e.key == pygame.K_RIGHT:
                    if self.player.xdir > 0:
                        self.player.xdir = 0
                elif e.key == pygame.K_UP:
                    if self.player.ydir < 0:
                        self.player.ydir = 0
                elif e.key == pygame.K_DOWN:
                    if self.player.ydir > 0:
                        self.player.ydir = 0

            elif e.type == pygame.JOYAXISMOTION:
                if e.axis == 0:
                    self.player.xdir = e.value if abs(e.value) > 0.05 else 0
                elif e.axis == 1:
                    self.player.ydir = e.value if abs(e.value) > 0.05 else 0

            elif e.type == pygame.JOYBUTTONDOWN:
                if self.mode == 'boot':
                    self.setMode('title')
                elif self.mode == 'title':
                    self.setMode('game')


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

        self.player.update()


    def setMode(self, mode):
        self.mode = mode
        cls()


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
