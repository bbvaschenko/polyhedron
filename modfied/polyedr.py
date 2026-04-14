from math import pi, sqrt, acos
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    def is_degenerate(self):
        return self.beg >= self.fin

    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]


class Edge:
    """ Ребро полиэдра """
    SBEG, SFIN = 0.0, 1.0

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    def shadow(self, facet):
        if facet.is_vertical():
            return
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return

        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)

    def is_fully_invisible(self):
        """Проверка: полностью ли невидимо ребро?"""
        return len(self.gaps) == 0

    def perimeter(self):
        """Длина ребра"""
        return sqrt((self.fin.x - self.beg.x) ** 2 +
                    (self.fin.y - self.beg.y) ** 2 +
                    (self.fin.z - self.beg.z) ** 2)


class Facet:
    """ Грань полиэдра """

    def __init__(self, vertexes):
        self.vertexes = vertexes
        self._edges = None  # Ссылки на рёбра будут установлены позже

    def set_edges(self, edges):
        """Установка ссылок на рёбра грани"""
        self._edges = edges

    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    def h_normal(self):
        n = (self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * (1.0 / len(self.vertexes))

    def all_edges_fully_invisible(self):
        """Все ли рёбра грани полностью невидимы?"""
        if self._edges is None:
            return False
        return all(e.is_fully_invisible() for e in self._edges)

    def angle_with_horizontal(self):
        """
        Угол между гранью и горизонтальной плоскостью.
        Возвращает угол в радианах.
        """
        normal = self.h_normal()
        # Нормализуем вектор нормали
        norm_len = sqrt(normal.x ** 2 + normal.y ** 2 + normal.z ** 2)
        if norm_len < 1e-10:
            return 0.0
        normal = R3(normal.x / norm_len, normal.y / norm_len, normal.z / norm_len)
        # Вектор вертикали
        vertical = Polyedr.V
        vert_len = sqrt(vertical.x ** 2 + vertical.y ** 2 + vertical.z ** 2)
        vertical = R3(vertical.x / vert_len, vertical.y / vert_len, vertical.z / vert_len)
        # Угол между нормалью и вертикалью
        dot_product = abs(normal.dot(vertical))
        if dot_product > 1.0:
            dot_product = 1.0
        angle = acos(dot_product)
        return angle

    def perimeter(self):
        """Периметр грани"""
        per = 0.0
        n = len(self.vertexes)
        for i in range(n):
            v1 = self.vertexes[i]
            v2 = self.vertexes[(i + 1) % n]
            per += sqrt((v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2 + (v2.z - v1.z) ** 2)
        return per

    def center_projection_outside_unit_square(self):
        """
        Проверка: находится ли проекция центра грани строго вне
        квадрата [-0.5, 0.5] x [-0.5, 0.5]?
        """
        cx = self.center().x
        cy = self.center().y
        # Строго вне: либо |cx| > 0.5, либо |cy| > 0.5
        return abs(cx) > 0.5 or abs(cy) > 0.5

    def meets_criteria(self):
        """Соответствует ли грань всем критериям?"""
        # 1. Все рёбра грани полностью невидимы
        if not self.all_edges_fully_invisible():
            return False
        # 2. Угол с горизонталью не более π/7
        if self.angle_with_horizontal() > pi / 7:
            return False
        # 3. Проекция центра вне квадрата
        if not self.center_projection_outside_unit_square():
            return False
        return True


class Polyedr:
    """ Полиэдр """
    V = R3(0.0, 0.0, 1.0)

    def __init__(self, file):
        self.vertexes, self.edges, self.facets = [], [], []

        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    buf = line.split()
                    c = float(buf.pop(0))
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(R3(x, y, z).rz(
                        alpha).ry(beta).rz(gamma) * c)
                else:
                    buf = line.split()
                    size = int(buf.pop(0))
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # Сохраняем рёбра для этой грани
                    facet_edges = []
                    for n in range(size):
                        e = Edge(vertexes[n - 1], vertexes[n])
                        self.edges.append(e)
                        facet_edges.append(e)
                    f = Facet(vertexes)
                    f.set_edges(facet_edges)
                    self.facets.append(f)

    def compute_sum_of_perimeters(self):
        """
        Вычисление суммы периметров граней, удовлетворяющих критериям.
        """
        total = 0.0
        for facet in self.facets:
            if facet.meets_criteria():
                total += facet.perimeter()
        return total

    def draw(self, tk):
        tk.clean()
        for e in self.edges:
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))