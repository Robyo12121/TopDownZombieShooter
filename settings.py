import pygame as pg
vec = pg.math.Vector2
# Colours (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
BEIGE = (150, 165, 50)
CYAN = (0, 255, 255)
# Game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 100
TITLE = "Tilemap Demo"
BGCOLOR = BROWN
TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE
MAP_NAME = 'level1.tmx'
#Player settings
PLAYER_SPRINT_SPEED = 300
PLAYER_NORMAL_SPEED = 200 #PIXELS per second
PLAYER_WALK_SPEED = 100
PLAYER_ROT_SPEED = 400 # Degrees per frame?
PLAYER_IMGS = {'gun': 'survivor1_gun.png',
               'stand': 'survivor1_stand.png',
               'hold': 'survivor1_hold.png'}
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)
PLAYER_HEALTH = 100
PLAYER_FATIGUE = 15000 # ms
PLAYER_FATIGUE_RATE =  100# ?
PLAYER_FATIGUE_REGEN_STATIONARY = 40 # * 1000 ms/s
PLAYER_FATIGUE_REGEN_WALKING = 30 # * 1000 ms/s
PLAYER_FATIGUE_REGEN_NORMAL = 10 # ?
PLAYER_INFECTION_CHANCE = 0.05
PLAYER_INFECTION_AMOUNT = 1
PLAYER_INFECTION_INTERVAL = 5000
PLAYER_INFECTION_AMOUNT = 0.5

WALL_IMG = 'tileGreen_39.png'

#Mob
MOB_IMG = 'zombie1_hold.png'
MOB_SPRINT_SPEEDS = [200, 150, 175, 100, 125, 150, 150, 300, 300]
MOB_WANDER_SPEEDS = [50, 20, 60, 40, 30]
MOB_HIT_RECT = pg.Rect(0,0,30,30)
MOB_HEALTH = 100
MOB_DAMAGE = 2
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
MOB_DETECT_BASE = 200
MOB_LOSE_DETECT = 400
MOB_DETECT_MOD = 0.25
MOB_ATTACK_RADIUS = 50
MOB_SEEK_FORCE = 0.1
MOB_HIT_CHANCE = 0.05
MOB_HIT_TIMEOUT = 1000 # ms
MOB_SOUND_CHANCE_DETECT_PLAYER = 0.004 #random.random()
MOB_PATH_UPDATE = 3000
MOB_SUSP_TIME = 10000

# Weapon Settings
BULLET_IMG = 'bulletBeige.png'
WEAPONS = {'pistol':{'name': 'pistol',
                     'bullet_speed': 3000,
                     'bullet_lifetime': 1000,
                     'rate': 500,
                     'recoil': 50,
                     'reload_time': 1500,
                     'capacity': 12,
                     'spread': 3,
                     'damage': 30,
                     'bullet_size': 'lg',
                     'bullet_count': 1,
                     #'sound': ['gun/pistol.wav']
                     },
           'shotgun':{'name':'shotgun',
                      'bullet_speed': 3000,
                     'bullet_lifetime': 1000,
                     'rate': 900,
                     'recoil': 200,
                     'reload_time': 1500,
                     'capacity': 6,
                     'spread': 8,
                     'damage': 5,
                     'bullet_size': 'lg',
                     'bullet_count': 12,
                     #'sound': ['gun/shotgun.wav']
                      }
           }
# Effects
MUZZLE_SMOKE = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png','whitePuff18.png']
SMOKE_DURATION = 40
SPLAT = 'splat green.png'
DAMAGE_ALPHA = [i for i in range(0,255,55)]
NIGHT_COLOUR = (50,50,50)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'obj_shotgun.png',
               'pistol': 'pistol.png'} #in images folder
HEALTH_PACK_AMOUNT = 100
BOB_RANGE = 15
BOB_SPEED = 0.5

# Sounds
DEATH_SCREEN_MUSIC = []
BG_MUSIC = ['samples/stinger_0.ogg','samples/stinger_1.ogg','samples/suspense_0.ogg',
                      'samples/suspense_1.ogg','samples/suspense_2.ogg','samples/suspense_3.ogg',
                      'samples/suspense_4.ogg','samples/suspense_5.ogg','samples/suspense_6.ogg',
                      'samples/suspense_7.ogg','samples/suspense_8.ogg','samples/suspense_9.ogg',
                      'samples/suspense_10.ogg','samples/suspense_11.ogg','samples/suspense_12.ogg',
                      'samples/suspense_13.ogg','samples/suspense_14.ogg','samples/suspense_15.ogg',
                      'samples/suspense_16.ogg','samples/suspense_17.ogg','samples/suspense_18.ogg',
                      'samples/suspense_19.ogg','samples/suspense_20.ogg','samples/suspense_21.ogg',
                      'samples/suspense_22.ogg','samples/suspense_23.ogg','samples/suspense_24.ogg',
                      'samples/suspense_25.ogg','samples/suspense_26.ogg','samples/suspense_27.ogg',
                      'samples/suspense_28.ogg','samples/suspense_29.ogg','samples/suspense_30.ogg',
                      'samples/suspense_31.ogg','samples/suspense_32.ogg','samples/suspense_33.ogg',
                      'samples/suspense_34.ogg','samples/suspense_35.ogg','samples/suspense_36.ogg',
                      'samples/suspense_37.ogg']
PLAYER_PAIN_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
PLAYER_HIT_SOUNDS = ['zombie/z_hit_0.ogg', 'zombie/z_hit_1.ogg', 'zombie/z_hit_2.ogg', 'zombie/z_hit_3.ogg',
                     'zombie/z_hit_4.ogg', 'zombie/z_hit_5.ogg', 'zombie/z_hit_6.ogg']
PLAYER_PANIC_SOUNDS = ['panic/panic_0.ogg', 'panic/panic_1.ogg']
ZOMBIE_MOAN_SOUNDS = ['zombie/spotted_0.ogg','zombie/spotted_1.ogg','zombie/spotted_2.ogg','zombie/spotted_3.ogg',
                      'zombie/spotted_5.ogg','zombie/spotted_6.ogg','zombie/spotted_7.ogg','zombie/spotted_8.ogg',
                      'zombie/spotted_8.ogg','zombie/spotted_9.ogg','zombie/spotted_10.ogg','zombie/spotted_11.ogg',
                      'zombie/spotted_12.ogg','zombie/spotted_13.ogg',]
ZOMBIE_HIT_SOUNDS = ['zombie/splat-15.wav']
WEAPON_SOUNDS = {'pistol':['gun/pistol.wav'],
                 'shotgun':['gun/shotgun.wav']
                 }
EFFECTS_SOUNDS = {'level_start': {'file': 'level_start.wav', 'volume': 0.1},
                  'health_up': {'file': 'items/health_pack.wav','volume': 0.1},
                  'gun_pickup': {'file': 'gun/gun_pickup.wav','volume': 0.1}}
# Sound levels
ZOMBIE_MOAN_LEVEL = 0.4
BG_MUSIC_LEVEL = 0.1
EFFECTS_LEVEL = 0.5
PLAYER_HIT_LEVEL = 0.5
ZOMBIE_HIT_LEVEL = 0.5
PLAYER_PAIN_LEVEL = 0.5
PLAYER_PANIC_LEVEL = 0.5
GUN_SOUND_LEVEL = 0.5
