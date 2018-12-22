import os, pygame
from pygame.locals import *

SCREEN_RECT = Rect(0, 0, 740, 480)
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