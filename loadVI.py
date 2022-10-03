# coding = utf-8
import timeit
import time, math

import pygame
import threading, queue

from hmiUtilities import *


class MenuItem(pygame.sprite.Sprite):
    '''
    클릭하면 해당 함수를 실행하는 링크
    '''
    font:pygame.font.Font = None

    def __init__(self, name:str, font:pygame.font.Font = None):
        super(MenuItem, self).__init__()
        self.name = name
        if font:
            MenuItem.font = font
        elif not font : MenuItem.font = pygame.font.Font('font//a전자시계.ttf', 20)
        self.color = '#bbbbbb'
        self.image = self.font.render(name, True, self.color)
        self.rect = self.image.get_rect()
        self.link = None
        self.visuable = False   # 서브메뉴 보이기

    def setLink(self, link, args:tuple=(), kwargs:dict={}):
        '''
        :param link: 메뉴 클릭시 실행할 함수. 만일 서브메뉴라면 MenuBox 객체로 전달
        :param args: link가 함수일 경우 전달할 파라미터
        :param kwargs: link가 함수일 경우 전달할 파라미터
        :return: 없음.
        '''
        self.link = link
        self.linkArgs = args
        self.linkKwargs = kwargs

    def update(self, screen:pygame.surface.Surface) -> None:
        # 마우스가 닿으면
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            # 사각형을 그리고
            pygame.draw.rect(screen, '#ddbbbb', self.rect, 1)
            # 서브메뉴라면 서브메뉴를 뜨우고
            if isinstance(self.link, MenuBox):
                self.link.rect.topleft = self.rect.bottomright
                self.link.update(screen)
            # 마우스 클릭되면
            if mouseUpEvent:
                # 서브메뉴이면 비져블 토글
                if isinstance(self.link, MenuBox):
                    self.visuable = not self.visuable
                # 실행링크가 걸려 있으면 링크 실행
                else:
                    try:
                        self.link(*self.linkArgs, **self.linkKwargs)
                    except:pass
        # 마우스가 닿지 않고
        elif mouseUpEvent:
            self.visuable=False
        screen.blit(self.image, self.rect)

class MenuBox(pygame.sprite.Sprite):
    '''
    MenuBox(type, menuList): type=가로/세로, munuList=menuItem list
    '''
    VERTICAL = 0
    HORIZONTAL = 1
    def __init__(self, type=None):
        super(MenuBox, self).__init__()
        self.type = MenuBox.VERTICAL if not type else type
        self.menuItemList = []
        self.rect = pygame.rect.Rect(0,0,0,0)

    def update(self, screen) -> None:
        x = self.rect.x
        y = self.rect.y
        for item in self.menuItemList:
            item.rect.topleft = (x, y)
            item.update(screen)
            if isinstance(item.link, MenuBox) and item.visuable:
                item.link.update(screen)
            if self.type == MenuBox.VERTICAL:
                y += 30
            else:
                x += 30 + item.rect.width

class LoadVI():
    def __init__(self, R, X):
        # 전압,전류, 평균전력, 피상전력, 무효전력, 역률, 스위치
        self.Vm =220*math.sqrt(2)    #약 311V
        self.omega = 2*math.pi*60    #약 377
        #R = 3   #저항
        #X = 2   #리액턴스
        self.Z = math.sqrt(R*R + X*X)    #임피던스크기
        PF = R/self.Z    #역률 cos(theta)
        self.direct = X/abs(X)   #역률의 방향, 양수이면 진연 용량성, 음수이면 지연 유도성
        self.theta = math.acos(PF)
        self.switch = True
        #print(PF)

    def __iter__(self):
        return self

    def __next__(self):
        time.sleep(0.0000001)
        now = time.perf_counter()
        vout = self.Vm * math.sin(self.omega*now)
        if self.direct > 0: iout = (self.Vm/self.Z) * math.sin(self.omega*now - self.theta) #용량성
        else: iout = (self.Vm/self.Z) * math.sin(self.omega*now + self.theta)   #유도성
        if not self.switch: iout = 0.000001 #차단전류
        return vout, iout

class LoadMonitor(Frame):
    def __init__(self, title, load, nos): #nos : number of sensing
        # frame 설정
        super(LoadMonitor, self).__init__((250,170), '#78a9deaa')
        #
        #self.rect.topleft = (400,300)
        self.title = DigitalLabel(title, 20,'#cd12de', 10)
        self.load = load
        self.nos = nos
        self.dataTitles = []
        self.dTitles = ['전압', '전류', '피상전력', '평균전력', '역률', '방향']
        for n in range(6):
            self.dataTitles.append(DigitalLabel(self.dTitles[n], 14,'#cdde12', 10))
        self.q = queue.SimpleQueue()
        self.data = []
        threading.Thread(target=self.runSensor, daemon=True).start()

    def runSensor(self):
        while True:
            data = calPower(self.load, self.nos)
            self.q.put(data)


    def update(self, screen: pygame.surface.Surface):
        #rmsV, rmsI, apPower, avPower, powerFactor, direction = calPower(self.load,10)
        #data = [rmsV, rmsI, apPower, avPower, powerFactor, direction]
        while True:
            try:
                self.data = self.q.get_nowait()
            except:
                break

        screen.blit(self.image, self.rect)
        self.title.print(screen,'left', (self.rect.x+10, self.rect.y+15), True)
        PFGage = ArcGage()
        try:
            degree = 180 * self.data[5] * math.acos(self.data[4]) / math.pi
        except: degree = 0
        PFGage.update(degree)
        screen.blit(PFGage.image, (self.rect.x+10, self.rect.y+50))
        for n in range(len(self.data)):
            self.dataTitles[n].print(screen, 'right', (self.rect.x + 150, self.rect.y + 45 + (n* 20)), False)
            dataImage= DigitalLabel(f'{self.data[n]:.2f}', 14, '#cddeac', 10)
            dataImage.print(screen, 'left', (self.rect.x + 160, self.rect.y + 45 + (n* 20)), False)

def calPower(load:LoadVI, snum:int):
    # snum : 샘플링 갯수
    vList = []
    iList = []
    powerList = []
    startT = time.perf_counter()
    direction = 0
    for n in range(snum):
        vout, iout = next(load)
        vList.append(vout)
        iList.append(iout)
        powerList.append(vout * iout)
    endT = time.perf_counter()
    duration = (endT - startT)
    dt = duration / snum
    avPower = 0
    rmsV = 0
    rmsI = 0
    for n in range(snum):
        #print(vList[n], iList[n])
        if n>0:
            if vList[n] > 0 and vList[n-1]<0:
                if iList[n] < 0 : direction = -1    #'유도성'
                elif iList[n-1] > 0 : direction = 1 #'용량성'
                #print(direction)
        rmsV += vList[n] * vList[n] * dt
        rmsI += iList[n] * iList[n] * dt
        avPower += powerList[n] * dt
    rmsV = math.sqrt(rmsV / duration)
    rmsI = math.sqrt(rmsI / duration)
    avPower = avPower / duration
    apPower = rmsV * rmsI
    powerFactor = avPower / apPower

    return rmsV, rmsI, apPower, avPower, powerFactor, direction

def main():
    global mouseUpEvent
    global mouseDownEvent
    global mouseMotionEvent
    pygame.init()

    screen = pygame.display.set_mode(display=1)
    rect = screen.get_rect()
    clock = pygame.time.Clock()
    #배경이미지
    backgroundImage = pygame.image.load('image//풍력발전소풍경.jpg')
    backgroundImage_rect = backgroundImage.get_rect()
    backgroundImage_rect.center = rect.center

    #타이틀
    htitle = DigitalLabel('분산 부하 모니터링 및 최적화 제어 시스템', 50, '#12cdde', 20)
    etitle = DigitalLabel('DL-MOCS:Distributed Load Monitoring and Optimazation Control System', 30, '#cdde12', 20)

    #
    arcGroup = pygame.sprite.Group(LevelArc())

    # main menu
    mainManu = MenuBox(MenuBox.VERTICAL)
    name = ['실시간 모니터링', '정밀관찰', '분석도구', '현황판', '관리도구']
    mainManu.rect.topleft = (10, 120)
    for text in name:
        mainManu.menuItemList.append(MenuItem(text))
    for item in mainManu.menuItemList:
        subMenu = MenuBox(MenuBox.VERTICAL)
        for i in range(4):
            subMenu.menuItemList.append(MenuItem(f'{item.name} submenu {i}'))
        item.setLink(subMenu)

    # 부하모니터링
    lNum = 20
    lMon = []
    for n in range(lNum):
        r = 10*random.random()
        x = 20*random.random() - 10.0
        title = f'{r:2.2f} + j{x:2.2f}'
        lMon.append(LoadMonitor(title, LoadVI(r,x),60))

    running = True
    while running:
        keyEvent = None
        mouseUpEvent = None
        mouseDownEvent= None
        mouseMotionEvent= None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                keyEvent = event
                if event.mod & pygame.KMOD_LSHIFT and event.key == pygame.K_ESCAPE: # Left-shift + esc    프로그램 끝내기
                    running = False
                    break
            elif event.type == pygame.MOUSEMOTION:
                mouseMotionEvent = event
            elif event.type == pygame.MOUSEBUTTONUP:
                mouseUpEvent = event
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseDownEvent = event

        arcGroup.update()
        #ltsGroup.update()
        #screen.fill('#122334')
        screen.blit(backgroundImage,backgroundImage_rect)
        arcGroup.draw(screen)
        #타이틀 출력
        htitle.print(screen,'center',(rect.width/2, rect.top + 30), True)
        etitle.print(screen,'center',(rect.width/2, rect.top + 100), True)
        for n in range(lNum):
            row = n // 5
            col = n % 5
            lMon[n].rect.topleft = (500 + 270*col, 200 + 200*row)
            lMon[n].update(screen)
        mainManu.update(screen)
        pygame.display.update()
        #clock.tick(60)
    pygame.quit()
if __name__ == '__main__':
    main()