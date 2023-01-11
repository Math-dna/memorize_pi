import re
import pygame

from ntpath import isfile
from os import getlogin

from datetime import datetime
from pymsgbox import prompt, alert

import requests
from bs4 import BeautifulSoup


class Button:
    OBJ = ()

    def __init__(
        self,
        position, # 버튼의 좌표
        size, # 버튼 크기
        clr=[100, 100, 100], # 버튼 색깔
        cngclr=None, # 마우스가 위에 올려져있을때 바뀌는 색상
        func=None, # 클릭되었을때 실행되는 함수
        text = '', # 내용 (문구)
        font = "malgungothic", # 글씨체
        font_size=16, # 글씨 크기
        font_clr=[0, 0, 0] # 글씨 색깔
    ):

        self.clr    = clr # 버튼 색상
        self.size   = size # 버튼 크기
        self.func   = func # 클릭 되었을때의 반응
        self.surf   = pygame.Surface(size) # 화면에 보여질 객체 만들기 (Surface)
        self.rect   = self.surf.get_rect(center=position) # rect 정보 저장하기 (크기로 이루어진 surf 객체랑 정보 객체 position)

        if cngclr: # 마우스가 올려져있을때의 칠해질 색상, 지정 안되어있어도 상관없음
            self.cngclr = cngclr # 색상 바꾸기용
        else: # 지정이 안되어있으면
            self.cngclr = clr # 색상 그대로 냅두기

        if len(clr) == 4: # 알파값 (투명도)가 지정되었다면
            self.surf.set_alpha(clr[3]) # 알파값 지정하기

        self.font = pygame.font.SysFont(font, font_size) # 글씨 폰트 객체 생성하기
        self.txt = text # 내용 (문구)
        self.font_clr = font_clr # 글씨 색깔
        self.txt_surf = self.font.render(self.txt, 1, self.font_clr) # 안티-앨리어싱 주어서 글씨 Surface 객체 생성하기
        self.txt_rect = self.txt_surf.get_rect(center=[wh//2 for wh in self.size]) # 글씨 정중앙에 배치하기

        Button.OBJ += (self,)

    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curclr)
        self.surf.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surf, self.rect)

    def mouseover(self):
        self.curclr = self.clr
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curclr = self.cngclr

    def call_back(self, *args):
        if self.func:
            return self.func(*args)

    @classmethod
    def draw_all(cls, screen):
        for obj in cls.OBJ: obj.draw(screen)

pygame.init()

url = 'https://kamilake.com/m/192'
page = requests.get(url)
page.raise_for_status()

soup = BeautifulSoup(page.text, 'lxml')
elem = soup.select_one('#mainContent > div.blogview_content.editor_ke > p > span')

pi = elem.text
pi = pi.replace(' ', '')
pi = pi.replace('\n', '')
pi = pi[2:]

del requests, BeautifulSoup, url, page, soup, elem

# set game constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
FPS = 60
FPSCLOCK = pygame.time.Clock()
BUTTON_WIDTH = 70
BUTTON_HEIGHT = 70
BUTTON_CENTER_Y = 700
BUTTON_XMARGIN = 27
CENTER_X = WINDOW_WIDTH // 2
LENGTH_PART_OF_PI = 36
MAX_DIGHT = 10000

DATE_PATTERN = re.compile(r'(?P<year>\d{4,})/(?P<month>\d{1,2})/(?P<day>\d{1,2}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})')

WRONG = 'wrong'
PERFECT = 'perfect'

# font
FONT = 'consolas'

# set history file
history_file_name = f'C:\\Users\\{getlogin()}\\memorize_pi_history.txt'
if isfile(history_file_name): mode = 'r'
else: mode = 'w'

with open(history_file_name, mode, encoding = 'utf-8') as hf:
    if mode == 'r': best_price = max([int(i.split(' ')[0]) for i in hf.readlines()] + [0])
    if mode == 'w': best_price = 0

# set game variables
running = True

try: dight = int(prompt(text = f'PI의 몇번째 자리에서 시작하시겠습니까? (0 ~ {best_price})', title = 'Memorize Pi의 내용:', default = '0'))
except: dight = 0
if dight not in range(best_price + 1): dight = 0

heart_point = 3
before_number = None
result = ''

# colors - R    G    B
RED   = (255,   0,   0)
WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
BLUE  = (  0,   0, 255)

def onclick(number):
    def wrapper():
        global dight, heart_point, best_price, before_number
        before_number = number

        if str(number) == pi[dight]:
            dight += 1

            if ((dight % 100) == 0) and (dight > 0): heart_point = 3
            if dight > best_price: best_price = dight
        else: heart_point -= 1

        if heart_point == 0: game_over(WRONG)
        elif dight == MAX_DIGHT: game_over(PERFECT)
        else: setup()

    return wrapper

# create window
DISPLAY = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Memorize PI Dights')

icon_image = pygame.image.load('related_files/icon.png')
icon_image = pygame.transform.scale(icon_image, (32, 32))
pygame.display.set_icon(icon_image)

DISPLAY.fill(BLACK)

# buttons
button_list = [
    Button(
        position = ((BUTTON_XMARGIN * (i + 1)) + (35 * ((2 * i) + 1)), BUTTON_CENTER_Y),
        size = (BUTTON_WIDTH, BUTTON_HEIGHT),
        clr = WHITE,
        cngclr = RED,
        func = onclick(i),
        text = str(i),
        font = FONT,
        font_size = 30,
        font_clr = BLACK
    ) for i in range(10)
]

def get_date(data, pattern=DATE_PATTERN):
    date = data['Time']

    match = pattern.match(date)
    assert match.string == date

    group = match.groupdict()
    year = int(group['year'])
    month = int(group['month'])
    day = int(group['day'])
    hour = int(group['hour'])
    minute = int(group['minute'])
    second = int(group['second'])

    return datetime(year, month, day, hour, minute, second)

# show history
def show_history():
    with open(history_file_name, 'r') as f: src = f.read()
    if src == '': return None

    src = src.splitlines()
    datas = [{'Time': t, 'Dights': dd} for (dd, t) in [((a.split(' ')[0], " ".join(a.split(' ')[1:]),)) for a in src]]

    ranks = sorted(datas, key = lambda x: int(x['Dights']), reverse=True)
    for idx in range(len(ranks)): ranks[idx]['rank'] = idx + 1
    times = sorted(ranks, key = get_date)

    sorted_by_rank = ''
    for rank in ranks:
        sorted_by_rank += rank['Dights']
        sorted_by_rank += ' / Time: '
        sorted_by_rank += rank['Time']
        sorted_by_rank += ' / Rank : '
        sorted_by_rank += str(rank['rank'])
        if rank['rank'] == 1: sorted_by_rank += ' ✮ Best Score!! ✮'

        sorted_by_rank += '\n'

    sorted_by_rank = sorted_by_rank[:-1]

    sorted_by_date = ''
    for time in times:
        sorted_by_date += time['Time']
        sorted_by_date += ' / Dights : '
        sorted_by_date += time['Dights']
        sorted_by_date += ' / Rank : '
        sorted_by_date += str(time['rank'])
        if time['rank'] == 1: sorted_by_date += ' ✮ Best Score!! ✮'

        sorted_by_date += '\n'

    alert(title = 'Memorize Pi 의 내용 (점수 순서):', text = sorted_by_rank)
    alert(title = 'Memorize PI 의 내용: (시간 순서)', text = sorted_by_date)

# button (onclick : show History)
show_history_button = Button(
    position = (CENTER_X, 350),
    size = (250, 40),
    clr = BLUE,
    cngclr = WHITE,
    func = show_history,
    text = 'See History...',
    font = FONT,
    font_size = 30,
    font_clr = RED
)
button_list.append(show_history_button)

# create text objects
def makeText(font_size: int, msg: str, clr: tuple[int, int, int], position: tuple[int, int]) -> tuple[pygame.Rect, pygame.Surface]:
    font = pygame.font.SysFont(FONT, font_size)
    surf = font.render(msg, True, clr)
    rect = surf.get_rect(center = position)

    return (surf, rect)

# texts
def setup_text():
    global best_price_rect, best_price_surf, hp_surf, hp_rect, dight_surf, dight_rect, pi_surf, pi_rect, ans_surf, ans_rect

    best_price_surf, best_price_rect = makeText(35, f'Best : {best_price}', WHITE, (CENTER_X, 30))
    DISPLAY.blit(best_price_surf, best_price_rect)

    hp_surf, hp_rect = makeText(40, ' '.join('♥' * heart_point), RED, (CENTER_X, 125))
    DISPLAY.blit(hp_surf, hp_rect)

    dight_surf, dight_rect = makeText(35, f'dight : {dight}', WHITE, (CENTER_X, 75))
    DISPLAY.blit(dight_surf, dight_rect)

    pi_surf, pi_rect = makeText(50, getPartOfPiFromDight(dight), WHITE, (CENTER_X, 190))
    DISPLAY.blit(pi_surf, pi_rect)

    ans_surf, ans_rect = makeText(35, result, RED, (CENTER_X, 250))
    DISPLAY.blit(ans_surf, ans_rect)

    pygame.display.flip()

def getPartOfPiFromDight(d: int) -> str:
    if d <= (LENGTH_PART_OF_PI - 1):
        part_of_pi = [char for char in pi[:(LENGTH_PART_OF_PI + 1)]]
        part_of_pi[dight:] = ['?' for _ in range(LENGTH_PART_OF_PI - d)]
        return "".join(part_of_pi)

    elif d == MAX_DIGHT:
        part_of_pi = pi[(MAX_DIGHT - LENGTH_PART_OF_PI):]
        return part_of_pi

    else:
        part_of_pi = [char for char in pi[(d + 1 - LENGTH_PART_OF_PI):(d + 1)]]
        part_of_pi[-1] = '?'
        return "".join(part_of_pi)

def setup():
    DISPLAY.fill(BLACK, best_price_rect)
    DISPLAY.fill(BLACK, hp_rect)
    DISPLAY.fill(BLACK, dight_rect)
    DISPLAY.fill(BLACK, pi_rect)
    DISPLAY.fill(BLACK, ans_rect)
    setup_text()

def game_over(mode):
    global dight, heart_point, result, running

    with open(history_file_name, 'a') as f:
        now = datetime.now()
        f.write(f'{dight} {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}\n')

    if mode == WRONG:
        result = f'Answer is {pi[dight]} but you pressed {before_number}'
        setup()
        pygame.time.wait(2000)

        result = ''

        try: dight = int(prompt(text = f'PI의 몇번째 자리에서 시작하시겠습니까? (0 ~ {best_price})', title = 'Memorize Pi의 내용:', default = '0'))
        except: dight = 0
        if dight not in range(best_price + 1): dight = 0

        heart_point = 3
        setup()

    else:
        assert mode == PERFECT
        result = f'You finished {MAX_DIGHT} dights!'
        setup()
        pygame.time.wait(2000)
        running = False

setup_text()

# main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE: running = False
            elif event.key == pygame.K_0: onclick(0)()
            elif event.key == pygame.K_1: onclick(1)()
            elif event.key == pygame.K_2: onclick(2)()
            elif event.key == pygame.K_3: onclick(3)()
            elif event.key == pygame.K_4: onclick(4)()
            elif event.key == pygame.K_5: onclick(5)()
            elif event.key == pygame.K_6: onclick(6)()
            elif event.key == pygame.K_7: onclick(7)()
            elif event.key == pygame.K_8: onclick(8)()
            elif event.key == pygame.K_9: onclick(9)()

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            for button in button_list:
                if button.rect.collidepoint(pos): button.call_back()

    Button.draw_all(DISPLAY)

    pygame.display.flip()
    FPSCLOCK.tick(FPS)

# exit (quit)
with open(history_file_name, 'a') as f:
    now = datetime.now()
    f.write(f'{dight} {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}:{now.second}\n')