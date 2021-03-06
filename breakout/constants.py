import os, pygame
from pygame.locals import *
from utility import *

collide_sound = load_sound("boop.wav")
error_sound = load_sound("error.wav")
sad_sound = load_sound("sad.wav")
win_sound = load_sound("win.wav")

SCREEN_RECT = Rect(0, 0, 840, 480)
FIELD_RECT = Rect(0, 0, 640, 480)

LEFTWALL_RECT = Rect(20,10,20,460)
RIGHTWALL_RECT = Rect(590,10,20,460)
TOPWALL_RECT = Rect(20,10,590,20)

BRICKS_RECTS = [Rect( 40, 100, 100, 30), 
                Rect(140, 100, 100, 30),
                Rect(240, 100, 100, 30),
                Rect(340, 100, 100, 30),
                Rect(440, 100, 100, 30),
                Rect(540, 100, 50, 30),
                 
                Rect( 40, 150, 50, 30),
                Rect( 90, 150, 100, 30),
                Rect(190, 150, 100, 30),
                Rect(290, 150, 100, 30),
                Rect(390, 150, 100, 30),
                Rect(490, 150, 100, 30)]

BALL_INIT_RECT = Rect(420,400,4,4)
PADDLE_INIT_RECT = Rect(400,440,64,20)
PADDLE_AREA_RECT = Rect(40,440,590-20-20,20)
DEFAULT_INIT_LIVES = 3
DEFAULT_INIT_BALL_SPD = 5

PADDLE_SPD_UP_COLOR = (0,255,0)
BALL_SLOW_COLOR = (255,0,255)

POWERUP_LIST_RECT = (640,40)
POWERUP_DROP_RATE = 0.5
MAX_ACQ_POWERS = 6

POWERUP_RECT_SIZE = (10,10)
POWERUP_CHOICES=["paddle_spd","ball_spd"]