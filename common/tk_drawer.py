import matplotlib.pyplot as plt

# Коэффициент гомотетии
SCALE = 1.5


class TkDrawer:
    """ Графический интерфейс (matplotlib backend) """

    # Конструктор
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.fig.canvas.manager.set_window_title("Изображение проекции полиэдра")
        self.ax.set_aspect('equal')
        self.ax.axis('off')

    # Завершение работы
    def close(self):
        plt.ioff()
        plt.close(self.fig)

    # Стирание существующей картинки
    def clean(self):
        self.ax.cla()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    # Рисование линии
    def draw_line(self, p, q):
        self.ax.plot(
            [SCALE * p.x, SCALE * q.x],
            [SCALE * p.y, SCALE * q.y],
            color='black', linewidth=0.5
        )
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


if __name__ == "__main__":  # pragma: no cover

    import time
    from r3 import R3
    tk = TkDrawer()
    tk.clean()
    tk.draw_line(R3(0.0, 0.0, 0.0), R3(100.0, 100.0, 0.0))
    tk.draw_line(R3(0.0, 0.0, 0.0), R3(0.0, 100.0, 0.0))
    time.sleep(5)
    tk.close()