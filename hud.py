import pygame
import math
from constants import *

class GameHUD:
    """Modern game heads-up display (HUD) with animated elements and visual styling"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load HUD assets
        self.life_icon = pygame.image.load("assets/images/life.png").convert_alpha()
        self.life_icon = pygame.transform.scale(self.life_icon, (30, 30))
        
        # Font setup
        self.title_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Animation variables
        self.score_display = 0  # Current displayed score (for animation)
        self.target_score = 0   # Target score to animate to
        self.score_change_time = 0  # Time when score last changed
        
        # Power-up display data
        self.powerup_icons = {
            POWERUP_AMMO: self._create_powerup_icon((50, 200, 50), "A"),
            POWERUP_FIRE_RATE: self._create_powerup_icon((200, 200, 50), "F"),
            POWERUP_SCORE: self._create_powerup_icon((200, 50, 200), "S"),
            POWERUP_INVINCIBILITY: self._create_powerup_icon((50, 50, 200), "I"),
        }
    
    def _create_powerup_icon(self, color, letter):
        """Create a colored icon surface for power-ups"""
        icon_size = 30
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Draw circle background
        pygame.draw.circle(icon, color, (icon_size//2, icon_size//2), icon_size//2)
        
        # Add letter
        text = self.font.render(letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=(icon_size//2, icon_size//2))
        icon.blit(text, text_rect)
        
        return icon
    
    def _draw_panel(self, screen, x, y, width, height, title=None):
        """Draw a semi-transparent panel with optional title"""
        # Create panel surface
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 180))  # Dark blue semi-transparent
        
        # Add border
        pygame.draw.rect(panel, (100, 100, 150, 200), (0, 0, width, height), 2)
        
        # Draw panel
        screen.blit(panel, (x, y))
        
        # Draw title if provided
        if title:
            title_text = self.font.render(title, True, (200, 200, 255))
            title_rect = title_text.get_rect(midtop=(x + width//2, y + 5))
            screen.blit(title_text, title_rect)
            
        return y + (25 if title else 0)  # Return new Y position after title
    
    def _draw_gradient_bar(self, screen, x, y, width, height, value, max_value, 
                          start_color, end_color, border_color=(200, 200, 200), 
                          text=None):
        """Draw a gradient-filled progress bar"""
        # Background (darker version of border)
        dark_border = tuple(max(c - 50, 0) for c in border_color)
        pygame.draw.rect(screen, dark_border, (x, y, width, height))
        
        # Calculate fill width
        fill_width = int((value / max_value) * (width - 4))
        
        if fill_width > 0:
            # Create gradient
            bar_surf = pygame.Surface((fill_width, height - 4))
            
            for i in range(fill_width):
                # Calculate gradient color
                progress = i / fill_width
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                
                # Draw vertical line of the gradient
                pygame.draw.line(bar_surf, (r, g, b), (i, 0), (i, height - 4))
            
            # Apply the gradient surface
            screen.blit(bar_surf, (x + 2, y + 2))
        
        # Border
        pygame.draw.rect(screen, border_color, (x, y, width, height), 2)
        
        # Text overlay
        if text:
            text_surf = self.small_font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(x + width//2, y + height//2))
            screen.blit(text_surf, text_rect)
    
    def update(self, dt, player, score_system):
        """Update HUD animations"""
        # Animate score
        self.target_score = score_system.score
        
        # Smooth animation for score changes
        if self.score_display != self.target_score:
            # Calculate how much to change score by
            diff = self.target_score - self.score_display
            
            # Animate faster for larger differences
            if abs(diff) > 1000:
                self.score_display += diff * dt * 5
            elif abs(diff) > 100:
                self.score_display += diff * dt * 3
            else:
                self.score_display += diff * dt * 10
                
            # Snap to target when very close
            if abs(self.target_score - self.score_display) < 1:
                self.score_display = self.target_score
    
    def draw(self, screen, player, score_system):
        """Draw the full game HUD"""
        # Left panel - Score and game info
        panel_left_width = 250
        panel_left_height = 150
        left_x = 10
        left_y = 10
        
        content_y = self._draw_panel(screen, left_x, left_y, panel_left_width, panel_left_height, "GAME INFO")
        
        # Score with animated value
        score_text = self.large_font.render(f"{int(self.score_display)}", True, (255, 255, 100))
        score_rect = score_text.get_rect(midtop=(left_x + panel_left_width//2, content_y + 5))
        screen.blit(score_text, score_rect)
        
        # Level info
        level_text = self.font.render(f"LEVEL: {1}", True, (200, 200, 255))  # Replace with actual level
        screen.blit(level_text, (left_x + 15, content_y + 45))
        
        # Combo display
        if score_system.combo_count > 1:
            combo_text = self.font.render(f"COMBO: x{score_system.combo_count}", True, (255, 200, 50))
            screen.blit(combo_text, (left_x + 15, content_y + 70))
            
            # Combo timer bar
            combo_width = panel_left_width - 30
            self._draw_gradient_bar(
                screen, left_x + 15, content_y + 95, combo_width, 15,
                score_system.combo_timer, 2.0,  # Assuming 2.0 is max combo timer
                (200, 50, 50), (255, 200, 50)
            )
        
        # Right panel - Player stats
        panel_right_width = 250
        panel_right_height = 150
        right_x = self.screen_width - panel_right_width - 10
        right_y = 10
        
        content_y = self._draw_panel(screen, right_x, right_y, panel_right_width, panel_right_height, "PLAYER")
        
        # Lives display with icons
        lives_text = self.font.render("LIVES:", True, (200, 200, 255))
        screen.blit(lives_text, (right_x + 15, content_y + 5))
        
        # Life icons
        for i in range(player.lives):
            screen.blit(self.life_icon, (right_x + 80 + i * 35, content_y))
            
        # Health bar
        health_text = self.font.render(f"HEALTH: {int(player.health)}/{PLAYER_MAX_HEALTH}", True, (200, 200, 255))
        screen.blit(health_text, (right_x + 15, content_y + 40))
        
        # Gradient health bar: red when low, yellow in middle, green when high
        self._draw_gradient_bar(
            screen, right_x + 15, content_y + 65, panel_right_width - 30, 20,
            player.health, PLAYER_MAX_HEALTH,
            (200, 50, 50), (50, 200, 50)
        )
        
        # Ammo counter
        ammo_text = self.font.render(f"AMMO: {player.current_ammo}/{AMMO_MAX_SHOTS}", True, (200, 200, 255))
        screen.blit(ammo_text, (right_x + 15, content_y + 95))
        
        # Ammo bar
        self._draw_gradient_bar(
            screen, right_x + 15, content_y + 120, panel_right_width - 30, 15,
            player.current_ammo, AMMO_MAX_SHOTS,
            (50, 150, 200), (200, 200, 255),
            text=f"{player.current_ammo}/{AMMO_MAX_SHOTS}"
        )
        
        # Active power-ups panel (bottom left)
        if player.active_powerups:
            powerup_panel_width = 250
            powerup_panel_height = 60
            powerup_x = 10
            powerup_y = self.screen_height - powerup_panel_height - 10
            
            content_y = self._draw_panel(screen, powerup_x, powerup_y, powerup_panel_width, powerup_panel_height, "ACTIVE POWER-UPS")
            
            # Display active power-ups
            icon_x = powerup_x + 15
            for powerup_type, remaining_time in player.active_powerups.items():
                if powerup_type in self.powerup_icons:
                    # Draw power-up icon
                    screen.blit(self.powerup_icons[powerup_type], (icon_x, content_y + 5))
                    
                    # Draw timer bar under icon
                    if powerup_type == POWERUP_FIRE_RATE:
                        max_time = POWERUP_FIRE_RATE_DURATION
                    elif powerup_type == POWERUP_INVINCIBILITY:
                        max_time = POWERUP_INVINCIBILITY_DURATION
                    else:
                        max_time = 5.0  # Default duration
                    
                    self._draw_gradient_bar(
                        screen, icon_x, content_y + 35, 30, 8,
                        remaining_time, max_time,
                        (200, 200, 50), (50, 200, 50)
                    )
                    
                    icon_x += 40  # Space between power-up icons
        
        # Draw achievement popup if active
        score_system.draw_achievement_popup(screen, self.font)

