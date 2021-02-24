import pygame


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

        self.turn = 1

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        k = 2
        cy = self.top
        for row in self.board:
            cx = self.left
            for elem in row:
                color = pygame.Color(220, 200, 0)
                pygame.draw.rect(screen, color,
                                 ((cx, cy),
                                  (self.cell_size, self.cell_size)), width=k)
                hsv = color.hsva
                color.hsva = (int(hsv[0]), int(hsv[1]), int(hsv[2] - 30), int(hsv[3]))
                pygame.draw.rect(screen, color,
                                 ((cx + k, cy + k),
                                  (self.cell_size, self.cell_size)), width=k)

                if elem == 1:
                    pygame.draw.line(screen, (0, 0, 255),
                                     (cx + 3 * k, cy + 3 * k),
                                     (cx + self.cell_size - 3 * k, cy + self.cell_size - 3 * k), width=k)
                    pygame.draw.line(screen, (0, 0, 255),
                                     (cx + self.cell_size - 3 * k, cy + 3 * k),
                                     (cx + 3 * k, cy + self.cell_size - 3 * k), width=k)
                elif elem == 2:
                    pygame.draw.circle(screen, (255, 0, 0),
                                       (cx + 0.5 * self.cell_size + k, cy + 0.5 * self.cell_size + k),
                                        self.cell_size // 2 - 2 * k, width=k)

                cx += self.cell_size
            cy += self.cell_size

    def get_cell(self, mouse_pos):
        if (mouse_pos[0] in range(self.left, self.left + self.width * self.cell_size)) and \
                (mouse_pos[1] in range(self.top, self.top + self.height * self.cell_size)):
            return ((mouse_pos[0] - self.left) // self.cell_size,
                    (mouse_pos[1] - self.top) // self.cell_size)
        else:
            return None

    def on_click(self, cell_coords):
        if cell_coords is not None:
            if self.board[cell_coords[1]][cell_coords[0]] == 0:
                self.board[cell_coords[1]][cell_coords[0]] = self.turn
                self.turn = self.turn % 2 + 1

        print(cell_coords)

    def get_click(self, mouse_pos):

        cell = self.get_cell(mouse_pos)
        self.on_click(cell)