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


class Brick(pygame.sprite.Sprite):
  """Logic for a brick"""
  def __init__(self,rect,color):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(rect.size)
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.rect.topleft = rect.topleft
    self.broken = False

  def destroy(self):
    self.broken = True
    self.image.set_alpha(0)

class Wall(pygame.sprite.Sprite):
  def __init__(self,rect):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(rect.size)
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.rect.topleft = rect.topleft

  def chgcolorto(self,color):
    self.image.fill(color)

class Paddle(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(PADDLE_INIT_RECT.size)
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.rect.topleft = PADDLE_INIT_RECT.topleft
    self.spd = 5

  def move(self, direction=None):
    if direction=="left":
      direction = -1
    elif direction=="right":
      direction = 1
    else: assert(0)
    self.rect.move_ip(direction*self.spd, 0)
    self.rect = self.rect.clamp(SCREEN_RECT)

class Ball(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.Surface(BALL_INIT_RECT.size)
    self.image.fill((255,255,255))
    self.rect = self.image.get_rect()
    self.rect.topleft = BALL_INIT_RECT.topleft

    self.spd = 4 #pixels per frame
    self.dir = (1,1) #+x and +y

  def _nextpos(self):
    return (self.spd*self.dir[0], self.spd*self.dir[1])

  def bounce(self,nextdir=None):
    if nextdir=="up":
      self.dir=(self.dir[0],-1)
    elif nextdir=="down":
      self.dir=(self.dir[0],1)
    elif nextdir=="left":
      self.dir=(-1,self.dir[0])
    elif nextdir=="right":
      self.dir=(1,self.dir[0])
    else: assert(False)
    
  def update(self):
    newpos = self.rect.move(self._nextpos())

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

    allsprites.update()

    #Draw Everything
    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pygame.display.flip()

    pygame.event.pump()

  pygame.quit()

if __name__ == '__main__':
  main()
