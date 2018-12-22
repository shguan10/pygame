import os, pygame
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

from constants import *

#functions to create our resources
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

  def collided(self):
    pass

  def update(self,ball):
    bnextpos = ball.nextpos()
    ball_col,ball_row = bnextpos.topleft
    bw,bh = bnextpos.size
    lcol, trow = self.rect.topleft
    w,h = self.rect.size
    rcol = lcol+w
    bot_row = trow+h
    ball_interior_col = lcol<= ball_col <= rcol
    ball_interior_row = trow<= ball_row <= bot_row
    if ball_interior_row and (rcol-1<=ball_col <=rcol+1):
      ball.bounce("right")
      self.collided()
    
    if ball_interior_row and (lcol-1<=ball_col+bw <=lcol+1):
      ball.bounce("left")
      self.collided()
    
    if ball_interior_col and (trow-2<=ball_row+bh <=trow+2):
      ball.bounce("up")
      self.collided()
    
    if ball_interior_col and (bot_row-2<=ball_row <=bot_row+2):
      ball.bounce("down")
      self.collided()

class Brick(Obstacle):
  def __init__(self,rect,color):
    Obstacle.__init__(self,rect,color)

  def collided(self):
    self.kill()

class Wall(Obstacle):
  def __init__(self,rect):
    Obstacle.__init__(self,rect,(255,255,255))

  def chgcolorto(self,color):
    self.image.fill(color)

class Paddle(Obstacle):
  def __init__(self):
    Obstacle.__init__(self,PADDLE_INIT_RECT,(255,255,255))
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
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.rect.topleft = BALL_INIT_RECT.topleft

    self.spd = 2 #pixels per frame
    self.dir = (1,1) #+x and +y

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
    
  def update(self,ball):
    self.rect.move_ip(self._poschg())

class Score(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.font = pygame.font.Font(None, 20)
    self.font.set_italic(1)
    self.color = Color('white')
    self.lastscore = -1
    self.update()
    self.rect = self.image.get_rect().move(10, 450)

  def update(self):
    if SCORE != self.lastscore:
      self.lastscore = SCORE
      msg = "Score: %d" % SCORE
      self.image = self.font.render(msg, 0, self.color)

def main():
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
  allsprites = bricks
  allsprites.extend([topwall,leftwall,rightwall,ball,paddle])
  allsprites = pygame.sprite.Group(allsprites)

  while True:
    clock.tick(60)

    currpressed = pygame.key.get_pressed()

    if currpressed[K_ESCAPE]:
      break
    elif currpressed[K_LEFT]:
      paddle.move("left")
    elif currpressed[K_RIGHT]:
      paddle.move("right")

    allsprites.update(ball)

    #Draw Everything
    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pygame.display.flip()

    pygame.event.pump()

  pygame.quit()

if __name__ == '__main__':
  main()
