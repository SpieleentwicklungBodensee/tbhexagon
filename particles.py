import pygame
import random

#from particles import Particles
#self.particles = Particles()
#self.particles.update_and_render(self.output,self.player)

PARTICLE_STYLE_SPARK=0
PARTICLE_STYLE_FLASH=1

class Particle:
    def __init__(self,x,y,style):
        self.x=x
        self.y=y
        self.vx=random.uniform(-2.0,2.0)
        self.vy=random.uniform(-2.0,2.0)
        self.style=style
        self.ttl=random.randrange(10,180)

particles_rnd_color=(0,0,0)

class Particles:
    def __init__(self):
        self.particles=[]
    def update_and_render(self,surface,camera,SCR_W,SCR_H):
        rnd_color=(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
        xx=-camera.xpos+SCR_W/2
        yy=-camera.ypos+SCR_H/2
        particles_remaining=[]
        for p in self.particles:
            p.ttl-=1
            if p.ttl>0: particles_remaining.append(p)
            p.x+=p.vx
            p.y+=p.vy
            if p.style==PARTICLE_STYLE_SPARK:
                p.vx*=0.9
                p.vy*=0.9
                p.vy+=0.1
                surface.set_at((int(p.x+xx),int(p.y+yy)),(255,255,255))
            elif p.style==PARTICLE_STYLE_FLASH:
                #s=4
                s=p.ttl/16
                pygame.draw.rect(surface,rnd_color,(int(p.x+xx-s),int(p.y+yy-s),s+s,s+s))

        self.particles=particles_remaining
    def player_collision(self,player):
        for i in range(8):
            p=Particle(player.xpos,player.ypos,PARTICLE_STYLE_SPARK)
            self.particles.append(p)
    def player_death(self,player):
        for i in range(16):
            p=Particle(player.xpos,player.ypos,PARTICLE_STYLE_SPARK)
            self.particles.append(p)
        for i in range(8):
            p=Particle(player.xpos,player.ypos,PARTICLE_STYLE_FLASH)
            self.particles.append(p)
