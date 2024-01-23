import sys
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap


class Game:
    def __init__(self):
        pygame.init()
        self.moving_left = False
        self.moving_right = False
        pygame.display.set_caption('Space Sentinel')
        self.screen = pygame.display.set_mode((640,
                                               480))
        self.display = pygame.Surface((320,
                                       240))
        self.current_level = None
        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': load_image('background.png'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'),
                                    img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'),
                                   img_dur=15),
            'spawners': load_images('tiles/spawners'),
            'player/idle': Animation(load_images('entities/player/idle'),
                                     img_dur=6),
            'player/run': Animation(load_images('entities/player/run'),
                                    img_dur=15),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/shoot': Animation(load_images('entities/player/shoot')),
            'bullet': load_image('entities/bullet.png'),
        }

        self.player = Player(self, (50, 50),
                             (10, 11))

        self.bullet = pygame.image.load('data/images/entities/bullet.png').convert_alpha()
        self.start_screen_bg = pygame.image.load('data/images/start_screen_background.png').convert()
        self.bullets = list()
        self.level_chosen = False

        self.tilemap = Tilemap(self,
                               tile_size=16)
        self.load_level(1)

    def show_start_screen(self):
        font = pygame.font.Font(None,
                                36)
        text = font.render("Choose a Level: 1, 2, or 3",
                           True,
                           (255, 255, 255))
        text_rect = text.get_rect(center=(320,
                                          240))
        self.screen.blit(self.start_screen_bg,
                         (0, 0))

        self.screen.blit(text,
                         text_rect)
        pygame.display.flip()

        self.level_chosen = False
        while not self.level_chosen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.current_level = 0
                        self.level_chosen = True
                    elif event.key == pygame.K_2:
                        self.current_level = 1
                        self.level_chosen = True
                    elif event.key == pygame.K_3:
                        self.current_level = 2
                        self.level_chosen = True

    def complete_game(self):
        font = pygame.font.Font(None,
                                36)
        text = font.render("Game Complete",
                           True,
                           (255, 255, 255))
        text_rect = text.get_rect(center=(320,
                                          240))
        self.screen.blit(self.start_screen_bg,
                         (0, 0))

        self.screen.blit(text,
                         text_rect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.enemies = list()
        for spawner in self.tilemap.extract([('spawners', 0),
                                             ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self,
                                          spawner['pos'],
                                          (10, 10)))

        self.scroll = [0, 0]

    def is_dead(self, player,
                level,
                bullets):
        if player.pos[1] > 600:
            self.kill_player(level,
                             bullets)

    def kill_player(self,
                    level,
                    bullets):

        self.load_level(level)
        bullets.clear()

    def run(self):
        self.show_start_screen()  # Показываем стартовый экран

        # Если выбран уровень, загружаем его
        if self.current_level is not None:
            self.load_level(self.current_level)

        while True:
            if (self.current_level == 0 and self.player.pos[0] >= 1008 and self.player.pos[1] == 501
                    and self.player.pos[0] <= 1046):
                self.current_level = 1
                self.load_level(self.current_level)
            if (self.current_level == 1 and self.player.pos[0] >= 1008 and self.player.pos[1] == 309 and
                    self.player.pos[0] <= 1046):
                self.current_level = 2
                self.load_level(self.current_level)
            if (self.current_level == 2 and self.player.pos[0] >= 1136 and self.player.pos[1] == 213 and
                    self.player.pos[0] <= 1142):
                self.complete_game()

            self.is_dead(self.player,
                         self.current_level,
                         self.bullets)
            self.display.blit(pygame.transform.scale(self.assets['background'], (640, 480)),
                              (0, 0))

            self.scroll[0] += ((self.player.rect().centerx
                                - self.display.get_width()
                                / 2 - self.scroll[0])
                               / 30)
            self.scroll[1] += ((self.player.rect().centery
                                - self.display.get_height()
                                / 2 - self.scroll[1])
                               / 30)
            render_scroll = (int(self.scroll[0]),
                             int(self.scroll[1]))

            self.tilemap.render(self.display,
                                offset=render_scroll)

            for enemy in self.enemies.copy():
                enemy.update(self.tilemap,
                             (0, 0))
                enemy.render(self.display,
                             offset=render_scroll)

            self.player.update(self.tilemap,
                               (self.movement[1]
                                - self.movement[0], 0))
            self.player.render(self.display,
                               offset=render_scroll)

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
                    if event.key == pygame.K_ESCAPE:
                        self.show_start_screen()
                        self.kill_player(self.current_level, self.bullets)

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
                bullets_to_remove = list()

                for i, bullet in enumerate(self.bullets):
                    flip = bullet[1] == -1
                    bullet[0].x += 3 * bullet[1]
                    bullet_rect = pygame.Rect(bullet[0].x,
                                              bullet[0].y,
                                              self.bullet.get_width(),
                                              self.bullet.get_height())
                    self.display.blit(pygame.transform.flip(self.bullet, flip,
                                                            False), (bullet[0].x,
                                                                     bullet[0].y))
                    if bullet[0].x > (640 / 2) or bullet[0].x < 0:
                        bullets_to_remove.append(i)

                    for enemy in self.enemies:
                        if bullet_rect.colliderect(enemy.rect()):
                            self.enemies.remove(enemy)
                            bullets_to_remove.append(i)
                            break

                for index in sorted(bullets_to_remove,
                                    reverse=True):
                    del self.bullets[index]

            self.screen.blit(pygame.transform.scale(self.display,
                                                    self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().run()
