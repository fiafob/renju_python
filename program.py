# Короче, тут будет сама игра, а классы в отдельном файле
import os
import sys

import pygame as pg

from classes import Board, BackgroundBlink, load_image

SIZE = WIDTH, HEIGHT = 900, 674
RC = 15  # renju_cells
STARS = 25
CHANGE_BACKGROUND = pg.USEREVENT + 1
DARKNESS_TICK = CHANGE_BACKGROUND + 1

# Инициализация и настройка окна с самой игрой
# pg.init()
# pg.display.set_caption("Рендзю")
renju_screen = pg.display.set_mode(SIZE)


def main():

    game_running = True

    # обрабатывает двойные нажатия
    clock = pg.time.Clock()
    timer = 0
    dt = 0

    # Доска | RC - количество клеток в рэндзю
    cell_size = HEIGHT // (RC + 1)
    board = Board(RC, RC)
    board.set_view(cell_size // 2, cell_size // 2, (HEIGHT - cell_size) // RC)

    # для заднего фона
    bg = BackgroundBlink(STARS)
    pg.time.set_timer(CHANGE_BACKGROUND, 12000)
    pg.time.set_timer(DARKNESS_TICK, 6000 // 200)

    while game_running:
        # изображение на заднем фоне
        renju_screen.blit(background, (0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                board.button_click(event.pos, 'down')

        # Надо обработать двойное нажатие левой кнопки
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if timer == 0:
                    timer = 0.001
                elif timer < 0.3:
                    board.get_click(event.pos)
                    timer = 0
                board.button_click(event.pos, 'up')

            elif event.type == pg.MOUSEMOTION:
                board.button_check(event.pos)

            elif event.type == CHANGE_BACKGROUND:
                bg.update()

            elif event.type == DARKNESS_TICK:
                bg.change_darkness()

        if timer != 0:
            timer += dt
            if timer >= 0.3:
                timer = 0

        bg.show_stars(renju_screen)
        board.render(renju_screen)

        dt = clock.tick() / 1000
        pg.display.flip()
    pg.quit()


background = load_image("img/bg.png")
background = pg.transform.scale(background, (int(1920 // 1.5), int(1080 // 1.5)))
main()
