from __future__ import annotations

from collections.abc import Generator
from math import acos, pi, sqrt
from typing import Any, Optional

from src.autoscription.core.logging import Monitoring


class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __str__(self) -> str:
        return f"{self.x:6.1f}, {self.y:6.1f}"

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Point):
            return obj.x == self.x and obj.y == self.y
        else:
            return False

    def distance_to_point(self, p: Point) -> float:
        return sqrt((self.x - p.x) ** 2 + (self.y - p.y) ** 2)

    def faces_line(self, line: tuple[Point, Point]) -> bool:
        return point_faces_edge(line, self)


class Rect:
    # Screen coordinates
    l_top: Point
    r_top: Point
    l_bot: Point
    r_bot: Point
    center: Point
    width: int
    height: int

    def __init__(self, name: str, coordinates: list[int]) -> None:
        self.x, self.y, self.width, self.height = coordinates
        if self.width <= 0:
            self.width = 1
        if self.height <= 0:
            self.height = 1
        # assert self.width > 0
        # assert self.height > 0
        self.name = str(name)
        self.l_top = Point(self.x, self.y)
        self.r_top = Point(self.x + self.width, self.y)
        self.r_bot = Point(self.x + self.width, self.y + self.height)
        self.l_bot = Point(self.x, self.y + self.height)
        self.center = Point(int(self.x + self.width / 2), int(self.y + self.height / 2))

    def __iter__(self) -> Generator[Optional[Point], Any, None]:
        yield self.l_top
        yield self.r_top
        yield self.r_bot
        yield self.l_bot

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rect):
            return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height
        else:
            return False

    def iter_edges(self) -> Generator[tuple[Point, Point], Any, None]:
        yield self.l_top, self.r_top
        yield self.r_top, self.r_bot
        yield self.r_bot, self.l_bot
        yield self.l_bot, self.l_top

    # Gives back a copy of this rectangle
    def copy(self) -> Rect:
        return Rect(self.name, [self.x, self.y, self.width, self.height])

    def is_point_inside_rect(self, point: Point) -> bool:
        return self.l_top.x <= point.x <= self.r_top.x and self.l_top.y <= point.y <= self.l_bot.y

    def align_with_top_edge_of(self, rect: Rect) -> Rect:
        self.l_top.y = self.r_top.y = rect.r_top.y
        self.l_bot.y = self.r_bot.y = self.l_top.y + self.height
        return self

    def overlaps_on_x_axis_with(self, rect: Rect) -> bool:
        return self.copy().align_with_top_edge_of(rect).overlaps_with(rect)

    def overlaps_with(self, rect: Rect) -> bool:
        for corner in rect:
            if corner is not None and self.is_point_inside_rect(corner):
                return True
        for corner in self:
            if corner is not None and rect.is_point_inside_rect(corner):
                return True
        return False

    def distance_to_rect(self, rect: Rect, monitoring: Monitoring) -> dict[str, Any]:
        # 1. see if they overlap
        if self.overlaps_with(rect):
            return {"names": {self.name, rect.name}, "distance": 0}

        # 2. draw a line between rectangles
        line = (self.center, rect.center)

        # 3. find the two edges that intersect the line
        edge1 = None
        edge2 = None
        for edge in self.iter_edges():
            if lines_intersect(edge, line):
                edge1 = edge
                break
        for edge in rect.iter_edges():
            if lines_intersect(edge, line):
                edge2 = edge
                break

        if edge1 is None or edge2 is None:
            monitoring.logger_adapter.warning(f"Failed on rectangle pair: {self}, {rect}")
            monitoring.logger_adapter.warning(f"Edge1: {edge1}, Edge2: {edge2}")
            monitoring.logger_adapter.warning(f"Line: {line}")
            return {"names": {self.name, rect.name}, "distance": float("inf")}

        # 4. find shortest distance between these two edges
        distances = [
            distance_between_edge_and_point(edge1, edge2[0]),
            distance_between_edge_and_point(edge1, edge2[1]),
            distance_between_edge_and_point(edge2, edge1[0]),
            distance_between_edge_and_point(edge2, edge1[1]),
        ]

        return {"names": {self.name, rect.name}, "distance": min(distances)}


def triangle_area_at_points(p1: Point, p2: Point, p3: Point) -> float:
    a = p1.distance_to_point(p2)
    b = p2.distance_to_point(p3)
    c = p1.distance_to_point(p3)
    s = (a + b + c) / float(2)
    area = sqrt(s * (s - a) * (s - b) * (s - c))
    return area


# Finds angle using cos law


def angle(a: float, b: float, c: float) -> float:
    divid = a**2 + b**2 - c**2
    divis = 2 * a * b
    if divis > 0:
        result = float(divid) / divis
        if 1.0 >= result >= -1.0:
            return acos(result)
        return 0
    else:
        return 0


# Checks if point faces edge


def point_faces_edge(edge: tuple[Point, Point], point: Point) -> bool:
    a = edge[0].distance_to_point(edge[1])
    b = edge[0].distance_to_point(point)
    c = edge[1].distance_to_point(point)
    ang1, ang2 = angle(b, a, c), angle(c, a, b)
    if ang1 > pi / 2 or ang2 > pi / 2:
        return False
    return True


def distance_between_points(point1: Point, point2: Point) -> float:
    return point1.distance_to_point(point2)


def distance_between_edge_and_point(edge: tuple[Point, Point], point: Point) -> float:  # edge is a tuple of points
    if point_faces_edge(edge, point):
        area = triangle_area_at_points(edge[0], edge[1], point)
        base = edge[0].distance_to_point(edge[1])
        height = area / (0.5 * base)
        return height
    return min(distance_between_points(edge[0], point), distance_between_points(edge[1], point))


def lines_intersect(line1: tuple[Point, Point], line2: tuple[Point, Point]) -> bool:
    return lines_overlap_on_x_axis(line1, line2) and lines_overlap_on_y_axis(line1, line2)


def lines_overlap_on_x_axis(line1: tuple[Point, Point], line2: tuple[Point, Point]) -> bool:
    (
        x1,
        x2,
    ) = (
        line1[0].x,
        line1[1].x,
    )
    (
        x3,
        x4,
    ) = (
        line2[0].x,
        line2[1].x,
    )
    e1_left, e1_right = min(x1, x2), max(x1, x2)
    e2_left, e2_right = min(x3, x4), max(x3, x4)
    return (
        (e1_left >= e2_left and e1_left <= e2_right)
        or (e1_right >= e2_left and e1_right <= e2_right)
        or (e2_left >= e1_left and e2_left <= e1_right)
        or (e2_right >= e1_left and e2_right <= e1_right)
    )


def lines_overlap_on_y_axis(line1: tuple[Point, Point], line2: tuple[Point, Point]) -> bool:
    (
        y1,
        y2,
    ) = (
        line1[0].y,
        line1[1].y,
    )
    (
        y3,
        y4,
    ) = (
        line2[0].y,
        line2[1].y,
    )
    e1_top, e1_bot = min(y1, y2), max(y1, y2)
    e2_top, e2_bot = min(y3, y4), max(y3, y4)
    return (
        (e1_top >= e2_top and e1_top <= e2_bot)
        or (e1_bot >= e2_top and e1_bot <= e2_bot)
        or (e2_top >= e1_top and e2_top <= e1_bot)
        or (e2_bot >= e1_top and e2_bot <= e1_bot)
    )


def min_rectangles_distances(rectangles: list[Rect], monitoring: Monitoring) -> list[str]:
    min_rect_distances = []
    for rect_a in rectangles:
        min_rect_distance: dict[str, Any] = {"names": {}, "distance": float("inf")}
        for rect_b in rectangles:
            if rect_a != rect_b:
                rect_distance = rect_a.distance_to_rect(rect_b, monitoring)
                if rect_distance["distance"] < min_rect_distance["distance"]:
                    min_rect_distance = rect_distance
        # TODO: CHECK WHY THIS PRODUCES INDEX ERROR (2209124181949, 2023-02-14)
        # TODO: rewrite
        try:
            first_rectangle: str = list(min_rect_distance["names"])[0]  # type: ignore[call-overload]
            second_rectangle: str = list(min_rect_distance["names"])[1]  # type: ignore[call-overload]
            distance: float = round(min_rect_distance["distance"], 2)  # type: ignore[call-overload]
            min_distance: str = (
                "Min distance between " + f"{first_rectangle} and " + f"{second_rectangle}: " + f"{distance}"
            )
            min_rect_distances.append(min_distance)
        except IndexError:
            min_rect_distances.append("Could not find minimum distance")
            continue
    return min_rect_distances
