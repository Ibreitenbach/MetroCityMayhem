import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__()

        # Appearance
        self.image = pygame.Surface((32, 64)) # Placeholder size
        self.image.fill(pygame.Color('red'))   # Red color for enemies
        self.rect = self.image.get_rect()

        # Position and Movement
        self.pos = pygame.math.Vector2(start_pos_x, start_pos_y)
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 2  # Enemies are a bit slower than the player

        # Stats
        self.health = 50
        self.max_health = self.health # Initialize max_health based on starting health
        self.strength = 8
        self.defense = 3
        self.xp_reward = 10
        self.money_drop = 5

        # AI attributes
        self.detection_radius = 250  # How far the enemy can 'see' the player
        self.attack_range = 40       # How close the enemy needs to be to attack
        self.is_attacking = False    # State flag for attacking
        self.player_ref = player_ref # Reference to the player object
        self.hit_cooldown_timer = 0.0 # For when enemy gets hit

    def update(self, dt, screen_width=None, screen_height=None): # Added screen_width/height for consistent signature with Player
        # Update hit cooldown timer
        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= dt
        else:
            self.hit_cooldown_timer = 0.0

        # AI: Move towards player if in detection_radius and not already attacking (basic version)
        if not self.is_attacking and self.player_ref:
            distance_to_player = self.pos.distance_to(self.player_ref.pos)
            if distance_to_player < self.detection_radius and distance_to_player > self.attack_range: # Chase if in range but not attack range
                if self.player_ref.pos.x < self.pos.x:
                    self.vel.x = -self.speed
                elif self.player_ref.pos.x > self.pos.x:
                    self.vel.x = self.speed
                else:
                    self.vel.x = 0
            elif distance_to_player <= self.attack_range: # In attack range
                self.vel.x = 0 # Stop to attack
                self.is_attacking = True # Simple flag, actual attack logic might be elsewhere or need timer
            else: # Outside detection radius
                self.vel.x = 0
        elif not self.player_ref: # No player reference
             self.vel.x = 0

        # Update position based on velocity
        self.pos += self.vel * dt
        # self.rect.midbottom = (round(self.pos.x), round(self.pos.y)) # Moved after boundary checks

        # Boundary checks for regular enemies
        if stage_width is not None and screen_height is not None:
            half_width = self.rect.width / 2
            # current_pos_y = self.pos.y # Store y before x adjustments affect rect.height for y check

            if self.pos.x < half_width:
                self.pos.x = half_width
                if self.vel.x < 0: self.vel.x = 0
            if self.pos.x > stage_width - half_width:
                self.pos.x = stage_width - half_width
                if self.vel.x > 0: self.vel.x = 0

            # Use current_pos_y for y checks if rect.height could change due to x boundary interactions (unlikely here but good practice)
            # self.rect might not be perfectly synced until after this block, so using self.image.get_height() is safer for sprite's own height
            sprite_height = self.image.get_height()
            if self.pos.y > screen_height:
                self.pos.y = screen_height
                if self.vel.y > 0: self.vel.y = 0 # Stop downward velocity if hit floor
            if self.pos.y < sprite_height:
                self.pos.y = sprite_height # Sprite's bottom cannot go above its own height from screen top
                if self.vel.y < 0: self.vel.y = 0 # Stop upward velocity if hit effective ceiling

        self.rect.midbottom = (round(self.pos.x), round(self.pos.y)) # Re-apply rect after all pos adjustments


class Thug(Enemy):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__(start_pos_x, start_pos_y, player_ref)
        self.image.fill(pygame.Color('lightcoral'))


class Bruiser(Enemy):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__(start_pos_x, start_pos_y, player_ref)

        self.health = 100
        self.max_health = self.health
        self.strength = 12
        self.defense = 5
        self.speed = 1.5
        self.xp_reward = 25
        self.money_drop = 10

        self.image = pygame.Surface((40, 70))
        self.image.fill(pygame.Color('darkred'))

        current_midbottom = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom
