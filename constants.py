SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

ASTEROID_MIN_RADIUS = 18
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 0.8
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS * .60
PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_MAX_HEALTH = 100
PLAYER_HEALTH_REGEN_RATE = 1.0

PLAYER_SHOT_COUNTDOWN = 0.3
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500

# Score related constants
SCORE_LARGE_ASTEROID = 100
SCORE_MEDIUM_ASTEROID = 50
SCORE_SMALL_ASTEROID = 25
FONT_SIZE = 24

# Sound related constants
SOUND_ENABLED = True
MUSIC_VOLUME = 0.5  # 0.0 to 1.0
SFX_VOLUME = 0.7    # 0.0 to 1.0

# UFO related constants
UFO_RADIUS = 30
UFO_SPEED = 120
UFO_SHOOT_COUNTDOWN = 2.0  # Seconds between shots
UFO_SPAWN_RATE = 15.0  # Seconds between UFO spawns
UFO_SCORE = 300
UFO_SHOOT_SPEED = 350

# Enhanced asteroid types
ASTEROID_TYPE_REGULAR = 0
ASTEROID_TYPE_EXPLOSIVE = 1
ASTEROID_TYPE_ARMORED = 2

# Explosive asteroid constants
EXPLOSIVE_PROJECTILE_COUNT = 4
EXPLOSIVE_PROJECTILE_SPEED = 200

# Armored asteroid constants
ARMORED_HITS_REQUIRED = 3

# Enemy projectile constants
ENEMY_SHOT_RADIUS = 4

# Difficulty levels
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2

# Difficulty modifiers (spawn rate multiplier, asteroid speed multiplier, score multiplier)
DIFFICULTY_MODIFIERS = {
    DIFFICULTY_EASY: {
        'spawn_rate_multiplier': 1.5,  # Slower spawn rate (higher number = slower)
        'asteroid_speed_multiplier': 0.7,  # Slower asteroids
        'score_multiplier': 0.8,  # Lower score
        'ufo_spawn_multiplier': 1.5,  # Less frequent UFOs
    },
    DIFFICULTY_NORMAL: {
        'spawn_rate_multiplier': 1.0,  # Normal spawn rate
        'asteroid_speed_multiplier': 1.0,  # Normal asteroid speed
        'score_multiplier': 1.0,  # Normal score
        'ufo_spawn_multiplier': 1.0,  # Normal UFO frequency
    },
    DIFFICULTY_HARD: {
        'spawn_rate_multiplier': 0.6,  # Faster spawn rate (lower number = faster)
        'asteroid_speed_multiplier': 1.3,  # Faster asteroids
        'score_multiplier': 1.5,  # Higher score
        'ufo_spawn_multiplier': 0.7,  # More frequent UFOs
    }
}

# Difficulty names for display
DIFFICULTY_NAMES = {
    DIFFICULTY_EASY: "Easy",
    DIFFICULTY_NORMAL: "Normal",
    DIFFICULTY_HARD: "Hard"
}

# Ammo system constants
AMMO_MAX_SHOTS = 80  # Maximum number of shots player can have
AMMO_INITIAL = 25  # Starting ammo
AMMO_RECHARGE_RATE = 2.0  # Seconds per ammo recharge
AMMO_RECHARGE_AMOUNT = 3  # How many ammo points recharged at once

# Power-up types
POWERUP_AMMO = 0
POWERUP_FIRE_RATE = 1
POWERUP_SCORE = 2
POWERUP_INVINCIBILITY = 3

# Power-up constants
POWERUP_RADIUS = 15
POWERUP_SPAWN_CHANCE = 0.3  # 30% chance to spawn when asteroid is destroyed
POWERUP_LIFETIME = 10.0  # How long power-ups stay on screen before disappearing
POWERUP_DRIFT_SPEED = 15  # Slow drift speed for floating effect

# Power-up effect durations (seconds)
POWERUP_FIRE_RATE_DURATION = 5.0
POWERUP_FIRE_RATE_MULTIPLIER = 0.3  # Lower is faster (30% of normal cooldown)
POWERUP_INVINCIBILITY_DURATION = 4.0
POWERUP_AMMO_AMOUNT = 5  # Amount of ammo to add
POWERUP_SCORE_AMOUNT = 500  # Score bonus

# Player lives system
PLAYER_INITIAL_LIVES = 3
PLAYER_RESPAWN_TIME = 2.0  # Seconds before respawning
PLAYER_SPAWN_INVULNERABILITY_TIME = 3.0  # Seconds of invulnerability after respawn
