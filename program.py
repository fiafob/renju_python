# Короче, тут будет сама игра, а классы в отдельном файле наверно
# Еще надо добавить кнопку сдроса доски / счеткик каждого из игроков
import pygame as pg

from classes import Board, BackgroundBlink

SIZE = WIDTH, HEIGHT = 1000, 780
RC = 15  # renju_cells
CHANGE_BACKGROUND = pg.USEREVENT + 1
DARKNESS_TICK = CHANGE_BACKGROUND + 1


def main():
    # Инициализация и настройка окна с самой игрой
    pg.init()
    pg.display.set_caption("Рендзю")
    renju_screen = pg.display.set_mode(SIZE)
    game_running = True

    # обрабатывает двойные нажатия
    clock = pg.time.Clock()
    timer = 0
    dt = 0

    # Доска | RC - количество клеток в рэндзю
    board = Board(RC, RC)
    board.set_view(RC, RC, (HEIGHT - RC * 2) // RC)

    bg = BackgroundBlink(100)
    pg.time.set_timer(CHANGE_BACKGROUND, 6000)
    pg.time.set_timer(DARKNESS_TICK, 6000 // 200)

    while game_running:
        renju_screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_running = False

        # Надо обработать двойное нажатие левой кнопки
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                if timer == 0:
                    timer = 0.001
                elif timer < 0.5:
                    board.get_click(event.pos)
                    timer = 0

            if event.type == CHANGE_BACKGROUND:
                bg.update()

            if event.type == DARKNESS_TICK:
                bg.change_darkness()

        if timer != 0:
            timer += dt
            if timer >= 0.5:
                timer = 0

        bg.show_stars(renju_screen)
        board.render(renju_screen)
        board.nums_letts(renju_screen)

        dt = clock.tick() / 1000
        pg.display.flip()
    pg.quit()


if __name__ == "__main__":
    main()
