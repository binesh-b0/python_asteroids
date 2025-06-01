import pygame
import json
import os
import time
from enum import Enum, auto
from constants import *

# Try to import sound manager without creating circular imports
try:
    from sound import SoundManager
    sound_manager = SoundManager()
except ImportError:
    sound_manager = None

# Game states
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORES = auto()
    HELP = auto()
    CREDITS = auto()

# Menu option types
class MenuOption(Enum):
    START_GAME = auto()
    HIGH_SCORES = auto()
    HELP = auto()
    CREDITS = auto()
    QUIT = auto()
    RESUME = auto()
    BACK_TO_MENU = auto()
    RESTART = auto()

# Achievement types
class Achievement(Enum):
    FIRST_KILL = auto()       # First asteroid destroyed
    COMBO_MASTER = auto()     # 5+ combo
    LEVEL_COMPLETE = auto()   # Complete a level
    UFO_HUNTER = auto()       # Destroy 5 UFOs
    SURVIVOR = auto()         # Survive 5 minutes
    PERFECT_WAVE = auto()     # Complete a wave without taking damage
    BOSS_SLAYER = auto()      # Defeat a boss wave

class ScoreSystem:
    """Handles score tracking, combos, multipliers, and high scores"""
    def __init__(self):
        self.score = 0
        self.high_scores = self._load_high_scores()
        
        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 1.5  # seconds before combo resets
        self.max_combo = 0  # Track highest combo in session
        
        # Score multipliers
        self.base_multiplier = 1.0
        self.combo_multiplier = 1.0
        self.level_multiplier = 1.0
        
        # Achievement tracking
        self.achievements = set()
        self.achievement_popup_timer = 0
        self.achievement_popup_text = ""
        
        # Stats for achievements
        self.asteroids_destroyed = 0
        self.ufos_destroyed = 0
        self.time_survived = 0
        self.waves_completed = 0
        self.perfect_wave = True  # Reset when taking damage
        
    def _load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists('high_scores.json'):
                with open('high_scores.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading high scores: {e}")
        
        # Default high scores if file doesn't exist or has an error
        return [
            {"name": "AAA", "score": 10000, "date": "2025-01-01"},
            {"name": "BBB", "score": 8000, "date": "2025-01-01"},
            {"name": "CCC", "score": 6000, "date": "2025-01-01"},
            {"name": "DDD", "score": 4000, "date": "2025-01-01"},
            {"name": "EEE", "score": 2000, "date": "2025-01-01"}
        ]
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open('high_scores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def add_score(self, points, level_multiplier=1.0):
        """Add points to score with multipliers applied"""
        # Apply multipliers
        self.level_multiplier = level_multiplier
        total_multiplier = self.base_multiplier * self.combo_multiplier * self.level_multiplier
        
        # Calculate final score
        adjusted_score = int(points * total_multiplier)
        self.score += adjusted_score
        
        # Update combo
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        
        # Update max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
        
        # Update combo multiplier (caps at 4x)
        if self.combo_count >= 10:
            self.combo_multiplier = 4.0
        elif self.combo_count >= 7:
            self.combo_multiplier = 3.0
        elif self.combo_count >= 5:
            self.combo_multiplier = 2.5
            # Award combo achievement
            self.add_achievement(Achievement.COMBO_MASTER)
        elif self.combo_count >= 3:
            self.combo_multiplier = 2.0
        elif self.combo_count >= 2:
            self.combo_multiplier = 1.5
        else:
            self.combo_multiplier = 1.0
            
        return adjusted_score
    
    def update(self, dt):
        """Update combo timer and other time-based elements"""
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Reset combo
                self.combo_count = 0
                self.combo_multiplier = 1.0
        
        # Update achievement popup timer
        if self.achievement_popup_timer > 0:
            self.achievement_popup_timer -= dt
        
        # Update survival time
        self.time_survived += dt
        
        # Check for time-based achievements
        if self.time_survived >= 300 and Achievement.SURVIVOR not in self.achievements:  # 5 minutes
            self.add_achievement(Achievement.SURVIVOR)
    
    def check_high_score(self):
        """Check if current score qualifies for high score table"""
        return self.score > self.high_scores[-1]["score"]
    
    def add_high_score(self, name):
        """Add current score to high score table"""
        # Create new high score entry
        new_entry = {
            "name": name,
            "score": self.score,
            "date": time.strftime("%Y-%m-%d")
        }
        
        # Add to list and sort
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Keep only top 10
        self.high_scores = self.high_scores[:10]
        
        # Save updated high scores
        self.save_high_scores()
    
    def add_achievement(self, achievement):
        """Add an achievement and show popup"""
        if achievement not in self.achievements:
            self.achievements.add(achievement)
            
            # Set achievement popup
            achievement_names = {
                Achievement.FIRST_KILL: "First Kill",
                Achievement.COMBO_MASTER: "Combo Master",
                Achievement.LEVEL_COMPLETE: "Level Complete",
                Achievement.UFO_HUNTER: "UFO Hunter",
                Achievement.SURVIVOR: "Survivor",
                Achievement.PERFECT_WAVE: "Perfect Wave",
                Achievement.BOSS_SLAYER: "Boss Slayer"
            }
            
            self.achievement_popup_text = f"Achievement Unlocked: {achievement_names[achievement]}"
            self.achievement_popup_timer = 3.0  # Show for 3 seconds
            
            # Play achievement sound
            if sound_manager:
                sound_manager.play_sound('ufo_appear')  # Reuse as achievement sound
    
    def reset(self):
        """Reset score system for a new game"""
        self.score = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
        self.max_combo = 0
        self.base_multiplier = 1.0
        self.level_multiplier = 1.0
        self.achievements = set()
        self.achievement_popup_timer = 0
        self.achievement_popup_text = ""
        self.asteroids_destroyed = 0
        self.ufos_destroyed = 0
        self.time_survived = 0
        self.waves_completed = 0
        self.perfect_wave = True
    
    def on_asteroid_destroyed(self):
        """Track asteroid destruction for achievements"""
        self.asteroids_destroyed += 1
        
        # First kill achievement
        if self.asteroids_destroyed == 1:
            self.add_achievement(Achievement.FIRST_KILL)
    
    def on_ufo_destroyed(self):
        """Track UFO destruction for achievements"""
        self.ufos_destroyed += 1
        
        # UFO hunter achievement
        if self.ufos_destroyed >= 5:
            self.add_achievement(Achievement.UFO_HUNTER)
    
    def on_wave_completed(self, is_boss_wave):
        """Track wave completion for achievements"""
        self.waves_completed += 1
        
        if self.perfect_wave:
            self.add_achievement(Achievement.PERFECT_WAVE)
        
        # Reset perfect wave flag for next wave
        self.perfect_wave = True
        
        # Track boss defeats
        if is_boss_wave:
            self.add_achievement(Achievement.BOSS_SLAYER)
    
    def on_level_completed(self):
        """Track level completion for achievements"""
        self.add_achievement(Achievement.LEVEL_COMPLETE)
    
    def on_player_hit(self):
        """Track player damage for perfect wave achievement"""
        self.perfect_wave = False
        # Reset combo on hit
        self.combo_count = 0
        self.combo_multiplier = 1.0
        self.combo_timer = 0
    
    def draw_score(self, screen, x, y, font):
        """Draw score and multiplier information"""
        # Draw current score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (x, y))
        
        # Draw combo counter if active
        if self.combo_count > 1:
            combo_color = (255, 255, 0)  # Yellow for active combo
            combo_text = font.render(f"Combo: x{self.combo_count} ({self.combo_multiplier:.1f}x)", True, combo_color)
            screen.blit(combo_text, (x, y + FONT_SIZE))
        else:
            # No active combo
            combo_text = font.render("Combo: -", True, (200, 200, 200))
            screen.blit(combo_text, (x, y + FONT_SIZE))
        
        # Draw total multiplier
        total_multiplier = self.base_multiplier * self.combo_multiplier * self.level_multiplier
        mult_text = font.render(f"Multiplier: {total_multiplier:.1f}x", True, (200, 200, 200))
        screen.blit(mult_text, (x, y + FONT_SIZE * 2))
        
        return y + FONT_SIZE * 3  # Return next Y position for other HUD elements
    
    def draw_achievement_popup(self, screen, font):
        """Draw achievement popup if active"""
        if self.achievement_popup_timer > 0:
            # Draw semi-transparent background
            popup_width = 400
            popup_height = 50
            popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
            popup_surface.fill((0, 0, 0, 180))
            
            # Position in top-center of screen
            x = (SCREEN_WIDTH - popup_width) // 2
            y = 20
            
            # Draw popup
            screen.blit(popup_surface, (x, y))
            
            # Draw text
            achievement_text = font.render(self.achievement_popup_text, True, (255, 215, 0))
            text_x = x + (popup_width - achievement_text.get_width()) // 2
            text_y = y + (popup_height - achievement_text.get_height()) // 2
            screen.blit(achievement_text, (text_x, text_y))

class GameStateManager:
    """Manages game states, menus, and transitions"""
    def __init__(self, screen):
        self.screen = screen
        self.current_state = GameState.MENU
        self.score_system = ScoreSystem()
        
        # UI elements
        self.title_font = pygame.font.SysFont(None, FONT_SIZE * 3)
        self.menu_font = pygame.font.SysFont(None, FONT_SIZE * 2)
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        
        # Menu state
        self.menu_options = []
        self.selected_option = 0
        
        # Pause state
        self.pause_options = []
        
        # Game over state
        self.game_over_options = []
        
        # High score entry
        self.entering_name = False
        self.player_name = ""
        self.name_entry_cursor_visible = True
        self.name_entry_cursor_timer = 0
        self.name_entry_cursor_blink_rate = 0.5  # seconds
        
        # Transition effects
        self.transition_alpha = 0
        self.transition_speed = 5  # alpha change per frame
        self.transitioning_to = None
        
        # Initialize menus
        self._init_menus()
    
    def _init_menus(self):
        """Initialize menu options for different states"""
        # Main menu options
        self.menu_options = [
            {"type": MenuOption.START_GAME, "text": "Start Game"},
            {"type": MenuOption.HIGH_SCORES, "text": "High Scores"},
            {"type": MenuOption.HELP, "text": "How to Play"},
            {"type": MenuOption.CREDITS, "text": "Credits"},
            {"type": MenuOption.QUIT, "text": "Quit Game"}
        ]
        
        # Pause menu options
        self.pause_options = [
            {"type": MenuOption.RESUME, "text": "Resume Game"},
            {"type": MenuOption.RESTART, "text": "Restart Game"},
            {"type": MenuOption.BACK_TO_MENU, "text": "Main Menu"},
            {"type": MenuOption.QUIT, "text": "Quit Game"}
        ]
        
        # Game over menu options
        self.game_over_options = [
            {"type": MenuOption.RESTART, "text": "Play Again"},
            {"type": MenuOption.HIGH_SCORES, "text": "High Scores"},
            {"type": MenuOption.BACK_TO_MENU, "text": "Main Menu"},
            {"type": MenuOption.QUIT, "text": "Quit Game"}
        ]
    
    def change_state(self, new_state):
        """Transition to a new game state"""
        # Start transition effect
        self.transition_alpha = 0
        self.transitioning_to = new_state
        
        # Reset selection for menus
        self.selected_option = 0
    
    def update(self, dt):
        """Update current game state"""
        # Handle transitions
        if self.transitioning_to:
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                # Complete transition
                self.current_state = self.transitioning_to
                self.transitioning_to = None
                self.transition_alpha = 255
            return
        elif self.transition_alpha > 0:
            # Fade in from transition
            self.transition_alpha -= self.transition_speed
            if self.transition_alpha < 0:
                self.transition_alpha = 0
        
        # Update score system
        self.score_system.update(dt)
        
        # Handle name entry cursor blinking
        if self.entering_name:
            self.name_entry_cursor_timer += dt
            if self.name_entry_cursor_timer >= self.name_entry_cursor_blink_rate:
                self.name_entry_cursor_timer -= self.name_entry_cursor_blink_rate
                self.name_entry_cursor_visible = not self.name_entry_cursor_visible
    
    def handle_event(self, event):
        """Handle input events based on current state"""
        if self.transitioning_to:
            return False  # Ignore input during transitions
        
        if event.type == pygame.KEYDOWN:
            if self.current_state == GameState.MENU:
                return self._handle_menu_input(event)
            elif self.current_state == GameState.PAUSED:
                return self._handle_pause_input(event)
            elif self.current_state == GameState.GAME_OVER:
                if self.entering_name:
                    return self._handle_name_entry_input(event)
                else:
                    return self._handle_game_over_input(event)
            elif self.current_state == GameState.HIGH_SCORES:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.change_state(GameState.MENU)
                return False
            elif self.current_state == GameState.HELP or self.current_state == GameState.CREDITS:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.change_state(GameState.MENU)
                return False
            elif self.current_state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.change_state(GameState.PAUSED)
                    if sound_manager:
                        sound_manager.play_sound('ufo_appear')
                    return True
        
        return False  # Event not handled
    
    def _handle_menu_input(self, event):
        """Handle input in main menu state"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_RETURN:
            option = self.menu_options[self.selected_option]["type"]
            
            if option == MenuOption.START_GAME:
                self.change_state(GameState.PLAYING)
                self.score_system.reset()
                if sound_manager:
                    sound_manager.play_sound('explosion_large')
            elif option == MenuOption.HIGH_SCORES:
                self.change_state(GameState.HIGH_SCORES)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
            elif option == MenuOption.HELP:
                self.change_state(GameState.HELP)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
            elif option == MenuOption.CREDITS:
                self.change_state(GameState.CREDITS)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
            elif option == MenuOption.QUIT:
                return True  # Signal to quit game
            
            return True
        
        return False
    
    def _handle_pause_input(self, event):
        """Handle input in pause menu state"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.pause_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.pause_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_RETURN:
            option = self.pause_options[self.selected_option]["type"]
            
            if option == MenuOption.RESUME:
                self.change_state(GameState.PLAYING)
                if sound_manager:
                    sound_manager.play_sound('phaser')
            elif option == MenuOption.RESTART:
                self.change_state(GameState.PLAYING)
                self.score_system.reset()
                if sound_manager:
                    sound_manager.play_sound('explosion_large')
                return {"restart": True}
            elif option == MenuOption.BACK_TO_MENU:
                self.change_state(GameState.MENU)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
                return {"back_to_menu": True}
            elif option == MenuOption.QUIT:
                return {"quit": True}  # Signal to quit game
            
            return True
        elif event.key == pygame.K_ESCAPE:
            # Resume game on Escape
            self.change_state(GameState.PLAYING)
            if sound_manager:
                sound_manager.play_sound('phaser')
            return True
        
        return False
    
    def _handle_game_over_input(self, event):
        """Handle input in game over state"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.game_over_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.game_over_options)
            if sound_manager:
                sound_manager.play_sound('shoot')
            return True
        elif event.key == pygame.K_RETURN:
            option = self.game_over_options[self.selected_option]["type"]
            
            if option == MenuOption.RESTART:
                self.change_state(GameState.PLAYING)
                self.score_system.reset()
                if sound_manager:
                    sound_manager.play_sound('explosion_large')
                return {"restart": True}
            elif option == MenuOption.HIGH_SCORES:
                self.change_state(GameState.HIGH_SCORES)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
            elif option == MenuOption.BACK_TO_MENU:
                self.change_state(GameState.MENU)
                if sound_manager:
                    sound_manager.play_sound('ufo_appear')
                return {"back_to_menu": True}
            elif option == MenuOption.QUIT:
                return {"quit": True}  # Signal to quit game
            
            return True
        
        return False
    
    def _handle_name_entry_input(self, event):
        """Handle input for high score name entry"""
        if event.key == pygame.K_RETURN:
            # Submit name
            if self.player_name:
                self.score_system.add_high_score(self.player_name)
                self.entering_name = False
                # Show high scores after entry
                self.change_state(GameState.HIGH_SCORES)
            return True
        elif event.key == pygame.K_BACKSPACE:
            # Delete last character
            self.player_name = self.player_name[:-1]
            return True
        elif event.key == pygame.K_ESCAPE:
            # Cancel name entry
            self.entering_name = False
            return True
        elif len(self.player_name) < 3:
            # Add character if it's a valid one
            if event.unicode.isalnum():
                self.player_name += event.unicode.upper()
                return True
        
        return False
    
    def on_game_over(self, score):
        """Handle game over state"""
        self.change_state(GameState.GAME_OVER)
        
        # Check for high score
        if self.score_system.check_high_score():
            self.entering_name = True
            self.player_name = ""
            self.name_entry_cursor_visible = True
            self.name_entry_cursor_timer = 0
    
    def draw(self):
        """Draw current state"""
        if self.current_state == GameState.MENU:
            self._draw_menu()
        elif self.current_state == GameState.PAUSED:
            self._draw_pause_menu()
        elif self.current_state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.current_state == GameState.HIGH_SCORES:
            self._draw_high_scores()
        elif self.current_state == GameState.HELP:
            self._draw_help()
        elif self.current_state == GameState.CREDITS:
            self._draw_credits()
        
        # Draw achievement popup if active
        self.score_system.draw_achievement_popup(self.screen, self.font)
        
        # Draw transition effect if active
        if self.transition_alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.transition_alpha)
            self.screen.blit(overlay, (0, 0))
    
    def _draw_menu(self):
        """Draw main menu screen"""
        # Draw title
        title = self.title_font.render("ASTEROIDS", True, (255, 255, 255))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 100
        self.screen.blit(title, (title_x, title_y))
        
        # Draw menu options
        option_y = 250
        for i, option in enumerate(self.menu_options):
            # Highlight selected option
            if i == self.selected_option:
                color = (255, 255, 0)  # Yellow for selected
                # Draw selection indicator
                pygame.draw.polygon(self.screen, color, [
                    (SCREEN_WIDTH // 2 - 150, option_y + 12),
                    (SCREEN_WIDTH // 2 - 130, option_y + 2),
                    (SCREEN_WIDTH // 2 - 130, option_y + 22)
                ])
            else:
                color = (200, 200, 200)  # Gray for unselected
            
            # Draw option text
            text = self.menu_font.render(option["text"], True, color)
            text_x = (SCREEN_WIDTH - text.get_width()) // 2
            self.screen.blit(text, (text_x, option_y))
            option_y += 50
        
        # Draw controls
        controls_text = self.font.render("Use UP/DOWN arrows to select, ENTER to confirm", True, (150, 150, 150))
        controls_x = (SCREEN_WIDTH - controls_text.get_width()) // 2
        controls_y = SCREEN_HEIGHT - 100
        self.screen.blit(controls_text, (controls_x, controls_y))
        
        # Draw high score
        high_score = max([score["score"] for score in self.score_system.high_scores]) if self.score_system.high_scores else 0
        high_score_text = self.font.render(f"High Score: {high_score}", True, (255, 215, 0))
        high_score_x = (SCREEN_WIDTH - high_score_text.get_width()) // 2
        high_score_y = SCREEN_HEIGHT - 50
        self.screen.blit(high_score_text, (high_score_x, high_score_y))
    
    def _draw_pause_menu(self):
        """Draw pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 100
        self.screen.blit(title, (title_x, title_y))
        
        # Draw menu options
        option_y = 250
        for i, option in enumerate(self.pause_options):
            # Highlight selected option
            if i == self.selected_option:
                color = (255, 255, 0)  # Yellow for selected
                # Draw selection indicator
                pygame.draw.polygon(self.screen, color, [
                    (SCREEN_WIDTH // 2 - 150, option_y + 12),
                    (SCREEN_WIDTH // 2 - 130, option_y + 2),
                    (SCREEN_WIDTH // 2 - 130, option_y + 22)
                ])
            else:
                color = (200, 200, 200)  # Gray for unselected
            
            # Draw option text
            text = self.menu_font.render(option["text"], True, color)
            text_x = (SCREEN_WIDTH - text.get_width()) // 2
            self.screen.blit(text, (text_x, option_y))
            option_y += 50
        
        # Draw current score
        score_text = self.font.render(f"Current Score: {self.score_system.score}", True, (255, 255, 255))
        score_x = (SCREEN_WIDTH - score_text.get_width()) // 2
        score_y = SCREEN_HEIGHT - 100
        self.screen.blit(score_text, (score_x, score_y))
    
    def _draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # More opaque black
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 100
        self.screen.blit(title, (title_x, title_y))
        
        # Draw final score
        score_text = self.menu_font.render(f"Final Score: {self.score_system.score}", True, (255, 255, 255))
        score_x = (SCREEN_WIDTH - score_text.get_width()) // 2
        score_y = 180
        self.screen.blit(score_text, (score_x, score_y))
        
        # If entering name for high score
        if self.entering_name:
            # Draw name entry instructions
            prompt_text = self.font.render("New High Score! Enter your name:", True, (255, 215, 0))
            prompt_x = (SCREEN_WIDTH - prompt_text.get_width()) // 2
            prompt_y = 250
            self.screen.blit(prompt_text, (prompt_x, prompt_y))
            
            # Draw name entry box
            name_box_width = 200
            name_box_height = 40
            name_box_x = (SCREEN_WIDTH - name_box_width) // 2
            name_box_y = 280
            pygame.draw.rect(self.screen, (100, 100, 100), (name_box_x, name_box_y, name_box_width, name_box_height))
            pygame.draw.rect(self.screen, (200, 200, 200), (name_box_x, name_box_y, name_box_width, name_box_height), 2)
            
            # Draw entered name
            name_display = self.player_name
            if self.name_entry_cursor_visible:
                name_display += "_"
            name_text = self.menu_font.render(name_display, True, (255, 255, 255))
            name_text_x = (SCREEN_WIDTH - name_text.get_width()) // 2
            name_text_y = name_box_y + 5
            self.screen.blit(name_text, (name_text_x, name_text_y))
            
            # Draw instructions
            instructions = self.font.render("Press ENTER to submit", True, (200, 200, 200))
            instructions_x = (SCREEN_WIDTH - instructions.get_width()) // 2
            instructions_y = name_box_y + 50
            self.screen.blit(instructions, (instructions_x, instructions_y))
        else:
            # Draw menu options
            option_y = 250
            for i, option in enumerate(self.game_over_options):
                # Highlight selected option
                if i == self.selected_option:
                    color = (255, 255, 0)  # Yellow for selected
                    # Draw selection indicator
                    pygame.draw.polygon(self.screen, color, [
                        (SCREEN_WIDTH // 2 - 150, option_y + 12),
                        (SCREEN_WIDTH // 2 - 130, option_y + 2),
                        (SCREEN_WIDTH // 2 - 130, option_y + 22)
                    ])
                else:
                    color = (200, 200, 200)  # Gray for unselected
                
                # Draw option text
                text = self.menu_font.render(option["text"], True, color)
                text_x = (SCREEN_WIDTH - text.get_width()) // 2
                self.screen.blit(text, (text_x, option_y))
                option_y += 50
            
            # Draw some stats
            stats_y = SCREEN_HEIGHT - 150
            stats_x = SCREEN_WIDTH // 2 - 150
            
            # Time survived
            minutes = int(self.score_system.time_survived // 60)
            seconds = int(self.score_system.time_survived % 60)
            time_text = self.font.render(f"Time Survived: {minutes}:{seconds:02d}", True, (200, 200, 200))
            self.screen.blit(time_text, (stats_x, stats_y))
            
            # Asteroids destroyed
            asteroids_text = self.font.render(f"Asteroids Destroyed: {self.score_system.asteroids_destroyed}", True, (200, 200, 200))
            self.screen.blit(asteroids_text, (stats_x, stats_y + 25))
            
            # UFOs destroyed
            ufos_text = self.font.render(f"UFOs Destroyed: {self.score_system.ufos_destroyed}", True, (200, 200, 200))
            self.screen.blit(ufos_text, (stats_x, stats_y + 50))
            
            # Max combo
            combo_text = self.font.render(f"Max Combo: {self.score_system.max_combo}", True, (200, 200, 200))
            self.screen.blit(combo_text, (stats_x, stats_y + 75))
    
    def _draw_high_scores(self):
        """Draw high score table"""
        # Draw title
        title = self.title_font.render("HIGH SCORES", True, (255, 215, 0))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 50
        self.screen.blit(title, (title_x, title_y))
        
        # Draw headers
        header_y = 150
        rank_header = self.menu_font.render("Rank", True, (255, 255, 255))
        name_header = self.menu_font.render("Name", True, (255, 255, 255))
        score_header = self.menu_font.render("Score", True, (255, 255, 255))
        date_header = self.menu_font.render("Date", True, (255, 255, 255))
        
        self.screen.blit(rank_header, (SCREEN_WIDTH // 5 - rank_header.get_width() // 2, header_y))
        self.screen.blit(name_header, (2 * SCREEN_WIDTH // 5 - name_header.get_width() // 2, header_y))
        self.screen.blit(score_header, (3 * SCREEN_WIDTH // 5 - score_header.get_width() // 2, header_y))
        self.screen.blit(date_header, (4 * SCREEN_WIDTH // 5 - date_header.get_width() // 2, header_y))
        
        # Draw horizontal line
        pygame.draw.line(self.screen, (200, 200, 200), (SCREEN_WIDTH // 5 - 100, header_y + 40), (4 * SCREEN_WIDTH // 5 + 100, header_y + 40), 2)
        
        # Draw scores
        score_y = header_y + 60
        for i, score in enumerate(self.score_system.high_scores[:10]):
            # Alternate row colors for readability
            if i % 2 == 0:
                row_color = (200, 200, 200)  # Light gray
            else:
                row_color = (170, 170, 170)  # Darker gray
            
            # Highlight if current score
            if self.score_system.score == score["score"] and not self.entering_name:
                row_color = (255, 255, 0)  # Yellow for current score
            
            rank_text = self.font.render(f"{i+1}", True, row_color)
            name_text = self.font.render(score["name"], True, row_color)
            score_text = self.font.render(f"{score['score']}", True, row_color)
            date_text = self.font.render(score["date"], True, row_color)
            
            self.screen.blit(rank_text, (SCREEN_WIDTH // 5 - rank_text.get_width() // 2, score_y))
            self.screen.blit(name_text, (2 * SCREEN_WIDTH // 5 - name_text.get_width() // 2, score_y))
            self.screen.blit(score_text, (3 * SCREEN_WIDTH // 5 - score_text.get_width() // 2, score_y))
            self.screen.blit(date_text, (4 * SCREEN_WIDTH // 5 - date_text.get_width() // 2, score_y))
            
            score_y += 35
        
        # Draw instructions
        instructions = self.font.render("Press ESC or ENTER to return to menu", True, (150, 150, 150))
        instructions_x = (SCREEN_WIDTH - instructions.get_width()) // 2
        instructions_y = SCREEN_HEIGHT - 50
        self.screen.blit(instructions, (instructions_x, instructions_y))
    
    def _draw_help(self):
        """Draw help/instructions screen"""
        # Draw title
        title = self.title_font.render("HOW TO PLAY", True, (255, 255, 255))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 50
        self.screen.blit(title, (title_x, title_y))
        
        # Draw instructions
        instructions = [
            "CONTROLS:",
            "- WASD keys to move your ship",
            "- SPACE to shoot",
            "- P or ESC to pause the game",
            "- M to toggle sound",
            "",
            "GAMEPLAY:",
            "- Destroy asteroids and UFOs to score points",
            "- Chain multiple hits to build combos and increase score multipliers",
            "- Collect power-ups to gain advantages",
            "- Complete waves and levels to progress",
            "- Each level has multiple waves and increasing difficulty",
            "- Boss waves appear every 3 levels",
            "",
            "POWER-UPS:",
            "- Ammo: Replenishes your ammunition",
            "- Rapid Fire: Temporarily increases firing rate",
            "- Score Boost: Instantly adds points to your score",
            "- Shield: Temporary invincibility"
        ]
        
        instruction_y = 130
        for line in instructions:
            if line == "":
                instruction_y += 10  # Add spacing for empty lines
                continue
                
            if ":" in line:
                # Section headers
                text = self.menu_font.render(line, True, (255, 215, 0))
            else:
                text = self.font.render(line, True, (200, 200, 200))
                
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
            self.screen.blit(text, (text_x, instruction_y))
            instruction_y += 30
        
        # Draw instructions to return
        back_text = self.font.render("Press ESC or ENTER to return to menu", True, (150, 150, 150))
        back_x = (SCREEN_WIDTH - back_text.get_width()) // 2
        back_y = SCREEN_HEIGHT - 50
        self.screen.blit(back_text, (back_x, back_y))
    
    def _draw_credits(self):
        """Draw credits screen"""
        # Draw title
        title = self.title_font.render("CREDITS", True, (255, 255, 255))
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        title_y = 50
        self.screen.blit(title, (title_x, title_y))
        
        # Draw credits text
        credits = [
            "ASTEROIDS",
            "A Python Pygame Implementation",
            "",
            "PROGRAMMING:",
            "Your Name Here",
            "",
            "GRAPHICS:",
            "Created with Pygame",
            "",
            "SOUND EFFECTS:",
            "Various sound libraries",
            "",
            "SPECIAL THANKS:",
            "The original Asteroids game by Atari",
            "The Pygame community",
            "And YOU for playing!"
        ]
        
        credit_y = 130
        for line in credits:
            if line == "":
                credit_y += 10  # Add spacing for empty lines
                continue
                
            if line == "ASTEROIDS":
                text = self.title_font.render(line, True, (255, 215, 0))
            elif ":" in line:
                # Section headers
                text = self.menu_font.render(line, True, (255, 215, 0))
            else:
                text = self.font.render(line, True, (200, 200, 200))
                
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
            self.screen.blit(text, (text_x, credit_y))
            credit_y += 35
        
        # Draw instructions to return
        back_text = self.font.render("Press ESC or ENTER to return to menu", True, (150, 150, 150))
        back_x = (SCREEN_WIDTH - back_text.get_width()) // 2
        back_y = SCREEN_HEIGHT - 50
        self.screen.blit(back_text, (back_x, back_y))

