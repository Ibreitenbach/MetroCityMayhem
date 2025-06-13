import pygame
import pygame.font # For text rendering
import random # For screen shake

# Initialize Pygame
pygame.init()
pygame.font.init() # Explicitly initialize font module
pygame.mixer.init() # Initialize the mixer

from src.player import Player
from src.enemy import Thug, Bruiser
from src.boss import Boss, Spike, Crusher, Viper
from src.stage import StageManager
from src.camera import Camera
from src.dialogue import DialogueBox # Import DialogueBox

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Metro City Mayhem")

# Create Player instance
player = Player(SCREEN_WIDTH, SCREEN_HEIGHT)

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group() # For all enemy types, including bosses
projectiles = pygame.sprite.Group() # For Viper's projectiles
all_sprites.add(player) # Add player to all_sprites group

# UI Font and Health Bar settings
UI_FONT = pygame.font.Font(None, 28)
HEALTH_BAR_HEIGHT = 7
HEALTH_BAR_OFFSET_Y = 10
INTRO_FONT = pygame.font.Font(None, 48) # Larger font for scenes
MENU_FONT_TITLE = pygame.font.Font(None, 74)
MENU_FONT_OPTIONS = pygame.font.Font(None, 54)
SCENE_TEXT_COLOR = pygame.Color('white')
MENU_TEXT_COLOR = pygame.Color('white')
MENU_HIGHLIGHT_COLOR = pygame.Color('yellow')
SCENE_TEXT_PADDING = 50

# Helper Function for Health Bar
def draw_health_bar(surface, current_health, max_health, bar_rect):
    if current_health < 0: current_health = 0
    if max_health == 0: fill_ratio = 0
    else: fill_ratio = current_health / max_health
    bar_width = bar_rect.width * fill_ratio
    outline_color = pygame.Color('grey')
    fill_color = pygame.Color('green')
    if fill_ratio < 0.6: fill_color = pygame.Color('yellow')
    if fill_ratio < 0.3: fill_color = pygame.Color('red')
    pygame.draw.rect(surface, outline_color, bar_rect, 1)
    if bar_width > 0: pygame.draw.rect(surface, fill_color, (bar_rect.x, bar_rect.y, bar_width, bar_rect.height))

# Scene Data
INTRO_SCENES_DATA = [
    {"id": 1, "image_color": pygame.Color("darkblue"), "text_lines": ["Metro City... A place of neon lights and dark alleys."]},
    {"id": 2, "image_color": pygame.Color("darkred"), "text_lines": ["One day, your best friend, Sam,", "was snatched by the notorious Viper Gang!"]},
    {"id": 3, "image_color": pygame.Color("darkslateblue"), "text_lines": ["You must fight your way through their turf,", "defeat their enforcers, and rescue Sam!"]},
    {"id": 4, "image_color": pygame.Color("black"), "text_lines": ["Your journey begins now..."]}
]

ENDING_SCENES_DATA = [
    {"id": 1, "image_color": pygame.Color("teal"), "text_lines": ["With Viper defeated, the gang's hold on the city crumbles."]},
    {"id": 2, "image_color": pygame.Color("skyblue"), "text_lines": ["You find Sam, shaken but safe.", "'You came for me!' they exclaim."]},
    {"id": 3, "image_color": pygame.Color("steelblue"), "text_lines": ["Together, you walk out into the dawn,", "leaving the mayhem behind."]},
    {"id": 4, "image_color": pygame.Color("black"), "text_lines": ["THE END"]}
]

# Helper function to draw scenes
def draw_scene(surface, scene_data, font, text_color, padding):
    surface.fill(scene_data["image_color"])
    y_offset = padding
    for i, line in enumerate(scene_data["text_lines"]):
        text_surface = font.render(line, True, text_color)
        text_rect = text_surface.get_rect(centerx=surface.get_width() / 2, y=y_offset + i * (font.get_linesize() * 0.8) )
        surface.blit(text_surface, text_rect)

    hint_font = pygame.font.Font(None, 28)
    hint_surface = hint_font.render("Press Enter to continue...", True, text_color)
    hint_rect = hint_surface.get_rect(centerx=surface.get_width() / 2, bottom=surface.get_height() - padding / 2)
    surface.blit(hint_surface, hint_rect)

# Stage Configurations (ensure this uses the correct Boss classes from src.boss)
STAGE_CONFIGURATIONS = [
    {
        "level_number": 1, "name": "Downtown Streets", "length": 3000,
        "background_image_path": "assets/sprites/placeholder_bg_stage1.png", "background_color": pygame.Color('dimgray'),
        "enemy_placements": [
            (Thug, 800, SCREEN_HEIGHT), (Thug, 1000, SCREEN_HEIGHT), (Thug, 1200, SCREEN_HEIGHT),
            (Thug, 1500, SCREEN_HEIGHT), (Thug, 1700, SCREEN_HEIGHT), (Thug, 2000, SCREEN_HEIGHT),
            (Thug, 2200, SCREEN_HEIGHT), (Thug, 2400, SCREEN_HEIGHT), (Thug, 2600, SCREEN_HEIGHT),
            (Thug, 2800, SCREEN_HEIGHT),
        ],
        "boss_data": (Spike, 2900, SCREEN_HEIGHT),
        "boss_dialogue": {"name": "Spike", "lines": ["Well, well, what have we here?", "You won't get past me to find your friend, runt!"]}
    },
    {
        "level_number": 2, "name": "Waterfront Warehouse", "length": 2500,
        "background_image_path": "assets/sprites/placeholder_bg_stage2.png", "background_color": pygame.Color('darkslategray'),
        "enemy_placements": [
            (Thug, 700, SCREEN_HEIGHT), (Bruiser, 900, SCREEN_HEIGHT), (Thug, 1100, SCREEN_HEIGHT),
            (Bruiser, 1300, SCREEN_HEIGHT), (Thug, 1500, SCREEN_HEIGHT), (Bruiser, 1700, SCREEN_HEIGHT),
            (Thug, 1900, SCREEN_HEIGHT), (Thug, 2100, SCREEN_HEIGHT),
        ],
        "boss_data": (Crusher, 2400, SCREEN_HEIGHT),
        "boss_dialogue": {"name": "Crusher", "lines": ["Hmph. The Boss said to crush anyone who came snooping around here.", "Guess that means you!"]}
    },
    {
        "level_number": 3, "name": "Viper Gang HQ", "length": 4000,
        "background_image_path": "assets/sprites/placeholder_bg_stage3.png", "background_color": pygame.Color('indigo'),
        "enemy_placements": [
            (Thug, 800, SCREEN_HEIGHT), (Bruiser, 1000, SCREEN_HEIGHT), (Thug, 1200, SCREEN_HEIGHT),
            (Thug, 1500, SCREEN_HEIGHT), (Bruiser, 1800, SCREEN_HEIGHT), (Thug, 2100, SCREEN_HEIGHT),
            (Bruiser, 2400, SCREEN_HEIGHT), (Thug, 2700, SCREEN_HEIGHT), (Thug, 3000, SCREEN_HEIGHT),
            (Bruiser, 3300, SCREEN_HEIGHT), (Thug, 3600, SCREEN_HEIGHT),
        ],
        "boss_data": (Viper, 3900, SCREEN_HEIGHT),
        "boss_dialogue": {"name": "Viper", "lines": ["So, you finally made it. Impressive... for a nobody.", "Sam is here, yes. But you'll never leave this place alive, let alone with them!"]}
    }
]

# Instantiate Managers and Game State
stage_manager = StageManager(stage_configurations=STAGE_CONFIGURATIONS, screen_height=SCREEN_HEIGHT)
camera = Camera(screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
dialogue_box = DialogueBox(SCREEN_WIDTH, SCREEN_HEIGHT, font=UI_FONT)
game_state = "MENU" # Initial game state changed to MENU
current_scene_index = 0
selected_menu_option = 0 # 0 for Start Game, 1 for Quit
selected_game_over_option = 0 # 0 for Retry, 1 for Quit to Menu
background_surface = None # Will be set after intro

# Sound Effects
sound_effects = {}
sound_files = {
    "punch": "assets/audio/punch.wav",
    "kick": "assets/audio/kick.wav",
    "take_damage": "assets/audio/take_damage.wav",
    "enemy_defeated": "assets/audio/enemy_defeated.wav",
    "item_pickup": "assets/audio/item_pickup.wav"
}

for effect_name, file_path in sound_files.items():
    try:
        sound_effects[effect_name] = pygame.mixer.Sound(file_path)
    except pygame.error as e:
        print(f"Warning: Could not load sound '{effect_name}' from {file_path}. Error: {e}")
        sound_effects[effect_name] = None # Store None if loading fails

# Pass sound_effects to Player instance
player.sound_effects = sound_effects


# Background Music Functions
def play_menu_music():
    try:
        pygame.mixer.music.load("assets/audio/menu_music.ogg")
        pygame.mixer.music.play(-1) # Play in a loop
    except pygame.error as e:
        print(f"Warning: Could not load menu music. Error: {e}")

def play_stage_music(stage_number):
    stop_music() # Stop any currently playing music
    music_file = f"assets/audio/stage{stage_number}_music.ogg"
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1) # Play in a loop
    except pygame.error as e:
        print(f"Warning: Could not load music for stage {stage_number} from {music_file}. Error: {e}")

def stop_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload() # Unload to free resources, good practice


# Adjust Player's Initial Position (Done after intro before playing)
# player.pos.x = 100
# player.pos.y = SCREEN_HEIGHT
# player.rect.midbottom = (round(player.pos.x), round(player.pos.y))
# player.vel.x = 0
# player.vel.y = 0

# Main Menu Drawing Function
def draw_main_menu(surface, selected_option):
    surface.fill(pygame.Color('black')) # Background for menu

    # Title
    title_text = MENU_FONT_TITLE.render("Metro City Mayhem", True, MENU_TEXT_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
    surface.blit(title_text, title_rect)

    # Menu Options
    options = ["Start Game", "Quit"]
    for i, option_text in enumerate(options):
        color = MENU_HIGHLIGHT_COLOR if i == selected_option else MENU_TEXT_COLOR
        text_surf = MENU_FONT_OPTIONS.render(option_text, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 60))
        surface.blit(text_surf, text_rect)

# Game Over Screen Drawing Function
def draw_game_over_screen(surface, selected_option):
    surface.fill(pygame.Color('black')) # Background for game over

    # Title
    title_text = MENU_FONT_TITLE.render("Game Over", True, MENU_TEXT_COLOR)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
    surface.blit(title_text, title_rect)

    # Menu Options
    options = ["Retry", "Quit to Menu"]
    for i, option_text in enumerate(options):
        color = MENU_HIGHLIGHT_COLOR if i == selected_option else MENU_TEXT_COLOR
        text_surf = MENU_FONT_OPTIONS.render(option_text, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 60))
        surface.blit(text_surf, text_rect)


# Initial music call for MENU state
play_menu_music()

# Main game loop
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60) / 1000.0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_UP:
                    selected_menu_option = (selected_menu_option - 1) % 2 # 2 options
                elif event.key == pygame.K_DOWN:
                    selected_menu_option = (selected_menu_option + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_menu_option == 0: # Start Game
                        game_state = "INTRO"
                        current_scene_index = 0 # Start intro from the beginning
                        # Menu music is already playing, it will transition to stage music after intro
                    elif selected_menu_option == 1: # Quit
                        running = False
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_UP:
                    selected_game_over_option = (selected_game_over_option - 1) % 2
                elif event.key == pygame.K_DOWN:
                    selected_game_over_option = (selected_game_over_option + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if selected_game_over_option == 0: # Retry
                        player.health = player.max_health
                        player.stamina = player.max_stamina # Also reset stamina
                        # Reset player position and reload current stage
                        current_stage_num_to_retry = stage_manager.current_stage_number if stage_manager.current_stage_number is not None else 1
                        if not stage_manager.load_stage(current_stage_num_to_retry, player, all_sprites, enemies, projectiles_group_ref=projectiles):
                            print(f"Failed to reload stage {current_stage_num_to_retry}. Returning to menu.")
                            game_state = "MENU"
                            play_menu_music()
                        else:
                            background_surface = stage_manager.background_surface
                            player.pos.x = 100 # Reset to start of stage
                            player.pos.y = SCREEN_HEIGHT
                            player.rect.midbottom = (round(player.pos.x), round(player.pos.y))
                            player.vel.x = player.vel.y = 0
                            game_state = "PLAYING"
                            play_stage_music(current_stage_num_to_retry)
                    elif selected_game_over_option == 1: # Quit to Menu
                        game_state = "MENU"
                        selected_menu_option = 0 # Reset menu selection
                        play_menu_music()
            elif game_state == "INTRO":
                if event.key == pygame.K_RETURN:
                    current_scene_index += 1
                    if current_scene_index >= len(INTRO_SCENES_DATA):
                        game_state = "PLAYING"
                        current_scene_index = 0 # Reset for potential future use
                        # Load stage 1 and play its music
                        if not stage_manager.load_stage(1, player, all_sprites, enemies, projectiles_group_ref=projectiles):
                            print("Failed to load initial stage. Exiting.")
                            running = False
                        else:
                            background_surface = stage_manager.background_surface
                            player.pos.x = 100
                            player.pos.y = SCREEN_HEIGHT
                            player.rect.midbottom = (round(player.pos.x), round(player.pos.y))
                            player.vel.x = player.vel.y = 0
                            play_stage_music(1) # Play stage 1 music
                    # print(f"Intro scene {current_scene_index}")
            elif game_state == "BOSS_DIALOGUE" and dialogue_box.is_showing:
                if event.key == pygame.K_RETURN:
                    if not dialogue_box.next_page():
                        game_state = "PLAYING"
                        # if stage_manager.boss: stage_manager.boss.current_state = "idle"
            elif game_state == "ENDING":
                if event.key == pygame.K_RETURN:
                    current_scene_index += 1
                    if current_scene_index >= len(ENDING_SCENES_DATA):
                        stop_music() # Stop music before quitting
                        running = False # End of game after ending sequence
                    # print(f"Ending scene {current_scene_index}")

            if game_state == "PLAYING": # Moved this block inside KEYDOWN check for PLAYING state
                if event.key == pygame.K_j: player.punch()
                if event.key == pygame.K_k: player.kick()

    # Get pressed keys for movement (polled continuously)
    keys = pygame.key.get_pressed() # Get keys regardless of state, but apply movement only if PLAYING

    # --- Update section based on game_state ---
    if game_state == "MENU" or game_state == "GAME_OVER":
        # No specific updates needed for menu or game over beyond event handling
        pass
    elif game_state == "PLAYING":
        player.vel.x = 0
        player.vel.y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.vel.x = -player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.vel.x = player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: player.vel.y = -player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player.vel.y = player.speed

        if stage_manager.current_stage_data:
            current_stage_length = stage_manager.current_stage_data["length"]
            all_sprites.update(dt, current_stage_length, SCREEN_HEIGHT)
            projectiles.update(dt, current_stage_length, SCREEN_HEIGHT)
        else: # Fallback if no stage is loaded (should not happen after initial load)
            all_sprites.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT) # Use SCREEN_WIDTH as fallback stage length
            projectiles.update(dt, SCREEN_WIDTH, SCREEN_HEIGHT)

        stage_manager.update()
        if stage_manager.current_stage_data: # Ensure stage_length is valid
            camera.update(target_sprite_rect=player.rect, stage_length=stage_manager.current_stage_data["length"], dt=dt)
        else: # Fallback if no stage data (e.g. before first load)
            camera.update(target_sprite_rect=player.rect, stage_length=SCREEN_WIDTH, dt=dt)


        # Combat Logic
        player_hitbox = player.get_hitbox()
        player_hitbox = player.get_hitbox()
        if player_hitbox:
            for enemy_hit in enemies: # This includes regular enemies and bosses
                if hasattr(enemy_hit, 'hit_cooldown_timer') and enemy_hit.hit_cooldown_timer <= 0: # Check if enemy can be hit again
                    if enemy_hit.rect.colliderect(player_hitbox):
                        damage_dealt = player.strength # Player's base strength
                        enemy_hit.take_damage(damage_dealt) # New way
                        if isinstance(enemy_hit, Boss):
                            camera.start_shake(intensity=8, duration=0.3) # Stronger shake for boss hits
                        else: # Regular enemy hit
                            camera.start_shake(intensity=3, duration=0.1) # Minor shake for regular enemy

        # Player taking damage from normal enemies
        for enemy_sprite in enemies:
            if not isinstance(enemy_sprite, Boss) and hasattr(enemy_sprite, 'is_attacking') and enemy_sprite.is_attacking:
                if enemy_sprite.rect.colliderect(player.rect):
                    if player.invulnerability_timer <= 0:
                        damage_taken = enemy_sprite.strength
                        player.take_damage(damage_taken)
                        camera.start_shake(intensity=5, duration=0.2) # Shake when player takes damage

        # Player taking damage from Boss
        if stage_manager.boss and stage_manager.boss.alive():
            boss_instance = stage_manager.boss
            boss_hitbox = boss_instance.get_hitbox() if hasattr(boss_instance, 'get_hitbox') else None

            if boss_hitbox and player.rect.colliderect(boss_hitbox):
                if player.invulnerability_timer <= 0:
                    boss_attack_damage = boss_instance.strength
                    if isinstance(boss_instance, Crusher) and boss_instance.current_state == "special_attack_active":
                        boss_attack_damage = boss_instance.stomp_damage

                    player.take_damage(boss_attack_damage)
                    camera.start_shake(intensity=7, duration=0.25) # Stronger shake for boss attacks on player

        # Player taking damage from projectiles
        for proj in projectiles:
            if proj.rect.colliderect(player.rect):
                if player.invulnerability_timer <= 0:
                    player.take_damage(proj.damage)
                    camera.start_shake(intensity=4, duration=0.15) # Shake for projectile hits
                    proj.kill()

        # Enemy defeat logic
        for enemy_defeated_sprite in list(enemies): # Iterate over a copy for safe removal
            if enemy_defeated_sprite.health <= 0:
                player.add_xp(enemy_defeated_sprite.xp_reward)
                player.money += getattr(enemy_defeated_sprite, 'money_drop', 5)
                print(f"{enemy_defeated_sprite.__class__.__name__} defeated! Player Money: ${player.money}")
                if sound_effects["enemy_defeated"]: sound_effects["enemy_defeated"].play()
                enemy_defeated_sprite.kill()

        if player.health <= 0 and game_state == "PLAYING": # Ensure this only triggers from PLAYING
            print("GAME OVER")
            stop_music() # Stop stage music
            game_state = "GAME_OVER"
            selected_game_over_option = 0 # Reset game over menu selection
            # Optional: play a game over sound effect here
            # if sound_effects["game_over_jingle"]: sound_effects["game_over_jingle"].play()

        if stage_manager.dialogue_to_trigger and not dialogue_box.is_showing:
            dialogue_data = stage_manager.dialogue_to_trigger
            dialogue_box.start_dialogue(dialogue_data["name"], dialogue_data["lines"])
            stage_manager.dialogue_to_trigger = None
            game_state = "BOSS_DIALOGUE"
            # if stage_manager.boss: stage_manager.boss.current_state = "paused_for_dialogue" # Optional pause

    elif game_state == "BOSS_DIALOGUE":
        # Minimal updates, mainly for input handling via event loop
        pass

    # Stage Transition Logic (Only if playing)
    if game_state == "PLAYING" and stage_manager.current_stage_data and stage_manager.check_stage_clear_condition(player.pos.x):
        current_level_num = stage_manager.current_stage_number
        next_level_num = current_level_num + 1
        next_stage_exists = any(config["level_number"] == next_level_num for config in STAGE_CONFIGURATIONS)
        if next_stage_exists:
            if stage_manager.load_stage(next_level_num, player, all_sprites, enemies, projectiles_group_ref=projectiles):
                background_surface = stage_manager.background_surface
                player.pos.x = 100; player.pos.y = SCREEN_HEIGHT
                player.rect.midbottom = (round(player.pos.x), round(player.pos.y))
                player.vel.x = 0; player.vel.y = 0
                play_stage_music(next_level_num) # Play music for the new stage
                if stage_manager.current_stage_data: camera.update(player.rect, stage_manager.current_stage_data["length"], dt)
            else:
                print(f"Failed to load Stage {next_level_num}. Ending game.")
                stop_music() # Stop music if loading fails
                running = False
        else: # No next stage exists
            print("Congratulations! Final boss defeated, triggering ENDING.")
            game_state = "ENDING"
            current_scene_index = 0 # Reset for ending scenes
            play_menu_music() # Or a specific victory/ending music if available

    # --- Rendering ---
    screen.fill(pygame.Color('black')) # Default background

    if game_state == "MENU":
        draw_main_menu(screen, selected_menu_option)
    elif game_state == "GAME_OVER":
        draw_game_over_screen(screen, selected_game_over_option)
    elif game_state == "INTRO":
        if current_scene_index < len(INTRO_SCENES_DATA):
            draw_scene(screen, INTRO_SCENES_DATA[current_scene_index], INTRO_FONT, SCENE_TEXT_COLOR, SCENE_TEXT_PADDING)
    elif game_state == "PLAYING" or game_state == "BOSS_DIALOGUE": # Draw game world if playing or dialogue overlay
        if background_surface:
            screen.blit(background_surface, camera.get_background_blit_rect(background_surface.get_rect()))

        # Draw all sprites (player, enemies, projectiles)
        # The .image attribute of each sprite will be the correct one (normal or flashed)
        # due to their own update() methods.
        for sprite_in_all in all_sprites:
            screen.blit(sprite_in_all.image, camera.apply_to_sprite(sprite_in_all))

        # Draw health bars for non-boss enemies
        for enemy in enemies:
            if stage_manager.boss and enemy == stage_manager.boss: continue # Boss health bar is drawn separately
            enemy_health_bar_base_rect = pygame.Rect(enemy.rect.x, enemy.rect.top - HEALTH_BAR_OFFSET_Y - HEALTH_BAR_HEIGHT, enemy.rect.width, HEALTH_BAR_HEIGHT)
            draw_health_bar(screen, enemy.health, enemy.max_health, camera.apply_to_rect(enemy_health_bar_base_rect))

        # HUD Drawing (Player stats, Stage info)
        player_hud_health_bar_rect = pygame.Rect(10, 10, 150, 20)
        draw_health_bar(screen, player.health, player.max_health, player_hud_health_bar_rect)
        player_hud_stamina_bar_rect = pygame.Rect(10, 35, 130, 15)
        draw_health_bar(screen, player.stamina, player.max_stamina, player_hud_stamina_bar_rect)
        money_text = UI_FONT.render(f"Money: ${player.money}", True, pygame.Color('white'))
        screen.blit(money_text, (10, 60))
        xp_text = UI_FONT.render(f"XP: {player.xp} / {player.xp_to_next_level}", True, pygame.Color('white'))
        screen.blit(xp_text, (10, 85))
        stage_name_text = stage_manager.current_stage_data['name'] if stage_manager.current_stage_data else "Loading..."
        stage_text = UI_FONT.render(f"Stage: {stage_manager.current_stage_number} - {stage_name_text}", True, pygame.Color('white'))
        screen.blit(stage_text, (10, 110))

        if stage_manager.boss and stage_manager.boss.alive(): # Boss HUD Health Bar
            boss_name_text = UI_FONT.render(f"{stage_manager.boss.__class__.__name__}", True, pygame.Color('white'))
            boss_name_rect = boss_name_text.get_rect(centerx=SCREEN_WIDTH / 2, y=10)
            screen.blit(boss_name_text, boss_name_rect)
            boss_health_bar_width = SCREEN_WIDTH * 0.6
            boss_health_bar_height = 25
            boss_health_bar_x = (SCREEN_WIDTH - boss_health_bar_width) / 2
            boss_health_bar_y = boss_name_rect.bottom + 5
            boss_health_bar_rect = pygame.Rect(boss_health_bar_x, boss_health_bar_y, boss_health_bar_width, boss_health_bar_height)
            draw_health_bar(screen, stage_manager.boss.health, stage_manager.boss.max_health, boss_health_bar_rect)

        if dialogue_box.is_showing: # Draw dialogue box on top of game world
            dialogue_box.draw(screen)

    elif game_state == "ENDING":
        if current_scene_index < len(ENDING_SCENES_DATA):
            draw_scene(screen, ENDING_SCENES_DATA[current_scene_index], INTRO_FONT, SCENE_TEXT_COLOR, SCENE_TEXT_PADDING)

    pygame.display.flip()
    draw_health_bar(screen, player.health, player.max_health, player_hud_health_bar_rect)
    player_hud_stamina_bar_rect = pygame.Rect(10, 35, 130, 15)
    draw_health_bar(screen, player.stamina, player.max_stamina, player_hud_stamina_bar_rect)
    money_text = UI_FONT.render(f"Money: ${player.money}", True, pygame.Color('white'))
    screen.blit(money_text, (10, 60))
    xp_text = UI_FONT.render(f"XP: {player.xp} / {player.xp_to_next_level}", True, pygame.Color('white'))
    screen.blit(xp_text, (10, 85))
    stage_name_text = stage_manager.current_stage_data['name'] if stage_manager.current_stage_data else "Loading..."
    stage_text = UI_FONT.render(f"Stage: {stage_manager.current_stage_number} - {stage_name_text}", True, pygame.Color('white'))
    screen.blit(stage_text, (10, 110))

    if stage_manager.boss and stage_manager.boss.alive():
        boss_name_text = UI_FONT.render(f"{stage_manager.boss.__class__.__name__}", True, pygame.Color('white'))
        boss_name_rect = boss_name_text.get_rect(centerx=SCREEN_WIDTH / 2, y=10)
        screen.blit(boss_name_text, boss_name_rect)
        boss_health_bar_width = SCREEN_WIDTH * 0.6
        boss_health_bar_height = 25
        boss_health_bar_x = (SCREEN_WIDTH - boss_health_bar_width) / 2
        boss_health_bar_y = boss_name_rect.bottom + 5
        boss_health_bar_rect = pygame.Rect(boss_health_bar_x, boss_health_bar_y, boss_health_bar_width, boss_health_bar_height)
        draw_health_bar(screen, stage_manager.boss.health, stage_manager.boss.max_health, boss_health_bar_rect)

    if dialogue_box.is_showing:
        dialogue_box.draw(screen)

    pygame.display.flip()

stop_music() # Ensure music is stopped when the game loop ends
pygame.quit()
