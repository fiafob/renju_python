# по всему коду при рисовании фигур можно увидеть + 1/2/3 пикселя - это не что-то особенное,
# просто ручная настройка чтобы все смотрелось более-менее приемлимо
import os
import random
import sys

import pygame

SIZE = WIDTH, HEIGHT = 900, 674
RC = 15  # renju_cells
COLOR = pygame.Color(200, 170, 0)  # тот оранжевый цвет
FONT = 'data/font/ARCADECLASSIC.TTF'
PNUM = 3  # количество разных моделей планет каждого цвета

chip_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    pygame.init()
    pygame.display.set_caption("Рэндзю")
    renju_screen = pygame.display.set_mode(SIZE)

    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        print('jj')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Очень сырой вариант : крестики-нолики вместо фишек // поле накладывается одно поверх другого
# какие-то границы есть стремные.
#
# Стоит добавить функцию, которая возвращает количество пикселей, которое занимает поле
class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

        # turn - определяет кто сейчас ходит. 1 - blue, 2 - red
        # p1 | p2 - player1 | player2 - сколько ходов сделал игрок
        self.turn = 1
        self.p1 = 0
        self.p2 = 0

        # rv - right version
        self.rvx = self.get_size()[0] - self.cell_size
        self.rvy = self.get_size()[1] - self.cell_size

        # коэффицент затемнения
        self.shdwK = 30
        self.button_clicked = False

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

        # rv - right version
        self.rvx = self.get_size()[0] - self.cell_size
        self.rvy = self.get_size()[1] - self.cell_size

    def render(self, screen):
        # k - коэффицент толщины рамки
        k = 3

        self.help_rect(screen)
        self.nums_letts(screen)
        self.hud(screen)

        # само поле
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        # cx, cy - count подсчитвыает текущее расположение ряда/колонны
        cy = self.top
        for row in self.board:
            cx = self.left
            for elem in row:
                for shadow_k in range(1, -1, -1):
                    color = pygame.Color(200, 170, 0)
                    hsv = color.hsva
                    color.hsva = (int(hsv[0]), int(hsv[1]),
                                  int(hsv[2] - 30 * shadow_k), int(hsv[3]))
                    # vertical line
                    pygame.draw.line(screen, color, (cx + k * shadow_k, self.top + k * shadow_k),
                                     (cx + k * shadow_k, self.rvy + self.top), width=k)
                    # horizontal line
                    pygame.draw.line(screen, color, (self.left, cy + shadow_k * k),
                                     (self.rvx + self.left, cy + k * shadow_k), width=k)

                cross_x = cx - self.left
                cross_y = cy - self.top
                if elem == 1:
                    chipb = BlueChip(chip_group)
                    chipb.rect.x = cross_x + k - 1
                    chipb.rect.y = cross_y + k - 1

                elif elem == 2:
                    chipr = RedChip(chip_group)
                    chipr.rect.x = cross_x + k - 1
                    chipr.rect.y = cross_y + k - 1

                cx += self.cell_size
            cy += self.cell_size
        # 4 точки, пока не знаю для чего они
        for k in range(1, 9, 7):
            pygame.draw.circle(screen, COLOR, (3 * self.cell_size + self.left + 1,
                                               (3 + k) * self.cell_size + self.top + 1), 8)
            pygame.draw.circle(screen, COLOR,
                               (self.get_size()[0] + self.left - self.cell_size * 4 + 1,
                                (3 + k) * self.cell_size + self.top + 1), 8)
        screen.blit(surf, (0, 0))
        chip_group.draw(screen)

    # Полупрозрачный квадрат, будет работать до 3 хода, помогает понять, где ходить
    def help_rect(self, screen):
        surf = pygame.surface.Surface(SIZE, pygame.SRCALPHA)
        width, height = self.get_size()
        color = pygame.Color(200, 170, 0, 50)
        # p1 + p2 - общее количество ходов
        if self.p1 + self.p2 == 0:
            pygame.draw.rect(surf, color, ((((width - 2 * self.cell_size) // 2) + self.left + 1,
                                            ((height - 2 * self.cell_size) // 2) + self.top + 1),
                                           (self.cell_size, self.cell_size)))
        elif self.p1 + self.p2 == 1:
            pygame.draw.rect(surf, color, ((((width - 2 * self.cell_size) // 2) + self.left + 1,
                                            ((height - 4 * self.cell_size) // 2) + self.top + 1),
                                           (2 * self.cell_size, self.cell_size)))
        elif self.p1 + self.p2 == 2:
            pygame.draw.rect(surf, color, ((((width - 6 * self.cell_size) // 2) + self.left + 1,
                                            ((height - 6 * self.cell_size) // 2) + self.top + 1),
                                           (5 * self.cell_size, 5 * self.cell_size)))
        screen.blit(surf, (0, 0))

    # Возможно это в итоге не пригодится, но сейчас это нужно чтобы понимать как работает игра
    # Отображает цифры и буквы
    def nums_letts(self, screen):
        font = pygame.font.Font(FONT, 2 * RC)
        for number in range(1, RC + 1):
            text = font.render(str(number), True, COLOR)
            screen.blit(text, (2 * self.left + self.rvx,
                               0.5 * self.top + (number - 1) * self.cell_size))

        letters = "ABCDEFGHIJKLMNO"
        for n in range(RC):
            text = font.render(letters[n], True, COLOR)
            screen.blit(text, (self.left // 1.5 + n * self.cell_size,
                               2 * self.top + self.rvy))

    #############################################################################################
    #############################################################################################

    def hud(self, screen):
        if self.turn == 1:
            pygame.draw.circle(screen, (0, 0, 255),
                               (self.get_size()[0] + 3 * self.cell_size,
                                self.top + self.cell_size),
                               self.cell_size)
        else:
            pygame.draw.circle(screen, (255, 0, 0),
                               (self.get_size()[0] + 3 * self.cell_size,
                                self.top + self.cell_size),
                               self.cell_size)

        self.button(screen)

    def button(self, screen):
        #
        btn_clr = pygame.Color(200, 170, 0)
        txt_clr = pygame.Color(240, 240, 240)
        font = pygame.font.Font(FONT, 2 * RC)
        for clr in [btn_clr, txt_clr]:
            hsv = clr.hsva
            clr.hsva = (int(hsv[0]), int(hsv[1]), int(hsv[2]) - self.shdwK, int(hsv[3]))
        x0, y0 = self.get_size()[0] + 2 * self.cell_size, HEIGHT - 2 * self.cell_size - self.top

        dy = 0
        if not self.button_clicked:
            btn_clr = (btn_clr[0] - 30, btn_clr[1] - 30, btn_clr[2])

            pygame.draw.rect(screen, (btn_clr[0] - 50, btn_clr[1] - 50, btn_clr[2]),
                             ((x0 - 1, y0 + self.cell_size // 2.8),
                              (int(3.5 * self.cell_size), int(1 * self.cell_size))),
                             border_radius=5)
        else:
            dy = 4
        pygame.draw.rect(screen, btn_clr, ((x0 - 1, y0 + self.cell_size // 3.8 + dy),
                                           (int(3.5 * self.cell_size), int(1 * self.cell_size))),
                         border_radius=5)
        text = font.render('RESTART', True, txt_clr)
        screen.blit(text, (x0 + self.cell_size // 2.4, y0 + self.cell_size // 2.5 + dy))

    def button_check(self, mouse_pos):
        x0 = self.get_size()[0] + 2 * self.cell_size
        y0 = HEIGHT - 2 * self.cell_size - self.top
        if mouse_pos[0] in range(x0, x0 + int(3.5 * self.cell_size)) and \
                mouse_pos[1] in range(y0, y0 + int(1.5 * self.cell_size)):
            self.shdwK = 0
        else:
            self.shdwK = 30

    def button_click(self, mouse_pos, action):
        x0 = self.get_size()[0] + 2 * self.cell_size
        y0 = HEIGHT - 2 * self.cell_size - self.top
        if mouse_pos[0] in range(x0, x0 + int(3.5 * self.cell_size)) and \
                mouse_pos[1] in range(y0, y0 + int(1.5 * self.cell_size)):
            if action == "down":
                self.button_clicked = True
            else:
                self.button_clicked = False
                self.update_desk()

    def update_desk(self):
        global chip_group
        chip_group = pygame.sprite.Group()
        self.board = [[0] * self.width for _ in range(self.height)]
        self.p1, self.p2 = 0, 0
        self.turn = 1
    #############################################################################################
    #############################################################################################

    def get_cell(self, mouse_pos):
        # она определяет точку в поле 16x16, где одна клетка является переврестием
        if (mouse_pos[0] in range(0, self.width * (self.cell_size + 1))) and \
                (mouse_pos[1] in range(0, self.height * (self.cell_size + 1))):
            return ((mouse_pos[0]) // (self.cell_size + 1),
                    (mouse_pos[1]) // (self.cell_size + 1))
        else:
            return None

    # обрабатывает что делать при нажатии
    def on_click(self, cell_coords):
        if cell_coords is not None:
            if self.board[cell_coords[1]][cell_coords[0]] == 0:
                if self.turn == 1:
                    self.p1 += 1
                elif self.turn == 2:
                    self.p2 += 1
                # если поле пустое, ему передается значение игрока, который ходит
                self.board[cell_coords[1]][cell_coords[0]] = self.turn
                self.turn = self.turn % 2 + 1

        print(cell_coords)

    # функция для основной программы можно сказать, чтобы сразу срабатывало
    def get_click(self, mouse_pos):

        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    ########################################################################

    # возвращает размер доски в пикселях
    def get_size(self):
        return self.cell_size * self.width, self.cell_size * self.height


#########################################################################
#########################################################################
#########################################################################


# класс фишки, т.к. я думаю с ней придется много работать
class BlueChip(pygame.sprite.Sprite):
    image = load_image(f"img/blue{random.randrange(3) + 1}.png")
    image = pygame.transform.scale(image, (40, 40))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = BlueChip.image
        self.rect = self.image.get_rect()


class RedChip(pygame.sprite.Sprite):
    image = load_image(f"img/red{random.randrange(3) + 1}.png")
    image = pygame.transform.scale(image, (40, 40))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = RedChip.image
        self.rect = self.image.get_rect()


#########################################################################
#########################################################################
#########################################################################

# класс представляет задний фон из точек, который напоминает мерцающие звезды
class BackgroundBlink:
    def __init__(self, stars):
        self.stars = stars

        # случайное расположение звезд
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT))
                          for _ in range(stars)]

        # переменная, из-за которой звезды затухают
        self.darkness = 200

        # Определяет будет ли затухать звезда или появляться
        self.get_darker = False

    # создаю поверхность с звездами, потому что прозрачность можно менять у поверхностей
    def show_stars(self, screen):
        surf = pygame.Surface(SIZE, pygame.SRCALPHA)
        counter = 0
        k = 3
        for x, y in self.positions:
            color = pygame.Color(220, 255, 255, 200 - self.darkness)
            # Отображение разных звезд

            # простой плюсик
            if counter == 0:
                pygame.draw.line(surf, color, (x - k - 1, y), (x + k + 1, y), width=k)
                pygame.draw.line(surf, color, (x, y - k - 1), (x, y + k + 1), width=k)
            # перекрестие
            elif counter == 1:
                for kk in range(-k, k + 1, k):
                    pygame.draw.rect(surf, color, ((x + kk, y + kk), (k, k)), border_radius=1)
                    pygame.draw.rect(surf, color, ((x + kk, y - kk), (k, k)), border_radius=1)
                pygame.draw.rect(surf, color, ((x, y), (k, k)), border_radius=1)
            # ромб
            elif counter == 2:
                kk = 4
                for w in range(3):
                    kk = 4 if kk == 2 else 2
                    for q in range(kk):
                        z = 1 if q % 2 == 0 else -1
                        if q > 1:
                            pygame.draw.rect(surf, color, ((x + z * (2 - w) * k, y + z * w * k),
                                                           (k, k)), border_radius=1)
                        else:
                            pygame.draw.rect(surf, color, ((x + z * (2 - w) * k, y - z * w * k),
                                                           (k, k)), border_radius=1)

            counter = (counter + 1) % 3
        screen.blit(surf, (0, 0))

    # функция вызывается так, чтобы за 6 секунд звезда потухла
    def change_darkness(self):
        if self.darkness < 200 and self.get_darker:
            self.darkness += 1
        elif self.darkness > 0 and not self.get_darker:
            self.darkness -= 1
        elif self.darkness == 200:
            self.get_darker = False
        else:
            self.get_darker = True

    # функция обновляется каждые 12 секунд, меняя расположение звезд
    def update(self):
        self.darkness = 200
        self.positions = [(random.randrange(WIDTH), random.randrange(HEIGHT))
                          for _ in range(self.stars)]
