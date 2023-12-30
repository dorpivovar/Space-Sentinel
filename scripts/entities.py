import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.animation_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rect_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True

                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True

                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.velocity[1] = min(5, self.velocity[1] + 0.1)  # падение

        if self.collisions['down'] and self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                     (self.pos[0] - offset[0] + self.animation_offset[0],
                      self.pos[1] - offset[1] + self.animation_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.is_shooting = False

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
            # self.size = (10, 11)
        elif self.is_shooting:
            self.set_action('shoot')
            self.size = (10, 10)
        else:
            self.set_action('idle')
            self.size = (10, 11)

    def jump(self):
        if self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5

    def shoot(self):
        if self.is_shooting:
            self.is_shooting = False
        else:
            self.is_shooting = True

    # def shooting(self, bullets_group):
    #     if not self.is_shooting:
    #         bullet = Bullet(self.rect.centerx, self.rect.y)  # Создание пули в позиции игрока
    #         bullets_group.add(bullet)


# class Bullet:
#     def __init__(self, game, pos):
#         self.game = game
#         # self.type = e_type
#         self.pos = list(pos)
#         # self.size = size
#         self.image = self.game.assets['bullet']
#         self.rect = self.image.img().get_rect()
#         self.speed = 7
#
#     def move(self):
#         self.rect.y -= self.speed
#
#     def update(self, surface):
#         surface.blit(self.image.img(), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5  # Скорость пули

    def update(self):
        self.rect.y -= self.speed  # Движение пули вверх

        # Если пуля выходит за границы экрана, уничтожаем её
        if self.rect.bottom < 0:
            self.kill()
