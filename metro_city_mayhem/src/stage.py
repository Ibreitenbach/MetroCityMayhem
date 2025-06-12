import pygame
# Enemy classes are not directly imported. StageManager receives class references
# through the stage_configurations data.

class StageManager:
    def __init__(self, stage_configurations, screen_height):
        self.stage_configurations = stage_configurations
        self.screen_height = screen_height

        self.current_stage_number = 0
        self.current_stage_data = None
        self.background_surface = None

        self.active_enemies = pygame.sprite.Group() # Enemies managed by StageManager for current stage
        # self.all_stage_sprites = pygame.sprite.Group() # For other potential stage elements
        self.boss = None
        self.is_boss_defeated = False
        self.player_ref = None # To pass to enemies
        self.projectiles_group_ref = None # For Viper

    def load_stage(self, level_number, player, all_sprites_main_group, enemies_main_group, **kwargs): # Added kwargs
        self.player_ref = player
        self.projectiles_group_ref = kwargs.get('projectiles_group_ref') # Get from kwargs

        stage_data_found = None
        for config in self.stage_configurations:
            if config["level_number"] == level_number:
                stage_data_found = config
                break

        if not stage_data_found:
            print(f"Error: Stage with level number {level_number} not found.")
            # Potentially raise an error or handle gracefully
            return False

        self.current_stage_data = stage_data_found
        self.current_stage_number = level_number
        self.is_boss_defeated = False

        # Clear previous stage entities from main groups and StageManager's groups
        for enemy_sprite in self.active_enemies:
            enemy_sprite.kill()
        if self.boss: # Ensure boss is also cleared if it was a separate reference
             if self.boss.alive(): # Check if it wasn't already killed by general enemy clearing
                self.boss.kill()

        self.active_enemies.empty()
        # self.all_stage_sprites.empty()
        self.boss = None

        # Create background surface
        stage_length = self.current_stage_data["length"]
        # Using fallback color, actual image loading would be here
        bg_color = self.current_stage_data.get("background_color", pygame.Color("darkgrey"))
        self.background_surface = pygame.Surface((stage_length, self.screen_height))
        self.background_surface.fill(bg_color)

        # Spawn enemies for the new stage
        for EnemyClass, x_pos, y_pos_config in self.current_stage_data["enemy_placements"]:
            # Assuming y_pos_config is the desired midbottom y, same as player and initial enemies
            enemy = EnemyClass(start_pos_x=x_pos, start_pos_y=y_pos_config, player_ref=player)
            self.active_enemies.add(enemy)
            all_sprites_main_group.add(enemy)
            enemies_main_group.add(enemy)

        # Spawn boss for the new stage
        boss_config = self.current_stage_data.get("boss_data")
        if boss_config:
            BossClass, x_pos, y_pos_config = boss_config
            if BossClass.__name__ == "Viper":
                if not self.projectiles_group_ref:
                    # This is an issue, Viper needs this group.
                    # For now, we'll let it be None, but ideally, this should be guaranteed or handled.
                    print("Warning: Projectiles group not provided to StageManager for Viper boss.")
                self.boss = BossClass(start_pos_x=x_pos, start_pos_y=y_pos_config, player_ref=player,
                                      all_sprites_group=all_sprites_main_group,
                                      projectiles_group=self.projectiles_group_ref)
            else:
                self.boss = BossClass(start_pos_x=x_pos, start_pos_y=y_pos_config, player_ref=player)

            if self.boss: # Add to groups if boss was successfully created
                # self.active_enemies.add(self.boss) # No, active_enemies is for non-bosses for now. Boss is self.boss
                                                # Correction: Bosses should also be in active_enemies if they are to be targeted by player attacks via iteration
                self.active_enemies.add(self.boss) # Add boss to active_enemies for consistent iteration if needed
                all_sprites_main_group.add(self.boss)
                enemies_main_group.add(self.boss) # Bosses are also in the 'enemies' group for player attacks

        print(f"Stage {self.current_stage_number}: '{self.current_stage_data['name']}' loaded.")
        print(f" - Length: {self.current_stage_data['length']}px, Enemies: {len(self.current_stage_data['enemy_placements'])}, Boss: {self.boss.__class__.__name__ if self.boss else 'None'}")

        self.dialogue_to_trigger = None # New attribute for StageManager
        if self.boss and self.current_stage_data.get("boss_dialogue"):
            self.dialogue_to_trigger = self.current_stage_data["boss_dialogue"]
            # Don't start dialogue here, let main.py control game_state change

        return True

    def update(self): # player parameter removed, uses self.player_ref established in load_stage
        if not self.current_stage_data:
            return

        if self.boss and not self.is_boss_defeated:
            if self.boss.health <= 0: # Check if boss health has dropped to zero
                self.is_boss_defeated = True
                print(f"Boss {self.boss.__class__.__name__} defeated in Stage {self.current_stage_number}!")
                # The boss sprite is killed by the main combat loop in main.py when health <= 0.
                # StageManager just updates its flag based on boss's health.

    def check_stage_clear_condition(self, player_current_pos_x):
        if not self.current_stage_data:
            return False

        # Player must reach the end of the stage
        reached_end = player_current_pos_x >= self.current_stage_data["length"]

        # If there's a boss, it must be defeated
        boss_condition_met = True
        if self.current_stage_data.get("boss_data"): # If stage has a boss
            boss_condition_met = self.is_boss_defeated

        if reached_end and boss_condition_met:
            print(f"Stage {self.current_stage_number} clear conditions met!")
            return True
        return False
