import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__()

        # Appearance
        self.image = pygame.Surface((32, 64)) # Placeholder size
        self.image.fill(pygame.Color('red'))   # Red color for enemies
        self.rect = self.image.get_rect()
        self.original_image = self.image.copy() # Store original image

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

        # Hit Flash Effect
        self.is_flashing = False
        self.flash_timer = 0.0
        self.flash_duration = 0.1 # Duration of the flash in seconds

    def update(self, dt, stage_width=None, screen_height=None): # Renamed screen_width to stage_width for clarity
        # Update hit cooldown timer
        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= dt
        else:
            self.hit_cooldown_timer = 0.0

        # Update flash timer
        if self.is_flashing:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.is_flashing = False
                self.image = self.original_image # Restore original image
        else: # Ensure original image is used if not flashing
            if self.image != self.original_image:
                self.image = self.original_image


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

    def take_damage(self, amount):
        if self.hit_cooldown_timer > 0: # Similar to player's invulnerability, but for taking hits rapidly
            return

        actual_damage = max(1, amount - self.defense) # Enemies also have defense
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0

        self.is_flashing = True
        self.flash_timer = self.flash_duration

        # Create a temporary white version of the enemy's image for flashing
        flash_image_surf = self.original_image.copy()
        flash_image_surf.fill(pygame.Color('white')) # Simple white flash
        self.image = flash_image_surf

        self.hit_cooldown_timer = 0.3 # Short cooldown to prevent instant multi-hits from single attack
        # print(f"{self.__class__.__name__} took {actual_damage} damage, health: {self.health}")


class Thug(Enemy):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__(start_pos_x, start_pos_y, player_ref)
        self.image.fill(pygame.Color('lightcoral'))
        self.original_image = self.image.copy() # Re-assign original_image for Thug


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
        self.original_image = self.image.copy() # Re-assign original_image for Bruiser

        current_midbottom = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom
