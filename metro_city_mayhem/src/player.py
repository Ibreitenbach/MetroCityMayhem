import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()

        # Appearance
        self.image = pygame.Surface((32, 64))
        self.image.fill(pygame.Color('blue'))
        self.rect = self.image.get_rect()

        # Position and Movement
        self.pos = pygame.math.Vector2(screen_width / 2, screen_height - self.rect.height / 2)
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.facing_right = True # For attack hitbox direction

        # Combat Attributes
        self.is_punching = False
        self.is_kicking = False
        self.attack_timer = 0.0  # Counts down
        self.attack_duration = 0.3 # Seconds, how long an attack state lasts
        self.invulnerability_timer = 0.0 # For when player gets hit

        # Player Stats
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.strength = 10
        self.defense = 5
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100 # Initial XP needed for level 2
        self.money = 0

    def add_xp(self, amount):
        if self.level >= 99: # Max level cap (optional)
            self.xp = 0 # Or set to max_xp for current level if not progressing further
            return

        self.xp += amount
        print(f"Player gained {amount} XP. Total XP: {self.xp}/{self.xp_to_next_level}")

        while self.xp >= self.xp_to_next_level and self.level < 99: # Check cap in loop condition
            self.level_up()

    def level_up(self):
        if self.level >= 99: # Should not be reached if cap is checked in add_xp's loop
            return

        self.xp -= self.xp_to_next_level # Subtract XP needed for current level, carry over excess
        self.level += 1

        # Increase stats (example increments)
        health_increase = 10
        stamina_increase = 10
        strength_increase = 2
        defense_increase = 1

        self.max_health += health_increase
        self.max_stamina += stamina_increase
        self.strength += strength_increase
        self.defense += defense_increase

        # Heal player fully on level up
        self.health = self.max_health
        self.stamina = self.max_stamina

        # Update XP needed for the next level (example formula)
        if self.level < 99:
            self.xp_to_next_level = int(100 * (self.level ** 1.5)) # Increasingly harder
        else: # Reached max level
            self.xp_to_next_level = 0 # Indicate no more progression
            self.xp = 0 # Optional: Clamp XP to 0 or max for current level

        print(f"LEVEL UP! Player reached Level {self.level}.")
        print(f"  Max Health: {self.max_health}, Max Stamina: {self.max_stamina}")
        print(f"  Strength: {self.strength}, Defense: {self.defense}")
        if self.xp_to_next_level > 0:
            print(f"  XP for next level: {self.xp_to_next_level}")
        else:
            print(f"  Max level reached!")


    def update(self, dt, stage_width, screen_height): # screen_width changed to stage_width
        # Update facing direction based on horizontal velocity
        if self.vel.x > 0:
            self.facing_right = True
        elif self.vel.x < 0:
            self.facing_right = False

        # Attack timer logic
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_punching = False
                self.is_kicking = False
                self.attack_timer = 0.0 # Ensure it's exactly zero

        # Update invulnerability timer
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= dt
        else:
            self.invulnerability_timer = 0.0


        # Update position based on velocity and delta time
        self.pos += self.vel * dt  # self.speed is already incorporated into self.vel by main.py

        # Boundary checks for X (pos.x is center x) - using stage_width
        if self.pos.x < self.rect.width / 2: # Left boundary of stage
            self.pos.x = self.rect.width / 2
        if self.pos.x > stage_width - self.rect.width / 2: # Right boundary of stage
            self.pos.x = stage_width - self.rect.width / 2

        # Boundary checks for Y (pos.y is bottom y) - using screen_height
        # Player's bottom edge cannot go above self.rect.height (player's top aligned with screen top)
        if self.pos.y < self.rect.height:
            self.pos.y = self.rect.height
        # Player's bottom edge cannot go below screen_height (player's bottom aligned with screen bottom)
        if self.pos.y > screen_height:
            self.pos.y = screen_height

        # Update rect based on new position
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))

    def punch(self):
        if not self.is_punching and not self.is_kicking and self.attack_timer <= 0: # Prevent attacking while already attacking or in cooldown
            self.is_punching = True
            self.attack_timer = self.attack_duration
            # Placeholder for punch animation/sound later
            # print("Player punches!") # For debugging

    def kick(self):
        if not self.is_punching and not self.is_kicking and self.attack_timer <= 0: # Prevent attacking while already attacking or in cooldown
            self.is_kicking = True
            self.attack_timer = self.attack_duration
            # Placeholder for kick animation/sound later
            # print("Player kicks!") # For debugging

    def get_hitbox(self):
        if self.is_punching or self.is_kicking:
            hitbox_width = 40
            hitbox_height = 20 # Relative to player's center

            # Hitbox y position: centered with player's own center y
            hitbox_y = self.rect.centery - (hitbox_height / 2)

            if self.facing_right:
                # Hitbox starts at the player's right edge and extends to the right
                hitbox_x = self.rect.right
            else: # Facing left
                # Hitbox starts hitbox_width to the left of player's left edge
                hitbox_x = self.rect.left - hitbox_width

            return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        return None # No hitbox if not attacking
