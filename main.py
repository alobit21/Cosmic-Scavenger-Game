# pyrefly: ignore [missing-import]
import pygame
import sys
import random
import asyncio

# --- CONSTANTS ---
# (Rubric: Proper use of constants where applicable)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- ASSETS DICTIONARY ---
ASSETS = {}

# --- CLASSES ---

class GameObject(pygame.sprite.Sprite):
    """
    Base class for all visible objects in the game.
    Demonstrates Inheritance.
    """
    def __init__(self, x, y, image_key):
        super().__init__()
        self.image = ASSETS[image_key]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y

    def update(self):
        # To be overridden by subclasses (Polymorphism)
        pass


class Player(GameObject):
    """
    The player's spaceship.
    Demonstrates Inheritance and Encapsulation.
    """
    def __init__(self, x, y):
        # Initialize the parent class (GameObject)
        super().__init__(x, y, 'player')
        # Adjust so x, y is the bottom center
        self.rect.bottom = y
        self.speed = 5
        self.health = 3
        self.shoot_timer = 0
        
    def update(self):
        """
        Handles player movement (Keyboard & Touch/Mouse) and keeps them on screen.
        """
        # Keyboard controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            
        # Mobile Touch / Mouse controls
        if pygame.mouse.get_pressed()[0]: # If screen is touched / clicked
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Instantly snap the ship's X position to the finger for faster navigation!
            self.rect.centerx = mouse_x
            
        # Prevent player from going off screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot(self):
        """Creates and returns a new Laser object."""
        return Laser(self.rect.centerx, self.rect.top)


class Laser(GameObject):
    """
    Projectile fired by the player.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 'laser')
        self.rect.bottom = y
        self.speed = 7

    def update(self):
        # Lasers move up the screen
        self.rect.y -= self.speed
        # If it goes off the top of the screen, kill it to save memory
        if self.rect.bottom < 0:
            self.kill()


class Enemy(GameObject):
    """
    Base enemy class. Falls straight down.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 'enemy')
        self.speed = random.randint(2, 5)

    def update(self):
        # Enemies fall down
        self.rect.y += self.speed
        
        # If it falls off the bottom, remove it
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class ZigZagEnemy(Enemy):
    """
    Demonstrates Polymorphism. Overrides the update method to move in a zig-zag.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = ASSETS['enemy_zigzag'] # Use the zigzag image instead
        self.direction = 1 # 1 for right, -1 for left
        self.x_speed = 3

    def update(self):
        # Still falls down using parent speed
        self.rect.y += self.speed
        
        # But also moves side to side
        self.rect.x += self.x_speed * self.direction
        
        # Bounce off screen edges
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1
            
        # If it falls off the bottom, remove it
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class GameManager:
    """
    Manages the game state, main loop, and sprite groups.
    Demonstrates meaningful class design.
    """
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init() # Using .ogg files now for WebAssembly compatibility!
        self.font = pygame.font.SysFont(None, 36)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cosmic Scavenger")
        
        # Load Assets
        ASSETS['player'] = pygame.image.load("assets/player.png").convert_alpha()
        ASSETS['enemy'] = pygame.image.load("assets/enemy.png").convert_alpha()
        ASSETS['enemy_zigzag'] = pygame.image.load("assets/enemy_zigzag.png").convert_alpha()
        ASSETS['laser'] = pygame.image.load("assets/laser.png").convert_alpha()
        
        # Background
        self.bg_image = pygame.image.load("assets/background.png").convert()
        # Scale background to fit screen
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load Sounds (Now using .ogg which is completely web-safe)
        self.sound_enabled = True
        self.shoot_sound = pygame.mixer.Sound("assets/shoot.ogg")
        self.shoot_sound.set_volume(0.3)
        self.explosion_sound = pygame.mixer.Sound("assets/explosion.ogg")
        self.explosion_sound.set_volume(0.3)
        
        # UI Buttons
        self.sound_btn = Button(SCREEN_WIDTH - 160, 10, 150, 35, "Sound: ON", (100, 100, 100))
        self.restart_btn = Button(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT//2 + 40, 150, 45, "RESTART", GREEN)
        
        self.clock = pygame.time.Clock()
        self.is_playing = True
        self.score = 0
        self.level = 1
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        
        # Initialize Player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
        self.all_sprites.add(self.player)

    def spawn_enemy(self):
        # Spawn an enemy at a random X position at the top
        x = random.randint(0, SCREEN_WIDTH - 30)
        
        # Speed increases slightly with level
        speed_boost = self.level // 2
        
        # 30% chance to spawn a ZigZagEnemy (Polymorphism in action!)
        if random.random() < 0.3:
            enemy = ZigZagEnemy(x, -30)
            enemy.speed += speed_boost
            enemy.x_speed += speed_boost
        else:
            enemy = Enemy(x, -30)
            enemy.speed += speed_boost
            
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def reset_game(self):
        """Resets the game state after a game over."""
        self.score = 0
        self.level = 1
        self.player.health = 3
        self.player.rect.centerx = SCREEN_WIDTH // 2
        
        # Clear enemies and lasers
        for enemy in self.enemies:
            enemy.kill()
        for laser in self.lasers:
            laser.kill()

    def handle_events(self):
        """Process keyboard/mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_playing = False
                
            elif event.type == pygame.KEYDOWN:
                if self.player.health > 0:
                    if event.key == pygame.K_SPACE:
                        # Shoot laser
                        if self.sound_enabled:
                            self.shoot_sound.play()
                        laser = self.player.shoot()
                        self.all_sprites.add(laser)
                        self.lasers.add(laser)
                else:
                    # Game Over controls
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.is_playing = False
                        
            # Mobile Button Taps
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check Sound Button
                if self.sound_btn.is_clicked(event.pos):
                    self.sound_enabled = not self.sound_enabled
                    self.sound_btn.text = "Sound: ON" if self.sound_enabled else "Sound: OFF"
                
                # Check Restart Button on Game Over
                if self.player.health <= 0:
                    if self.restart_btn.is_clicked(event.pos):
                        self.reset_game()

    def check_collisions(self):
        """Handle interactions between objects."""
        # check if lasers hit enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.lasers, True, True)
        for hit in hits:
            if self.sound_enabled:
                self.explosion_sound.play()
            self.score += 10  # Increase score
            # Level up every 100 points
            if self.score > 0 and self.score % 100 == 0:
                self.level += 1
            
        # check if enemies hit player. "True" destroys the enemy upon hit
        crashes = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if crashes:
            if self.sound_enabled:
                self.explosion_sound.play()
            self.player.health -= 1
            print(f"Player hit! Health: {self.player.health}")

    def draw_ui(self):
        """Draws the score, level, and health on the screen."""
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        # Health turns red if it's 1
        health_color = GREEN if self.player.health > 1 else RED
        health_text = self.font.render(f"Health: {self.player.health}", True, health_color)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(health_text, (10, 90))
        
        # Draw sound toggle button
        self.sound_btn.draw(self.screen)
        
        if self.player.health <= 0:
            game_over_text = self.font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
            self.screen.blit(game_over_text, text_rect)
            # Draw restart button
            self.restart_btn.draw(self.screen)

    async def run(self):
        """The main game loop."""
        enemy_spawn_timer = 0
        
        while self.is_playing:
            self.clock.tick(FPS) # Control the frame rate
            
            self.handle_events()
            
            # Only update game objects if player is alive
            if self.player.health > 0:
                # Mobile Auto-Shoot (fires a laser every 20 frames)
                self.player.shoot_timer += 1
                if self.player.shoot_timer > 20:
                    if self.sound_enabled:
                        self.shoot_sound.play()
                    laser = self.player.shoot()
                    self.all_sprites.add(laser)
                    self.lasers.add(laser)
                    self.player.shoot_timer = 0
                    
                # Spawn enemy faster based on level
                # Base spawn rate is 60 frames. Min spawn rate is 20 frames.
                spawn_rate = max(20, 60 - (self.level * 5))
                
                enemy_spawn_timer += 1
                if enemy_spawn_timer > spawn_rate: 
                    self.spawn_enemy()
                    enemy_spawn_timer = 0
                
                self.all_sprites.update()
                self.check_collisions()
            
            # Drawing
            self.screen.blit(self.bg_image, (0, 0)) # Draw Background
            self.all_sprites.draw(self.screen)
            self.draw_ui()
            
            pygame.display.flip()
            await asyncio.sleep(0)  # Required for pygbag / web hosting
            
        pygame.quit()
        sys.exit()


# --- START GAME ---
async def main():
    game = GameManager()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
