# Короче, тут будет сама игра, а классы в отдельном файле наверно
# Еще надо добавить кнопку сдроса доски / счеткик каждого из игроков
import pygame as pg

from classes import Board

SIZE = WIDTH, HEIGHT = 930, 780
RC = 14  # renju_cells


def main():
    # Инициализация и настройка окна с самой игрой
    pg.init()
    pg.display.set_caption("Рендзю")
    renju_screen = pg.display.set_mode(SIZE)
    game_running = True

    # Доска | RC - количество клеток в рэндзю
    board = Board(RC, RC)
    board.set_view(RC, 5, (HEIGHT - RC * 2) // RC)
    print(RC, (HEIGHT - RC * 2) // RC)

    while game_running:
        renju_screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

        # Надо обработать двойное нажатие левой кнопки
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                board.get_click(event.pos)
                ...

        board.render(renju_screen)
        board.nums_letts(renju_screen)
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
