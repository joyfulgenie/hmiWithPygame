## 임포트

```buildoutcfg
import pygame
from hangul_utils import join_jamos

SIZE = width, height = 640, 240
screen = pygame.display.set_mode(SIZE)
screen.fill('blue')
pygame.init()
box = HangulInputBox('a전자시계.ttf', 16, 20,'white', 'blue')
box.rect.center = (640/2, 240/2)
running=True
while running:
    keyEvent = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            keyEvent = event
        if event.type == pygame.USEREVENT:
            if event.name == 'enterEvent': print(event.text)
    screen.fill('black')
    box.update(keyEvent)
    screen.blit(box.image, box.rect)
    pygame.display.update()

pygame.quit()
```