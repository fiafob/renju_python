# Короче, тут будет сама игра, а классы в отдельном файле наверно
# Еще надо добавить кнопку сдроса доски / счеткик каждого из игроков
import pygame as pg

from classes import Board, BackgroundBlick

SIZE = WIDTH, HEIGHT = 1000, 780
RC = 15  # renju_cells
FPS = 144


def main():
    # Инициализация и настройка окна с самой игрой
    pg.init()
    pg.display.set_caption("Рендзю")
    renju_screen = pg.display.set_mode(SIZE)
    clock = pg.time.Clock()
    game_running = True

    # Доска | RC - количество клеток в рэндзю
    board = Board(RC, RC)
    board.set_view(RC, RC, (HEIGHT - RC * 2) // RC)

    bg = BackgroundBlick(100)

    while game_running:
        renju_screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

        # Надо обработать двойное нажатие левой кнопки
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                board.get_click(event.pos)
                ...

        bg.show_stars(renju_screen)
        board.render(renju_screen)
        board.nums_letts(renju_screen)

        clock.tick()
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
