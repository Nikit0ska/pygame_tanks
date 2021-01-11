import os.path
import pygame
from tanks.constants import PIXEL_RATIO
from tanks.grid import cell_to_screen, get_rect
from tanks.time import delta_time


def load_image(name):
    image = pygame.image.load(os.path.join('data', name))
    rect = image.get_rect()
    return pygame.transform.scale(image, (rect.w * PIXEL_RATIO, rect.h * PIXEL_RATIO))


class SpriteBase(pygame.sprite.Sprite):
    sheet = None

    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = self.sheet
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(x, y)


class GridSprite(SpriteBase):
    char = None
    destroyable = False
    tank_obstacle = True
    shell_obstacle = True

    def __init__(self, grid_x, grid_y, *groups):
        super().__init__(*cell_to_screen(grid_x, grid_y), *groups)


class ConcreteWall(GridSprite):
    sheet = load_image('concrete.png')
    char = '#'


class BrickWall(GridSprite):
    sheet = load_image('brick.png')
    char = '%'
    destroyable = True


class Bush(GridSprite):
    sheet = load_image('bush.png')
    char = '*'
    tank_obstacle = False
    shell_obstacle = False


class Water(GridSprite):
    sheet = load_image('water.png')
    char = '~'
    shell_obstacle = False


class Shell(SpriteBase):
    __img = load_image('shell.png')
    sheet = __img

    def __init__(self, x, y, vector_x, vector_y, *groups):
        size = self.__img.get_size()
        if vector_x < 0:
            x -= size[0] * 1.5
            y -= size[1] / 2
            self.sheet = pygame.transform.rotate(self.__img, 90)
        if vector_y < 0:
            x -= size[0] / 2
            y -= size[1]
        if vector_y > 0:
            x -= size[0] / 2
            self.sheet = pygame.transform.rotate(self.__img, 180)
        if vector_x > 0:
            y -= size[1] / 2
            self.sheet = pygame.transform.rotate(self.__img, -90)
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(vector_x, vector_y)
        super().__init__(x, y, *groups)

    def update(self):
        self.pos += self.velocity / delta_time()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        field = get_rect()

        if self.pos.x > field.right or self.pos.x < field.left or self.pos.y > field.bottom or self.pos.y < field.top:
            self.kill()

        for group in self.groups():
            for sprite in group:
                if sprite is not self:
                    if self.is_collided_with(sprite):
                        if isinstance(sprite, GridSprite):
                            if sprite.destroyable:
                                sprite.kill()
                                self.kill()
                            elif sprite.shell_obstacle:
                                self.kill()
                        elif isinstance(sprite, Shell):
                            self.kill()
                            sprite.kill()

    def is_collided_with(self, sprite):
        return self.rect.colliderect(sprite.rect)
