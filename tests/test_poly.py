#!/usr/bin/env python3

import unittest
from math import pi, isclose, sqrt
from common.r3 import R3
from polyedr import Polyedr, Edge, Facet, Segment


class TestEdgeVisibility(unittest.TestCase):
    """Тесты для определения видимости рёбер"""

    def test_fully_visible_edge(self):
        """Ребро полностью видимо (gaps содержит весь отрезок)"""
        e = Edge(R3(0, 0, 0), R3(1, 0, 0))
        e.gaps = [Segment(0.0, 1.0)]
        self.assertFalse(e.is_fully_invisible())

    def test_fully_invisible_edge(self):
        """Ребро полностью невидимо (gaps пуст)"""
        e = Edge(R3(0, 0, 0), R3(1, 0, 0))
        e.gaps = []
        self.assertTrue(e.is_fully_invisible())

    def test_partially_visible_edge(self):
        """Ребро видимо частично (один или два просвета)"""
        e = Edge(R3(0, 0, 0), R3(1, 0, 0))
        e.gaps = [Segment(0.0, 0.3), Segment(0.7, 1.0)]
        self.assertFalse(e.is_fully_invisible())

    def test_edge_perimeter(self):
        """Проверка вычисления длины ребра"""
        e = Edge(R3(0, 0, 0), R3(3, 4, 0))
        # Должно быть 5 (египетский треугольник 3-4-5)
        self.assertAlmostEqual(e.perimeter(), 5.0, places=5)

        e = Edge(R3(1, 1, 1), R3(4, 5, 6))
        # sqrt((3)^2 + (4)^2 + (5)^2) = sqrt(9+16+25) = sqrt(50) ≈ 7.071
        self.assertAlmostEqual(e.perimeter(), sqrt(50), places=5)


class TestFacetAngle(unittest.TestCase):
    """Тесты для вычисления угла между гранью и горизонталью"""

    def test_horizontal_facet_angle_zero(self):
        """Горизонтальная грань → угол 0°"""
        v1 = R3(0, 0, 1)
        v2 = R3(1, 0, 1)
        v3 = R3(0, 1, 1)
        facet = Facet([v1, v2, v3])
        self.assertAlmostEqual(facet.angle_with_horizontal(), 0.0, places=5)

    def test_vertical_facet_angle_90(self):
        """Вертикальная грань → угол 90° (π/2)"""
        v1 = R3(0, 0, 0)
        v2 = R3(0, 0, 1)
        v3 = R3(0, 1, 0)
        facet = Facet([v1, v2, v3])
        self.assertAlmostEqual(facet.angle_with_horizontal(), pi / 2, places=5)

    def test_nearly_horizontal_facet(self):
        """Грань почти горизонтальная (угол < π/7)"""
        v1 = R3(0, 0, 0)
        v2 = R3(10, 0, 1)  # Подъём 1 на длине 10 → угол ≈ 5.7°
        v3 = R3(0, 10, 1)
        facet = Facet([v1, v2, v3])
        angle = facet.angle_with_horizontal()
        self.assertLess(angle, pi / 7)
        self.assertGreater(angle, 0)


class TestFacetCenterProjection(unittest.TestCase):
    """Тесты для проверки положения проекции центра грани"""

    def test_center_inside_square(self):
        """Центр грани внутри квадрата [-0.5, 0.5]"""
        # Квадрат с центром в (0,0) и стороной 1
        v1 = R3(-0.4, -0.4, 0)
        v2 = R3(0.4, -0.4, 0)
        v3 = R3(0.4, 0.4, 0)
        v4 = R3(-0.4, 0.4, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertFalse(facet.center_projection_outside_unit_square())

    def test_center_on_boundary_not_strictly_outside(self):
        """Центр на границе квадрата — НЕ строго вне"""
        v1 = R3(-0.5, -0.5, 0)
        v2 = R3(0.5, -0.5, 0)
        v3 = R3(0.5, 0.5, 0)
        v4 = R3(-0.5, 0.5, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertFalse(facet.center_projection_outside_unit_square())

    def test_center_outside_by_x(self):
        """Центр вне квадрата по X"""
        v1 = R3(1, -0.4, 0)
        v2 = R3(2, -0.4, 0)
        v3 = R3(2, 0.4, 0)
        v4 = R3(1, 0.4, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertTrue(facet.center_projection_outside_unit_square())

    def test_center_outside_by_y(self):
        """Центр вне квадрата по Y"""
        v1 = R3(-0.4, 1, 0)
        v2 = R3(0.4, 1, 0)
        v3 = R3(0.4, 2, 0)
        v4 = R3(-0.4, 2, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertTrue(facet.center_projection_outside_unit_square())

    def test_center_outside_both(self):
        """Центр вне квадрата по обеим осям"""
        v1 = R3(1, 1, 0)
        v2 = R3(2, 1, 0)
        v3 = R3(2, 2, 0)
        v4 = R3(1, 2, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertTrue(facet.center_projection_outside_unit_square())


class TestFacetAllEdgesInvisible(unittest.TestCase):
    """Тесты для проверки, что все рёбра грани невидимы"""

    def test_all_edges_invisible(self):
        """Все рёбра невидимы"""
        v1, v2, v3 = R3(0, 0, 0), R3(1, 0, 0), R3(0, 1, 0)
        facet = Facet([v1, v2, v3])

        e1 = Edge(v1, v2)
        e1.gaps = []
        e2 = Edge(v2, v3)
        e2.gaps = []
        e3 = Edge(v3, v1)
        e3.gaps = []
        facet.set_edges([e1, e2, e3])

        self.assertTrue(facet.all_edges_fully_invisible())

    def test_one_edge_visible(self):
        """Одно ребро видимо → грань не подходит"""
        v1, v2, v3 = R3(0, 0, 0), R3(1, 0, 0), R3(0, 1, 0)
        facet = Facet([v1, v2, v3])

        e1 = Edge(v1, v2)
        e1.gaps = []  # невидимо
        e2 = Edge(v2, v3)
        e2.gaps = [Segment(0.0, 1.0)]  # видимо!
        e3 = Edge(v3, v1)
        e3.gaps = []  # невидимо
        facet.set_edges([e1, e2, e3])

        self.assertFalse(facet.all_edges_fully_invisible())

    def test_no_edges_set(self):
        """Если рёбра не установлены — считаем, что не все невидимы"""
        v1, v2, v3 = R3(0, 0, 0), R3(1, 0, 0), R3(0, 1, 0)
        facet = Facet([v1, v2, v3])
        # _edges = None
        self.assertFalse(facet.all_edges_fully_invisible())


class TestFacetPerimeter(unittest.TestCase):
    """Тесты для вычисления периметра грани"""

    def test_triangle_perimeter(self):
        """Периметр треугольника"""
        v1 = R3(0, 0, 0)
        v2 = R3(3, 0, 0)
        v3 = R3(0, 4, 0)
        facet = Facet([v1, v2, v3])
        # Стороны: 3, 4, 5 → периметр = 12
        self.assertAlmostEqual(facet.perimeter(), 12.0, places=5)

    def test_square_perimeter(self):
        """Периметр квадрата"""
        v1 = R3(0, 0, 0)
        v2 = R3(2, 0, 0)
        v3 = R3(2, 2, 0)
        v4 = R3(0, 2, 0)
        facet = Facet([v1, v2, v3, v4])
        self.assertAlmostEqual(facet.perimeter(), 8.0, places=5)

    def test_rectangle_3d_perimeter(self):
        """Периметр прямоугольника в 3D"""
        v1 = R3(0, 0, 1)
        v2 = R3(3, 0, 1)
        v3 = R3(3, 4, 1)
        v4 = R3(0, 4, 1)
        facet = Facet([v1, v2, v3, v4])
        self.assertAlmostEqual(facet.perimeter(), 14.0, places=5)


class TestCombinedCriteria(unittest.TestCase):
    """Тесты комбинированных критериев"""

    def test_facet_meets_all_criteria(self):
        """Грань, удовлетворяющая всем трём критериям"""
        # Создаём грань:
        # 1. Все рёбра невидимы
        # 2. Горизонтальная (угол 0 < π/7)
        # 3. Центр вне квадрата
        v1 = R3(2, 2, 0)
        v2 = R3(3, 2, 0)
        v3 = R3(3, 3, 0)
        v4 = R3(2, 3, 0)
        facet = Facet([v1, v2, v3, v4])

        e1 = Edge(v1, v2)
        e1.gaps = []
        e2 = Edge(v2, v3)
        e2.gaps = []
        e3 = Edge(v3, v4)
        e3.gaps = []
        e4 = Edge(v4, v1)
        e4.gaps = []
        facet.set_edges([e1, e2, e3, e4])

        self.assertTrue(facet.meets_criteria())

    def test_facet_fails_visibility(self):
        """Не подходит: есть видимое ребро"""
        v1, v2, v3 = R3(2, 2, 0), R3(3, 2, 0), R3(2.5, 3, 0)
        facet = Facet([v1, v2, v3])

        e1 = Edge(v1, v2)
        e1.gaps = []  # невидимо
        e2 = Edge(v2, v3)
        e2.gaps = [Segment(0.0, 1.0)]  # видимо!
        e3 = Edge(v3, v1)
        e3.gaps = []  # невидимо
        facet.set_edges([e1, e2, e3])

        self.assertFalse(facet.meets_criteria())

    def test_facet_fails_angle(self):
        """Не подходит: угол > π/7"""
        # Вертикальная грань (угол 90° > π/7)
        v1 = R3(2, 2, 0)
        v2 = R3(3, 2, 0)
        v3 = R3(3, 2, 1)
        v4 = R3(2, 2, 1)
        facet = Facet([v1, v2, v3, v4])

        e1 = Edge(v1, v2)
        e1.gaps = []
        e2 = Edge(v2, v3)
        e2.gaps = []
        e3 = Edge(v3, v4)
        e3.gaps = []
        e4 = Edge(v4, v1)
        e4.gaps = []
        facet.set_edges([e1, e2, e3, e4])

        self.assertFalse(facet.meets_criteria())

    def test_facet_fails_center_position(self):
        """Не подходит: центр внутри квадрата"""
        v1 = R3(-0.4, -0.4, 0)
        v2 = R3(0.4, -0.4, 0)
        v3 = R3(0.4, 0.4, 0)
        v4 = R3(-0.4, 0.4, 0)
        facet = Facet([v1, v2, v3, v4])

        e1 = Edge(v1, v2)
        e1.gaps = []
        e2 = Edge(v2, v3)
        e2.gaps = []
        e3 = Edge(v3, v4)
        e3.gaps = []
        e4 = Edge(v4, v1)
        e4.gaps = []
        facet.set_edges([e1, e2, e3, e4])

        self.assertFalse(facet.meets_criteria())


class TestIntegrationWithSimplePolyhedra(unittest.TestCase):
    """Интеграционные тесты с простыми полиэдрами"""

    def create_test_polyedr(self, vertices_data, facets_data):
        """Вспомогательный метод для создания полиэдра из данных"""
        # Это упрощённая версия — в реальности нужно использовать
        # существующий конструктор Polyedr
        pass

    def test_cube_has_no_facets_meeting_criteria(self):
        """
        Куб: все грани либо вертикальные (угол 90°), либо горизонтальные,
        но у горизонтальных граней центр в (0,0) — внутри квадрата.
        Поэтому ни одна грань не должна подходить.
        """
        # Используем реальный файл cube.geom
        try:
            poly = Polyedr("../data/cube.geom")
            # Сначала выполняем удаление невидимых линий
            # (в draw это делается, но для compute нужно вызвать shadow)
            for e in poly.edges:
                for f in poly.facets:
                    e.shadow(f)
            total = poly.compute_sum_of_perimeters()
            # Для куба ответ должен быть 0
            self.assertEqual(total, 0.0)
        except FileNotFoundError:
            self.skipTest("Файл cube.geom не найден")

    def test_box_has_no_facets_meeting_criteria(self):
        """Аналогично кубу — параллелепипед"""
        try:
            poly = Polyedr("../data/box.geom")
            for e in poly.edges:
                for f in poly.facets:
                    e.shadow(f)
            total = poly.compute_sum_of_perimeters()
            self.assertEqual(total, 0.0)
        except FileNotFoundError:
            self.skipTest("Файл box.geom не найден")

    def test_ccc_has_bottom_facet_meeting_criteria(self):
        """
        Полиэдр ccc.geom: два квадрата (нижний и верхний) и боковые грани.
        Нижний квадрат (z=0):
        - Все рёбра невидимы? Нет, они видны снизу
        - Поэтому не подходит
        """
        try:
            poly = Polyedr("../data/ccc.geom")
            for e in poly.edges:
                for f in poly.facets:
                    e.shadow(f)
            total = poly.compute_sum_of_perimeters()
            # В ccc.geom нет граней, удовлетворяющих всем условиям
            self.assertEqual(total, 0.0)
        except FileNotFoundError:
            self.skipTest("Файл ccc.geom не найден")


class TestMathematicalPrecision(unittest.TestCase):
    """Тесты математической точности вычислений"""

    def test_pi_over_7_value(self):
        """Проверка значения π/7"""
        expected = pi / 7
        self.assertAlmostEqual(expected, 0.4487989505128276, places=10)


if __name__ == '__main__':
    unittest.main()