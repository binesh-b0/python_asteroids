import pygame
import os
import json
import random
from constants import *
from player import Player
from asteroid import Asteroid 
from asteroidfield import AsteroidField
from shoot import Shoot
from sound import SoundManager
from ufo import UFO
from enemy_projectile import EnemyProjectile
from powerup import PowerUp
from game_state import GameStateManager, GameState
from level_manager import LevelManager
import math


def load_high_score():
    """Load high score from file"""
    try:
        if os.path.exists('high_score.json'):
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except Exception as e:
        print(f"Error loading high score: {e}")
    return 0

def save_high_score(score):
    """Save high score to file"""
    try:
        with open('high_score.json', 'w') as f:
            json.dump({'high_score': score}, f)
    except Exception as e:
        print(f"Error saving high score: {e}")

def select_difficulty(screen, font):
    """Display difficulty selection screen and return the chosen difficulty level"""
    selected = DIFFICULTY_NORMAL  # Default to normal difficulty
    selection_done = False
    
    # Create a slightly larger font for the title
    title_font = pygame.font.SysFont(None, FONT_SIZE * 2)
    
    while not selection_done:
        screen.fill((0, 0, 0))
        
        # Draw title
        title = title_font.render("ASTEROIDS", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Draw instructions
        instructions = font.render("Select Difficulty:", True, (255, 255, 255))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 200))
        
        # Draw difficulty options
        y_pos = 250
        for diff in [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]:
            # Highlight the selected difficulty
            color = (255, 255, 0) if diff == selected else (200, 200, 200)
            text = font.render(DIFFICULTY_NAMES[diff], True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 50
        
        # Draw controls
        controls = font.render("UP/DOWN arrows to select, ENTER to confirm", True, (200, 200, 200))
        screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 100))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                return None  # Signal to exit the game
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # Move selection up
                    selected = max(DIFFICULTY_EASY, selected - 1)
                elif event.key == pygame.K_DOWN:
                    # Move selection down
                    selected = min(DIFFICULTY_HARD, selected + 1)
                elif event.key == pygame.K_RETURN:
                    # Confirm selection
                    selection_done = True
    
    return selected

def init_game_objects(difficulty):
    """Initialize game objects, sprite groups, and return them"""
    # Get difficulty modifiers
    difficulty_mods = DIFFICULTY_MODIFIERS[difficulty]
    
    # Create sprite groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    ufos = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    
    # Set up sprite containers
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shoot.containers = (shots, updatable, drawable)
    UFO.containers = (ufos, updatable, drawable)
    EnemyProjectile.containers = (enemy_projectiles, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    
    # Create player at center of screen
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    
    # Create asteroid field with difficulty-adjusted speed multiplier
    asteroid_field = AsteroidField(speed_multiplier=difficulty_mods['asteroid_speed_multiplier'])
    
    # Apply difficulty modifiers to spawn rates
    asteroid_field.spawn_rate = ASTEROID_SPAWN_RATE * difficulty_mods['spawn_rate_multiplier']
    
    return {
        'player': player,
        'asteroid_field': asteroid_field,
        'updatable': updatable,
        'drawable': drawable,
        'asteroids': asteroids,
        'shots': shots,
        'ufos': ufos,
        'enemy_projectiles': enemy_projectiles,
        'powerups': powerups
    }

def spawn_asteroid(size=None):
    """Spawn an asteroid of the given size (or random if None)"""
    edge = random.choice(AsteroidField.edges)
    position = edge[1](random.uniform(0, 1))
    if size is None:
        size = random.randint(1, ASTEROID_KINDS)
    asteroid = Asteroid(position.x, position.y, size)
    return asteroid

def spawn_ufo():
    """Spawn a UFO at a random edge"""
    edge = random.choice(AsteroidField.edges)
    position = edge[1](random.uniform(0, 1))
    ufo = UFO(position.x, position.y)
    if sound_manager:
        sound_manager.play_sound('ufo_appear')
    return ufo

def main():
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # Initialize pygame and fonts
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont(None, FONT_SIZE)
    # load and initialize background image
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Ensure video mode is enabled before loading assets
    try:
        background_image = pygame.image.load("assets/images/Background/black.png").convert()

    except pygame.error as e:
        print(f"Error loading background image: {e}")
        background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background_image.fill((0, 0, 0))  # Fallback to a black background

    # Create a larger surface to repeat the background image
    repeated_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for x in range(0, SCREEN_WIDTH, background_image.get_width()):
        for y in range(0, SCREEN_HEIGHT, background_image.get_height()):
            repeated_background.blit(background_image, (x, y))



    # Setup screen and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    dt = 0
    
    # Initialize sound manager
    global sound_manager
    sound_manager = SoundManager()
    sound_manager.start_background_music()
    
    # Initialize game state manager
    game_state_manager = GameStateManager(screen)
    
    # Initial difficulty level (will be selected in menu)
    difficulty = DIFFICULTY_NORMAL
    
    # Initialize game objects
    game_objects = None
    
    # Create level manager
    level_manager = None
    
    # Game initialization status
    game_initialized = False
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
            # Pass events to game state manager first
            result = game_state_manager.handle_event(event)
            if result:
                # Handle special return values from game state manager
                if isinstance(result, dict):
                    if result.get('quit'):
                        running = False
                        break
                    if result.get('restart'):
                        # Reinitialize game objects
                        game_objects = init_game_objects(difficulty)
                        level_manager = LevelManager(difficulty)
                        game_initialized = True
                    if result.get('back_to_menu'):
                        game_initialized = False
                continue
                
            # Handle key press events for sound controls
            if event.type == pygame.KEYDOWN:
                # M key toggles sound on/off
                if event.key == pygame.K_m:
                    sound_manager.toggle_sound()
                # + key increases volume
                elif event.key == pygame.K_EQUALS and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    sound_manager.set_music_volume(sound_manager.music_volume + 0.1)
                    sound_manager.set_sfx_volume(sound_manager.sfx_volume + 0.1)
                # - key decreases volume
                elif event.key == pygame.K_MINUS:
                    sound_manager.set_music_volume(sound_manager.music_volume - 0.1)
                    sound_manager.set_sfx_volume(sound_manager.sfx_volume - 0.1)
        
        # Clear screen
        screen.blit(repeated_background, (0, 0))
        
        # Update game state manager
        game_state_manager.update(dt)
        
        # Handle different game states
        if game_state_manager.current_state == GameState.PLAYING:
            # Initialize game if not already done
            if not game_initialized:
                game_objects = init_game_objects(difficulty)
                level_manager = LevelManager(difficulty)
                game_initialized = True
                
            # Unpack game objects for easier access
            player = game_objects['player']
            asteroid_field = game_objects['asteroid_field']
            updatable = game_objects['updatable']
            drawable = game_objects['drawable']
            asteroids = game_objects['asteroids']
            shots = game_objects['shots']
            ufos = game_objects['ufos']
            enemy_projectiles = game_objects['enemy_projectiles']
            powerups = game_objects['powerups']
            
            # Update level manager
            level_manager.update(
                dt, 
                len(asteroids), 
                lambda size: spawn_asteroid(size),
                spawn_ufo
            )
            
            # Make UFOs shoot at the player
            for ufo in ufos:
                projectile = ufo.shoot_at_player(player.position)
            
            # Update all game objects
            updatable.update(dt)
        
            # Check collisions between player and power-ups
            for powerup in powerups:
                if powerup.is_colliding(player):
                    # Apply power-up effect and remove it
                    powerup.apply_effect(player)
                    powerup.kill()
            
            # Check collisions between player and asteroids (only if vulnerable)
            if player.is_vulnerable():
                for asteroid in asteroids:
                    if asteroid.is_colliding(player):
                        # Record hit for score system
                        game_state_manager.score_system.on_player_hit()
                        
                        # Player loses a life
                        game_over = player.lose_life()
                        
                        # If no lives left, game over
                        if game_over:
                            game_state_manager.on_game_over(player.score)
                            sound_manager.play_sound('player_death')
                        break  # Exit collision check loop after hit
            
            # Check collisions between player and UFOs (only if vulnerable)
            if player.is_vulnerable():
                for ufo in ufos:
                    if ufo.is_colliding(player):
                        # Record hit for score system
                        game_state_manager.score_system.on_player_hit()
                        
                        # Player loses a life
                        game_over = player.lose_life()
                        
                        # If no lives left, game over
                        if game_over:
                            game_state_manager.on_game_over(player.score)
                            sound_manager.play_sound('player_death')
                        break  # Exit collision check loop after hit
            
            # Check collisions between player and enemy projectiles (only if vulnerable)
            if player.is_vulnerable():
                for projectile in enemy_projectiles:
                    if projectile.is_colliding(player):
                        # Destroy the projectile
                        projectile.kill()
                        
                        # Record hit for score system
                        game_state_manager.score_system.on_player_hit()
                        
                        # Player loses a life
                        game_over = player.lose_life()
                        
                        # If no lives left, game over
                        if game_over:
                            game_state_manager.on_game_over(player.score)
                            sound_manager.play_sound('player_death')
                        break  # Exit collision check loop after hit
        
            # Check collisions between player shots and asteroids
            for asteroid in asteroids:
                for shot in shots:
                    if shot.is_colliding(asteroid):
                        shot.kill()
                        
                        # Hit the asteroid and check if it was destroyed
                        destroyed = asteroid.hit()
                        
                        if destroyed:
                            # Track asteroid destruction for achievements
                            game_state_manager.score_system.on_asteroid_destroyed()
                            
                            # Add points based on asteroid size and type, adjusted by level multiplier
                            level_multiplier = level_manager.get_score_multiplier()
                            adjusted_score = game_state_manager.score_system.add_score(
                                asteroid.score_value, level_multiplier)
                            
                            # Play explosion sound based on asteroid size
                            sound_manager.play_explosion_sound(asteroid.radius)
                            
                            # Chance to spawn a power-up
                            if random.random() < POWERUP_SPAWN_CHANCE:
                                PowerUp(asteroid.position.x, asteroid.position.y)
            
            # Check collisions between player shots and UFOs
            for ufo in ufos:
                for shot in shots:
                    if shot.is_colliding(ufo):
                        shot.kill()
                        ufo.kill()
                        
                        # Track UFO destruction for achievements
                        game_state_manager.score_system.on_ufo_destroyed()
                        
                        # Add points for destroying UFO, adjusted by level multiplier
                        level_multiplier = level_manager.get_score_multiplier()
                        adjusted_score = game_state_manager.score_system.add_score(
                            ufo.score_value, level_multiplier)
                        
                        # Play explosion sound
                        sound_manager.play_sound('explosion_large')
            
            # Draw game objects
            for item in drawable:
                item.draw(screen)
                
            # Create HUD instance if it doesn't exist
            if 'hud' not in locals():
                try:
                    from hud import GameHUD
                    hud = GameHUD(SCREEN_WIDTH, SCREEN_HEIGHT)
                except ImportError:
                    # Fall back to old HUD if GameHUD is not available
                    next_y = level_manager.draw_hud(screen, 10, 10)
                    next_y = game_state_manager.score_system.draw_score(screen, 10, next_y + 10, font)
                    
                    # Display ammo
                    ammo_text = font.render(f"Ammo: {player.current_ammo}/{AMMO_MAX_SHOTS}", True, (255, 255, 255))
                    screen.blit(ammo_text, (10, next_y))
                    next_y += FONT_SIZE
                    
                    # Display lives
                    lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
                    screen.blit(lives_text, (10, next_y))
                    
                    # Draw life icons
                    life_icon_spacing = 30
                    for i in range(player.lives):
                        # Draw a small ship icon for each life
                        icon_x = 100 + i * life_icon_spacing
                        icon_y = next_y
                        pygame.draw.polygon(screen, (255, 255, 255), [
                            (icon_x, icon_y - 8),
                            (icon_x - 5, icon_y + 4),
                            (icon_x + 5, icon_y + 4)
                        ], 1)
            else:
                # Update and draw the modern HUD
                hud.update(dt, player, game_state_manager.score_system)
                hud.draw(screen, player, game_state_manager.score_system)
            
            # Display respawn countdown if player is respawning
            if player.is_respawning:
                respawn_text = font.render(f"Respawning in: {round(player.respawn_timer, 1)}", True, (255, 100, 100))
                text_width = respawn_text.get_width()
                screen.blit(respawn_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2))
            
            # Draw level transition screen if active
            level_manager.draw_transition(screen)
        else:
            # Draw game state (menu, pause, game over, etc.)
            game_state_manager.draw()
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()
