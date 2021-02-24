# Короче, тут будет сама игра, а классы в отдельном файле наверно
import pygame as pg

from classes import Board

SIZE = WIDTH, HEIGHT = 930, 780
RC = 15  # renju_cells


def main():
    # Инициализация и настройка окна с самой игрой
    pg.init()
    pg.display.set_caption("Рендзю")
    renju_screen = pg.display.set_mode(SIZE)
    game_running = True

    # Доска | 15 - количество клеток в рэндзю
    board = Board(RC, RC)
    board.set_view(RC, RC, (HEIGHT - RC * 2) // RC)

    while game_running:
        renju_screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

        # Обработать двойное нажатие левой кнопки
            if event.type == pg.MOUSEBUTTONUP:
                board.get_click(event.pos)
                ...

        board.render(renju_screen)
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
