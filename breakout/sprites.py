import os, pygame
from pygame.locals import *
from constants import *

class Obstacle(pygame.sprite.Sprite):
  def __init__(self,rect,color):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(rect.size)
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.topleft = rect.topleft
    self.reset()
    
  def reset(self):
    pass

  def collided(self,collide_sound):
    collide_sound.play()

  def update(self,ps):
    ball = ps["ball"]
    collide_sound = ps["collide_sound"]
    bnextpos = ball.nextpos()
    ball_col,ball_row = bnextpos.topleft
    bw,bh = bnextpos.size
    lcol, trow = self.rect.topleft
    w,h = self.rect.size
    rcol = lcol+w
    bot_row = trow+h
    ball_interior_col = lcol<= ball_col <= rcol
    ball_interior_row = trow<= ball_row <= bot_row
    if not ps["inplay"]: return
    if ball_interior_row and (rcol-ball.spd<=ball_col <=rcol+1):
      ball.bounce("right")
      self.collided(collide_sound)
    
    if ball_interior_row and (lcol-1<=ball_col+bw <=lcol+ball.spd):
      ball.bounce("left")
      self.collided(collide_sound)
    
    if ball_interior_col and (trow-2*ball.spd<=ball_row+bh <=trow+2):
      ball.bounce("up")
      self.collided(collide_sound)
    
    if ball_interior_col and (bot_row-2<=ball_row <=bot_row+ball.spd):
      ball.bounce("down")
      self.collided(collide_sound)

class Brick(Obstacle):
  def __init__(self,rect,color):
    Obstacle.__init__(self,rect,color)

  def collided(self,collide_sound):
    collide_sound.play()
    self.kill()

class Wall(Obstacle):
  def __init__(self,rect):
    Obstacle.__init__(self,rect,(255,255,255))

  def chgcolorto(self,color):
    self.image.fill(color)

class Paddle(Obstacle):
  def __init__(self):
    Obstacle.__init__(self,PADDLE_INIT_RECT,(255,255,255))

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

class Ball(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(BALL_INIT_RECT.size)
    self.reset()

  def reset(self):
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.resetspd()

  def resetspd(self):
    self.spd = DEFAULT_INIT_BALL_SPD #pixels per frame
    self.dir = (1,-1) #+x and +y

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
