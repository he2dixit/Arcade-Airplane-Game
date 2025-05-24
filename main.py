import pygame
import random

pygame.init()
pygame.mixer.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Arcade Missile Game")
clock = pygame.time.Clock()
FPS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
game_state = STATE_MENU
score = 0
MISSILE_COOLDOWN = 500
ENEMY_SPAWN_DELAY = 1500
try:
    missile_fire_sound = pygame.mixer.Sound("assets/sounds/missile_fire.wav")
    explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.wav")
    game_over_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    missile_fire_sound = explosion_sound = game_over_sound = None
try:
    pygame.mixer.music.load("assets/sounds/background_music.ogg")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Error loading music: {e}")
def draw_text(surface, text, size, x, y, anchor="center"):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    setattr(text_rect, anchor, (x, y))
    surface.blit(text_surface, text_rect)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/images/player.png").convert_alpha()
        except pygame.error as e:
            print(f"Failed to load player image: {e}")
            self.image = pygame.Surface((50, 30))
            self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 300
        self.lives = 3
        self.last_shot_time = 0
    def update(self, dt, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= int(self.speed * dt)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += int(self.speed * dt)
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)
    def fire_missile(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > MISSILE_COOLDOWN:
            missile = Missile(self.rect.centerx, self.rect.top)
            self.last_shot_time = current_time
            if missile_fire_sound:
                missile_fire_sound.play()
            return missile
        return None
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/images/missile.png").convert_alpha()
        except pygame.error as e:
            print(f"Failed to load missile image: {e}")
            self.image = pygame.Surface((5, 15))
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -500
    def update(self, dt):
        self.rect.y += int(self.speed * dt)
        if self.rect.bottom < 0:
            self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("assets/images/enemy.png").convert_alpha()
        except pygame.error as e:
            print(f"Failed to load enemy image: {e}")
            self.image = pygame.Surface((40, 30))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 150
        self.score_value = 10
    def update(self, dt):
        self.rect.y += int(self.speed * dt)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.frames = [pygame.image.load(f"assets/images/explosion/{i}.png").convert_alpha() for i in range(6)]
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=center)
        self.frame_rate = 50
        self.last_update = pygame.time.get_ticks()
    def update(self, dt):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]
all_sprites = pygame.sprite.Group()
missiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()
explosions = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
last_spawn_time = pygame.time.get_ticks()
running = True
while running:
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = STATE_PLAYING
                    score = 0
                    player.lives = 3
                    all_sprites.empty()
                    missiles.empty()
                    enemies.empty()
                    explosions.empty()
                    player = Player()
                    all_sprites.add(player)
        elif game_state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    missile = player.fire_missile()
                    if missile:
                        all_sprites.add(missile)
                        missiles.add(missile)
        elif game_state == STATE_GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = STATE_PLAYING
                    score = 0
                    player.lives = 3
                    all_sprites.empty()
                    missiles.empty()
                    enemies.empty()
                    explosions.empty()
                    player = Player()
                    all_sprites.add(player)
                elif event.key == pygame.K_ESCAPE:
                    running = False
    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        player.update(dt, keys)
        missiles.update(dt)
        enemies.update(dt)
        explosions.update(dt)
        current_time = pygame.time.get_ticks()
        spawn_interval = max(200, ENEMY_SPAWN_DELAY - score // 10)
        if current_time - last_spawn_time > spawn_interval:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            last_spawn_time = current_time
        hits = pygame.sprite.groupcollide(enemies, missiles, True, True)
        for enemy_hit in hits:
            score += enemy_hit.score_value
            explosion = Explosion(enemy_hit.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if explosion_sound:
                explosion_sound.play()
        player_hits = pygame.sprite.spritecollide(player, enemies, True)
        if player_hits:
            explosion = Explosion(player.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            player.lives -= 1
            if explosion_sound:
                explosion_sound.play()
            if player.lives <= 0:
                game_state = STATE_GAME_OVER
                if game_over_sound:
                    game_over_sound.play()
    screen.fill(BLACK)
    if game_state == STATE_MENU:
        draw_text(screen, "Arcade Missile Game", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, "Press ENTER to Start", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "WASD or Arrows to Move, SPACE to Fire", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    elif game_state == STATE_PLAYING:
        all_sprites.draw(screen)
        draw_text(screen, f"Score: {score}", 25, 10, 10, anchor="topleft")
        draw_text(screen, f"Lives: {player.lives}", 25, SCREEN_WIDTH - 10, 10, anchor="topright")
    elif game_state == STATE_GAME_OVER:
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(screen, f"Final Score: {score}", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(screen, "Press ENTER to Restart", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        draw_text(screen, "Press ESCAPE to Quit", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
    pygame.display.flip()
pygame.quit()