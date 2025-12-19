"""
A class to animate a solver through multiple games on a grid.
Use key up and key down to adjust speed.
Use Y / N to play again or quit.

Built using pygame, upon run_single_test
"""
import pygame
from random import choice
from collections import deque
from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency

BG_COLOR    = (0, 0, 0)
BODY_COLOR  = (0, 200, 0)
HEAD_COLOR  = (0, 100, 0)
APPLE_COLOR = (255, 0, 0)
LINE_COLOR  = (255, 255, 255)

FPS_DEFAULT = 1
CELL = 100
SEG_MARGIN = 4
SCORE_HEIGHT = 40
RECT_EXPAND = 1

RADIUS = CELL//2 - SEG_MARGIN

class GridAnimator():
    def __init__(self, m, n, solver):
        self.adjacency = find_grid_adjacency(m, n)

        self.index_to_rect  = [(j*CELL, i*CELL + SCORE_HEIGHT)
                                for i in range(m) for j in range(n)]

        self.index_to_centre = [(j*CELL + CELL//2, i*CELL + CELL//2 + SCORE_HEIGHT)
                                for i in range(m) for j in range(n)] 
        self.solver = solver
        self.area = m * n
        self.fps = FPS_DEFAULT
        self.height = n*CELL
        self.create_board_layers(n*CELL, m*CELL + SCORE_HEIGHT)

    def animate_single_game(self):  

        # keep track of occupied, empty vertices
        occupied = [False] * self.area
        empty_vertices = list(range(self.area))  # list of empty vertices
        empty_indices = list(range(self.area))   # index of empty vertex within that list

        # choose starting location, pass to solver
        start = choice(empty_vertices)
        self.solver.start_new_game(start)
        
        occupied[start] = True
        snake = deque([start])
        head = start

        # update empty space
        i = empty_indices[start]
        temp = empty_vertices[-1]
        empty_vertices[i] = temp
        empty_indices[temp] = i
        empty_vertices.pop()

        # animation
        self.start_new_game(start)
        self.refresh_screen()
        
        score = 0
        for length in range(1, self.area):
            # generate random apple
            apple = choice(empty_vertices)
            self.draw_apple(apple)
            self.refresh_screen()

            # ask solver for path to apple
            path = self.solver.find_path(apple)
            self.draw_path_and_loop(head, path)
            self.refresh_screen()
            
            for new_head in path[:-1]:
                # move tail, check legality, move head
                old_tail = snake.popleft()
                occupied[old_tail] = False

                if new_head not in self.adjacency[head]:
                    print('ERROR: non-adjacent move!')
                    return None
                if occupied[new_head]:
                    print('ERROR: collision with body!')
                    return None
                if new_head == apple:
                    print('ERROR: collision with apple!')
                    return None
                
                occupied[new_head] = True
                snake.append(new_head)
                self.update_snake(head, new_head, old_tail)
                head = new_head
                
                # replace new_head by old_tail in empty vertices list
                # unless they are the same (then neither are in that list)
                if new_head == old_tail:
                    continue
                i = empty_indices[new_head]
                empty_vertices[i] = old_tail
                empty_indices[old_tail] = i

                # animate
                score += 1
                self.update_score(length, score)
                self.refresh_screen()


            # check and execute final move
            if path[-1] != apple:
                print('ERROR: missed apple!')
                return None
            if apple not in self.adjacency[head]:
                print('ERROR: non-adjacent move!')
                return None

            occupied[apple] = True
            snake.append(apple) 
            self.update_snake(head, apple)
            head = apple

            # remove apple from list of empty vertices
            i = empty_indices[apple]
            temp = empty_vertices[-1]
            empty_vertices[i] = temp
            empty_indices[temp] = i
            empty_vertices.pop()

            # animate
            length += 1
            score += 1
            self.update_score(length, score)
            self.refresh_screen()
        return score
     
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
        self.score_layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        # background design
        self.bg_layer.fill(BG_COLOR)
        # design scoreboard
        self.font = pygame.font.SysFont(None, 28)

    def refresh_screen(self):
        pygame.display.update()
        self.events()
        self.clock.tick(self.fps)

    def start_new_game(self, start):
        # clear all board layers with transparent rectangles
        pygame.draw.rect(self.bg_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.loop_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.path_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.snake_layer, (0, 0, 0, 0), self.full_rect)
        pygame.draw.rect(self.score_layer, (0, 0, 0, 0), self.full_rect)

        # put snake head at start location
        pygame.draw.circle(self.snake_layer, HEAD_COLOR, self.index_to_centre[start], RADIUS)
        # show empty score
        self.update_score(1, 0)
        self.screen.blit(self.bg_layer, (0, 0))
        self.screen.blit(self.loop_layer, (0, 0))
        self.screen.blit(self.path_layer, (0, 0))
        self.screen.blit(self.snake_layer, (0, 0))
        self.screen.blit(self.score_layer, (0, 0))

        self.refresh_screen()
        
    def update_score(self, length, score):
        scoreboard = self.font.render(f"FPS: {self.fps}   L: {length}   S: {score}", True, (255, 255, 255))
        self.score_layer.fill(BG_COLOR, pygame.Rect(0, 0, self.height, SCORE_HEIGHT))
        self.score_layer.blit(scoreboard, (5, 5))
        pygame.draw.line(self.score_layer, LINE_COLOR, (0, SCORE_HEIGHT-1), (n*CELL, SCORE_HEIGHT-1), 2)
        self.screen.blit(self.score_layer, (0, 0))
        pygame.display.update()

    def draw_apple(self, apple):
        centre = self.index_to_centre[apple]
        pygame.draw.circle(self.snake_layer, APPLE_COLOR, centre, RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))
        pygame.display.update()
        
    def update_snake(self, old_head, new_head, old_tail = None):
        if old_tail != None and old_tail != old_head:
            self.clear_tail(old_tail)
          
        oh_centre = self.index_to_centre[old_head]
        nh_centre = self.index_to_centre[new_head]
        # draw old_head as body
        pygame.draw.circle(self.snake_layer, BODY_COLOR, oh_centre, RADIUS)   
        # delete path under old head
        x, y = self.index_to_rect[old_head]
        rect = pygame.Rect(x, y, CELL, CELL)
        pygame.draw.rect(
            self.path_layer,
            (0, 0, 0, 0),
            rect
        )   
        # draw new head connected to old head
        self.draw_connection(oh_centre, nh_centre)

        if old_tail == old_head:
            self.clear_tail(old_tail)

        pygame.draw.circle(self.snake_layer, HEAD_COLOR, nh_centre, RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))
        
    def clear_tail(self, tail):
        x, y = self.index_to_rect[tail]
        rect = pygame.Rect(x, y, CELL, CELL)
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
            x = cx1 - RADIUS
            y = min(cy1, cy2)
            width = 2 * RADIUS
            height = abs(cy1 - cy2)
        else:
            x = min(cx1, cx2)
            y = cy1 - RADIUS
            width = abs(cx1 - cx2)
            height = 2 * RADIUS
        x = int(x) - RECT_EXPAND
        y = int(y) - RECT_EXPAND
        width = int(width) + 2*RECT_EXPAND
        height = int(height) + 2*RECT_EXPAND
        pygame.draw.rect(self.snake_layer, BODY_COLOR, (x, y, width, height))
    
    def draw_path_and_loop(self, head, path):
        # draw planned loop, if exists
        if hasattr(self.solver, 'loop'):
            pygame.draw.rect(self.loop_layer, (0, 0, 0, 0), self.full_rect) 
            self.screen.blit(self.loop_layer, (0, 0))
            loop_points = [self.index_to_centre[c] for c in self.solver.loop]
            pygame.draw.lines(
                self.loop_layer,
                BODY_COLOR + (180,),
                True,
                loop_points,
                2
            )
            self.screen.blit(self.loop_layer, (0, 0))

        # draw path to apple
        self.path_layer.fill((0,0,0,0)) 
        points = [self.index_to_centre[head]] + [
            self.index_to_centre[p] for p in path
        ]
        pygame.draw.lines(
            self.path_layer,
            (255, 0, 0, 200),
            False,
            points,
            5
        )
        self.screen.blit(self.path_layer, (0, 0))

        # redraw head on top
        pygame.draw.circle(self.snake_layer, HEAD_COLOR, self.index_to_centre[head], RADIUS)
        self.screen.blit(self.snake_layer, (0, 0))  

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.fps += 1
                elif event.key == pygame.K_DOWN:
                    self.fps = max(1, self.fps-1)


if __name__ == "__main__":
    m = 4
    n = 4
    from Methods.Loop import GridSolverLoop
    solver = GridSolverLoop(m, n)
    animator = GridAnimator(m, n, solver)
    scores = animator.animate_many_games()
    print(scores)