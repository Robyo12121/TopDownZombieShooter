# KidsCanCode - Game Development with Pygame video series
# Tile-based game - Part 1
# Project setup
# Video link: https://youtu.be/3UxnelT9aCo
import pygame as pg
import sys
from settings import *
from sprites import *
from os import path
from tilemap import *
import random
import AI
import Zombie_States

# HUD functions
def draw_player_stats(surf, x, y, pct, col=None):
    """Passed surface to draw health bar on,
        X, Y coords to draw it,
        Percentage health"""
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x,y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x,y, fill, BAR_HEIGHT)
    if col == None:
        if pct > 0.6:
            col = GREEN
        elif pct > 0.3:
            col = YELLOW
        else:
            col = RED
    else:
        col = col
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 1024)  # increase sound buffer to minise lag when playing sounds
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        #pg.key.set_repeat(10, 100)  # Lets you hold down a key to keep the move going
        self.game_folder = path.dirname(__file__)
        self.load_images()
        self.load_sounds()
        self.player = None
        

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x,y)
        if align == "ne":
            text_rect.topright = (x,y)
        if align == "sw":
            text_rect.bottomleft = (x,y)
        if align == "se":
            text_rect.bottomright = (x,y)
        if align == "n":
            text_rect.midtop = (x,y)
        if align == "s":
            text_rect.midbottom = (x,y)
        if align == "e":
            text_rect.midright = (x,y)
        if align == "w":
            text_rect.midleft = (x,y)
        if align == "center":
            text_rect.center = (x,y)
        self.screen.blit(text_surface, text_rect)

    def load_images(self):
        # Define game folders
        image_folder = path.join(self.game_folder, 'images')
        # Load images from files
        self.title_font = path.join(image_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(image_folder, 'Impacted2.0.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        self.player_imgs = {}
        for img in PLAYER_IMGS:
            self.player_imgs[img] = pg.image.load(path.join(image_folder, PLAYER_IMGS[img])).convert_alpha()
        self.wall_img = pg.image.load(path.join(image_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.mob_img = pg.image.load(path.join(image_folder, MOB_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(image_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['lg'] = pg.transform.scale(self.bullet_images['lg'], (5,5))        
        self.splat = pg.image.load(path.join(image_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_smoke = []
        for img in MUZZLE_SMOKE:
            self.gun_smoke.append(pg.image.load(path.join(image_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(image_folder, ITEM_IMAGES[item])).convert_alpha()
        # Lighting
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOUR)
        self.light_mask = pg.image.load(path.join(image_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def load_sounds(self):
        sound_folder = path.join(self.game_folder, 'sounds')
        self.music_folder = path.join(self.game_folder, 'music')
        # Load initial music - define user event to trigger when it ends, picked up in events()
        self.SONG_END = pg.USEREVENT + 1
        self.current_song = random.choice(BG_MUSIC)
        pg.mixer.music.set_endevent(self.SONG_END)
        pg.mixer.music.load(path.join(self.music_folder, self.current_song))
        pg.mixer.music.set_volume(BG_MUSIC_LEVEL)
        # Effects
        self.effects_sounds = {}
        for eff in EFFECTS_SOUNDS:
            self.effects_sounds[eff] = pg.mixer.Sound(path.join(sound_folder, EFFECTS_SOUNDS[eff]['file']))
            self.effects_sounds[eff].set_volume(EFFECTS_SOUNDS[eff]['volume'])
                
        # Weapons
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for sound in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(sound_folder, sound))
                s.set_volume(GUN_SOUND_LEVEL)
                self.weapon_sounds[weapon].append(s)
        #  Zombies
        self.zombie_moan_sounds = []
        for sound in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, sound))
            s.set_volume(ZOMBIE_MOAN_LEVEL)
            self.zombie_moan_sounds.append(s)
        self.zombie_hit_sounds = []
        for sound in ZOMBIE_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, sound))
            s.set_volume(ZOMBIE_HIT_LEVEL)
            self.zombie_hit_sounds.append(s)
        # Player 
        self.player_hit_sounds = []
        for sound in PLAYER_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, sound))
            s.set_volume(PLAYER_HIT_LEVEL)
            self.player_hit_sounds.append(s)
        self.player_pain_sounds = []
        for sound in PLAYER_PAIN_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, sound))
            s.set_volume(PLAYER_PAIN_LEVEL)
            self.player_pain_sounds.append(s)
        self.player_panic_sounds = []
        for sound in PLAYER_PANIC_SOUNDS:
            s = pg.mixer.Sound(path.join(sound_folder, sound))
            s.set_volume(PLAYER_PANIC_LEVEL)
            self.player_panic_sounds.append(s)
        
    def new(self):
        """For things that should happen once, at the start of a new game"""
        # Load map from file
        self.map_folder = path.join(self.game_folder, 'maps')
        #self.map = Map(path.join(game_folder, 'map.txt'))
        self.map = TiledMap(self, path.join(self.map_folder, MAP_NAME))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        #self.paths = breadth_first_search(self.map, self
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        
        

        #For Loading map from tmx data
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width/2, tile_object.y + tile_object.height/2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y) #For EM all entities must have unique id
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'pistol']:
                Item(self, obj_center, tile_object.name)

##        self.EM = AI.EntityManager()
        for mob in self.mobs:
            #self.EM.add_entity(mob.id) #All entities must have a unique id
            mob.SM.current_state = Zombie_States.Idle(self, mob)
            mob.SM.global_state = Zombie_States.ZombieGlobalState(self, mob)

                        
        assert self.player is not None
        self.camera = Camera(self.map.width, self.map.height) #Give camera total size of map
        # Flags
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.effects_sounds['level_start'].play()

        
        
    def run(self):
        pg.mixer.music.play()
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        """For things that should happen every frame"""
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player) # Call camera.update - give player as target to follow

        # Game over condition - No more zombies
##        if len(self.mobs) == 0:
##            self.playing = False
        
        #Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            now = pg.time.get_ticks()
            if now - hit.last_hit > MOB_HIT_TIMEOUT and random.random() < MOB_HIT_CHANCE:
                hit.last_hit = now
                #self.player.health -= MOB_DAMAGE
                hit.vel = vec(0,0)
                choice(self.player_hit_sounds).play()
                if self.player.health <= 0:
                    self.playing = False
                self.player.got_hit()
                self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # Bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            #hit.draw_health()
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0,0)

        # Player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)

            if hit.type in WEAPONS.keys():
                hit.kill()
                self.player.pickup(hit.type)
                #print(hit.type)
        
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, GREEN, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, GREEN, (0, y), (WIDTH, y))
            
    def render_fog(self):
        #draw light mask (gradient) onto fog image
        self.fog.fill((NIGHT_COLOUR))
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0,0), special_flags=pg.BLEND_MULT)
        
    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))        
        #self.draw_grid()
        #self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite)) # blit all sprites to screen in location of where the camera says the sprite is
##            if self.draw_debug:
##                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)              

        if self.night:
            self.render_fog()
        # DEBUG HUD
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
            for sprite in self.all_sprites:
                if isinstance(sprite, Mob):
                    sprite.draw_health()
                    pg.draw.circle(self.screen, CYAN, (self.camera.apply(sprite).centerx,self.camera.apply(sprite).centery), sprite.detect_radius, 1)
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
                

        #HUD functions
        draw_player_stats(self.screen, 10, 10, (self.player.health / PLAYER_HEALTH))
        draw_player_stats(self.screen, 10, 40, (self.player.fatigue / PLAYER_FATIGUE), BEIGE)
        self.draw_text("Zombies: {}".format(len(self.mobs)), self.hud_font, 30, WHITE,
                       WIDTH - 10, 10, align="ne")
        if self.player.weapon != None:
            self.draw_text("{}:{}".format(self.player.weapon.name,self.player.weapon.remaining_shots), self.hud_font, 30, WHITE,
                           10, HEIGHT-50, align="nw")
     
        # Paused
        if self.paused:
            self.screen.blit(self.dim_screen, (0,0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH/2, HEIGHT/2, align='center')
        pg.display.flip()

    def play_new_song(self):
        next_song = random.choice(BG_MUSIC)
        self.current_song = next_song
        #pg.mixer.music.load(next_song)
        pg.mixer.music.load(path.join(self.music_folder, next_song))
        pg.mixer.music.play()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
##                print(event.button)
                if event.button == 1:
                    self.player.shoot()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_n:
                    self.night = not self.night
                ##### THIS IS SPRITE SPECIFIC CODE - SHOULDN'T BE HERE ####
                if event.key == pg.K_r:
                    self.player.reload()
                if event.key == pg.K_SPACE:
                    self.player.cycle_weapon()                    
                if event.key == pg.K_g:
                    self.player.print_inventory()
            if event.type == self.SONG_END:
                self.play_new_song()   

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        pg.mixer.fadeout(5000)
        self.draw_text("GAME OVER", self.title_font, 180, RED, WIDTH/2, HEIGHT/2, align='center')
        self.draw_text("Press any key to start", self.title_font, 75, WHITE, WIDTH/2, HEIGHT*3/4, align='center')
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait() # Clears event queue
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()

                if event.type == pg.KEYUP:
                    waiting = False

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
