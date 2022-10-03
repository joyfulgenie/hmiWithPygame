import pygame
from PIL import Image, ImageOps, ImageFilter
import math, random, time


class SinSignal:
    # 0 ~ 65535값의 sin값을 발생 32767, 16383
    # ssignal = SinSignal('Test')
    # for i in ssignal:
    #     print(i)
    #     time.sleep(0.1)

    def __init__(self, name):
        self.name = name
        self.data = 0
        self.Offset = 32767
        self.Magnitude = [random.randrange(5000,15000), random.randrange(500,1000), random.randrange(50,380)]
        self.Duration = [random.randrange(500, 3000), random.randrange(10, 100), random.randrange(3, 8)] #msec
        self.Theta = [2 * 3.14 * random.random(), 2 * 3.14 * random.random(), 2 * 3.14 * random.random()] #초기 라디안
        self.now = time.time()

    def __iter__(self):
        return self

    def __next__(self):
        ptime = self.now
        self.now = time.time()
        deltaT = self.now - ptime
        data = 0
        for i in range(3):
            self.Theta[i] += 2 * math.pi * deltaT / self.Duration[i]
            if self.Theta[i] > 200 * math.pi: self.Theta[i] -= 200 * math.pi  # Theta를 순환하기 위해
            data += self.Magnitude[i] * math.sin(self.Theta[i])
            self.data =  int(data)
        self.data += self.Offset
        return self.data

class LevelBar(pygame.sprite.Sprite):
    def __init__(self):
        super(LevelBar, self).__init__()
        self.setData(50, 0, 100)
        self.setBar('Virtical', 10, 100, '#ff000088')

    def setData(self, data, dLow, dHigh):
        # data setting
        self.data = data
        self.dHigh = dHigh
        self.dLow  = dLow
        self.dThird = 0.75 * (self.dHigh - self.dLow)
        self.dMid = 0.5 * (self.dHigh - self.dLow)
        self.dFirst = 0.25 * (self.dHigh - self.dLow)

    def setBar(self,direction, width, height, color):
        #bar
        self.bDirection = direction # 'Virtical, Horizontal'
        self.bWidth = width
        self.bHeight = height
        self.indicatorColor = color#'#ff000088'
        if self.bDirection == 'Virtical': self.factor = self.bHeight/(self.dHigh - self.dLow)
        else : self.factor = self.bWidth/(self.dHigh - self.dLow)

        self.image = pygame.surface.Surface((self.bWidth, self.bHeight), pygame.SRCALPHA) #픽셀별 알파
        self.image.fill('#eeeeee44')
        self.baseImage = self.image.copy()
        self.rect = self.baseImage.get_rect()
        #위치시키기
        #self.rect.center = pygame.display.get_surface().get_rect().center

    def update(self) -> None:
        indicator = self.data * self.factor
        if self.bDirection == 'Virtical':
            #print((self.data, self.factor))
            bar = pygame.surface.Surface((self.bWidth, indicator), pygame.SRCALPHA) #픽셀별 알파
            rect = bar.get_rect()
            rect.bottom =self.bHeight
        else:
            bar = pygame.surface.Surface((indicator, self.bHeight), pygame.SRCALPHA)  # 픽셀별 알파
            rect = bar.get_rect()
            rect.left = 0
        bar.fill(self.indicatorColor)
        self.image = self.baseImage.copy()
        self.image.blit(bar, rect)
        if self.data >= self.dHigh : self.data = self.dLow
        self.data += 0.1

class LevelArc(pygame.sprite.Sprite):
    def __init__(self):
        super(LevelArc, self).__init__()
        self.setData(50, 0, 100)
        self.draw('Virtical', 100, '#ff000088')

    def setData(self, data, dLow, dHigh):
        # data setting
        self.data = data
        self.dHigh = dHigh
        self.dLow  = dLow
        self.dThird = 0.75 * (self.dHigh - self.dLow)
        self.dMid = 0.5 * (self.dHigh - self.dLow)
        self.dFirst = 0.25 * (self.dHigh - self.dLow)
        self.factor = 3.1416 / (self.dHigh - self.dLow)

    def draw(self, direction, radius, color):
        #bar
        self.direction = direction # 'Virtical, Horizontal'
        self.radius = radius
        self.width = int(self.radius/2)
        self.indicatorColor = color#'#ff000088'
        self.image = pygame.surface.Surface((2*self.radius, 2*self.radius), pygame.SRCALPHA) #픽셀별 알파
        pygame.draw.arc(self.image, '#eeeeee44', self.image.get_rect(), 0, math.pi, self.width)
        self.baseImage = self.image.copy()
        self.rect = self.baseImage.get_rect()
        #위치시키기
        #self.rect.center = pygame.display.get_surface().get_rect().center

    def update(self) -> None:
        indicator = self.data * self.factor
        #print(indicator)
        self.image = self.baseImage.copy()
        pygame.draw.arc(self.image, self.indicatorColor, self.image.get_rect(), math.pi - indicator, math.pi - 0, self.width)
        if self.data >= self.dHigh : self.data = self.dLow
        self.data += 0.1

class DigitalLabel(pygame.sprite.Sprite):
    def __init__(self, letter, size, color, blurValue):
        super(DigitalLabel, self).__init__()
        font = pygame.font.Font('font//a전자시계.ttf', size)
        self.image = font.render(letter, False, color, 'black')
        self.blured = self.__BlurImage__(self.image, blurValue)
        self.rect = self.image.get_rect()
        self.bluredRect = self.blured.get_rect()
        self.bluredRect.center = self.rect.center
        self.image.set_colorkey('black')

    def print(self, screen, align, position, glow):
        if align == 'left' : self.rect.midleft = position
        elif align == 'right' : self.rect.midright = position
        else : self.rect.center = position
        self.bluredRect.center = self.rect.center
        screen.blit(self.image, self.rect, special_flags=pygame.BLEND_RGBA_ADD)
        if glow : screen.blit(self.blured, self.bluredRect, special_flags=pygame.BLEND_RGBA_ADD)

    def __BlurImage__(self, image, value):
        imageString = pygame.image.tostring(image, 'RGBA', False)
        pilImage = Image.frombytes('RGBA', image.get_size(), imageString)
        theImage = ImageOps.expand(pilImage,3*value,0)
        blurI = theImage.filter(ImageFilter.GaussianBlur(value))
        raw_str = blurI.tobytes("raw", 'RGBA')
        surf = pygame.image.fromstring(raw_str, blurI.size, 'RGBA')
        return surf

class Frame(pygame.sprite.Sprite):
    def __init__(self, size, color):
        super(Frame, self).__init__()
        self.image = pygame.surface.Surface(size, pygame.SRCALPHA) #픽셀별 알파
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def update(self, screen:pygame.surface.Surface):
        screen.blit(self.image, self.rect)#, special_flags=pygame.BLEND_RGBA_MULT)

class ArcGage(pygame.sprite.Sprite):
    def __init__(self):
        super(ArcGage, self).__init__()
        self.image = pygame.surface.Surface((100,100), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self, angle) -> None:
        # 계기판 디자인
        pygame.draw.circle(self.image, '#ab3456aa', (50,50), 50, draw_top_left=True)
        pygame.draw.circle(self.image, '#3456abaa', (50,50), 50, draw_top_right=True)
        niddle = pygame.surface.Surface((4, 90), pygame.SRCALPHA)
        niddle.fill('#abcd34')
        niddle = pygame.transform.rotozoom(niddle, angle, 1)
        niddle_rec = niddle.get_rect()
        niddle_rec.center = (50,50)
        self.image.blit(niddle, niddle_rec)


    