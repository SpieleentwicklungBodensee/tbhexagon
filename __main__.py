import pygame
import pygame._sdl2.controller
import time
import random
import math
import colorsys
import zensur

from bitmapfont import BitmapFont
from particles import Particles
import highscore


# read settings from settings.py
# use default values if no settings.py exists

try:
    from settings import *
except ImportError:
    pass

if not 'RENDER_MODE' in dir():
    # 'led' = for led wall output
    # 'plain' = for pc/laptop or testing
    # 'sim' = led simulation for uli (deprecated)
    # 'arcade' = for toolbox arcade cabinet
    # 'square' = for square displays
    RENDER_MODE = 'led'

if not 'JOY_DEADZONE' in dir():
    JOY_DEADZONE = 0.2

if not 'FORCE_JOYSTICK_API' in dir():
    FORCE_JOYSTICK_API = False

if not 'DEFAULT_MODE' in dir():
    # 'boot', 'title', 'game', 'high'
    DEFAULT_MODE = 'boot'

if not 'DEFAULT_BRIGHTNESS' in dir():
    if RENDER_MODE == 'led':
        DEFAULT_BRIGHTNESS = -4
    else:
        DEFAULT_BRIGHTNESS = 0

if not 'HIGHSCORE_LIST_ENABLED' in dir():
    # if highscore list is disabled, only the 'simple' mode
    # with one highscore is supported. player can still enter
    # his name if HIGHSCORE_NAME_ENTRY_ENABLED is True
    HIGHSCORE_LIST_ENABLED = True

if not 'HIGHSCORE_NAME_ENTRY_ENABLED' in dir():
    # only has effect if highscore list is disabled
    HIGHSCORE_NAME_ENTRY_ENABLED = True

if not 'DONT_CENSOR_HIGHSCORE_NAMES' in dir():
    DONT_CENSOR_HIGHSCORE_NAMES = False



brightnessValue = DEFAULT_BRIGHTNESS
def gamma(v):
    return min(v * 2**(brightnessValue / 4), 255)

def brightness(color):
    color = list(color)
    if isinstance(color[0], (list, tuple)):
        result = []
        for co in color:
            result.append(tuple([gamma(c) for c in co]))
        return result
    return tuple([gamma(c) for c in color])

def colorize(surface, color):
    color = brightness(color)
    s = surface.copy()
    s.fill(color, special_flags=pygame.BLEND_MULT)
    return s

def expo(x, e):
    if e == 0.0:
        return x
    if e > 0.0:
        return ((1.0 + e)**x - 1.0) / e
    return math.log(1.0 - x * e) / math.log(1.0 - e)

def controlCurve(x):
    v = max(0.0, min((abs(x) - JOY_DEADZONE) / (1.0 - JOY_DEADZONE), 1.0))
    return math.copysign(expo(v, 1.0) * 1.5, x)

# custom print functions

PRINTLOG = []

__oldprint = print
def __newprint(*msgs):
    PRINTLOG.append(' '.join(str(msg) for msg in msgs))
    __oldprint(*msgs)
print = __newprint

def cls():
    PRINTLOG.clear()


# vector draw/render functions

FIRST_PERSON = not False
LOGO_FILLED = pygame.image.load('gfx/tb-logo-black.png')
LOGO_INVERSE = pygame.image.load('gfx/tb-logo-inverse.png')

class Wall:
    def __init__(self):
        self.pos=(0,0,200)
        self.vel=(0,0,-0.5)
        self.rot=0
        self.rot_vel=0
        self.color=(255,0,0)
        self.collisionSprite = None
        self.inverseSprite = None
        self.score = 10

    def update(self):
        self.pos=(self.pos[0]+self.vel[0],self.pos[1]+self.vel[1],self.pos[2]+self.vel[2])
        self.rot+=self.rot_vel

    def render(self,surface,x,y):
        if self.pos[2]<=0: return

        x+=self.pos[0]
        y+=self.pos[1]

        size=2560/self.pos[2]
        color=(max(min(int( self.color[0]/255 * min(0.1*size*size,255) ),255),0),
               max(min(int( self.color[1]/255 * min(0.1*size*size,255) ),255),0),
               max(min(int( self.color[2]/255 * min(0.1*size*size,255) ),255),0))
        xy_mul=0.01
        if not FIRST_PERSON: xy_mul=0

        if self.pos[2]>4:
            img=pygame.transform.scale(LOGO_FILLED,(size,size))
            #img.set_alpha(128)
            img=pygame.transform.rotate(img,self.rot)
            img_x=(SCR_W-img.get_width() )/2-x*xy_mul*size
            img_y=(SCR_H-img.get_height())/2-y*xy_mul*size
            #surface.blit(colorize(img, (0, 0, 0)),(img_x,img_y))
            surface.blit (         img            ,(img_x,img_y))

        if self.pos[2]<8 and self.pos[2]>4:
            self.collisionSprite = img
            self.collisionSprite_xpos = img_x
            self.collisionSprite_ypos = img_y

            # inverse collision logo
            img=pygame.transform.scale(LOGO_INVERSE,(size,size))
            #img.set_alpha(128)
            img=pygame.transform.rotate(img,self.rot)
            img_x=(SCR_W-img.get_width() )/2-x*xy_mul*size
            img_y=(SCR_H-img.get_height())/2-y*xy_mul*size

            self.inverseSprite = img
            self.inverseSprite_xpos = img_x
            self.inverseSprite_ypos = img_y
        else:
            self.collisionSprite = None
            self.inverseSprite = None

        draw_lines(surface,color,-x*xy_mul*size,-y*xy_mul*size,self.rot,size,[[26.261813, -13.008806], [26.249923, -13.001606], [26.237643, -13.008806], [26.225762999999997, -12.987656], [-7.500179600000006, 6.467753700000001], [-7.5574196000000065, 6.467753700000001], [-7.5465796000000065, 46.014574], [26.26750099999999, 65.508813], [60.05742099999999, 46.016152000000005], [60.05742099999999, 30.444071], [59.99233099999999, 30.444071], [60.05742099999999, 30.331587000000003], [53.08590099999999, 26.310009], [60.05742099999999, 22.288034], [60.05532099999999, 22.284334], [60.05742099999999, 22.283234], [60.05742099999999, 6.5575257], [60.02442099999999, 6.5575257], [60.05742099999999, 6.5007557], [26.27370599999999, -12.987662], [26.26182599999999, -13.008812]]);
        draw_lines(surface,color,-x*xy_mul*size,-y*xy_mul*size,self.rot,size,[[29.62222799999999, 28.488001000000004], [29.62222799999999, 28.488001000000004], [29.67740799999999, -2.853285299999996], [53.05539799999999, 10.545036000000003], [53.05539799999999, 18.243743000000002], [46.07939099999999, 22.267830000000004], [38.97228299999999, 18.167961000000005], [38.97228299999999, 26.251254000000003], [53.05539799999999, 34.375341000000006], [53.05539799999999, 41.971861000000004], [26.256672, 57.431595], [-0.55549667, 41.96421], [-0.55549667, 10.545041], [22.62034, -2.8120226], [22.62034, 24.438571], [17.035071, 21.20808], [10.032657999999998, 25.247745], [30.968867999999997, 37.359877999999995], [37.974318, 33.318099999999994], [29.622223999999996, 28.488006999999996]]);

def draw_lines(surface,color,x,y,rot,size,verts):
    verts_final=[]
    for v in verts:

        # tb logo specific adjustments
        v=[v[0]*1.333333+30,v[1]*-1.333333+100]
        v=[v[0]-130/2,v[1]-130/2]

        # rotate
        v1=rotate((0,0),v,-rot*math.pi/180)

        # scale
        v1=scale(v1,size*0.0087)

        # offset + center on screen
        v1=(v1[0]+x+SCR_W/2,v1[1]+y+SCR_H/2)

        verts_final.append(v1)
    pygame.draw.lines(surface,brightness(color),True,verts_final,width=max(int(size/80),1))

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


# the game

SCR_W, SCR_H = 256, 320     # the 'designed' resolution for the game
WIN_W, WIN_H = 1024, 1280   # window size for led simulation mode

COLORS = {'red': (255, 0, 0),
          'white': (255, 255, 255),
          'black': (0, 0, 0),
          }

DISTANCE = 64
SPEED = 1.0 / 128

pygame.display.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)


class Player():
    def __init__(self, x, y):
        self.xpos = x
        self.ypos = y

        self.xdir = 0
        self.ydir = 0

    def update(self,camera):
        self.xpos += self.xdir
        self.ypos += self.ydir


class Camera():
    def __init__(self,):
        self.xpos = 0
        self.ypos = 0
    def update(self, player, speed=0.1):
        if FIRST_PERSON:
            self.xpos = self.xpos*(1-speed) + player.xpos*speed
            self.ypos = self.ypos*(1-speed) + player.ypos*speed


class EventTimer():
    events = {}

    def set(name, ticks):
        EventTimer.events[name] = (ticks, 0)

    def tick():
        for name, e in EventTimer.events.items():
            EventTimer.events[name] = (e[0], e[1] + 1)

    def isDue(name, delete=True):
        if not name in EventTimer.events:
            return False

        when, current = EventTimer.events[name]

        if current >= when:
            if delete:
                del EventTimer.events[name]

            return True

        return False

    def isPending(name):
        if not name in EventTimer.events:
            return False

        return not EventTimer.isDue(name, False)

    def getTicks(name):
        return EventTimer.events[name][1]


class Game():
    def __init__(self):
        global SCR_W
        global SCR_H

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

        elif RENDER_MODE == 'arcade':
            SCR_W = 320
            SCR_H = 256
            self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED|pygame.FULLSCREEN)
            self.output = self.window

        elif RENDER_MODE == 'square':
            SCR_W = 256
            SCR_H = 256
            self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED|pygame.FULLSCREEN)
            self.output = self.window

        elif RENDER_MODE == 'wide':
            SCR_W = 452
            SCR_H = 256
            self.window = pygame.display.set_mode((SCR_W, SCR_H), flags=pygame.SCALED|pygame.FULLSCREEN)
            self.output = self.window

        self.running = False

        print('loading graphics...')

        self.font = BitmapFont('gfx/heimatfont.png', scr_w=SCR_W, scr_h=SCR_H)
        self.font_big = BitmapFont('gfx/heimatfont.png', zoom=2, scr_w=SCR_W, scr_h=SCR_H)
        self.font_huge = BitmapFont('gfx/heimatfont.png', zoom=3, scr_w=SCR_W, scr_h=SCR_H)

        self.logo = pygame.image.load('gfx/tb-logo-pure-1.png')
        self.logo_filled = pygame.image.load('gfx/tb-logo-pure-2.png')
        self.logo_inverse = pygame.image.load('gfx/tb-logo-inverse.png')

        self.copter_sprites = (pygame.image.load('gfx/copter1.png'), pygame.image.load('gfx/copter2.png'))

        print('loading sound fx...')

        self.sound_passthrough1 = pygame.mixer.Sound('sfx/passthrough1.wav')
        self.sound_passthrough2 = pygame.mixer.Sound('sfx/passthrough2.wav')
        self.sound_gameover = pygame.mixer.Sound('sfx/verrecksound.wav')
        self.music = None # loaded later
        self.musicCount = 0

        self.musicVolume = 1.0
        self.soundVolume = 1.0

        if HIGHSCORE_LIST_ENABLED:
            print('loading highscores...')
            try:
                highscore.load()
            except:
                print(' - not found')

        self.collisionInfo = None

        self.walls = []

        self.tick = 0

        self.player = Player(0, 0)
        self.player_drawx = SCR_W/2 # for collision
        self.player_drawy = SCR_H/2 # for collision

        self.camera = Camera()

        self.particles = Particles()

        self.score = 0
        self.highscore = 0

        self.debounce_x = 0
        self.debounce_y = 0
        self.debounce_tick = 0

        self.mode = DEFAULT_MODE

        self.gameover = False

        print('init game controllers...')
        pygame._sdl2.controller.init()
        self.joymode = None

        if not FORCE_JOYSTICK_API:
            if not pygame._sdl2.controller.get_count():
                print('no controllers detected')
            else:
                self.joymode = 'controller'
                print('found controllers:')
                for i in range(pygame._sdl2.controller.get_count()):
                    joy = pygame._sdl2.controller.Controller(i)
                    print(' - ' + joy.as_joystick().get_name())

        if not self.joymode:    # use joystick lib as fallback
            pygame.joystick.init()
            if not pygame.joystick.get_count():
                print('no joystick detected')
            else:
                self.joymode = 'joystick'
                print('found joysticks:')
                for i in range(pygame.joystick.get_count()):
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    print(' - ' + joy.get_name())

        print('\ninit ok')

        # show help
        print('\n\n\nkeyboard commands:')
        print('------------------')
        print('f1  less brightness')
        print('f2  more brightness')
        print('f3  - music volume')
        print('f4  + music volume')
        print('f5  - sound volume')
        print('f6  + sound volume')
        print('')
        print('f8  clear highscore')

        if RENDER_MODE != 'led':
            print('\nf11 toggle fullscreen')

        if self.joymode is not None:
            print('\n\n\npress button/space to continue')
        else:
            print('\n\n\npress space to continue')

    def render(self):
        self.output.fill((0, 0, 0))

        if self.mode == 'game':
            self.drawTunnel()

            if self.gameover:
                self.drawGameover()
            else:
                self.drawPlayer()

            self.drawScoreboard()

            if EventTimer.isPending('getready'):
                self.drawGetReady()

        elif self.mode == 'title':
            self.drawTunnel()
            self.drawScoreboard()
            self.drawTitle()

            if HIGHSCORE_LIST_ENABLED:
                self.drawHallOfFame()

        elif self.mode == 'high':
            self.drawTunnel()
            self.drawNameEnty()

        self.particles.update_and_render(self.output,self.player,SCR_W,SCR_H)

        self.drawPrintlog()
        #self.drawDebugInfo()

        # draw volume message
        if EventTimer.isPending('musicvol-msg'):
            self.font.centerText(self.output, 'MUSIC VOLUME: %2i%%' % round(self.musicVolume * 100))
        if EventTimer.isPending('soundvol-msg'):
            self.font.centerText(self.output, 'SOUND VOLUME: %2i%%' % round(self.soundVolume * 100))
        if EventTimer.isPending('brightness-msg'):
            self.font.centerText(self.output, 'DARKNESS: %2i' % round(-brightnessValue))

        # compose and zoom
        if RENDER_MODE == 'plain':
            pass
        elif RENDER_MODE == 'led':
            pygame.transform.scale(self.output, (SCR_W * 2, SCR_H), self.scaled)
            self.window.blit(self.scaled, (0, 0))
            self.window.blit(self.overlay, (0, 0))
        elif RENDER_MODE == 'sim':
            pygame.transform.scale(self.output, (WIN_W, WIN_H), self.window)
            self.window.blit(self.overlay, (0, 0))
        elif RENDER_MODE == 'arcade':
            pass
        elif RENDER_MODE == 'square':
            pass

        pygame.display.flip()


    def drawTunnel(self):
        for wall in sorted(self.walls,key=lambda x: -x.pos[2]):
            wall.render(self.output,self.camera.xpos,self.camera.ypos)


    def drawPlayer(self):
        anim = (self.tick // 3) % 2
        sprite = self.copter_sprites[anim]

        x = SCR_W/2+self.player.xpos-self.camera.xpos-sprite.get_width()/2
        y = SCR_H/2+self.player.ypos-self.camera.ypos-sprite.get_height()/2

        self.output.blit(colorize(sprite, (255,255,255)), (x, y))

        self.player_drawx = x   # for collision
        self.player_drawy = y   # for collision


    def drawTitle(self):
        if self.tick % 32 < 16:
            title_color = COLORS['red']
        else:
            title_color = COLORS['white']

        if RENDER_MODE in ('arcade', 'square'):
            y = 1.5
        elif RENDER_MODE in ('wide'):
            y = 1
        else:
            y = 2

        self.font_huge.centerText(self.output, 'TOOLBOX', y=y, fgcolor=brightness(title_color))
        self.font_huge.centerText(self.output, 'HEXAGON', fgcolor=brightness(title_color))

        if self.tick % 32 < 16:
            if self.joymode is not None:
                presstext = 'PRESS BUTTON'
            else:
                presstext = 'PRESS SPACE'

            y = SCR_H//8 * 0.75

            if RENDER_MODE in ('arcade', 'square'):
                y += 2
            elif RENDER_MODE in ('wide'):
                y += 4

            self.font.centerText(self.output, presstext, y=y, fgcolor=brightness(COLORS['white']))


    def drawScoreboard(self):
        y = 0

        if HIGHSCORE_LIST_ENABLED:
            hs = highscore.highscorelist[0][0]
            hn = highscore.highscorelist[0][1]
        else:
            hs = self.highscore
            hn = highscore.name

        self.font.drawText(self.output, hn or 'HI', x=1, y=y, fgcolor=brightness(COLORS['white']))
        self.font.drawText(self.output, '%05i' % hs, x=1, y=y+1, fgcolor=brightness(COLORS['white']))
        self.font.drawText(self.output, '1UP', x=SCR_W/8-4, y=y, fgcolor=brightness(COLORS['white']))
        self.font.drawText(self.output, '%05i' % self.score, x=SCR_W/8-6, y=y+1, fgcolor=brightness(COLORS['white']))


    def drawHallOfFame(self):
        if (self.tick - self.tick_last_mode_change) % 800 < 300:
            return

        y = SCR_H/self.font.font_h/2-5

        if RENDER_MODE in ('arcade', 'square'):
            y += 1
        elif RENDER_MODE in ('wide'):
            y += 1.5

        self.font.centerText(self.output, 'TOP SCORES', y=y)
        self.font.centerText(self.output, '')
        self.font.centerText(self.output, '')

        for i, entry in enumerate(highscore.gettop(5)):
            score, name = entry

            if (self.tick - self.tick_last_mode_change) % 800 - 300 > (i + 1) * 50:
                self.font.centerText(self.output, '%05i  %s' % (score, name), fgcolor=brightness(COLORS['white']))
                self.font.centerText(self.output, '')


    def drawPrintlog(self):
        self.font.locate(0, 0)

        outlines = []
        maxlines = SCR_H // 8

        for msg in PRINTLOG[-maxlines:]:
            for s in str(msg).split('\n'):
                outlines.append(s)

        for line in outlines[-maxlines:]:
            self.font.drawText(self.output, line.upper(), x=1, fgcolor=brightness(COLORS['white']))


    def drawDebugInfo(self):
        if self.collisionInfo is not None:
            self.output.fill((40, 40, 40))
            self.output.blit(self.collisionInfo[0], (self.collisionInfo[1], self.collisionInfo[2]))
            self.output.blit(self.copter_sprites[0], (self.player_drawx, self.player_drawy))

            self.font_big.centerText(self.output, 'C R A S H', y=(SCR_H/self.font_big.font_h)/2-3)

            pygame.display.flip()

            time.sleep(0.05)

            self.collisionInfo = None


    def drawGameover(self):
        if EventTimer.getTicks('gameover') > 30:
            self.font_huge.centerText(self.output, 'GAME OVER', y=(SCR_H/self.font_huge.font_h)/2, fgcolor=brightness(COLORS['white']))


    def drawGetReady(self):
        if self.tick % 32 < 16:
            self.font.centerText(self.output, 'GET READY', y=(SCR_H/self.font.font_h)/3, fgcolor=brightness(COLORS['white']))


    def drawNameEnty(self):
        self.font_big.centerText(self.output, '%05i' % self.score, y=SCR_H/self.font_big.font_h/2-2, fgcolor=brightness(COLORS['white']))
        self.font.centerText(self.output, 'NEW HIGHSCORE!', y=SCR_H/self.font.font_h/2, fgcolor=brightness(COLORS['white']))
        self.font.centerText(self.output, '')
        self.font.centerText(self.output, 'ENTER YOUR NAME:', fgcolor=brightness(COLORS['white']))

        self.font_big.centerText(self.output, highscore.name, y=SCR_H/self.font_big.font_h/2+2, fgcolor=brightness(COLORS['white']))

        # draw cursor
        if self.tick % 32 < 16:
            curstr = (' ' * highscore.name_cursor) + '_' + ' ' * (highscore.MAX_LENGTH - highscore.name_cursor - 1)
            self.font_big.centerText(self.output, curstr, y=SCR_H/self.font_big.font_h/2+2.3, fgcolor=brightness(COLORS['white']))


    def collisionCheck(self):
        playermask = pygame.mask.from_surface(self.copter_sprites[0])

        self.collisionInfo = None

        for wall in self.walls:
            if wall.collisionSprite is not None:
                mask = pygame.mask.from_surface(wall.collisionSprite)

                if mask.overlap(playermask, (self.player_drawx - wall.collisionSprite_xpos,
                                             self.player_drawy - wall.collisionSprite_ypos)) is not None:
                    self.collisionInfo = (wall.collisionSprite, wall.collisionSprite_xpos, wall.collisionSprite_ypos)
                    self.doGameOver()
                    return

                mask = pygame.mask.from_surface(wall.inverseSprite)

                if mask.overlap(playermask, (self.player_drawx - wall.inverseSprite_xpos,
                                             self.player_drawy - wall.inverseSprite_ypos)) is not None:
                    #self.collisionInfo = (wall.inverseSprite, wall.inverseSprite_xpos, wall.inverseSprite_ypos)

                    if wall.score != 0:
                        self.score += wall.score
                        wall.score = 0

                        if wall.style != 2:
                            self.sound_passthrough1.play()
                        else:
                            self.sound_passthrough2.play()
                        return

                self.score -= wall.score
                wall.score = 0
                if self.score <0:
                    self.score = 0
                    self.doGameOver()
                return


    def doGameOver(self):
        self.gameover = True

        if HIGHSCORE_LIST_ENABLED and highscore.check(self.score):
            EventTimer.set('gameover', 100) # shorter wait time on highscore
        elif HIGHSCORE_NAME_ENTRY_ENABLED and self.score > self.highscore:
            EventTimer.set('gameover', 100) # shorter wait time on highscore
        else:
            EventTimer.set('gameover', 200)

        self.music.stop()
        self.music = None
        self.particles.player_death(self.player)
        self.sound_gameover.play()


    def controls(self):
        events = pygame.event.get()

        modstate = pygame.key.get_mods()

        for e in events:
            if e.type==pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                if e.key == pygame.K_F8:
                    self.highscore = 0
                    highscore.clear()

                if e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

                if e.key == pygame.K_RETURN:
                    if modstate & pygame.KMOD_ALT:
                        pygame.display.toggle_fullscreen()

                global brightnessValue
                if e.key == pygame.K_F1:
                    brightnessValue -= 1
                    EventTimer.set('brightness-msg', 60)
                elif e.key == pygame.K_F2:
                    brightnessValue = min(brightnessValue + 1, 0)
                    EventTimer.set('brightness-msg', 60)

                elif e.key == pygame.K_F3:
                    self.musicVolume = max(self.musicVolume -0.1, 0)
                    EventTimer.set('musicvol-msg', 60)
                elif e.key == pygame.K_F4:
                    self.musicVolume = min(self.musicVolume +0.1, 1.0)
                    EventTimer.set('musicvol-msg', 60)
                elif e.key == pygame.K_F5:
                    self.soundVolume = max(self.soundVolume -0.1, 0)
                    EventTimer.set('soundvol-msg', 60)
                elif e.key == pygame.K_F6:
                    self.soundVolume = min(self.soundVolume +0.1, 1.0)
                    EventTimer.set('soundvol-msg', 60)

                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.on_left_pressed()
                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.on_right_pressed()
                elif e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.on_up_pressed()
                elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
                    self.on_down_pressed()

                if e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
                    self.on_fire_pressed()

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    self.on_left_released()
                elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    self.on_right_released()
                elif e.key == pygame.K_UP or e.key == pygame.K_w:
                    self.on_up_released()
                elif e.key == pygame.K_DOWN or e.key == pygame.K_s:
                    self.on_down_released()

            elif e.type == pygame.CONTROLLERAXISMOTION and self.joymode == 'controller':
                value = max(-1, e.value / 32767)

                if e.axis == pygame.CONTROLLER_AXIS_LEFTX:
                    self.on_axis_x(value)
                elif e.axis == pygame.CONTROLLER_AXIS_LEFTY:
                    self.on_axis_y(value)

            elif e.type == pygame.CONTROLLERBUTTONDOWN and self.joymode == 'controller':
                if e.button in (pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_X, pygame.CONTROLLER_BUTTON_Y):
                    self.on_fire_pressed()

                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    self.on_left_pressed()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.on_right_pressed()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_UP:
                    self.on_up_pressed()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                    self.on_down_pressed()

            elif e.type == pygame.CONTROLLERBUTTONUP and self.joymode == 'controller':
                if e.button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    self.on_left_released()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.on_right_released()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_UP:
                    self.on_up_released()
                elif e.button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                    self.on_down_released()

            elif e.type == pygame.JOYAXISMOTION and self.joymode == 'joystick':
                if e.axis == 0:
                    self.on_axis_x(e.value)
                elif e.axis == 1:
                    self.on_axis_y(e.value)

            elif e.type == pygame.JOYBUTTONDOWN and self.joymode == 'joystick':
                self.on_fire_pressed()

    def on_fire_pressed(self):
        if self.mode == 'boot':
            self.setMode('title')
        elif self.mode == 'title':
            self.newGame()
        elif self.mode == 'high':
            if not highscore.step(1):
                self.setMode('title')
                if not DONT_CENSOR_HIGHSCORE_NAMES: highscore.name = zensur.censor_highscore_name(highscore.name)
                if highscore.insert(self.score, highscore.name):
                    self.tick_last_mode_change -= 280   # show high score list sooner

                    if HIGHSCORE_LIST_ENABLED:
                        try:
                            highscore.save()
                        except:
                            print('error saving highscores')

    def on_left_pressed(self):
        if self.mode == 'game':
            self.player.xdir = -1.5
        elif self.mode == 'high':
            highscore.step(-1)

    def on_right_pressed(self):
        if self.mode == 'game':
            self.player.xdir = 1.5
        elif self.mode == 'high':
            highscore.step(1)

    def on_up_pressed(self):
        if self.mode == 'game':
            self.player.ydir = -1.5
        elif self.mode == 'high':
            highscore.scroll(-1)

    def on_down_pressed(self):
        if self.mode == 'game':
            self.player.ydir = 1.5
        elif self.mode == 'high':
            highscore.scroll(1)

    def on_left_released(self):
        if self.player.xdir < 0:
            self.player.xdir = 0

    def on_right_released(self):
        if self.player.xdir > 0:
            self.player.xdir = 0

    def on_up_released(self):
        if self.player.ydir < 0:
            self.player.ydir = 0

    def on_down_released(self):
        if self.player.ydir > 0:
            self.player.ydir = 0

    def on_axis_x(self, value):
        if self.mode == 'game':
            self.player.xdir = controlCurve(value)

        elif self.mode == 'high':
            if value > 0.75:
                if self.debounce_x == 0:
                    highscore.step(1)
                    self.debounce_x = 1
            elif value < -0.75:
                if self.debounce_x == 0:
                    highscore.step(-1)
                    self.debounce_x = -1
            else:
                self.debounce_x = 0

    def on_axis_y(self, value):
        if self.mode == 'game':
            self.player.ydir = controlCurve(value)

        elif self.mode == 'high':
            if value > 0.75:
                if self.debounce_y == 0:
                    #highscore.scroll(-1)   # will be scrolled in update()
                    self.debounce_y = 1
                    self.debounce_tick = self.tick
            elif value < -0.75:
                if self.debounce_y == 0:
                    #highscore.scroll(1)    # will be scrolled in update()
                    self.debounce_y = -1
                    self.debounce_tick = self.tick
            else:
                self.debounce_y = 0


    def update(self):
        if self.music:
            self.music.set_volume(self.musicVolume)

        self.sound_passthrough1.set_volume(self.soundVolume)
        self.sound_passthrough2.set_volume(self.soundVolume)
        self.sound_gameover.set_volume(self.soundVolume)

        for wall in self.walls:
            wall.update()

        # generate new walls
        wall_style   =int(self.tick/60/3)%4
        level_repeats=int(self.tick/60/3 /4)
        level_intensity=level_repeats/6
        if self.mode!='game': level_intensity=0

        level_intensity = expo(level_intensity, -1.5) * 0.75 # "was ist jetzt los?"

        sway_amp_per_second=1
        sway_amp_max=100
        # |
        # V
        t=self.tick/180
        a=sway_amp_per_second*self.tick/60
        if a>sway_amp_max: a=sway_amp_max
        if a<0 or self.mode!='game': a=0
        wall_pos=(math.sin(t)*a,math.cos(t)*a,200)

        if(wall_style==0):
            if level_intensity>=2 or self.tick%(int(60-30*level_intensity))==0:
                wall=Wall()
                #wall.color=(wall.color[0]-255*level_intensity,wall.color[1]-255*level_intensity,wall.color[2]-255*level_intensity)
                sub_sway_t=self.tick%(60*3)/(60*3) # normalized
                sub_sway_a=40*math.sin(sub_sway_t*math.pi)*level_intensity
                sub_sway_x=math.sin(sub_sway_t*5)*sub_sway_a
                sub_sway_y=math.cos(sub_sway_t*5)*sub_sway_a
                wall.pos=(wall_pos[0]+sub_sway_x,wall_pos[1]+sub_sway_y,wall_pos[2])
                wall.style=wall_style
                self.walls.append(wall)
        elif(wall_style==1):
            if self.tick%60==0:
                wall=Wall()
                wall.rot=-self.tick*2*level_intensity
                wall.rot_vel=0.2+2*level_intensity
                wall.pos=wall_pos
                wall.style=wall_style
                self.walls.append(wall)
        elif(wall_style==2):
            if self.tick%15==0:
                wall=Wall()
                wall.rot=self.tick*2*level_intensity
                wall.rot_vel=-1.2*level_intensity
                color_min=30
                #wall.color=(random.randrange(color_min,255),random.randrange(color_min,255),random.randrange(color_min,255))
                wall.color=colorsys.hsv_to_rgb((self.tick%100)/100,1,1)
                wall.color=(int(wall.color[0]*255),int(wall.color[1]*255),int(wall.color[2]*255))
                wall.pos=wall_pos
                wall.style=wall_style
                self.walls.append(wall)
        elif(wall_style==3):
            if self.tick%60==30:
                wall=Wall()
                wall.color=(0,128,255)
                wall.pos=wall_pos
                wall.style=wall_style
                self.walls.append(wall)

                wall=Wall()
                wall.color=(0,128,255)
                wall.rot_vel=level_intensity*0.25
                wall.pos=wall_pos
                wall.style=wall_style
                self.walls.append(wall)

        # delete passed walls
        new_walls = []
        for wall in self.walls:
            if wall.pos[2]>0: new_walls.append(wall)
        self.walls = new_walls

        self.camera.update(self.player, speed=0.02 if self.mode == 'title' else 0.1)

        if not self.gameover and self.mode != 'title':
            self.player.update(self.camera)
            self.collisionCheck()

        if self.gameover:
            if EventTimer.isDue('gameover'):
                self.backToTitle()


        # auto scroll through letters in highscore name entry when analog input is used
        if self.mode == 'high':
            if self.debounce_y:
                if (self.tick - self.debounce_tick) % 12 == 0:
                    highscore.scroll(self.debounce_y * -1)


    def setMode(self, mode):
        self.mode = mode
        self.tick_last_mode_change = self.tick
        cls()


    def backToTitle(self):
        self.player.xpos = 0
        self.player.ypos = 0

        if HIGHSCORE_LIST_ENABLED:
            if highscore.check(self.score):
                self.setMode('high')
                highscore.reset()
                return

        elif HIGHSCORE_NAME_ENTRY_ENABLED:
            if self.score > self.highscore:
                self.highscore = self.score
                self.setMode('high')
                highscore.reset()
                return

        self.setMode('title')


    def newGame(self):
        self.score = 0

        self.walls = []
        self.tick = 0

        self.player.xpos = 0
        self.player.ypos = 0

        self.gameover = False

        self.collisionInfo = False

        self.musicCount += 1
        self.music = pygame.mixer.Sound(['sfx/tbhexagon-space-soundtrack-1.wav',
                                         'sfx/tbhexagon-space-soundtrack-2.wav'][self.musicCount % 2])
        self.music.play(loops=-1, fade_ms=6000)

        self.setMode('game')

        EventTimer.set('getready', 32*6)


    def start(self):
        self.running = True

        clock = pygame.time.Clock()

        while self.running:
            self.render()
            self.controls()
            self.update()

            self.tick += 1
            EventTimer.tick()

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
