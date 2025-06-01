import pygame
import random
import math

class SpriteAnimation:
    """Handles frame-by-frame sprite animations"""
    
    def __init__(self, frames, frame_duration=0.1, loop=True):
        """Initialize with a list of frame surfaces and frame duration in seconds"""
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.current_time = 0
        self.loop = loop
        self.finished = False
        
    def update(self, dt):
        """Update animation and return the current frame"""
        if self.finished:
            return self.frames[-1]
            
        self.current_time += dt
        
        # Check if it's time to advance to the next frame
        if self.current_time >= self.frame_duration:
            self.current_frame += 1
            self.current_time = 0
            
            # Check if animation is complete
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0  # Loop back to start
                else:
                    self.current_frame = len(self.frames) - 1  # Stay on last frame
                    self.finished = True
        
        return self.frames[self.current_frame]
    
    def reset(self):
        """Reset the animation to the beginning"""
        self.current_frame = 0
        self.current_time = 0
        self.finished = False
        
    def is_finished(self):
        """Check if a non-looping animation has finished"""
        return self.finished


class ParticleSystem:
    """Handles particle effects like explosions, engine trails, etc."""
    
    def __init__(self, position, particle_count=20, duration=1.0, colors=None, 
                 size_range=(2, 6), speed_range=(20, 80), decay_rate=0.5):
        self.position = pygame.Vector2(position)
        self.particles = []
        self.duration = duration
        self.lifetime = 0
        
        # Default particle colors if none provided
        if colors is None:
            colors = [(255, 255, 0), (255, 150, 0), (255, 50, 0)]
            
        # Create particles
        for _ in range(particle_count):
            # Random angle and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_range[0], speed_range[1])
            
            # Convert angle to velocity vector
            velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            
            # Random size and color
            size = random.uniform(size_range[0], size_range[1])
            color = random.choice(colors)
            
            # Random lifetime
            lifetime = random.uniform(duration * 0.5, duration)
            
            self.particles.append({
                'position': pygame.Vector2(position),
                'velocity': velocity,
                'color': color,
                'size': size,
                'lifetime': lifetime,
                'current_time': 0,
                'decay_rate': decay_rate
            })
    
    def update(self, dt):
        """Update all particles"""
        self.lifetime += dt
        
        for particle in self.particles:
            # Update particle lifetime
            particle['current_time'] += dt
            
            # Skip dead particles
            if particle['current_time'] >= particle['lifetime']:
                continue
                
            # Update position
            particle['position'] += particle['velocity'] * dt
            
            # Slow down over time
            particle['velocity'] *= (1 - particle['decay_rate'] * dt)
            
            # Shrink over time
            life_fraction = particle['current_time'] / particle['lifetime']
            particle['size'] *= (1 - 0.5 * dt)
    
    def draw(self, screen):
        """Draw all active particles"""
        for particle in self.particles:
            # Skip dead particles
            if particle['current_time'] >= particle['lifetime']:
                continue
                
            # Calculate alpha (fade out)
            alpha = int(255 * (1 - particle['current_time'] / particle['lifetime']))
            
            # Create color with alpha
            color = particle['color'] + (alpha,)
            
            # Draw particle
            pos = (int(particle['position'].x), int(particle['position'].y))
            size = int(particle['size'])
            
            # Create surface for this particle
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (size, size), size)
            
            # Draw particle
            screen.blit(particle_surf, (pos[0] - size, pos[1] - size))
    
    def is_finished(self):
        """Check if all particles have died"""
        if self.lifetime >= self.duration:
            for particle in self.particles:
                if particle['current_time'] < particle['lifetime']:
                    return False
            return True
        return False


class EffectManager:
    """Manages all effects and animations in the game"""
    
    def __init__(self):
        self.particle_systems = []
        self.animations = {}  # Dictionary of named animations
        
        # Cache loaded animations
        self._animation_cache = {}
        
    def add_particle_system(self, position, effect_type="explosion", **kwargs):
        """Add a new particle system at the given position"""
        if effect_type == "explosion":
            colors = [(255, 255, 0), (255, 150, 0), (255, 50, 0)]
            particle_count = 30
            duration = 1.0
            size_range = (3, 8)
            speed_range = (30, 100)
            
        elif effect_type == "thrust":
            colors = [(100, 150, 255), (50, 100, 255), (200, 220, 255)]
            particle_count = 15
            duration = 0.5
            size_range = (2, 5)
            speed_range = (10, 30)
            
        elif effect_type == "sparkle":
            colors = [(255, 255, 255), (200, 200, 255), (255, 255, 200)]
            particle_count = 10
            duration = 0.8
            size_range = (1, 3)
            speed_range = (5, 20)
            
        # Override defaults with any provided kwargs
        kwargs.setdefault('colors', colors)
        kwargs.setdefault('particle_count', particle_count)
        kwargs.setdefault('duration', duration)
        kwargs.setdefault('size_range', size_range)
        kwargs.setdefault('speed_range', speed_range)
        
        # Create and add the particle system
        self.particle_systems.append(ParticleSystem(position, **kwargs))
    
    def load_animation(self, name, pattern, frame_count, frame_duration=0.1, loop=True):
        """Load an animation from files matching a pattern (e.g. 'fire{:02d}.png')"""
        if name in self._animation_cache:
            return self._animation_cache[name]
            
        frames = []
        for i in range(frame_count):
            try:
                # Format pattern with frame number
                filename = pattern.format(i)
                image = pygame.image.load(filename).convert_alpha()
                frames.append(image)
            except pygame.error:
                print(f"Error loading animation frame: {filename}")
                
        if not frames:
            print(f"No frames loaded for animation: {name}")
            return None
            
        animation = SpriteAnimation(frames, frame_duration, loop)
        self._animation_cache[name] = animation
        return animation
    
    def play_animation(self, name, position, scale=1.0, angle=0, layer=0):
        """Play a named animation at the given position"""
        if name not in self._animation_cache:
            print(f"Animation not loaded: {name}")
            return
            
        # Clone the animation from cache
        anim = SpriteAnimation(
            self._animation_cache[name].frames,
            self._animation_cache[name].frame_duration,
            self._animation_cache[name].loop
        )
        
        # Add to active animations
        anim_id = f"{name}_{id(anim)}"
        self.animations[anim_id] = {
            'animation': anim,
            'position': position,
            'scale': scale,
            'angle': angle,
            'layer': layer
        }
        
        return anim_id
    
    def update(self, dt):
        """Update all effects and animations"""
        # Update particle systems and remove finished ones
        self.particle_systems = [ps for ps in self.particle_systems if not ps.is_finished()]
        for ps in self.particle_systems:
            ps.update(dt)
            
        # Update animations and remove finished ones
        finished_anims = []
        for anim_id, anim_data in self.animations.items():
            anim_data['animation'].update(dt)
            if anim_data['animation'].is_finished():
                finished_anims.append(anim_id)
                
        for anim_id in finished_anims:
            del self.animations[anim_id]
    
    def draw(self, screen):
        """Draw all effects sorted by layer"""
        # Draw particle systems
        for ps in self.particle_systems:
            ps.draw(screen)
            
        # Sort animations by layer
        sorted_anims = sorted(self.animations.items(), key=lambda x: x[1]['layer'])
        
        # Draw animations
        for _, anim_data in sorted_anims:
            frame = anim_data['animation'].update(0)  # Get current frame without advancing
            
            # Scale if needed
            if anim_data['scale'] != 1.0:
                orig_size = frame.get_size()
                new_size = (int(orig_size[0] * anim_data['scale']), int(orig_size[1] * anim_data['scale']))
                frame = pygame.transform.scale(frame, new_size)
                
            # Rotate if needed
            if anim_data['angle'] != 0:
                frame = pygame.transform.rotate(frame, -anim_data['angle'])
                
            # Draw the frame
            rect = frame.get_rect(center=anim_data['position'])
            screen.blit(frame, rect)

