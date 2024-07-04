from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from src.app import App

import src.constants as constants


class Button:
    def __init__(
        self,
        app: "App",
        x: int,
        y: int,
        width: int,
        height: int,
        colour: tuple[int, int, int],
        text_colour: tuple[int, int, int],
    ):
        self.app = app
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.text_colour = text_colour
        self.rect = pygame.Rect(x, y, width, height)
        self.font_size = self.app.screen_w // 40
        self.font = pygame.font.Font(constants.FONT_PATH, self.font_size)
        self.clicked = False

    def draw(self, screen: pygame.Surface, text: str):
        pygame.draw.rect(screen, self.colour, self.rect)
        text_surf = self.font.render(text, True, self.text_colour)
        screen.blit(
            text_surf,
            (
                self.rect.centerx - text_surf.get_width() // 2,
                self.rect.centery - text_surf.get_height() // 2,
            ),
        )

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)


class GUI:
    def __init__(self, app: "App"):
        self.app = app
        self.init_bottom_panel()
        self.init_fact_surf()
        self.init_font()
        self.init_buttons()
        self.init_game_complete()

    def init_bottom_panel(self):
        self.bottom_panel = pygame.Surface((self.app.screen_w, self.app.screen_h // 4))
        self.bottom_panel_colour = constants.BLUE
        self.bottom_panel.fill(self.bottom_panel_colour)
        self.bottom_panel_rect = self.bottom_panel.get_rect(
            topleft=(0, self.app.screen_h - self.app.screen_h // 4)
        )

    def init_game_complete(self):
        self.game_complete_surf = pygame.Surface(
            (self.app.screen_w // 2, self.app.screen_h // 3)
        )
        self.game_complete_surf.fill(constants.WHITE)
        self.game_complete_rect = self.game_complete_surf.get_rect(
            center=(self.app.screen_w // 2, self.app.screen_h // 2)
        )
        text_surf = self.font.render(
            "Congratulations!" "",
            True,
            constants.BLACK,
        )
        text_surf_2 = self.font.render(
            "You completed the game!" "",
            True,
            constants.BLACK,
        )
        self.game_complete_surf.blit(
            text_surf,
            (
                self.game_complete_rect.w // 2 - text_surf.get_width() // 2,
                self.game_complete_rect.h // 3 - text_surf.get_height() // 2,
            ),
        )
        self.game_complete_surf.blit(
            text_surf_2,
            (
                self.game_complete_rect.w // 2 - text_surf_2.get_width() // 2,
                self.game_complete_rect.h // 3
                - text_surf_2.get_height() // 2
                + text_surf_2.get_height() * 2,
            ),
        )

    def init_buttons(self):
        self.show_hint_button = Button(
            self.app,
            self.app.screen_w - self.app.screen_w // 4,
            self.bottom_panel_rect.top + self.app.screen_h // 80,
            self.app.screen_w // 5,
            self.app.screen_h // 20,
            constants.GREEN,
            constants.BLACK,
        )
        self.reset_button = Button(
            self.app,
            self.app.screen_w - self.app.screen_w // 4,
            self.bottom_panel_rect.top + self.app.screen_h // 10,
            self.app.screen_w // 5,
            self.app.screen_h // 20,
            constants.BLACK,
            constants.WHITE,
        )

    def init_fact_surf(self):
        self.fact_surf = pygame.Surface(
            (self.app.screen_w, self.app.screen_h // 2), pygame.SRCALPHA
        )
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

    def draw_game_complete(self, screen: pygame.Surface):
        screen.blit(self.game_complete_surf, self.game_complete_rect)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.bottom_panel, self.bottom_panel_rect)
        text = self.font.render(
            (
                f"Constellations completed: {self.app.game.constellations_completed}/{self.app.game.max_level}"
                f"\n\nCurrent Time: {self.app.game.current_time:.0f} seconds"
                # f"\nFPS: {self.app.clock.get_fps():.0f}"
            ),
            True,
            constants.WHITE,
        )
        screen.blit(
            text,
            (
                self.app.screen_w // 100,
                self.bottom_panel_rect.centery - text.get_height() // 2,
            ),
        )
        self.show_hint_button.draw(
            screen, f"Show Hint ({self.app.game.hints_remaining})"
        )
        self.reset_button.draw(screen, "Reset")

    def draw_fact(self, fact: str):
        text = self.font.render(
            fact + "\n\nClick to continue...",
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
            constants.LIGHT_GREEN,
        )
        pygame.draw.rect(
            screen,
            constants.GREEN,
            (
                self.app.screen_w // 2 - text.get_width(),
                self.bottom_panel_rect.top - text.get_height(),
                text.get_width() * 2,
                text.get_height(),
            ),
            border_radius=self.app.screen_w // 200,
        )
        screen.blit(
            text,
            (
                self.app.screen_w // 2 - text.get_width() // 2,
                self.bottom_panel_rect.top - text.get_height(),
            ),
        )
