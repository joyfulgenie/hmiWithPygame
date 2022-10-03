import pygame
import time

from hangul_utils import join_jamos

# 자음-초성/종성
cons = {'r':'ㄱ', 'R':'ㄲ', 's':'ㄴ', 'e':'ㄷ', 'E':'ㄸ', 'f':'ㄹ', 'a':'ㅁ', 'q':'ㅂ', 'Q':'ㅃ', 't':'ㅅ', 'T':'ㅆ',
           'd':'ㅇ', 'w':'ㅈ', 'W':'ㅉ', 'c':'ㅊ', 'z':'ㅋ', 'x':'ㅌ', 'v':'ㅍ', 'g':'ㅎ'}
# 모음-중성
vowels = {'k':'ㅏ', 'o':'ㅐ', 'i':'ㅑ', 'O':'ㅒ', 'j':'ㅓ', 'p':'ㅔ', 'u':'ㅕ', 'P':'ㅖ', 'h':'ㅗ', 'hk':'ㅘ', 'ho':'ㅙ', 'hl':'ㅚ',
           'y':'ㅛ', 'n':'ㅜ', 'nj':'ㅝ', 'np':'ㅞ', 'nl':'ㅟ', 'b':'ㅠ',  'm':'ㅡ', 'ml':'ㅢ', 'l':'ㅣ'}

# 자음-종성
cons_double = {'rt':'ㄳ', 'sw':'ㄵ', 'sg':'ㄶ', 'fr':'ㄺ', 'fa':'ㄻ', 'fq':'ㄼ', 'ft':'ㄽ', 'fx':'ㄾ', 'fv':'ㄿ', 'fg':'ㅀ', 'qt':'ㅄ'}

def engkor(text):
    result = ''  # 영 > 한 변환 결과

    # 1. 해당 글자가 자음인지 모음인지 확인
    vc = ''
    for t in text:
        if t in cons:
            vc += 'c'
        elif t in vowels:
            vc += 'v'
        else:
            vc += '!'

    # cvv → fVV / cv → fv / cc → dd
    vc = vc.replace('cvv', 'fVV').replace('cv', 'fv').replace('cc', 'dd')

    # 2. 자음 / 모음 / 두글자 자음 에서 검색
    i = 0
    while i < len(text):
        v = vc[i]
        t = text[i]

        j = 1
        # 한글일 경우
        try:
            if v == 'f' or v == 'c':  # 초성(f) & 자음(c) = 자음
                result += cons[t]

            elif v == 'V':  # 더블 모음
                result += vowels[text[i:i + 2]]
                j += 1

            elif v == 'v':  # 모음
                result += vowels[t]

            elif v == 'd':  # 더블 자음
                result += cons_double[text[i:i + 2]]
                j += 1
            else:
                result += t

        # 한글이 아닐 경우
        except:
            if v in cons:
                result += cons[t]
            elif v in vowels:
                result += vowels[t]
            else:
                result += t

        i += j

    return join_jamos(result)


SIZE = width,height = 640,240

screen = pygame.display.set_mode(SIZE)
screen.fill('blue')
pygame.init()

# Text Editing
text1 = '' #영문 유니코드 텍스트
font1 = pygame.font.Font('a전자시계.ttf',16)
img1 = font1.render(text1,True,'white')
hanText = ''
hanMode = False

rect1 = img1.get_rect()
rect1.topleft = (40,50)
cursor1 = pygame.Rect(rect1.topright,(3,rect1.height))

pygame.key.set_repeat(500, 50)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN: #키다운 이벤트라면, key, mod, ucicode, scancode 속성을 가진다.
            if event.key == pygame.K_BACKSPACE:
                if hanMode and len(hanText) > 0: hanText = hanText[:-1]
                elif len(text1) > 0:
                    text1 = text1[:-1]

            elif event.mod & pygame.KMOD_LSHIFT and event.key == pygame.K_SPACE:    #한영 변환 인식 Left Shift + space
                if hanMode: #영문모드로 토글
                    text1 += engkor(hanText)
                    cursor1 = pygame.Rect(rect1.topright, (3, rect1.height))
                    hanMode = False
                else:   #한글모드로 토클
                    cursor1 = pygame.Rect(rect1.topright, (16, rect1.height))
                    hanMode = True
                hanText = ''
            else:
                if hanMode:
                    hanText += event.unicode
                else: text1 += event.unicode
            text2 = text1 + engkor(hanText)
            img1 = font1.render(text2,True,'white')
            rect1.size = img1.get_size()
            if rect1.width > 600: rect1.topright = (600,50)
            else : rect1.topleft = (40,50)
            cursor1.topleft = rect1.topright

    screen.fill('blue')
    screen.blit(img1,rect1)
    if time.time() % 1 > 0.5:
        pygame.draw.rect(screen, 'red', cursor1)
    pygame.display.update()

pygame.quit()