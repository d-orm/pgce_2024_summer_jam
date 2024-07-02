import pygame

import asyncio
import random
import time

import src.constants as constants
from src.gui import GUI
from src.stars import Stars
from src.star_facts import STAR_FACTS


class App:
    def __init__(self):
        self.screen_size = self.screen_w, self.screen_h = constants.SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Constellations")
        self.clock = pygame.time.Clock()
        self.gui = GUI(self)
        self.num_const_points = 5
        self.num_rand_points = 50
        self.seen_facts = set()
        self.init_level(self.num_const_points, self.num_rand_points)
        self.constellations_completed = 0
        self.running = True

    def init_level(self, num_constellation_points: int, num_random_points: int):
        random.seed(time.time())
        self.stars = Stars(
            self,
            star_min_radius=self.screen_w // 400,
            star_max_radius=self.screen_w // 200,
            constellation_max_radius=self.screen_w // 12,
            max_constellation_points=21,
            num_constellation_points=num_constellation_points,
            num_random_points=num_random_points,
            max_random_points=750,
        )
        self.level_start_time = pygame.time.get_ticks()
        self.start_drag_x = 0
        self.start_drag_y = 0
        self.is_dragging = False
        self.show_fact = False
        self.continue_pressed = False
        self.show_hint = False
        unseen_facts = [fact for fact in STAR_FACTS if fact not in self.seen_facts]
        self.fact = (
            random.choice(unseen_facts)
            if len(self.seen_facts) < len(unseen_facts)
            else random.choice(STAR_FACTS)
        )
        self.seen_facts.add(self.fact)
        self.gui.draw_fact(self.fact)

    def handle_reference_drag(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.stars.reference_rect.collidepoint(mouse_pos):
            current_mouse_x, current_mouse_y = mouse_pos
            delta_x = current_mouse_x - self.start_drag_x
            delta_y = current_mouse_y - self.start_drag_y
            self.stars.move_reference_pos(delta_x, delta_y)
            self.start_drag_x, self.start_drag_y = mouse_pos

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.is_dragging = True
                    self.start_drag_x, self.start_drag_y = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.show_fact:
                        self.continue_pressed = True

            current_time = pygame.time.get_ticks() - self.level_start_time
            self.current_time = (
                current_time if not self.show_fact else self.current_time
            )

            self.stars.draw(self.screen)
            self.gui.draw(self.screen)
            self.stars.draw_reference(self.screen)

            if self.is_dragging:
                self.handle_reference_drag()

            if self.stars.shapes_are_matched() and not self.is_dragging:
                if not self.show_fact:
                    self.constellations_completed += 1
                self.show_fact = True
                self.show_hint = False
                if self.continue_pressed:
                    if self.constellations_completed % 2 == 0:
                        self.num_const_points += 1
                    self.num_rand_points += 25
                    self.continue_pressed = False
                    self.show_fact = False
                    self.init_level(self.num_const_points, self.num_rand_points)

            elif not self.is_dragging:
                self.stars.reset_reference_pos()

            if (
                self.show_hint
                or self.constellations_completed < 1
                and not self.show_fact
            ):
                self.stars.draw_reveal_surf(self.screen)
                self.gui.draw_instructions(self.screen)

            if self.show_fact:
                self.screen.blit(self.gui.fact_surf, self.gui.fact_rect)

            pygame.display.flip()
            self.clock.tick()
            await asyncio.sleep(0)
