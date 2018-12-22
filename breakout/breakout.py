import os, pygame
from pygame.locals import *

from constants import *
from utility import *
from sprites import *

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
  bricks = [Brick(brect,(255,0,0) if i%2 else (0,0,255)) for i,brect in enumerate(BRICKS_RECTS)]
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