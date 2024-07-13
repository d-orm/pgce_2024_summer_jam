from typing import TYPE_CHECKING
import pygame

import random
import time

import src.constants as constants
from src.gui import GUI
from src.stars import Stars
from src.star_facts import STAR_FACTS

if TYPE_CHECKING:
    from src.app import App


class Game:
    def __init__(self, app: "App"):
        self.app = app
        self.gui = GUI(self.app)
        self.start_const_points = 4
        self.start_rand_points = 25
        self.max_level = 42
        self.num_start_hints = 3
        self.max_constellation_points = 8
        self.max_random_points = 100
        self.start_constellation_max_radius = self.app.screen_w // 12
        self.star_min_radius = self.app.screen_w // 400
        self.star_max_radius = self.app.screen_w // 200
        self.const_points_increment = 1
        self.rand_points_increment = 3

        self.constellation_max_radius = self.start_constellation_max_radius
        self.num_const_points = self.start_const_points
        self.num_rand_points = self.start_rand_points
        self.const_complete_sound = pygame.mixer.Sound(
            constants.CONST_COMPLETE_SOUND_PATH
        )
        self.music_started = False

    def draw(self, screen: pygame.Surface):
        screen.fill((0, 0, 0, 0))
        self.gui.draw(screen)
        if not self.game_complete:
            self.stars.draw_reference(screen)

        if self.show_hint or self.constellations_completed < 1 and not self.show_fact:
            self.stars.draw_reveal_surf(screen)
            if self.constellations_completed < 1:
                self.gui.draw_instructions(screen)

        if self.show_fact and not self.game_complete:
            screen.blit(self.gui.fact_surf, self.gui.fact_rect)

        if self.game_complete:
            self.gui.draw_game_complete(screen)

    def update(self):
        self.handle_timer()

        if self.is_dragging and not self.game_complete:
            self.handle_reference_drag()

        if self.stars.shapes_are_matched() and not self.is_dragging:
            self.handle_shape_match()

            if self.continue_pressed:
                self.handle_fact_close()
                self.increment_level()

        elif not self.is_dragging:
            self.stars.reset_reference_pos()

    def reset_level(self):
        self.seen_facts = set()
        self.constellations_completed = 0
        self.hints_remaining = self.num_start_hints
        self.gui.show_hint_button.colour = constants.GREEN
        self.game_complete = False
        self.fact_display_duration = 0
        self.start_time = pygame.time.get_ticks()
        self.num_const_points = self.start_const_points
        self.num_rand_points = self.start_rand_points
        self.constellation_max_radius = self.start_constellation_max_radius

    def init_stars(self):
        self.stars = Stars(
            self.app,
            star_min_radius=self.star_min_radius,
            star_max_radius=self.star_max_radius,
            constellation_max_radius=self.constellation_max_radius,
            max_constellation_points=self.max_constellation_points,
            num_constellation_points=self.num_const_points,
            num_random_points=self.num_rand_points,
            max_random_points=self.max_random_points,
        )

    def init_level(self):
        random.seed(time.time())
        self.init_stars()
        self.start_drag_x = 0
        self.start_drag_y = 0
        self.is_dragging = False
        self.show_fact = False
        self.continue_pressed = False
        self.show_hint = False
        self.fact_start_time = None
        unseen_facts = [fact for fact in STAR_FACTS if fact not in self.seen_facts]
        self.fact = (
            random.choice(unseen_facts)
            if len(self.seen_facts) < len(unseen_facts)
            else random.choice(STAR_FACTS)
        )
        self.seen_facts.add(self.fact)
        self.gui.draw_fact(self.fact)
        self.complete_sound_played = False

    def handle_reference_drag(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.stars.reference_rect.collidepoint(mouse_pos):
            current_mouse_x, current_mouse_y = mouse_pos
            delta_x = current_mouse_x - self.start_drag_x
            delta_y = current_mouse_y - self.start_drag_y
            self.stars.move_reference_pos(delta_x, delta_y)
            self.start_drag_x, self.start_drag_y = mouse_pos

    def handle_hint_click(self):
        if (
            not self.show_hint
            and self.hints_remaining > 0
            and self.constellations_completed > 0
            and not self.game_complete
            and not self.show_fact
        ):
            self.hints_remaining -= 1
            self.show_hint = True
            if self.hints_remaining == 0:
                self.gui.show_hint_button.colour = constants.GREY

    def handle_fact_close(self):
        self.fact_display_duration += pygame.time.get_ticks() - self.fact_start_time

    def handle_shape_match(self):
        if not self.complete_sound_played:
            self.const_complete_sound.play()
            self.complete_sound_played = True
        if not self.show_fact and not self.game_complete:
            self.constellations_completed += 1

        self.show_fact = True
        self.show_hint = False

        if self.fact_start_time is None:
            self.fact_start_time = pygame.time.get_ticks()

    def handle_timer(self):
        current_time = (
            pygame.time.get_ticks() - self.start_time - self.fact_display_duration
        ) / 1000
        self.current_time = current_time if not self.show_fact else self.current_time

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_fact:
                self.continue_pressed = True

            self.is_dragging = True
            self.start_drag_x, self.start_drag_y = event.pos

            if not self.music_started:
                pygame.mixer.music.play(-1)
                self.music_started = True

            if self.gui.show_hint_button.is_clicked(event.pos):
                self.handle_hint_click()

            if self.gui.reset_button.is_clicked(event.pos):
                self.reset_level()
                self.init_level()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

    def increment_level(self):
        if self.constellations_completed >= self.max_level:
            self.game_complete = True
            return

        if self.constellations_completed % 2 == 0:
            self.num_const_points += self.const_points_increment

        self.num_rand_points += self.rand_points_increment

        self.init_level()
