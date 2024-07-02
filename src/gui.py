from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.app import App

import src.constants as constants


class GUI:
    def __init__(self, app: "App"):
        self.app = app
        self.init_bottom_panel()
        self.init_fact_surf()
        self.init_font()

    def init_bottom_panel(self):
        self.bottom_panel = pygame.Surface((self.app.screen_w, self.app.screen_h // 4))
        self.bottom_panel_colour = constants.BLUE
        self.bottom_panel.fill(self.bottom_panel_colour)
        self.bottom_panel_rect = self.bottom_panel.get_rect(
            topleft=(0, self.app.screen_h - self.app.screen_h // 4)
        )

    def init_fact_surf(self):
        self.fact_surf = pygame.Surface(
            (self.app.screen_w, self.app.screen_h // 2), pygame.SRCALPHA
        ).convert_alpha()
        self.fact_colour = constants.PURPLE
        self.fact_surf.fill(self.fact_colour)
        self.fact_rect = self.fact_surf.get_rect(
            center=(
                self.app.screen_w // 2,
                (self.app.screen_h - self.bottom_panel_rect.h) // 2,
            )
        )

    def init_font(self):
        self.font_size = self.app.screen_w // 40
        pygame.font.init()
        self.font = pygame.Font(constants.FONT_PATH, self.font_size)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bottom_panel, self.bottom_panel_rect)
        text = self.font.render(
            (
                f"Constellations completed: {self.app.constellations_completed}"
                f"\nCurrent Time: {self.app.current_time // 1000} seconds"
                f"\nFPS: {self.app.clock.get_fps():.0f}"
            ),
            True,
            constants.WHITE,
        )
        screen.blit(
            text,
            (
                self.app.screen_w // 60,
                self.bottom_panel_rect.centery - text.get_height() // 2,
            ),
        )

    def draw_fact(self, fact: str):
        text = self.font.render(
            fact + "\n\nPress Space to Continue...",
            True,
            constants.WHITE,
            wraplength=self.app.screen_w - self.app.screen_w // 10,
        )
        self.fact_surf.fill(self.fact_colour)
        self.fact_surf.blit(
            text,
            (
                self.fact_rect.centerx - text.get_width() // 2,
                self.fact_rect.centery - text.get_height(),
            ),
        )

    def draw_instructions(self, screen: pygame.Surface):
        text = self.font.render(
            "Drag the reference shape to match the constellation!",
            True,
            constants.GREEN,
        )
        screen.blit(
            text,
            (
                self.app.screen_w // 2 - text.get_width() // 2,
                self.bottom_panel_rect.top - text.get_height(),
            ),
        )
