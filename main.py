import sys

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds


class Game:
    def __init__(self):
        pygame.init()
        self.moving_left = False
        self.moving_right = False
        pygame.display.set_caption('untitled game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=15),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/shoot': Animation(load_images('entities/player/shoot')),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (10, 11))

        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')

        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                        self.moving_left = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                        self.moving_right = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_z:
                        self.player.shoot()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                        self.moving_left = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        self.moving_right = False
                    if event.key == pygame.K_z:
                        self.player.shoot()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
