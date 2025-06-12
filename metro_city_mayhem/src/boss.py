import pygame
from src.enemy import Enemy # Bosses are a type of Enemy
from src.projectile import Projectile # For Viper boss

class Boss(Enemy):
    def __init__(self, start_pos_x, start_pos_y, player_ref, health, strength, defense, speed, xp_reward, money_drop, image_path=None, image_color=None, image_size=None):
        super().__init__(start_pos_x, start_pos_y, player_ref) # Call Enemy's init

        # Override or set specific boss stats
        self.health = health
        self.max_health = self.health # Ensure max_health is also set
        self.strength = strength
        self.defense = defense
        self.speed = speed
        self.xp_reward = xp_reward
        self.money_drop = money_drop

        # Boss-specific attributes
        self.special_attack_cooldown_max = 10.0 # Default: 10 seconds cooldown for special
        self.special_attack_cooldown_timer = 0.0
        self.current_state = "idle" # e.g., "idle", "chasing", "attacking", "special_attack_charging", "special_attack_active", "vulnerable"

        # Visuals - Allow customization via parameters
        # Base Enemy class already creates a default surface. We might override it here.
        original_rect_midbottom = self.rect.midbottom # Preserve position from Enemy.__init__

        if image_path:
            # self.image = pygame.image.load(image_path).convert_alpha() # Actual image loading
            # For now, if image_path is provided but not loaded, we don't change the image from super
            pass # Placeholder for now, actual image loading would replace self.image
        elif image_color and image_size:
            self.image = pygame.Surface(image_size)
            self.image.fill(pygame.Color(image_color))
        # else, it will use the default red Enemy image if not overridden by subclass or above logic

        # Update rect if image was changed from the default Enemy image
        if image_path or (image_color and image_size): # Check if image was intended to be changed
            self.rect = self.image.get_rect()
            self.rect.midbottom = original_rect_midbottom # Restore position

        # print(f"Boss {self.__class__.__name__} initialized. State: {self.current_state}, HP: {self.health}")

    def update(self, dt, stage_width, screen_height): # Ensure it takes all params
        if self.special_attack_cooldown_timer > 0:
            self.special_attack_cooldown_timer -= dt
        else:
            self.special_attack_cooldown_timer = 0.0
        # Call Enemy's update. Velocity decisions made in Boss subclass. Enemy applies vel to pos.
        # Enemy.update now also handles basic boundary checks for normal enemies.
        # Bosses will use their own _apply_boundary_checks after super().update()
        super().update(dt, stage_width, screen_height)

        # Example state transition (very basic, to be expanded by subclasses)
        # if self.current_state == "idle":
        #     if self.can_see_player():
        #         self.current_state = "chasing"

        # print(f"Boss {self.__class__.__name__} update. State: {self.current_state}, Cooldown: {self.special_attack_cooldown_timer:.2f}")


    def attempt_special_attack(self):
        if self.special_attack_cooldown_timer <= 0:
            # Logic for special attack would go here or be triggered by state change
            # print(f"Boss {self.__class__.__name__} attempts special attack!")
            self.special_attack_cooldown_timer = self.special_attack_cooldown_max
            # self.current_state = "special_attack_charging" # Example state change
            return True
        return False

    # Placeholder for specific AI logic helper (can_see_player already possible via detection_radius)
    # def can_see_player(self): # Removed player_rect parameter, uses self.player_ref
    #     if self.player_ref:
    #         distance = self.pos.distance_to(self.player_ref.pos)
    #         # detection_radius is inherited from Enemy class
    #         return distance < getattr(self, 'detection_radius', 10000) # Use getattr for safety
    #     return False

    def _apply_boundary_checks(self, stage_width, screen_height):
        half_width = self.rect.width / 2
        if self.pos.x < half_width:
            self.pos.x = half_width
            if self.vel.x < 0: self.vel.x = 0
        elif self.pos.x > stage_width - half_width:
            self.pos.x = stage_width - half_width
            if self.vel.x > 0: self.vel.x = 0

        sprite_height = self.image.get_height()
        if self.pos.y > screen_height: # Fell through floor
            self.pos.y = screen_height
            if self.vel.y > 0: self.vel.y = 0
        if self.pos.y < sprite_height: # Hit ceiling (bottom of sprite at its height from screen top)
             self.pos.y = sprite_height
             if self.vel.y < 0: self.vel.y = 0
        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))


class Spike(Boss):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__(
            start_pos_x, start_pos_y, player_ref,
            health=150, strength=15, defense=5, speed=3.5,
            xp_reward=100, money_drop=50,
            image_color='darkgreen', image_size=(40, 70)
        )
        self.attack_range = 60
        self.punch_cooldown_max = 0.8
        self.punch_cooldown_timer = 0.0
        self.is_punching_now = False
        self.punch_duration = 0.25
        self.punch_timer = 0.0

    def update(self, dt, stage_width, screen_height):
        self.vel.x = 0 # Default to no horizontal movement unless chasing
        if self.punch_cooldown_timer > 0: self.punch_cooldown_timer -= dt

        if self.is_punching_now:
            self.punch_timer -= dt
            if self.punch_timer <=0:
                self.is_punching_now = False
                self.current_state = "idle"
        else:
            distance_to_player = self.pos.distance_to(self.player_ref.pos)
            if distance_to_player < self.attack_range and self.punch_cooldown_timer <= 0:
                self.current_state = "attacking"
                self.is_punching_now = True # This boss's normal attack state
                self.is_attacking = True # Set base Enemy flag for generic attack interactions
                self.punch_timer = self.punch_duration
                self.punch_cooldown_timer = self.punch_cooldown_max
            elif distance_to_player < self.detection_radius:
                self.current_state = "chasing"
                self.is_attacking = False
                if self.player_ref.pos.x < self.pos.x: self.vel.x = -self.speed
                else: self.vel.x = self.speed
            else:
                self.current_state = "idle"
                self.is_attacking = False # Clear base enemy flag

        super().update(dt, stage_width, screen_height)
        self._apply_boundary_checks(stage_width, screen_height)

    def get_hitbox(self):
        if self.is_punching_now:
            hitbox_width = 35
            hitbox_height = 20
            hitbox_y = self.rect.centery - (hitbox_height / 2)
            facing_right = self.player_ref.pos.x > self.pos.x
            if facing_right: hitbox_x = self.rect.right
            else: hitbox_x = self.rect.left - hitbox_width
            return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        return None

class Crusher(Boss):
    def __init__(self, start_pos_x, start_pos_y, player_ref):
        super().__init__(
            start_pos_x, start_pos_y, player_ref,
            health=250, strength=20, defense=8, speed=1.2,
            xp_reward=200, money_drop=100,
            image_color='darkblue', image_size=(60, 80)
        )
        self.stomp_charge_time = 1.2
        self.stomp_duration = 0.6
        self.stomp_aoe_width = 180
        self.stomp_aoe_height = 25 # Relative to Crusher's bottom
        self.stomp_timer = 0.0
        self.stomp_damage = 30 # Overrides base strength for this attack
        self.special_attack_cooldown_max = 7.0 # Uses Boss's timer attribute

    def update(self, dt, stage_width, screen_height):
        self.vel.x = 0 # Default to no horizontal movement
        self.is_attacking = False # Base Enemy flag, set true if special is active

        if self.current_state == "special_attack_charging":
            self.stomp_timer -= dt
            if self.stomp_timer <= 0:
                self.current_state = "special_attack_active"
                self.stomp_timer = self.stomp_duration
                self.is_attacking = True # To allow hitbox check in main
        elif self.current_state == "special_attack_active":
            self.stomp_timer -= dt
            self.is_attacking = True
            if self.stomp_timer <= 0:
                self.current_state = "idle"
                self.special_attack_cooldown_timer = self.special_attack_cooldown_max # Reset main cooldown
        else: # Idle or chasing
            distance_to_player = self.pos.distance_to(self.player_ref.pos)
            # Try to use special attack if off cooldown and player is generally near
            if distance_to_player < self.detection_radius * 1.2 and self.special_attack_cooldown_timer <= 0 :
                self.current_state = "special_attack_charging"
                self.stomp_timer = self.stomp_charge_time
            elif distance_to_player < self.detection_radius: # Normal chase
                self.current_state = "chasing"
                if self.player_ref.pos.x < self.pos.x: self.vel.x = -self.speed
                else: self.vel.x = self.speed
            else:
                self.current_state = "idle"

        super().update(dt, stage_width, screen_height)
        self._apply_boundary_checks(stage_width, screen_height)

    def get_hitbox(self): # For stomp AoE
        if self.current_state == "special_attack_active":
            hitbox_y = self.rect.bottom - self.stomp_aoe_height
            hitbox_x = self.rect.centerx - (self.stomp_aoe_width / 2)
            return pygame.Rect(hitbox_x, hitbox_y, self.stomp_aoe_width, self.stomp_aoe_height)
        return None

class Viper(Boss):
    def __init__(self, start_pos_x, start_pos_y, player_ref, all_sprites_group, projectiles_group):
        super().__init__(
            start_pos_x, start_pos_y, player_ref,
            health=200, strength=18, defense=6, speed=3.2,
            xp_reward=300, money_drop=150,
            image_color='purple', image_size=(45, 65)
        )
        self.melee_attack_range = 70
        self.melee_cooldown_max = 1.2; self.melee_cooldown_timer = 0.0
        self.is_melee_attacking_now = False # Specific to Viper's melee
        self.melee_duration = 0.35; self.melee_timer = 0.0

        self.ranged_attack_range_min = 180
        self.ranged_attack_range_max = 450
        self.special_attack_cooldown_max = 4.0 # Uses Boss's timer for ranged attack

        self.all_sprites = all_sprites_group # For adding projectiles
        self.projectiles = projectiles_group # For adding projectiles

    def update(self, dt, stage_width, screen_height):
        self.vel.x = 0
        self.is_attacking = False # Base Enemy flag, set true if melee is active

        if self.melee_cooldown_timer > 0: self.melee_cooldown_timer -= dt

        if self.is_melee_attacking_now:
            self.melee_timer -= dt
            self.is_attacking = True # Melee is a form of generic attack
            if self.melee_timer <=0:
                self.is_melee_attacking_now = False
                self.current_state = "idle"
        else:
            distance_to_player = self.pos.distance_to(self.player_ref.pos)
            can_shoot = self.ranged_attack_range_min < distance_to_player < self.ranged_attack_range_max

            if can_shoot and self.special_attack_cooldown_timer <= 0:
                self.current_state = "special_attack_active" # Viper's special is shooting
                proj_start_x = self.rect.centerx
                proj_start_y = self.rect.centery
                proj_vel_x = 450
                if self.player_ref.pos.x < self.pos.x: proj_vel_x = -proj_vel_x

                projectile = Projectile(proj_start_x, proj_start_y, proj_vel_x)
                if self.all_sprites is not None: self.all_sprites.add(projectile)
                if self.projectiles is not None: self.projectiles.add(projectile)
                self.special_attack_cooldown_timer = self.special_attack_cooldown_max # Main cooldown used for ranged
            elif distance_to_player < self.melee_attack_range and self.melee_cooldown_timer <= 0:
                self.current_state = "attacking"
                self.is_melee_attacking_now = True
                self.is_attacking = True # Set base flag
                self.melee_timer = self.melee_duration
                self.melee_cooldown_timer = self.melee_cooldown_max
            elif self.current_state not in ["attacking", "special_attack_active"]:
                if distance_to_player < self.detection_radius:
                    self.current_state = "chasing"
                    if self.player_ref.pos.x < self.pos.x: self.vel.x = -self.speed
                    else: self.vel.x = self.speed
                else:
                    self.current_state = "idle"

        super().update(dt, stage_width, screen_height)
        self._apply_boundary_checks(stage_width, screen_height)

    def get_hitbox(self): # For melee attack
        if self.is_melee_attacking_now:
            hitbox_width = 40; hitbox_height = 20
            hitbox_y = self.rect.centery - (hitbox_height / 2)
            facing_right = self.player_ref.pos.x > self.pos.x
            if facing_right: hitbox_x = self.rect.right
            else: hitbox_x = self.rect.left - hitbox_width
            return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        return None
