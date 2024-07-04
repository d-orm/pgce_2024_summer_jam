import asyncio

import pygame

import src.constants as constants
from src.game import Game


class App:
    def __init__(self):
        self.screen_size = self.screen_w, self.screen_h = constants.SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Constellations")
        self.clock = pygame.time.Clock()
        self.game = Game(self)
        self.game.reset_level()
        self.game.init_level()
        self.running = True

    async def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    self.running = False
                self.game.handle_events(event)

            self.game.update()
            self.game.draw(self.screen)

            pygame.display.flip()
            self.clock.tick()
            await asyncio.sleep(0)
