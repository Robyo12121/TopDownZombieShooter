import pygame as pg
import settings
import pytmx
from collections import deque
import heapq

# import Path_finding
vec = pg.math.Vector2


def collide_hit_rect(one, two):
    """Check if hit box of one sprite has collided with
        another sprite's rect"""
    return one.hit_rect.colliderect(two.rect)


def heuristic(node1, node2):  # rule of thumb = estimate the distance and prioritize direction
    # manhattan distance
    return (abs(node1.x - node2.x) + abs(node1.y - node2.y)) * 10  # as we multiplied everything by 10 before


def vec2int(v):
    """Convert vector to tuple of ints as vectors not hashable"""
    return (int(v.x), int(v.y))


def breadth_first_search(graph, start, end):
    """Return dict with path from start"""
    frontier = deque()
    frontier.append(start)
    came_from = {}
    came_from[vec2int(start)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
#         if current == end: # Found goal tile, stop searching
#            break # Don't want early exit as it will be used for all zombies everywhere
        for next in graph.find_neighbors(current):
            if vec2int(next) not in came_from:
                frontier.append(next)
                came_from[vec2int(next)] = current - next
    # print(path)
    return came_from


def reconstruct_path(came_from, start, goal):
    """Follow the path back from start"""
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = current + came_from[vec2int(current)]
    path.append(start)  # optional
    # path.reverse()  # optional
    return path


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())  # Strip gets rid of invisible newline chars in text file

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * settings.TILESIZE
        self.height = self.tileheight * settings.TILESIZE


class TiledMap:
    def __init__(self, game, filename):
        """Reads in tilemap using pytmx module
            Extracts some map info from it"""
        self.game = game
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

        # Pathfinding ###
        # self.walls =
        # Down, Up, Right, Left Possible neighbours - not 8 -way
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1)]
        # Diagonals
        self.connections += [vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)]
        self.weights = {}

    def render(self, surface):
        """Takes a pygame surface and draws tile in map onto it"""
        ti = self.tmxdata.get_tile_image_by_gid  # Alias command to ti = tile image # Func gets image specified by its unique gid in tmx file
        for layer in self.tmxdata.visible_layers:  # Get all visible layers in map file.
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        """Create surface to draw map onto"""
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

    # Pathfinding functions ###

    def in_bounds(self, node):
        """Check if a node is outside the map dimensions"""
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        """Returns true if a node isn't in the walls list and can be passed by an entity"""
        return node not in self.game.walls  # self.walls

    def find_neighbors(self, node):
        """Take all possible direction and find neighbours of a nodw
            Filter out - out of bounds nodes and walls
            Return remaining nodes"""
        neighbors = [node + connection for connection in self.connections]
        # don't use this for diagonals
        neighbors = filter(self.in_bounds, neighbors)  # Filters out a node from neighbours if not in map
        neighbors = filter(self.passable, neighbors)  # Filters out if nodes containing walls
        return neighbors

    def cost(self, from_node, to_node):
        if (vec(to_node) - vec(from_node)).length_squared() == 1:  # not diagonal 1**2 == 1
            return self.weights.get(to_node, 0) + 10  # 1 and 1.4 but nice integers instead of fractions
        else:
            return self.weights.get(to_node, 0) + 14


class PriorityQueue:
    """To make it easy to work with heapq"""
    def __init__(self):
        self.nodes = []

    def put(self, node, cost):  # heapq priority is the cost
        heapq.heappush(self.nodes, (cost, node))  # heapq automatically orders queue so that highest priority is the lowest cost

    def get(self):
        return heapq.heappop(self.nodes)[1]  # only get node from queue (not cost)

    def empty(self):
        return len(self.nodes) == 0  # if True stop searching


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)  # Rectangle keeps track of offset amount we need to apply to drawing the map
        self.width = width
        self.height = height

    def apply(self, entity):
        """applies camera move offset to a sprite entity"""
        return entity.rect.move(self.camera.topleft)  # move entity sprite's rectangle by amount given by top left coord of camera

    def apply_rect(self, rect):
        """Applies a camera move to a rectangle"""
        return rect.move(self.camera.topleft)

    def apply_pos(self, pos):
        """Apply camera move to x,y position"""
        pass

    def apply_cursor(self):
        """Applies camera move to cursor position"""
        pass

    def update(self, target):
        """Follow target sprite"""
        x = -target.rect.centerx + int(settings.WIDTH / 2)  # Set x pos of camera to minus the x movement of player - keeping player centered
        y = -target.rect.centery + int(settings.HEIGHT / 2)

        x = min(0, x)  # Prevents x from going below 0
        y = min(0, y)
        x = max(-(self.width - settings.WIDTH), x)  # Prevents x from going lower than
        y = max(-(self.height - settings.HEIGHT), y)
        self.camera = pg.Rect(x, y, self.width, self.height)


if __name__ == '__main__':
    pass
