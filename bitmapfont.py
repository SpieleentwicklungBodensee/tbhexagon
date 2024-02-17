
import pygame

NUM_CHARS = 96
TEXT_CACHING = True
UPPERCASE_MODE = False


class BitmapFont(object):
    def __init__(self, filename, font_w=8, font_h=8, colors=None, zoom=1, scr_w=320, scr_h=240):
        self.lastxpos, self.lastypos = 0, 0

        self.font_w = font_w
        self.font_h = font_h
        
        self.scr_w = scr_w
        self.scr_h = scr_h

        self.fonts = {}

        self.lastcolor = (255, 255, 255)

        self.font = pygame.image.load(filename)

        self.font_w *= zoom
        self.font_h *= zoom

        self.textCache = {}

    def loadFont(self, c):
        f = pygame.transform.scale(self.font, (self.font_w * NUM_CHARS, self.font_h))
        f.fill(c, special_flags=pygame.BLEND_MULT)
        self.fonts[c] = f

    def drawText(self, output, text, x=None, y=None, fgcolor=None, bgcolor=None, blink=False):
        global tick
        if blink:
            if tick % 90 >= 45:
                return

        if x is None:
            x = self.lastxpos
        if y is None:
            y = self.lastypos

        if fgcolor is None:
            fgcolor = self.lastcolor
        else:
            self.lastcolor = fgcolor

        if UPPERCASE_MODE:
            text = text.upper()

        if bgcolor is not None:
            output.fill(bgcolor, (x * self.font_w,
                                 (y * self.font_h),
                                 len(text) * self.font_w,
                                 (self.font_h))
                                 )

        if fgcolor not in self.fonts:
            self.loadFont(fgcolor)

        if TEXT_CACHING:
            key = (text, fgcolor, bgcolor)

            if key not in self.textCache:
                cacheSurface = pygame.Surface((len(text) * self.font_w, self.font_h), flags=pygame.SRCALPHA)

                for i, c in enumerate(text):
                    grabx = (ord(c) - 32) * self.font_w
                    blitx = i * self.font_w
                    blity = (self.font_h - self.font_h + 1) / 2

                    cacheSurface.blit(self.fonts[fgcolor], (blitx, blity), (grabx, 0, self.font_w, self.font_h))
                    self.textCache[key] = cacheSurface
            else:
                cacheSurface = self.textCache[key]

            blitx = x * self.font_w
            blity = y * self.font_h + (self.font_h - self.font_h + 1) / 2
            output.blit(cacheSurface, (blitx, blity))
        else:
            for i, c in enumerate(text):
                grabx = (ord(c) - 32) * self.font_w
                blitx = (x + i) * self.font_w
                blity = y * self.font_h + (self.font_h - self.font_h + 1) / 2

                output.blit(self.fonts[fgcolor], (blitx, blity), (grabx, 0, self.font_w, self.font_h))

        self.lastxpos = x
        self.lastypos = y + 1

    def centerText(self, output, text, y=None, fgcolor=None, bgcolor=None, blink=False):
        x = ((self.scr_w / self.font_w) - len(text)) / 2
        self.drawText(output, text, x, y, fgcolor, bgcolor, blink)

    def locate(self, x=None, y=None):
        if x is not None:
            self.lastxpos = x
        if y is not None:
            self.lastypos = y

    def locateRel(self, x=None, y=None):
        if x is not None:
            self.lastxpos += x
        if y is not None:
            self.lastypos += y


