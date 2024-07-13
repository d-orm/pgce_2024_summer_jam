from typing import TYPE_CHECKING
import math
import random

import pygame

if TYPE_CHECKING:
    from src.app import App

import src.constants as constants


class Stars:
    def __init__(
        self,
        app: "App",
        star_max_radius: int,
        star_min_radius: int,
        constellation_max_radius: int,
        max_constellation_points: int,
        num_constellation_points: int,
        num_random_points: int,
        max_random_points: int,
    ):
        self.app = app
        self.star_max_radius = star_max_radius
        self.star_min_radius = star_min_radius
        self.constellation_max_radius = constellation_max_radius
        self.max_constellation_points = max_constellation_points
        self.num_constellation_points = max(
            3, min(num_constellation_points, max_constellation_points)
        )
        self.num_random_points = max(3, min(num_random_points, max_random_points))
        self.match_threshold = self.app.screen_w // 50
        self.init_constellation()
        self.init_reference()
        self.init_all_stars()
        self.reset_reference_pos()
        self.init_draw()

    def draw_reference(self, screen: pygame.Surface):
        pygame.draw.rect(
            screen,
            constants.BLACK,
            self.reference_outline_rect,
            border_radius=self.app.screen_w // 24,
        )
        pygame.draw.rect(
            screen,
            constants.WHITE,
            self.reference_outline_rect,
            width=self.app.screen_w // 200,
            border_radius=self.app.screen_w // 24,
        )
        screen.blit(self.reference_surf, self.reference_rect)

    def init_all_stars(self):
        gui = self.app.game.gui
        self.random_points = [
            point
            for point in self.generate_random_points(self.num_random_points)
            if not self.constellation_rect.collidepoint(point)
            and not gui.bottom_panel_rect.collidepoint(point)
        ]
        self.constellation_points = self.move_and_scale_points(
            self.constellation_points,
            self.constellation_center_pos,
            1,
        )
        self.all_points = self.constellation_points + self.random_points
        self.const_brightnesses = [
            random.uniform(0.005, 0.015) for _ in range(len(self.constellation_points))
        ]
        self.const_points_and_brightnesses = [
            (*point, brightness)
            for point, brightness in zip(
                self.constellation_points, self.const_brightnesses
            )
        ]
        self.rand_brightnesses = [
            random.uniform(0.0005, 0.015) for _ in range(len(self.random_points))
        ]
        self.rand_points_and_brightnesses = [
            (*point, brightness)
            for point, brightness in zip(self.random_points, self.rand_brightnesses)
        ]

    def init_draw(self):
        pygame.draw.polygon(
            self.reference_surf,
            (255, 0, 0, 100),
            self.reference_points,
        )
        self.draw_connecting_lines(
            self.reference_surf, self.reference_points, constants.RED
        )

    def init_bg(self):
        self.background_surf = pygame.Surface(
            (
                self.app.screen_size[0],
                self.app.screen_size[1] - self.app.game.gui.bottom_panel_rect.h,
            ),
            pygame.SRCALPHA,
        )
        self.background_surf.fill((0, 0, 0, 0))
        self.background_sizes = [
            random.randint(self.star_min_radius, self.star_max_radius)
            for _ in range(self.num_random_points)
        ]

    def move_points(self, points, new_center):
        dx = new_center[0] - points[0][0]
        dy = new_center[1] - points[0][1]
        return [(point[0] + dx, point[1] + dy) for point in points]

    def init_constellation(self):
        gui = self.app.game.gui
        self.constellation_points = self.generate_random_shape_points(
            (
                self.constellation_max_radius + self.star_max_radius * 2,
                self.constellation_max_radius + self.star_max_radius * 2,
            )
        )
        self.constellation_rect = self.get_rect_from_points(self.constellation_points)
        self.constellation_surf = pygame.Surface(
            (
                self.constellation_rect.w + self.star_max_radius,
                self.constellation_rect.h + self.star_max_radius,
            ),
            pygame.SRCALPHA,
        )
        self.constellation_center_pos = random.randint(
            self.constellation_rect.w // 2,
            self.app.screen_w - self.constellation_rect.w,
        ), random.randint(
            self.constellation_rect.h // 2,
            gui.bottom_panel_rect.top - self.constellation_rect.h,
        )
        self.constellation_rect.center = self.constellation_center_pos

    def init_reference(self):
        gui = self.app.game.gui
        self.reference_points = self.constellation_points.copy()
        self.reference_rect = self.constellation_rect.copy()
        self.reference_surf = self.constellation_surf.copy()
        self.reference_start_pos = (
            self.app.screen_w // 2 - gui.bottom_panel_rect.h // 2,
            gui.bottom_panel_rect.top,
        )
        self.reference_outline_rect = pygame.Rect(
            *self.reference_start_pos, gui.bottom_panel_rect.h, gui.bottom_panel_rect.h
        )

    def draw_reveal_surf(self, screen: pygame.Surface):
        rect = (
            self.constellation_rect.inflate(
                self.star_max_radius * 8, self.star_max_radius * 8
            ),
        )
        pygame.draw.rect(
            screen,
            constants.LIGHT_GREEN,
            rect,
            width=self.app.screen_w // 200,
            border_radius=self.app.screen_w // 24,
        )

    def draw_connecting_lines(
        self, surf: pygame.Surface, points: list[tuple[int, int]], color: tuple
    ):
        num_points = len(points)
        lines = [
            (
                points[i],
                points[(i + 1) % num_points],
            )
            for i in range(num_points)
        ]
        for line in lines:
            pygame.draw.line(surf, color, line[0], line[1], 2)

    def move_reference_pos(self, dx: int, dy: int):
        self.reference_rect.x += dx
        self.reference_rect.y += dy

    def reset_reference_pos(self):
        self.reference_rect.topleft = self.reference_start_pos

    def generate_random_shape_points(
        self, center: tuple[int, int]
    ) -> list[tuple[int, int]]:
        max_radius = self.constellation_max_radius
        n = self.num_constellation_points
        points = []
        angle_increment = 2 * math.pi / n

        for i in range(n):
            radius = random.uniform(max_radius * 0.5, max_radius)
            angle = i * angle_increment + random.uniform(-0.2, 0.2)

            x = center[0] + int(radius * math.cos(angle))
            y = center[1] + int(radius * math.sin(angle))
            points.append((x, y))

        return points

    def get_rect_from_points(self, points: list[tuple[int, int]]) -> pygame.Rect:
        max_y = max(points, key=lambda x: x[1])[1]
        min_y = min(points, key=lambda x: x[1])[1]
        max_x = max(points, key=lambda x: x[0])[0]
        min_x = min(points, key=lambda x: x[0])[0]

        return pygame.Rect(min_x, min_y, max_x + min_x, max_y + min_y)

    def move_and_scale_points(
        self, points: list[tuple[int, int]], new_center: tuple, scale: float
    ) -> list[tuple[int, int]]:
        x_shift = new_center[0] - sum(x for x, y in points) / len(points)
        y_shift = new_center[1] - sum(y for x, y in points) / len(points)

        moved_scaled_points = [
            ((x + x_shift) * scale, (y + y_shift) * scale) for x, y in points
        ]

        return moved_scaled_points

    def generate_random_points(self, n: int) -> list[tuple[int, int]]:
        return [
            (
                float(random.randint(0, self.app.screen_w)),
                float(
                    random.randint(
                        0, self.app.screen_h - self.app.game.gui.bottom_panel_rect.h
                    )
                ),
            )
            for _ in range(n)
        ]

    def shapes_are_matched(self) -> bool:
        distance = math.sqrt(
            (self.reference_rect.centerx - self.constellation_rect.centerx) ** 2
            + (self.reference_rect.centery - self.constellation_rect.centery) ** 2
        )

        return distance <= self.match_threshold

    def draw_points(
        self,
        screen: pygame.Surface,
        points: list[tuple[int, int]],
        sizes: list[int],
        color: tuple,
    ):
        for point, size in zip(points, sizes):
            pygame.draw.circle(
                screen,
                color,
                point,
                size,
            )
