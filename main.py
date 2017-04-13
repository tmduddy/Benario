import pygame

pygame.init()

# Colors #
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen Dimensions #
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(pygame.sprite.Sprite):

    # Methods #
    def __init__(self):

        super().__init__()

        width = 40
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()

        # Speed Vector #
        self.change_x = 0
        self.change_y = 0

        self.level = None

    def update(self):

        self.calc_gravity()

        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = self.block.left
            elif self.change_x < 0:
                self.rect.left = self.block.right

        self.rect.y += self.change_y

        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = self.block.top
            elif self.change_y < 0:
                self.rect.top = self.block.bottom

            self.change_y = 0

    def calc_gravity(self):
        if self.change_y == 0:
            self.change_y = 1
        else: self.change_y = 0.35

        # check if we're on the ground or not #
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    def go_left(self):
        self.change_x = -6

    def go_right(self):
        self.change_x = 6

    def stop(self):
        self.change_x = 0
### END PLAYER CLASS ###


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        """
        Platform constructor. Assumes constructed with user passing in
        an array of 5 numbers like what's defined at the top of this code.
        """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
### END PLATFORM CLASS ###


class Level():

    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        self.world_shift = 0


    def update(self):
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        screen.fill(WHITE)

        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)

    def shift_world(self, shift_x):
        self.world_shift = shift_x

        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x
### END LEVEL CLASS ###

class Level_01(Level):

    def __init__(self, player):

        Level.__init__(self, player)

        self.level_limit = -1000

        # Width, Height, x, y (x, y of top left pixel)
        level = [[210, 70, 500, 500],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 ]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
### END LEVEL01 CLASS ###

def main():
    ### MAIN GAME LOOP ###

    pygame.init()

    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Benario")

    # create the player
    player = Player()

    level_list = []
    level_list.append(Level_01(player))

    current_level_num = 0
    current_level = level_list[current_level_num]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    # start the loop at true:
    running = True

    # assign the clock
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        active_sprite_list.update()

        current_level.update()

        # If the player gets near the right side, shift the world to the left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # Same, but left side (x)
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)

        # set the event for when the player reaches the end of the level
        # in this case, we go to Level02
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_num < len(level_list)-1:
                current_level_num += 1
                current_level = level_list[current_level_num]
                player.level = current_level

        ### ALL DRAWING CODE GOES HERE ###

        current_level.draw(screen)
        active_sprite_list.draw(screen)

        ### ALL DRAWING CODE GOES ABOVE HERE ###

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()
