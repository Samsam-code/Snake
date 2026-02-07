"""
A class to animate a solver through multiple games on a grid.
Use key up and key down to adjust speed.
Use Y / N to play again or quit.

Built using pygame and run_single_test
"""
import pygame
from random import choice
from random import seed as rand_set_seed
from GridsAndGraphs.Adjacencies import find_adjacency_grid


BG_COLOR    = (0, 0, 0)
BODY_COLOR  = (0, 200, 0)
HEAD_COLOR  = (0, 100, 0)
APPLE_COLOR = (255, 0, 0)
LINE_COLOR  = (255, 255, 255)

BOARD_SIZE = 600
SEG_MARGIN = 4
BANNER_HEIGHT = 40
RECT_EXPAND = 1

class GridAnimator():
    def __init__(self, m, n, solver, FPS=10):
        CELL = BOARD_SIZE // n
        RADIUS = CELL//2 - SEG_MARGIN
        self.CELL = CELL
        self.RADIUS = RADIUS

        self.adjacency = find_adjacency_grid(m, n)

        self.index_to_rect  = [(j*CELL, i*CELL + BANNER_HEIGHT)
                                for i in range(m) for j in range(n)]

        self.index_to_centre = [(j*CELL + CELL//2, i*CELL + CELL//2 + BANNER_HEIGHT)
                                for i in range(m) for j in range(n)] 
        self.solver = solver
        self.area = m * n
        self.fps = FPS
        
        self.height = n*CELL
        self.create_board_layers(n*CELL, m*CELL + BANNER_HEIGHT)
        self.paused = False

    def animate_single_game(self, seed=None):  
        if seed != None:
            rand_set_seed(seed) 
        area = self.area
        solver = self.solver
        adjacency = self.adjacency
        vertices = list(range(area))
        occupied = [False] * area
        next_tail = [None] * area
        start = choice(vertices)
        occupied[start] = True
        head = start
        tail = start
        apple = start
        length = 1
        move_counter = 0
        move_generator = solver.yield_moves_to_simulator(start)
        self.start_new_game(start)
        self.refresh_screen()
        for apples_eaten in range(area-1):
            while occupied[apple]:
                apple = choice(vertices)
            solver.apple = apple
            self.draw_apple(apple)
            self.refresh_screen()
            while True:
                new_head = next(move_generator)
                move_counter += 1
                if new_head not in adjacency[head]:
                    print('ERROR: non-adjacent move!')
                    return None
                if new_head == apple:
                    break
                occupied[tail] = False
                if occupied[new_head]:
                    print('ERROR: collision with body!')
                    return None
                occupied[new_head] = True
                next_tail[head] = new_head
                self.update_snake(head, new_head, tail)
                self.update_banner(length, move_counter)
                self.refresh_screen()
                head = new_head
                tail = next_tail[tail]
            occupied[apple] = True
            next_tail[head] = apple
            self.update_snake(head, apple)
            head = apple
            length += 1
            self.update_banner(length, move_counter)
            self.refresh_screen()
        return move_counter

    def animate_many_games(self):
        # also return scores for user
        scores = []
        while True:
            scores.append(self.animate_single_game())
            if not self.ask_play_again():
                break
        return scores

    def ask_play_again(self):        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return True
                    elif event.key == pygame.K_n:
                        return False
            self.clock.tick(10)   
    
    def create_board_layers(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.full_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        # background, (snake and apple), path, loop are drawn in 4 separate layers
        self.bg_layer    = pygame.Surface(self.screen.get_size())
        self.loop_layer  = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.path_layer  = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.snake_layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.banner_layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        # background design
        self.bg_layer.fill(BG_COLOR)
        # design banner
        self.font = pygame.font.SysFont(None, 28)

    def refresh_screen(self):
        pygame.display.update()
        self.clock.tick(self.fps)
        self.events()
        while self.paused:
            self.events()    

    def start_new_game(self, start):
        # clear all board layers with transparent rectangles
        pygame.draw.rect(self.bg_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.loop_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.path_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.snake_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.banner_layer, (0, 0, 0, 0), self.full_rect)

        # put snake head at start location
        pygame.draw.circle(self.snake_layer, HEAD_COLOR, self.index_to_centre[start], self.RADIUS)
        self.update_banner(1, 0)
        self.screen.blit(self.bg_layer, (0, 0))
        self.screen.blit(self.loop_layer, (0, 0))
        self.screen.blit(self.path_layer, (0, 0))
        self.screen.blit(self.snake_layer, (0, 0))
        self.screen.blit(self.banner_layer, (0, 0))

        self.refresh_screen()
        
    def update_banner(self, length, move_counter):
        banner = self.font.render(f"FPS: {self.fps}   L: {length}   M: {move_counter}", True, (255, 255, 255))
        self.banner_layer.fill(BG_COLOR, pygame.Rect(0, 0, self.height, BANNER_HEIGHT))
        self.banner_layer.blit(banner, (5, 5))
        pygame.draw.line(self.banner_layer, LINE_COLOR, (0, BANNER_HEIGHT-1), (self.height, BANNER_HEIGHT-1), 2)
        self.screen.blit(self.banner_layer, (0, 0))
        pygame.display.update()

    def draw_apple(self, apple):
        centre = self.index_to_centre[apple]
        pygame.draw.circle(self.snake_layer, APPLE_COLOR, centre, self.RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))
        pygame.display.update()
        
    def update_snake(self, old_head, new_head, old_tail = None):
        if old_tail != None and old_tail != old_head:
            self.clear_tail(old_tail)
          
        oh_centre = self.index_to_centre[old_head]
        nh_centre = self.index_to_centre[new_head]
        # draw old_head as body
        pygame.draw.circle(self.snake_layer, BODY_COLOR, oh_centre, self.RADIUS)   
        # delete path under old head
        x, y = self.index_to_rect[old_head]
        rect = pygame.Rect(x, y, self.CELL, self.CELL)
        pygame.draw.rect(
            self.path_layer,
            (0, 0, 0, 0),
            rect
        )   
        # draw new head connected to old head
        self.draw_connection(oh_centre, nh_centre)

        if old_tail == old_head:
            self.clear_tail(old_tail)

        pygame.draw.circle(self.snake_layer, HEAD_COLOR, nh_centre, self.RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))
        
    def clear_tail(self, tail):
        x, y = self.index_to_rect[tail]
        rect = pygame.Rect(x, y, self.CELL, self.CELL)
        pygame.draw.rect(
            self.snake_layer,
            (0, 0, 0, 0),
            rect
            )
        
        # repaint this rectangle
        self.screen.blit(self.bg_layer, rect, rect)
        self.screen.blit(self.loop_layer, rect, rect)
        self.screen.blit(self.path_layer, rect, rect)

    def draw_connection(self, c1, c2):
        cx1, cy1 = c1
        cx2, cy2 = c2
        if cx1 == cx2:
            x = cx1 - self.RADIUS
            y = min(cy1, cy2)
            width = 2 * self.RADIUS
            height = abs(cy1 - cy2)
        else:
            x = min(cx1, cx2)
            y = cy1 - self.RADIUS
            width = abs(cx1 - cx2)
            height = 2 * self.RADIUS
        x = int(x) - RECT_EXPAND
        y = int(y) - RECT_EXPAND
        width = int(width) + 2*RECT_EXPAND
        height = int(height) + 2*RECT_EXPAND
        pygame.draw.rect(self.snake_layer, BODY_COLOR, (x, y, width, height))
    
    def draw_loop(self):
            
        # clear the loop layer
        pygame.draw.rect(self.loop_layer, (0, 0, 0, 0), self.full_rect) 
        self.screen.blit(self.loop_layer, (0, 0))
        self.screen.blit(self.bg_layer, (0, 0))        

        # prevent banner from flashing (not an ideal fix but whatever)
        self.screen.blit(self.banner_layer, (0, 0))   

        # draw planned loop, if exists
        if self.show_loop:
           if hasattr(self.solver, 'loop') and self.solver.loop is not None:
                loop_points = [self.index_to_centre[c] for c in self.solver.loop]
                pygame.draw.lines(
                    self.loop_layer,
                    BODY_COLOR + (180,),
                    True,
                    loop_points,
                    2
                )
        self.screen.blit(self.loop_layer, (0, 0))

    def draw_path(self, head, path):
        

        # draw path to apple
        points = [self.index_to_centre[head]] + [self.index_to_centre[p] for p in path]
        pygame.draw.lines(
            self.path_layer,
            (255, 0, 0, 200),
            False,
            points,
            5
        )
        self.screen.blit(self.path_layer, (0, 0))

        # redraw head on top
        pygame.draw.circle(self.snake_layer, HEAD_COLOR, self.index_to_centre[head], self.RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))  

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if self.fps < 10:
                        self.fps += 1
                    else:
                        self.fps += 10
                elif event.key == pygame.K_DOWN:
                    if self.fps > 10:
                        self.fps -= 10
                    else:
                        self.fps = max(1, self.fps-1)

                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused