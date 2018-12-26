import pygame as pg
from settings import *
from random import uniform, choice
from sprites import BaseGameEntity, collide_with_walls
# import pathfinding
import AI
# from math import acos
import logging

vec = pg.math.Vector2
logger = logging.getLogger('game.Game.mob_class')
logger.debug(f"logging from game.Game.mob_class")


class Mob(pg.sprite.Sprite, BaseGameEntity):
    def __init__(self, game, x, y):
        BaseGameEntity.__init__(self)
        self.logger = logging.getLogger('game.Game.Mob')
        self.logger.debug("Creating mob")
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()  # more than one mob
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)  # Acceleration to delay movement speed
        self.rect.center = self.pos
        self.rot = uniform(0, 360)
        self.direction = vec(self.rot, 0).normalize
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.health = MOB_HEALTH
        self.speed = choice(MOB_WANDER_SPEEDS)
        self.detect_radius = MOB_DETECT_BASE
        self.target = None
        self.alerted = False
        self.last_hit = 0
        self.current_target = None
        self.last_path_update = 0
        self.first = False
        self.last_known = None
        self.last_known_grid = None
        self.path = None
        self.last_wander = 0

        self.SM = AI.State_Machine(self)

#    def follow_path(self, path, current_target):
#        """Sets target to first item in path and once sprite reaches it change to the
#            next target"""
#        if path == None:
#            return self.game.player.pos
#        if self.grid_pos == current_target:
#            index = path.index(current_target)
#            try:
#                self.target = path[index + 1]
#            except IndexError:
#                return self.game.player.pos
#            print("Changing target: {}".format(self.target))
#            return self.target
#        else:
#            print("Keeping target: {}".format(current_target))
#            return current_target

#    def move_set_path(self):
#        """move along a preset series of grid squares"""
#        if self.grid_pos == self.path[
#        pass
    def arrived(self, target):
        assert isinstance(target, vec)
        target_dist = self.pos - target
        if target_dist.length_squared() > MOB_NEARBY_DIST:
            return False
        else:
            return True

    def wander(self, wander_speed=choice(MOB_WANDER_SPEEDS), target_change_time=MOB_WANDER_TIME):
        now = pg.time.get_ticks()
        if self.target is None:
            self.target = self.get_rand_nearby_point()

        if now - self.last_wander > target_change_time:
            self.logger.info("performing wander...")
            self.last_wander = now
            self.target = self.get_rand_nearby_point()

        if self.arrived(self.target):
            self.vec = vec(0, 0)
        else:
            self.move_to_target(self.target)

        # pg.draw.line(self.image, RED, self.pos, self.target, 7)
        # move that way for a few seconds
        # stop for a few seconds
        # repeat

    def get_rand_nearby_point(self):
        del_x = uniform(-self.detect_radius, self.detect_radius)
        del_y = uniform(-self.detect_radius, self.detect_radius)
        offset = vec(del_x, del_y)
        return self.pos + offset * 2

    def face_target(self, target):
        """Accepts a position """
        assert isinstance(target, vec)
        target_vec = target - self.pos  # vector from first pos to target pos
        self.rot = target_vec.angle_to(vec(1, 0))  # get angle between current target and 'east'.
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos  # away from other mob
                if 0 < dist.length() < MOB_AVOID_RADIUS:
                    self.acc += dist.normalize()

    def seek(self, target):
        """Given a target, return a seek vector to face it
        at a given speed"""
        self.desired = (target - self.pos).normalize() * self.speed
        steer = (self.desired - self.vel)
        if steer.length() > MOB_SEEK_FORCE:
            steer.scale_to_length(MOB_SEEK_FORCE)
        return steer

    def move_to_target(self, target):
        """Moves to a specific point"""
        # target = vec2int(target)
        if target is None:
            return
        target = vec(target)
        self.face_target(target)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # Mob movement
        # self.acc = vec(1, 0).rotate(-self.rot)
        # self.acc = self.seek(self.path_to_player(next))
        # self.acc = self.seek(self.game.player.pos)
        self.acc = self.seek(target)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        # Equation of motion Pos = Vt + 0.5*Acc + (t^2) ?
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.grid_pos = (self.pos.x // TILESIZE, self.pos.y // TILESIZE)
        # Mob collisions
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

#    def pathfind_a_star(self):
#        now = pg.time.get_ticks()
#        self.start = vec(self.grid_pos)
#        self.goal = vec(self.game.player.grid_pos)
#        print("Start: {}, Goal: {}".format(self.start, self.goal))

#        if now - self.last_path_update > MOB_PATH_UPDATE:
#            print(now-self.last_path_update)
#            print("Updating search")
#            print("Z: {}, P: {}".format(self.start, self.goal))
#            path,cost = a_star_search(self.game.map, self.start, self.goal)
#            #self.draw_path(path,self.start, self.goal)
#            self.path = reconstruct_path(path, self.start, self.goal)
#            self.last_path_update = now
#            self.target = vec2int(self.path[0])

#        self.target = self.follow_path(self.path, self.target)
#        self.move(self.target)

#    def bfs_map_follow(self):
#        path = self.game.map.reconstruct_path(

#        player_dist = player.pos - self.pos
#        player_direction = player_dist.normalize()
#        dot_product = self_rot_norm.dot(player_rot_norm)
#        angle_to_player = acos(dot_product)
#        print(angle_to_player)
#        self.update_radius(player.vel)

    def test_for_player(self, player):
        if self.pos.distance_squared_to(player.pos) < self.detect_radius**2:
            # dot_product =
            return True
        else:
            return False

    def update(self):
        # Things to do every frame
        self.SM.update()
        self.direction = vec(self.rot, 0).normalize
#        print(self.direction[0], self.direction[1])
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
        self.draw_health()

    def draw_health(self):
        if self.health < MOB_HEALTH:
            if self.health > 60:
                col = GREEN
            elif self.health > 30:
                col = YELLOW
            else:
                col = RED
            width = int(self.rect.width * self.health / MOB_HEALTH)
            self.health_bar = pg.Rect(0, 0, width, 7)
            pg.draw.rect(self.image, col, self.health_bar)
