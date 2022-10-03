import pygame


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

def test(arg):
    print(f'테스트용 함수 입니다. = {arg}')

def close():
    pygame.quit()
    quit()
    exit()

#mouseUpEvent:pygame.event = None
#mouseDownEvent:pygame.event = None
#mouseMotionEvent:pygame.event = None
def main():
    global mouseUpEvent
    global mouseDownEvent
    global mouseMotionEvent

    pygame.init()
    screen = pygame.display.set_mode((800,600))
    clock = pygame.time.Clock()

    # main menu
    mainManu = MenuBox(MenuBox.HORIZONTAL)
    name = ['파 일', '편 집', '열 기', '도움말', '끝내기']
    for text in name:
        mainManu.menuItemList.append(MenuItem(text))
    for item in mainManu.menuItemList:
        subMenu = MenuBox(MenuBox.VERTICAL)
        for i in range(4):
            subMenu.menuItemList.append(MenuItem(f'{item.name} submenu {i}'))
        item.setLink(subMenu)

    running = True
    mainManu.menuItemList[4].setLink(close)

    while running:
        mouseUpEvent = None
        mouseDownEvent = None
        mouseMotionEvent = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION: mouseMotionEvent = event
            elif event.type == pygame.MOUSEBUTTONUP: mouseUpEvent = event
            elif event.type == pygame.MOUSEBUTTONDOWN: mouseDownEvent = event


        screen.fill('Black')

        mainManu.update(screen)
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
