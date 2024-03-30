from pygame import transform
from pygame.sprite import Sprite
from time import time
from pygame.locals import *
import random, fileinput, time
import src.utils.functions as f
from src.utils.settings import *


class Tank(Sprite):
    def __init__(self, screen, img_filename, speed, pos):
        Sprite.__init__(self)
        self.screen = screen
        self.speed = speed
        self.image = pygame.image.load(img_filename)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.bullets = pygame.sprite.Group()
        self.bullet_time = 0
        self.direction = 0
        self.alive = True

    def shot(self, speed):
        pos = []
        if self.direction == 0:
            pos.append(self.rect.centerx)
            pos.append(self.rect.centery - self.rect.height / 2)

        elif self.direction == 1:
            pos.append(self.rect.centerx + self.rect.width / 2)
            pos.append(self.rect.centery)
        elif self.direction == 2:
            pos.append(self.rect.centerx)
            pos.append(self.rect.centery + self.rect.height / 2)
        else:
            pos.append(self.rect.centerx - self.rect.width / 2)
            pos.append(self.rect.centery)
        self.bullets.add(Bullet(self.screen, speed, pos, self.direction))

    def collision_detect(self, sprite):
        return pygame.sprite.collide_rect(self, sprite)

    def rotate(self, direct):
        if self.direction != direct:
            self.image = transform.rotate(self.image,
                                          (self.direction - direct) * 90)
            self.direction = direct


class PlayerTank(Tank):
    INIT_COORDS = [400, 580]

    def __init__(self, screen, img_filename, speed, shot_sound):

        Tank.__init__(self, screen, img_filename, speed, PlayerTank.INIT_COORDS)
        self.shot_sound = shot_sound
        self.area = screen.get_rect()

    def update(self, time_passed, move, enemy, Map):

        self.rect.centerx += move[0] * self.speed
        self.rect.centery += move[1] * self.speed

        if pygame.sprite.spritecollideany(self, enemy):
            self.rect.centerx -= move[0] * self.speed
            self.rect.centery -= move[1] * self.speed

        if Map.is_collide_with_map(self.rect):
            self.rect.centerx -= move[0] * self.speed
            self.rect.centery -= move[1] * self.speed

        if self.rect.left < 0 or self.rect.right > self.area.right:
            self.rect.centerx -= move[0] * self.speed
        if self.rect.top < 0 or self.rect.bottom > self.area.bottom:
            self.rect.centery -= move[1] * self.speed

        if move[0] > 0:
            self.rotate(1)
        elif move[0] < 0:
            self.rotate(3)
        elif move[1] > 0:
            self.rotate(2)
        elif move[1] < 0:
            self.rotate(0)

        self.bullet_time -= time_passed
        self.bullets.update()
        self.bullets.draw(self.screen)

    def shot(self):
        if self.bullet_time <= 0:
            self.bullet_time = 500
            self.shot_sound.play()
            Tank.shot(self, self.speed + 5)


class EnemyTank(Tank):
    def __init__(self, screen, img_filename, speed, pos):
        Tank.__init__(self, screen, img_filename, speed, pos)
        self.area = screen.get_rect()
        self.distance = 0

    def update(self, time_passed, tanks, Map):
        if self.distance <= 0:
            self.distance = random.randrange(200)
            self.rotate(random.randrange(4))
        else:
            self.distance -= self.speed

        move = [0, 0]
        if self.direction == 0:
            move[1] -= 1
        elif self.direction == 1:
            move[0] += 1
        elif self.direction == 2:
            move[1] += 1
        else:
            move[0] -= 1

        self.rect.centerx += self.speed * move[0]
        self.rect.centery += self.speed * move[1]

        tanks.remove(self)
        if pygame.sprite.spritecollideany(self, tanks):
            self.rect.centerx -= move[0] * self.speed
            self.rect.centery -= move[1] * self.speed
            self.distance = 0
        tanks.add(self)

        if Map.is_collide_with_map(self.rect):
            self.rect.centerx -= move[0] * self.speed
            self.rect.centery -= move[1] * self.speed
            self.distance = 0

        if self.rect.left < 0 or self.rect.right >= self.area.right:
            self.rect.centerx -= move[0] * self.speed
            self.distance = 0
        if self.rect.top < 0 or self.rect.bottom >= self.area.bottom:
            self.rect.centery -= move[1] * self.speed
            self.distance = 0

        self.bullet_time -= time_passed
        self.bullets.update()
        self.bullets.draw(self.screen)

        self.shot()

    def shot(self):
        if self.bullet_time > 0:
            return
        else:
            self.bullet_time = random.randrange(200, 2000)
        Tank.shot(self, self.speed + 1)


class Bullet(Sprite):
    def __init__(self, screen, speed, pos, direction):
        Sprite.__init__(self)
        self.screen = screen
        self.area = screen.get_rect()
        self.speed = speed

        self.direction = direction
        self.image = pygame.image.load(SPRITE_BULLET)

        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):

        if self.direction == 0:
            self.rect.centery -= self.speed
        elif self.direction == 1:
            self.rect.centerx += self.speed
        elif self.direction == 2:
            self.rect.centery += self.speed
        else:
            self.rect.centerx -= self.speed

        if (self.rect.centerx < 0 or self.rect.centerx > self.area.right
                or self.rect.centery < 0
                or self.rect.centery > self.area.bottom):
            self.kill()


class Explosion(Sprite):

    def __init__(self, image, screen, rect, sound, fps=10):
        Sprite.__init__(self)
        self.screen = screen
        self.frame = 0
        self.delay = 1000 / fps
        self.time = 0
        self.tiles = (
            (0, 0, 50, 50),
            (60, 0, 50, 50),
            (124, 0, 50, 50),
            (188, 0, 50, 50),
            (253, 0, 50, 50),
            (316, 0, 50, 50),
            (380, 0, 50, 50),)
        self.image = pygame.image.load(image)
        self.area = pygame.Rect(self.tiles[self.frame])
        self.rect = pygame.Rect(rect)
        sound.play()

    def update(self, time_passed):
        if (time_passed + self.time > self.delay):
            self.frame += 1
            if self.frame >= len(self.tiles):
                self.kill()
            else:
                self.area = pygame.rect.Rect(self.tiles[self.frame])
                self.time = 0
        else:
            self.time += time_passed


class Level():
    def __init__(self, level=1):
        self.level = level
        self.map = Map(SPRITE_BLOCKS)
        self.map.load_map(os.path.join("Maps", str(level) + ".map"))


class Map():
    (BLOCK_EMPTY, BLOCK_BRICK, BLOCK_STEEL, BLOCK_WATER, BLOCK_GRASS,
     BLOCK_FROZE) = range(6)
    DESTRUCTABLE = [BLOCK_BRICK]
    BULLET_STOPPER = (BLOCK_BRICK, BLOCK_STEEL)
    WALL = (BLOCK_BRICK, BLOCK_STEEL, BLOCK_WATER)
    BLOCK_SIZE = 20

    def __init__(self, blocks_filename):
        blocks = pygame.image.load(blocks_filename)
        block_images = [
            blocks.subsurface(0, 0, Map.BLOCK_SIZE, Map.BLOCK_SIZE),
            blocks.subsurface(0, Map.BLOCK_SIZE, Map.BLOCK_SIZE,
                              Map.BLOCK_SIZE),
            blocks.subsurface(Map.BLOCK_SIZE, Map.BLOCK_SIZE, Map.BLOCK_SIZE,
                              Map.BLOCK_SIZE),
            blocks.subsurface(2 * Map.BLOCK_SIZE, 0, Map.BLOCK_SIZE,
                              Map.BLOCK_SIZE),
            blocks.subsurface(3 * Map.BLOCK_SIZE, 0, Map.BLOCK_SIZE,
                              Map.BLOCK_SIZE)
        ]
        self.block_brick = block_images[0]
        self.block_steel = block_images[1]
        self.block_grass = block_images[2]
        self.block_water = block_images[3]
        self.block_water1 = block_images[4]

    def load_map(self, filename):
        self.map = []
        x, y = 0, 0
        for line in fileinput.input(filename):
            for current in line:
                if current == "#":
                    self.map.append((Map.BLOCK_BRICK,
                                     pygame.Rect(x, y, Map.BLOCK_SIZE,
                                                 Map.BLOCK_SIZE)))
                elif current == "@":
                    self.map.append((Map.BLOCK_STEEL,
                                     pygame.Rect(x, y, Map.BLOCK_SIZE,
                                                 Map.BLOCK_SIZE)))
                elif current == "%":
                    self.map.append((Map.BLOCK_GRASS,
                                     pygame.Rect(x, y, Map.BLOCK_SIZE,
                                                 Map.BLOCK_SIZE)))
                elif current == "$":
                    self.map.append((Map.BLOCK_WATER,
                                     pygame.Rect(x, y, Map.BLOCK_SIZE,
                                                 Map.BLOCK_SIZE)))
                x += Map.BLOCK_SIZE
            x = 0
            y += Map.BLOCK_SIZE
        self.update_rects()

    def draw_map(self, screen):
        for block in self.map:
            if block[0] == Map.BLOCK_BRICK:
                screen.blit(self.block_brick, block[1].topleft)
            elif block[0] == Map.BLOCK_STEEL:
                screen.blit(self.block_steel, block[1].topleft)
            elif block[0] == Map.BLOCK_GRASS:
                screen.blit(self.block_grass, block[1].topleft)
            elif block[0] == Map.BLOCK_WATER:
                if random.randrange(1):
                    screen.blit(self.block_water, block[1].topleft)
                else:
                    screen.blit(self.block_water1, block[1].topleft)

    def is_collide_with_map(self, rect):
        for block in self.map:
            if block[0] in Map.WALL:
                if block[1].colliderect(rect):
                    return True
        return False

    def is_bullet_collide_with_map(self, rect):
        index = rect.collidelist(self.block_rects)
        if index == -1:
            return False
        else:
            if self.map[index][0] in Map.DESTRUCTABLE:
                self.map.pop(index)
                self.block_rects.pop(index)
                return True
            elif self.map[index][0] in Map.BULLET_STOPPER:
                return True
            return False

    def update_rects(self):
        self.block_rects = []
        for block in self.map:
            if block[0] in (
                    self.BLOCK_BRICK, self.BLOCK_STEEL, self.BLOCK_WATER,
                    self.BLOCK_GRASS):
                self.block_rects.append(block[1])


class Game:
    def __init__(self, stage=1):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tanks")

        # grupy
        self.tanks, self.player, self.enemies, self.killed = [
            pygame.sprite.Group() for i in range(4)]
        self.data = f.get_data()

        self.shot_sound = pygame.mixer.Sound(SOUND_SHOT)
        self.explosion_sound = pygame.mixer.Sound(SOUND_EXPLOSION)
        self.startgame_sound = pygame.mixer.Sound(SOUND_GAMESTART)
        self.gameover_sound = pygame.mixer.Sound(SOUND_GAMEOVER)
        self.game_sound = pygame.mixer.Sound(SOUND_GAME)
        self.intro_sound = pygame.mixer.music.load(SOUND_INTRO)

        self.stage = stage
        self.level = Level(stage)
        self.killed_count = 0

        self.player_Sprite = PlayerTank(self.screen, SPRITE_PLAYER1, 2.0,
                                        self.shot_sound)
        self.player_Sprite.add(self.tanks, self.player)

    def text_objects(self, text, color, size):
        if size == "small":
            textSurface = pygame.font.Font(
                (os.path.join("fonts", "Stencilgothic.ttf")), 25).render(text,
                                                                         True,
                                                                         color)
        elif size == "large":
            textSurface = pygame.font.Font(
                (os.path.join("fonts", "Stencilgothic.ttf")), 80).render(text,
                                                                         True,
                                                                         color)
        return textSurface, textSurface.get_rect()

    def text_to_button(self, msg, color, buttonx, buttony, buttonwidth,
                       buttonheight, size="small"):
        self.textSurf, self.textRect = self.text_objects(msg, color, size)
        self.textRect.center = (
            (buttonx + (buttonwidth / 2)), buttony + (buttonheight / 2))
        self.screen.blit(self.textSurf, self.textRect)

    def message_to_screen(self, msg, color, y_display=0, size="small"):
        self.textSurf, self.textRect = self.text_objects(msg, color, size)
        self.textRect.center = (DISPLAY_WIDTH / 2), (DISPLAY_HEIGHT /
                                                     2) + y_display
        self.screen.blit(self.textSurf, self.textRect)

    def button(self, text, x, y, width, height, size, inactive_color,
               active_color, action=None):
        cur = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x + width > cur[0] > x and y + height > cur[1] > y:
            pygame.draw.rect(self.screen, active_color, (x, y, width, height))
            if click[0] == 1 and action != None:
                if action == "quit":
                    pygame.quit()
                    quit()
                if action == "play":
                    self.data[0] += 1
                    self.startgame_sound.play()
                    f.write_data(self.data[0], self.data[1])
                    Game().game()

                if action == "static":
                    f.write_data(self.data[0], self.data[1])
                    Game().show_statistic()
        else:
            pygame.draw.rect(self.screen, inactive_color, (x, y, width, height))
        self.text_to_button(text, "#000000", x, y, width, height, size)

    def game_intro(self):
        pygame.mixer.music.play(1)
        intro = True
        while intro:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_ESCAPE]:
                pygame.quit()
                quit()
            self.screen.fill("#000000")
            self.message_to_screen("BATTLE", '#9b9b00', -100, "large")
            self.message_to_screen("CITY", '#9b9b00', 0, "large")
            self.button("play", 150, 500, 100, 50, "small", '#009b00',
                        '#00ff00',
                        "play")
            self.button("QUit", 550, 500, 100, 50, "small", '#9b0000',
                        '#ff0000',
                        "quit")
            self.button("Statistic", 320, 500, 150, 50, "small", "#ffd700",
                        "#ffff00",
                        "static")
            pygame.display.update()
            self.clock.tick(50)

    def show_statistic(self):
        game_over = True
        pygame.mixer.music.play(-1)
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_ESCAPE]:
                pygame.quit()
                quit()
            self.screen.fill("#000000")
            self.message_to_screen(f"Tanks killed {self.data[1]}", '#9b9b00',
                                   -100,
                                   "large")
            self.message_to_screen(f"Starts: {self.data[0]}", '#9b9b00', 0,
                                   "large")
            self.button("Play", 150, 500, 100, 50, "small", '#009b00',
                        '#00ff00',
                        "play")
            self.button("Quit", 550, 500, 100, 50, "small", '#9b0000',
                        '#ff0000',
                        "quit")
            pygame.display.update()
            self.clock.tick(50)

    def won(self):
        game_over = True
        time.sleep(1)
        self.game_sound.stop()
        pygame.mixer.music.play(-1)
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_ESCAPE]:
                pygame.quit()
                quit()
            self.screen.fill("#000000")
            self.message_to_screen("You", '#9b9b00', -100, "large")
            self.message_to_screen("Won!", '#9b9b00', 0, "large")
            self.button("Play", 150, 500, 100, 50, "small", '#009b00',
                        '#00ff00',
                        "play")
            self.button("Quit", 550, 500, 100, 50, "small", '#9b0000',
                        '#ff0000',
                        "quit")
            self.button("Statistic", 320, 500, 150, 50, "small", "#ffd700",
                        "#ffff00",
                        "static")
            pygame.display.update()
            self.clock.tick(50)

    def game_over(self):
        time.sleep(1)
        self.data[1] += self.killed_count
        game_over = True
        pygame.mixer.music.play(-1)
        while game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_ESCAPE]:
                pygame.quit()
                quit()
            self.screen.fill("#000000")
            self.game_sound.stop()
            self.message_to_screen("Game", '#9b9b00', -100, "large")
            self.message_to_screen("Over", '#9b9b00', 0, "large")
            self.button("Play", 150, 500, 100, 50, "small", '#009b00',
                        '#00ff00',
                        "play")
            self.button("Quit", 550, 500, 100, 50, "small", '#9b0000',
                        '#ff0000',
                        "quit")
            self.button("Statistic", 320, 500, 150, 50, "small", "#ffd700",
                        "#ffff00",
                        "static")
            pygame.display.update()
            self.clock.tick(50)

    def game(self):
        game_exit = False
        game_next = False
        game_over = False
        pygame.mixer.music.load(SOUND_GAME)
        pygame.mixer.music.play(-1)

        while not game_exit:
            if game_next is True:
                print(self.data[1], KILL_GOAL)
                if self.stage == LAST_LEVEL:
                    f.write_data(self.data[0], self.data[1])
                    Game().won()
                else:
                    self.startgame_sound.play()
                    f.write_data(self.data[0], self.data[1])
                    Game(self.stage + 1).game()
            elif game_over is True:
                self.game_over()
            if not self.player:
                game_over = True
            time_passed = self.clock.tick(50)
            self.screen.fill("#000000")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_exit = True
            key_pressed = pygame.key.get_pressed()
            if self.player:
                if key_pressed[K_SPACE]:
                    self.player_Sprite.shot()

                if key_pressed[K_UP] or key_pressed[K_w]:
                    self.player_Sprite.update(time_passed, (0, -1),
                                              self.enemies, self.level.map)
                elif key_pressed[K_DOWN] or key_pressed[K_s]:
                    self.player_Sprite.update(time_passed, (0, 1), self.enemies,
                                              self.level.map)
                elif key_pressed[K_LEFT] or key_pressed[K_a]:
                    self.player_Sprite.update(time_passed, (-1, 0),
                                              self.enemies, self.level.map)
                elif key_pressed[K_RIGHT] or key_pressed[K_d]:
                    self.player_Sprite.update(time_passed, (1, 0), self.enemies,
                                              self.level.map)
                elif key_pressed[K_ESCAPE]:
                    game_exit = True
                else:
                    self.player_Sprite.update(time_passed, (0, 0), self.enemies,
                                              self.level.map)
            for die in pygame.sprite.groupcollide(self.enemies,
                                                  self.player_Sprite.bullets,
                                                  False, True):
                self.killed.add(
                    Explosion(SPRITE_EXPLOSION2, self.screen, die.rect,
                              self.explosion_sound))
                die.kill()
                self.killed_count += 1
                self.data[1] += 1

            for enemy in self.enemies.sprites():
                if pygame.sprite.groupcollide(self.player, enemy.bullets, False,
                                              True):
                    self.killed.add(Explosion(SPRITE_EXPLOSION2, self.screen,
                                              self.player_Sprite,
                                              self.explosion_sound))
                    self.player_Sprite.kill()
                    self.gameover_sound.play()

            for bullet in self.player_Sprite.bullets:
                if self.level.map.is_bullet_collide_with_map(bullet.rect):
                    bullet.kill()
            for enemy in self.enemies:
                for bullet in enemy.bullets:
                    if self.level.map.is_bullet_collide_with_map(bullet.rect):
                        bullet.kill()

            if (len(self.enemies) < ENEMIES
                    and self.killed_count <= KILL_GOAL - ENEMIES):
                for i in range(ENEMIES - len(self.enemies)):
                    enemy = (EnemyTank(self.screen, SPRITE_ENEMY, 2.0, [
                        20 + random.randrange(SCREEN_SIZE[0] - 50), 20]))
                    if (not pygame.sprite.spritecollideany(enemy, self.tanks)
                            and not self.level.map.is_collide_with_map(
                                enemy.rect)):
                        enemy.add(self.tanks, self.enemies)

            self.enemies.update(time_passed, self.tanks, self.level.map)
            self.killed.update(time_passed)
            self.tanks.draw(self.screen)
            self.level.map.draw_map(self.screen)

            for ex in self.killed:
                self.screen.blit(ex.image, ex.rect, ex.area)
            if self.killed_count == KILL_GOAL:
                game_next = True
            pygame.display.update()

        pygame.quit()
        f.write_data(self.data[0], self.data[1])
        quit()
