import os, pygame
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

from constants import *

def load_image(name, colorkey=None):
  fullname = os.path.join(data_dir, name)
  try:
    image = pygame.image.load(fullname)
  except pygame.error:
    print('Cannot load image:', fullname)
    raise SystemExit(str(geterror()))
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()

def load_sound(name):
  class NoneSound:
    def play(self): pass
  if not pygame.mixer or not pygame.mixer.get_init():
    return NoneSound()
  fullname = os.path.join(data_dir, name)
  try:
    sound = pygame.mixer.Sound(fullname)
  except pygame.error:
    print ('Cannot load sound: %s' % fullname)
    raise SystemExit(str(geterror()))
  return sound

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
    if not SCREEN_RECT.contains(self.rect):
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
    self.rect = self.image.get_rect().move((SCREEN_RECT.size[0]/2-200,SCREEN_RECT.size[1]/2))

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
      

def main():
  pygame.mixer.pre_init(44100, -16, 2, 512)
  pygame.mixer.init()
  pygame.init()

  screen = pygame.display.set_mode(SCREEN_RECT.size)
  pygame.display.set_caption('Breakout')
  pygame.mouse.set_visible(0)

  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill((0,0,0))

  screen.blit(background, (0, 0))
  pygame.display.flip()

  clock = pygame.time.Clock()
  topwall = Wall(TOPWALL_RECT)
  leftwall = Wall(LEFTWALL_RECT)
  rightwall = Wall(RIGHTWALL_RECT)
  ball = Ball()
  paddle = Paddle()
  bricks = [Brick(brect,(255,0,255)) for brect in BRICKS_RECTS]
  lives = Lives()
  msg = Message()
  BricksGroup = pygame.sprite.Group(bricks)
  BallsGroup = pygame.sprite.Group(ball)
  TextsGroup = pygame.sprite.Group([lives,msg])
  Others = pygame.sprite.Group([topwall,leftwall,rightwall,paddle])

  collide_sound = load_sound("boop.wav")
  error_sound = load_sound("error.wav")
  sad_sound = load_sound("sad.wav")
  win_sound = load_sound("win.wav")

  state="wait"
  inplay=False
  lost = False
  won = False

  prevserve = False

  while True:
    clock.tick(60)

    currpressed = pygame.key.get_pressed()

    if currpressed[K_ESCAPE]: break
    elif currpressed[K_LEFT]:  paddle.move("left")
    elif currpressed[K_RIGHT]: paddle.move("right")

    if state=="wait" and currpressed[K_SPACE] and not prevserve:
      inplay=True
      prevserve = False
      state="inplay"
      for b in BallsGroup: b.resetspd()
      msg.chgmsg("Good luck")
    elif state=="inplay" and lives.decreased:
      inplay=False
      error_sound.play()
      state="wait" if lives.livesleft else "lost"
      lost = lives.livesleft == 0
      lives.decreased = False
      msg.chgmsg(":(")
    elif state=="inplay" and not BricksGroup:
      inplay = False
      state="won"
      won=True
    elif state=="lost":
      sad_sound.play()
      state="newgame"
      msg.chgmsg(">:(")
    elif state=="won":
      win_sound.play()
      state="newgame"
      msg.chgmsg("A Winner is You!")
    elif state=="newgame"and currpressed[K_SPACE]:
      inplay=False
      state="wait"
      lost,won=False,False
      BricksGroup.add(bricks)
      for s in Others: s.reset()
      for x in TextsGroup: x.reset()

    prevserve = currpressed[K_SPACE]

    updateargs = {"ball":ball,
                  "collide_sound":collide_sound,
                  "lives":lives,
                  "inplay":inplay,
                  "lost":lost,
                  "won":won}
    
    BricksGroup.update(updateargs)
    Others.update(updateargs)
    TextsGroup.update()
    BallsGroup.update({"inplay":inplay,"lives":lives,"prect":paddle.rect})

    #Draw Everything
    screen.blit(background, (0, 0))
    BricksGroup.draw(screen)
    BallsGroup.draw(screen)
    TextsGroup.draw(screen)
    Others.draw(screen)
    pygame.display.flip()

    pygame.event.pump()

  pygame.quit()

if __name__ == '__main__':
  main()
