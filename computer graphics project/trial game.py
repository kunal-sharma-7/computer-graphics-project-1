import pygame
import random
import math
import sys
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Evolution Game")
clock = pygame.time.Clock()
WW = 9000
WH = 4000
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WATER_TOP = (15, 110, 180)
WATER_BOTTOM = (0, 50, 120)
player = pygame.image.load("fish.png").convert_alpha()
evolved_image = pygame.image.load("fish_evolved.png").convert_alpha()
enemy_image = pygame.image.load("enemy_fish.png").convert_alpha()
FOOD_COUNT = 100
ENEMY_COUNT = 40
MAX_BUBBLES = 150
def spawn_food():
    return [random.randint(0, WW), random.randint(0, WH)]
def draw_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = WATER_TOP[0] * (1 - ratio) + WATER_BOTTOM[0] * ratio
        g = WATER_TOP[1] * (1 - ratio) + WATER_BOTTOM[1] * ratio
        b = WATER_TOP[2] * (1 - ratio) + WATER_BOTTOM[2] * ratio
        pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))
def draw_button(screen, rect, text, color, text_color):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont(None, 50)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
def wait_for_retry():
    retry_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)
    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        draw_button(screen, retry_rect, "Retry", GREEN, WHITE)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    waiting = False
class Fish:
    def __init__(self):
        self.x = WW // 2
        self.y = WH // 2
        self.angle = 0
        self.normal_speed = 4
        self.dash_speed = 10
        self.dashing = False
        self.dash_timer = 0
        self.food_eaten = 0
        self.level = 1
        self.max_level = 20
        self.health = 100
        self.max_health = 100
        self.image = player
        self.base_scale = 0.015
        self.scale_per_level = 0.004
        self.max_scale = 0.6
        self.scale = self.base_scale
        self.update_hitbox()
        self.evolving = False
        self.evolve_timer = 0
        self.hit_flash = 0
        self.won = False
    def update_hitbox(self):
        width = self.image.get_width() * self.scale
        height = self.image.get_height() * self.scale
        self.radius = min(width, height) / 2
    def update_scale(self):
        self.scale = self.base_scale + (self.level - 1) * self.scale_per_level
        if self.scale > self.max_scale:
            self.scale = self.max_scale
        self.update_hitbox()
    def update(self, keys):
        if self.won or self.health <= 0:
            return
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        length = math.hypot(dx, dy)
        if length != 0:
            dx /= length
            dy /= length
        speed = self.dash_speed if self.dashing else self.normal_speed
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
        self.x += dx * speed
        self.y += dy * speed
        if length != 0:
            target_angle = math.degrees(math.atan2(-dy, dx))
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * 0.2
        self.x = max(0, min(WW, self.x))
        self.y = max(0, min(WH, self.y))
        if random.random() < 0.05 and len(bubbles) < MAX_BUBBLES:
            bubbles.append([self.x, self.y, random.randint(3, 6)])
        if self.evolving:
            self.evolve_timer -= 1
            if self.evolve_timer <= 0:
                self.evolving = False
        if self.hit_flash > 0:
            self.hit_flash -= 1
    def eat_food(self):
        if self.won:
            return
        self.food_eaten += 1
        if self.food_eaten % 5 == 0:
            self.level += 1
            self.update_scale()
        if self.level == 10 and self.image == player:
            self.start_evolution()
        if self.level >= self.max_level:
            self.won = True
    def start_evolution(self):
        self.evolving = True
        self.evolve_timer = 120
        self.image = evolved_image
        self.update_scale()
    def draw(self, screen, camera_x, camera_y):
        rotated = pygame.transform.rotozoom(self.image, self.angle, self.scale)
        rect = rotated.get_rect(center=(self.x - camera_x, self.y - camera_y))
        if self.evolving:
            alpha = int(90 * self.evolve_timer / 120)
            glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (0, 255, 255, alpha), glow.get_rect())
            screen.blit(glow, (rect.x - 20, rect.y - 20))
        screen.blit(rotated, rect)
        font = pygame.font.SysFont(None, 25)
        level_text = font.render(f"Lv {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(self.x - camera_x, self.y - camera_y - self.radius - 10))
        screen.blit(level_text, level_rect)
class EnemyFish:
    def __init__(self):
        self.x = random.randint(0, WW)
        self.y = random.randint(0, WH)
        self.speed = random.uniform(2, 3)
        self.level = random.randint(1, 15)
        self.scale = 0.02 + 0.01 * self.level
        self.image = enemy_image
        self.update_hitbox()
    def update_hitbox(self):
        width = self.image.get_width() * self.scale
        height = self.image.get_height() * self.scale
        self.radius = min(width, height) / 2
    def update(self, player: Fish):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 400:
            if self.level < player.level:  # flee
                dx /= dist
                dy /= dist
                self.x -= dx * self.speed * 1.2
                self.y -= dy * self.speed * 1.2
            else:
                dx /= dist
                dy /= dist
                self.x += dx * self.speed
                self.y += dy * self.speed
        else:
            self.x += random.uniform(-1, 1) * self.speed
            self.y += random.uniform(-1, 1) * self.speed
        self.x = max(0, min(WW, self.x))
        self.y = max(0, min(WH, self.y))
    def draw(self, screen, camera_x, camera_y):
        rotated = pygame.transform.rotozoom(self.image, 0, self.scale)
        rect = rotated.get_rect(center=(self.x - camera_x, self.y - camera_y))
        screen.blit(rotated, rect)
        font = pygame.font.SysFont(None, 20)
        level_text = font.render(f"Lv {self.level}", True, RED)
        level_rect = level_text.get_rect(center=(self.x - camera_x, self.y - camera_y - self.radius - 10))
        screen.blit(level_text, level_rect)
def create_game():
    return Fish(), [EnemyFish() for _ in range(ENEMY_COUNT)], [spawn_food() for _ in range(FOOD_COUNT)]
while True:
    player, enemies, foods = create_game()
    bubbles = []
    running = True
    while running:
        clock.tick(60)
        camera_x = max(0, min(WW - WIDTH, player.x - WIDTH // 2))
        camera_y = max(0, min(WH - HEIGHT, player.y - HEIGHT // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not player.dashing:
                player.dashing = True
                player.dash_timer = 20
        keys = pygame.key.get_pressed()
        player.update(keys)
        for food in foods[:]:
            if math.hypot(player.x - food[0], player.y - food[1]) < player.radius:
                foods.remove(food)
                player.eat_food()
                foods.append(spawn_food())
        for enemy in enemies[:]:
            enemy.update(player)
            dist = math.hypot(player.x - enemy.x, player.y - enemy.y)
            if dist < player.radius + enemy.radius:
                if player.level > enemy.level:
                    player.food_eaten += 1
                    if player.food_eaten % 5 == 0:
                        player.level += 1
                        player.update_scale()
                    enemies.remove(enemy)
                else:
                    player.health -= 10
                    player.hit_flash = 5
        draw_background()
        for food in foods:
            pygame.draw.circle(screen, (255, 200, 0),
                               (int(food[0] - camera_x), int(food[1] - camera_y)), 5)
        for bubble in bubbles[:]:
            bubble[1] -= 2
            bubble[2] -= 0.1
            if bubble[2] <= 0:
                bubbles.remove(bubble)
            else:
                pygame.draw.circle(screen, WHITE,
                                   (int(bubble[0] - camera_x), int(bubble[1] - camera_y)),
                                   int(bubble[2]), 1)
        for enemy in enemies:
            enemy.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        font = pygame.font.SysFont(None, 30)
        ui_text = font.render(f"Food: {player.food_eaten}  Health: {player.health}", True, WHITE)
        screen.blit(ui_text, (20, 20))
        if player.hit_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 100))
            screen.blit(flash, (0, 0))
        pygame.display.flip()
        if player.won or player.health <= 0:
            running = False
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    font = pygame.font.SysFont(None, 80)
    if player.won:
        text = font.render("You Beat the Game!", True, (255, 255, 0))
    else:
        text = font.render("Game Over!", True, RED)
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.delay(500)
    wait_for_retry()