import os, pygame
from ptext import ptext
from pygame.locals import *
from constants import *

import random
import pdb
class Obstacle(pygame.sprite.Sprite):
  def __init__(self,rect,color,collide_sound):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(rect.size)
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.topleft = rect.topleft
    self.sound = collide_sound
    self.reset()
    
  def reset(self):
    pass

  def collided(self):
    # pdb.set_trace()
    self.sound.play()
    return True

  def update(self,ps):
    ball = ps["ball"]
    bnextpos = ball.nextpos()
    ball_col,ball_row = bnextpos.topleft
    bw,bh = bnextpos.size
    lcol, trow = self.rect.topleft
    w,h = self.rect.size
    rcol = lcol+w
    bot_row = trow+h
    ball_interior_col = lcol<= ball_col <= rcol
    ball_interior_row = trow<= ball_row <= bot_row
    if not ps["inplay"]: return False
    if ball_interior_row and (rcol-ball.spd<=ball_col <=rcol+1):
      ball.bounce("right")
      return self.collided()
    
    if ball_interior_row and (lcol-1<=ball_col+bw <=lcol+ball.spd):
      ball.bounce("left")
      return self.collided()
    
    if ball_interior_col and (trow-2*ball.spd<=ball_row+bh <=trow+2):
      ball.bounce("up")
      return self.collided()
    
    if ball_interior_col and (bot_row-2<=ball_row <=bot_row+ball.spd):
      ball.bounce("down")
      return self.collided()

    return False

class Bounceable(pygame.sprite.Sprite):
  def __init__(self,rect,speed,dir):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(rect.size)
    self.initspd = speed
    self.initdir = dir
    self.reset()

  def reset(self):
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.resetspd()

  def resetspd(self):
    self.spd = self.initspd #pixels per frame
    self.dir = self.initdir #+x and +y

  def nextpos(self):
    return self.rect.move(self._poschg())

  def _poschg(self):
    return (self.spd*self.dir[0], self.spd*self.dir[1])

  def bounce(self,nextdir=None):
    if nextdir=="up":
      self.dir=(self.dir[0],-1)
    elif nextdir=="down":
      self.dir=(self.dir[0],1)
    elif nextdir=="left":
      self.dir=(-1,self.dir[1])
    elif nextdir=="right":
      self.dir=(1,self.dir[1])
    else: assert(False)
    
  def update(self,ps):
    pass

class Brick(Obstacle):
  active_powerups_group = None
  def __init__(self,rect,color,sound,active_powerups_group):
    Obstacle.__init__(self,rect,color,sound)
    Brick.active_powerups_group = active_powerups_group

  def collided(self):
    Obstacle.collided(self)
    self.kill()
    return True

  def update(self,ps):
    if Obstacle.update(self,ps):
      if len(ps["acq_plist"])<MAX_ACQ_POWERS and random.random() < POWERUP_DROP_RATE:
        prect = Rect((0,0),POWERUP_RECT_SIZE).clamp(self.rect)
        ch = random.choice(POWERUP_CHOICES)
        if ch=="paddle_spd":
          powerup = PaddleSpeed(prect, ps["acq_plist"], collide_sound,1.5)
        elif ch=="ball_spd":
          powerup = BallSpeed(prect, ps["acq_plist"], collide_sound,0.8)
        Brick.active_powerups_group.add(powerup)

class Wall(Obstacle):
  def __init__(self,rect,sound):
    Obstacle.__init__(self,rect,(255,255,255),sound)

  def chgcolorto(self,color):
    self.image.fill(color)

class Paddle(Obstacle):
  def __init__(self,sound):
    Obstacle.__init__(self,PADDLE_INIT_RECT,(255,255,255),sound)

  def reset(self):
    Obstacle.reset(self)
    self.spd = 5

  def move(self, direction=None):
    if direction=="left":
      direction = -1
    elif direction=="right":
      direction = 1
    else: assert(0)
    self.rect.move_ip(direction*self.spd, 0)
    self.rect = self.rect.clamp(PADDLE_AREA_RECT)

class Ball(Bounceable):
  def __init__(self):
    Bounceable.__init__(self,BALL_INIT_RECT,DEFAULT_INIT_BALL_SPD,(1,-1))

  def update(self,ps):
    if ps["inplay"]: self.rect.move_ip(self._poschg())
    else: 
      self.rect.clamp_ip(ps["prect"])
      self.rect.move_ip((0,-self.rect.size[1]-1))
    if not FIELD_RECT.contains(self.rect):
      ps["lives"].decrement()

class Message(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.font = pygame.font.Font(None, 50)
    self.font.set_italic(1)
    self.color = Color('white')
    self.chgmsg("Press Space!")

  def reset(self):
    self.chgmsg("Press Space!")

  def chgmsg(self,msg):
    self.image = self.font.render(msg, 0, self.color)
    self.rect = self.image.get_rect().move((FIELD_RECT.size[0]/2-200,FIELD_RECT.size[1]/2))

class Lives(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.font = pygame.font.Font(None, 20)
    self.font.set_italic(1)
    self.color = Color('white')
    self.reset()

  def reset(self):
    self.livesleft = DEFAULT_INIT_LIVES
    self.decreased = False
    self.increased = False
    self.image = self.font.render("Lives: "+str(self.livesleft), 0, self.color)
    self.rect = self.image.get_rect().move(45, 40)

  def decrement(self):
    self.livesleft-=1
    self.decreased = True

  def increment(self):
    self.livesleft+=1
    self.increased = True

  def update(self):
    self.image = self.font.render("Lives: "+str(self.livesleft), 0, self.color)
import pdb
class PowerupList(pygame.sprite.Sprite):
  paddle = None
  ball = None
  def __init__(self,paddle=None,ball=None):
    pygame.sprite.Sprite.__init__(self)
    self.font = pygame.font.Font(None, 30)
    self.font.set_italic(1)
    self.color = Color('white')
    PowerupList.paddle = paddle
    PowerupList.ball = ball
    self.reset()

  def __len__(self):
    return len(self.powerups)

  def getstr(self):
    return "Powerups:\n"+('\n'.join(self.desc_list))

  def reset(self):
    self.powerups = []
    self.desc_list = []
    PowerupList.paddle.reset()
    PowerupList.ball.reset()
    ptext.draw("Power ups:\nNone",POWERUP_LIST_RECT)

  def add(self,powerup):
    p=powerup
    d=powerup.get_description()
    if d.startswith("Paddle"):
      PowerupList.paddle.spd *= p.ratio
    elif d.startswith("Ball Speed"):
      PowerupList.ball.spd *= p.ratio
    self.powerups.append(p)
    self.desc_list.append(d)

  def pop(self):
    p=self.powerups.pop()
    d=self.desc_list.pop()
    if d.startswith("Paddle"):
      PowerupList.paddle.spd /= p.ratio
    elif d.startswith("Ball Speed"):
      PowerupList.ball.spd /= p.ratio
    
  def update(self):
    ptext.draw(self.getstr(),POWERUP_LIST_RECT)

class Powerup(Obstacle):
  def __init__(self,rect,color,initdir,initspd,poweruplist,sound):
    Obstacle.__init__(self,rect,color,sound)
    self.poweruplist = poweruplist
    self.dir = initdir
    self.spd = initspd

  def get_description(self):
    pass

  def collided(self):
    Obstacle.collided(self)
    self.poweruplist.add(self)
    self.kill()
    return True

  def update(self,ps):
    if Obstacle.update(self,ps): return True # ball collision
    if not FIELD_RECT.contains(self.rect):
      self.kill()
      return False
    if self.rect.colliderect(ps["prect"]): # paddle collision
      return self.collided()
    self.rect.move_ip((self.dir[0]*self.spd,self.dir[1]*self.spd))
    return False

class PaddleSpeed(Powerup):
  def __init__(self,rect,plist,sound,num):
    Powerup.__init__(self,rect,PADDLE_SPD_UP_COLOR,(0,1),5,plist,sound)
    self.ratio = num

  def get_description(self):
    return "Paddle Speed times "+str(self.ratio)

class BallSpeed(Powerup):
  def __init__(self,rect,plist,sound,num):
    Powerup.__init__(self,rect,BALL_SLOW_COLOR,(0,1),5,plist,sound)
    self.ratio = num

  def get_description(self):
    return "Ball Speed times "+str(self.ratio)