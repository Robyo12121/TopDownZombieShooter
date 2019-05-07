import pygame as pg
import heapq
from collections import deque

# from sprites import Player

vec = pg.math.Vector2

TILESIZE = 48
GRIDWIDTH = 28
GRIDHEIGHT = 15
WIDTH = TILESIZE * GRIDWIDTH

HEIGHT = TILESIZE * GRIDHEIGHT
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
MEDGRAY = (75, 75, 75)
LIGHTGRAY = (140, 140, 140)

pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

font_name = pg.font.match_font('hack')


def draw_text(text, size, color, x, y, align="topleft"):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        # Down, Up, Right, Left Possible neighbours - not 8 -way
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1)]
        # Diagonals
        self.connections += [vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)]

    def in_bounds(self, node):
        """Check if a node is outside the map dimensions"""
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        """Returns true if a node isn't in the walls list and can be passed by an entity"""
        return node not in self.walls

    def find_neighbors(self, node):
        """Take all possible direction and find neighbours of a nodw
            Filter out - out of bounds nodes and walls
            Return remaining nodes"""
        neighbors = [node + connection for connection in self.connections]
        # don't use this for diagonals
        neighbors = filter(self.in_bounds, neighbors)  # Filters out a node from neighbours if not in map
        neighbors = filter(self.passable, neighbors)  # Filters out if nodes containing walls
        return neighbors

    def draw(self):
        """Draw each wall"""
        for wall in self.walls:
            rect = pg.Rect(wall * TILESIZE, (TILESIZE, TILESIZE))
            pg.draw.rect(screen, LIGHTGRAY, rect)


class WeightedGrid(SquareGrid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.weights = {}  # k,v = grid_loc, cost

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


def heuristic(a, b):  # rule of thumb = estimate the distance and prioritize direction
    # manhattan distance
    (x1, y1) = a
    (x2, y2) = b
    return (abs(x1 - x2) + abs(y1 - y2)) * 10  # as we multiplied everything by 10 before


def dijkstra_search(graph, start, goal):
    frontier = PriorityQueue()  # heapq
    frontier.put(vec2int(start), 0)  # doesn't cost to move to tile already on
    came_from = {}  # dict of unit vector directions
    cost_so_far = {}  # cost to move to each square
    came_from[vec2int(start)] = None
    cost_so_far[vec2int(start)] = 0

    while not frontier.empty():
        current = frontier.get()  # look at next one (automatically lowest cost from heapq)
        if current == goal:  # could leave this out if you want to look at all paths for whole map
            break
        for next in graph.find_neighbors(vec(current)):  # l
            next = vec2int(next)
            new_cost = cost_so_far[current] + graph.cost(current, next)  # calc current cost plus cost of next square
            if next not in cost_so_far or new_cost < cost_so_far[next]:  # if we haven't looked at it before or we have and it had a lower cost then
                cost_so_far[next] = new_cost  # update values
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = vec(current) - vec(next)
    return came_from, cost_so_far


def a_star_search(graph, start, goal):
    frontier = PriorityQueue()  # heapq
    frontier.put(vec2int(start), 0)  # doesn't cost to move to tile already on
    came_from = {}  # dict of unit vector directions
    cost_so_far = {}  # cost to move to each square
    came_from[vec2int(start)] = None
    cost_so_far[vec2int(start)] = 0

    while not frontier.empty():
        current = frontier.get()  # look at next one (automatically lowest cost from heapq)
        if current == goal:  # could leave this out if you want to look at all paths for whole map
            break
        for next in graph.find_neighbors(vec(current)):  # l
            next = vec2int(next)
            new_cost = cost_so_far[current] + graph.cost(current, next)  # calc current cost plus cost of next square
            if next not in cost_so_far or new_cost < cost_so_far[next]:  # if we haven't looked at it before or we have and it had a lower cost then
                cost_so_far[next] = new_cost  # update values
                priority = new_cost + heuristic(goal, vec(next))
                frontier.put(next, priority)
                came_from[next] = vec(current) - vec(next)
    return came_from, cost_so_far


def draw_grid():
    for x in range(0, WIDTH, TILESIZE):
        pg.draw.line(screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILESIZE):
        pg.draw.line(screen, LIGHTGRAY, (0, y), (WIDTH, y))


def vec2int(v):
    """Convert vector to tuple of ints as vectors not hashable"""
    return (int(v.x), int(v.y))


def draw_icons(home_img, cross_img):
    start_center = (goal.x * TILESIZE + TILESIZE / 2, goal.y * TILESIZE + TILESIZE / 2)
    screen.blit(home_img, home_img.get_rect(center=start_center))
    goal_center = (start.x * TILESIZE + TILESIZE / 2, start.y * TILESIZE + TILESIZE / 2)
    screen.blit(cross_img, cross_img.get_rect(center=goal_center))


def breadth_first_search(graph, start, end):
    """Return dict with path from start"""
    frontier = deque()
    frontier.append(start)
    came_from = {}
    came_from[vec2int(start)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
        if current == end:  # Found goal tile, stop searching
            break
        for next in graph.find_neighbors(current):
            if vec2int(next) not in came_from:
                frontier.append(next)
                came_from[vec2int(next)] = current - next
    # print(path)
    return came_from


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[vec2int(current)]
    # path.append(start)
    # path.reverse()
    return path


def load():
    icon_dir = path.join(path.dirname(__file__), './icons')
    home_img = pg.image.load(path.join(icon_dir, 'home1.png')).convert_alpha()
    home_img = pg.transform.scale(home_img, (50, 50))
    home_img.fill((0, 255, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
    cross_img = pg.image.load(path.join(icon_dir, 'cross.png')).convert_alpha()
    cross_img = pg.transform.scale(cross_img, (50, 50))
    cross_img.fill((255, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
    arrows = {}
    arrow_img = pg.image.load(path.join(icon_dir, 'arrowRight.png')).convert_alpha()
    arrow_img = pg.transform.scale(arrow_img, (50, 50))
    images = {'arrow': arrow_img,
              'home': home_img,
              'cross': cross_img}
    return images, arrows


if __name__ == '__main__':
    images, arrows = load()
    for k in images:
        print(k)

    for dir in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        arrows[dir] = pg.transform.rotate(images['arrow'], vec(dir).angle_to(vec(1, 0)))

    g = WeightedGrid(GRIDWIDTH, GRIDHEIGHT)
    walls = [(10, 7), (11, 7), (12, 7), (13, 7), (14, 7), (15, 7), (16, 7), (7, 7), (6, 7), (5, 7), (5, 5), (5, 6), (1, 6), (2, 6), (3, 6), (5, 10), (5, 11), (5, 12), (5, 9), (5, 8), (12, 8), (12, 9), (12, 10), (12, 11), (15, 14), (15, 13), (15, 12), (15, 11), (15, 10), (17, 7), (18, 7), (21, 7), (21, 6), (21, 5), (21, 4), (21, 3), (22, 5), (23, 5), (24, 5), (25, 5), (18, 10), (20, 10), (19, 10), (21, 10), (22, 10), (23, 10), (14, 4), (14, 5), (14, 6), (14, 0), (14, 1), (9, 2), (9, 1), (7, 3), (8, 3), (10, 3), (9, 3), (11, 3), (2, 5), (2, 4), (2, 3), (2, 2), (2, 0), (2, 1), (0, 11), (1, 11), (2, 11), (21, 2), (20, 11), (20, 12), (23, 13), (23, 14), (24, 10), (25, 10), (6, 12), (7, 12), (10, 12), (11, 12), (12, 12), (5, 3), (6, 3), (5, 4)]
    for wall in walls:
        g.walls.append(vec(wall))
    print(g.walls)
    goal = vec(10, 2)
    start = vec(20, 6)

    search_type = a_star_search
    path, c = a_star_search(g, goal, start)
    # print(path)
    running = True
    while running:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    if search_type == a_star_search:
                        search_type = dijkstra_search
                    else:
                        search_type = a_star_search
                    path, c = search_type(g, goal, start)
                    print(path)
                    actual_path = reconstruct_path(path, start, goal)
                    print("CAME_FROM: {}, ACTUAL: {}".format(path, actual_path))
                if event.key == pg.K_m:
                    # dump the wall list for saving
                    print([(int(loc.x), int(loc.y)) for loc in g.walls])
            if event.type == pg.MOUSEBUTTONDOWN:
                mpos = vec(pg.mouse.get_pos()) // TILESIZE
                if event.button == 1:
                    if mpos in g.walls:
                        g.walls.remove(mpos)
                    else:
                        g.walls.append(mpos)
                if event.button == 2:
                    start = mpos
                if event.button == 3:
                    goal = mpos
                path, c = search_type(g, goal, start)
                print(path)
                actual_path = reconstruct_path(path, start, goal)
                print(actual_path)

        pg.display.set_caption("{:.2f}".format(clock.get_fps()))
        screen.fill(DARKGRAY)
        # fill explored area
        for node in path:
            x, y = node
            rect = pg.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            pg.draw.rect(screen, MEDGRAY, rect)
        draw_grid()
        g.draw()
        # Draw path from start to goal
        current = start  # + path[vec2int(start)]
        path_length = 0
        while current != goal:
            v = path[(current.x, current.y)]
            if v.length_squared() == 1:
                path_length += 10
            else:
                path_length += 14
            img = arrows[vec2int(v)]
            x = current.x * TILESIZE + TILESIZE / 2
            y = current.y * TILESIZE + TILESIZE / 2
            r = img.get_rect(center=(x, y))
            screen.blit(img, r)
            # Find next node in path
            current = current + path[vec2int(current)]

        draw_icons(images['home'], images['cross'])
        draw_text(search_type.__name__, 30, GREEN, WIDTH - 10, HEIGHT - 10, align="bottomright")
        draw_text('Path length:{}'.format(path_length), 30, GREEN, WIDTH - 10, HEIGHT - 45, align="bottomright")
        pg.display.flip()
