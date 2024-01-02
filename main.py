import sys
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=15),
            'spawners': load_images('tiles/spawners'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=15),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/shoot': Animation(load_images('entities/player/shoot')),
            'bullet': load_image('entities/bullet.png'),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.player = Player(self, (50, 50), (10, 11))

        self.bullet = pygame.image.load('data/images/entities/bullet.png').convert_alpha()
        self.bullets = list()

        self.tilemap = Tilemap(self, tile_size=16)
        self.load_level(0)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = list()
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (10, 10)))

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

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)

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
                        if self.player.flip:
                            self.bullets.append([
                                self.bullet.get_rect(top=self.player.pos[1] - render_scroll[1],
                                                     left=self.player.pos[0] - render_scroll[0] - 15), -1])
                        else:
                            self.bullets.append([
                                self.bullet.get_rect(top=self.player.pos[1] - render_scroll[1],
                                                     left=self.player.pos[0] - render_scroll[0] + 15), 1])
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                        self.moving_left = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        self.moving_right = False
                    if event.key == pygame.K_z:
                        self.player.shoot()
            if self.bullets:
                for (i, bullet) in enumerate(self.bullets):
                    flip = False
                    if bullet[1] == -1:
                        flip = True
                    else:
                        flip = False
                    bullet[0].x += 3 * bullet[1]
                    self.display.blit(pygame.transform.flip(self.bullet, flip, False),
                                      (bullet[0].x, bullet[0].y))
                    if bullet[0].x > (640 / 2) or bullet[0].x < 0:
                        self.bullets.pop(i)
                    # print(bullet[0].x)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
