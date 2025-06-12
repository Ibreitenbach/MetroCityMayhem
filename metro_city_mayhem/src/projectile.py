import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, velocity_x, color=pygame.Color('magenta'), width=25, height=10): # Slightly larger projectile
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = start_x # Spawn from center
        self.rect.centery = start_y
        self.velocity_x = velocity_x # Pixels per second / dt
        self.damage = 15 # Viper's projectile damage

    def update(self, dt, stage_width, screen_height): # screen_height for consistency, stage_width for boundary
        self.rect.x += self.velocity_x * dt
        if self.rect.right < 0 or self.rect.left > stage_width:
            self.kill()
