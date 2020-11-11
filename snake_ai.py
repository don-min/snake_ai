import pygame
from pygame.locals import *  # full screen option
import random
import time

pygame.init()  # pygame files must always start like this
board_x = 600  # horizontal board size
board_y = 600  # vertical board size
screen = pygame.display.set_mode((board_x, board_y), RESIZABLE)  # initialize the screen to a square size
pygame.display.set_caption('Snake AI Game')
pygame.display.update()  # update any changes made to the screen

# colors
blue = (0, 0, 255)
red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
yellow = (255, 255, 102)

snake_body = 10  # snake body block
snake_speed = 250

timer = pygame.time.Clock()  # tracking the amount of time
lose_font = pygame.font.SysFont('bahnschrift', 30)  # tell pygame to choose a font for a piece of text
score_font = pygame.font.SysFont('comicsansms', 35)

# gathering data
points = []

# functions
def loser(msg, msg2, msg3, msg4, color):  # create a function for losers
    text = lose_font.render(msg, True, color)
    screen.blit(text, [0, 0])  # display a message at the top of the screen when the player loses
    text2 = lose_font.render(msg2, True, color)
    screen.blit(text2, [0, 30])
    text3 = lose_font.render(msg3, True, color)
    screen.blit(text3, [0, 60])
    text4 = lose_font.render(msg4, True, color)
    screen.blit(text4, [0, 90])

def snake(snake_body, snake_list):
    '''
    essentially the body parts of a snake will be contained in a list, and the intial size of the body is 1
    '''
    for i in snake_list:
        pygame.draw.rect(screen, black, [i[0], i[1], snake_body, snake_body])  # in this case, snake appears as a square

def score(score):
    value = str(score)
    return value

def show_fps():
    fps = "FPS: " + str(int(timer.get_fps()))
    fps_text = lose_font.render(fps, 1, pygame.Color("coral"))
    return fps_text

#timer
board_size = 600
play_time = (((4 * board_size) - (0.4 * board_size)) * 1.5) / (snake_speed / 10) # frames to seconds conversion equation (one of the terminating conditions)
start_time = pygame.time.get_ticks()
time_left = pygame.time.get_ticks() - start_time
time_left = time_left / 1000

# A node class for A* algorithm
class Node():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def astar(maze, start, end):
    '''
    Returns a list of tuples, which is basically the path from the source node to the goal node
    '''

    # Create source and goal node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = [] # for tracking the current node
    closed_list = [] # pop from the open_list, then append the current node to this list

    # Append the start node to the list
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:
        current_node = open_list[0]
        current_index = 0

        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        open_list.pop(current_index)
        closed_list.append(current_node)

        # when the goal node is found
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return a reversed path

        # Generate children
        children = []

        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares, considering diagonal cases
            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Check the range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (
                    len(maze[len(maze) - 1]) - 1) or node_position[1] < 0:
                continue

            # Make sure if the path is walkable
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)
            children.append(new_node)

        # Loop through children
        for child in children:
            for closed_child in closed_list:
                if child == closed_child:
                    break
            else:
                # summation of the exact cost and the heuristic
                child.g = current_node.g + 1
                child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
                child.f = child.g + child.h

                for open_node in open_list: # check if the new path to children is equal to or worse than the path in the open_list by measuring g value
                    if child == open_node and child.g >= open_node.g:
                        break
                else:
                    open_list.append(child)

# Main loop of the game
def GameLoop():

    t1 = time.time()
    end = False
    close = False

    x = board_x / 2  # snake x-coordinate
    y = board_y / 2  # snake y-coordinate

    x_coord_change = 0  # change in x-coordinates after pressing arrow keys
    y_coord_change = 0  # change in y-coordinates after pressing arrow keys

    snake_list = []  # initializing the list to append the snake body as it eats the food
    snake_length = 1  # beginning with the length of 1, will increment by 1 as it eats the food

    food_x = round(random.randrange(0, board_x - snake_body) / 10.0) * 10.0  # randomize the food's x-coordinate
    food_y = round(random.randrange(0, board_y - snake_body) / 10.0) * 10.0  # randomize the food's y-coordinate

    path = []
    direction = 0
    lastDirection = 0

    while not end: # When the game is not over

        t2 = time.time()
        while close == True:  # new screen pops up when you lose
            screen.fill(blue)
            loser("You Lost!", "Press E to Play Again", "Press Q to Quit", "Final Score: " + score(snake_length - 1),
                  red)
            pygame.display.set_caption('Snake AI Game | Score: ' + score(snake_length - 1))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # quit the game
                        end = True
                        close = False
                    if event.key == pygame.K_e:  # restart the game
                        GameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # click x to exit the screen
                end = True

        # find path to the new spawn food (not taking into account that snake tail will move)
        # if path is not found, let the snake move randomly until it finds a path
        # or else another terminating condition applies
        grid = [[0 for x in range(int(board_x / 10))] for y in range(int(board_y / 10))] # Grid
        for point in snake_list:
            try:
                grid[int(point[1] / 10)][int(point[0] / 10)] = 1
            except IndexError:
                close = True

        try:
            grid[int(x / 10)][int(y / 10)] = 0
        except IndexError:
            close = True

        print("\n\n")

        for line in grid:
            print(line)

        print("\n\n")
        print("x: " + str(x / 10) + " y: " + str(y / 10))

        # returns the cells in a form of (y, x), so the snake follows the found path
        path = astar(grid, (int(y / 10), int(x / 10)), (int(food_y / 10), int(food_x / 10)))

        print(path)
        if path == None or path == []:
            pass
        else:
            path.pop(0)  # this is because the starting position is included in the path

        print("food_x: " + str(food_x / 10) + "  food_y: " + str(food_y / 10))

        if path == None or path == []:
            direction = lastDirection
        else:

            print("path[0][1]: " + str(path[0][1]))
            print("path[0][0]: " + str(path[0][0]))
            print("x: " + str(x / 10))
            print("y: " + str(y / 10))

            changeX = path[0][1] - int(x / 10)
            changeY = path[0][0] - int(y / 10)
            path.pop(0)
            print("changeX: " + str(changeX) + " changeY: " + str(changeY))
            print("")

            if changeX == 1:
                direction = 2
            elif changeX == -1:
                direction = 3
            elif changeY == 1:
                direction = 1
            else:
                direction = 0

        if direction == 0:  # moving up
            print("up")
            x_coord_change = 0
            y_coord_change = -snake_body  # snake will move in even increments
            lastDirection = 0

        elif direction == 1:  # moving down
            print("down")
            x_coord_change = 0
            y_coord_change = snake_body
            lastDirection = direction

        elif direction == 2:  # moving right
            print("right")
            x_coord_change = snake_body
            y_coord_change = 0
            lastDirection = direction

        elif direction == 3:  # moving left
            print("left")
            x_coord_change = -snake_body
            y_coord_change = 0
            lastDirection = direction

        if (board_x <= x or x < 0) or (board_y <= y or y < 0):  # when the snake hits the boundary, the game is over
            close = True

        x += x_coord_change  # applying the change caused by pressing arrow keys
        y += y_coord_change  # applying the change caused by pressing arrow keys
        screen.fill(yellow)  # change screen color to white
        screen.blit(show_fps(), (10, 0))
        pygame.draw.rect(screen, green, [food_x, food_y, snake_body, snake_body])  # parameters of draw.rect(display, color, width), width is actually [centerx, centery, length, width]

        snake_head = []  # initializing the snake head
        snake_head.append(x)  # appending the x-coordinate of the snake
        snake_head.append(y)  # appending the y-coordinate of the snake
        snake_list.append(snake_head)  # appending the coordinates of the snake head

        if len(snake_list) > snake_length:
            del snake_list[0]

        for i in snake_list[:-1]:
            if i == snake_head:
                close = True
                break

        dt = round((t2 - t1), 2)
        # seconds = (pygame.time.get_ticks()) / 1000, because it returns in milliseconds
        if (x == food_x and y == food_y):
            t1 = t2
        if dt > play_time:
            close = True

        if close == True:
            points.append(int(score(snake_length - 1)))

        snake(snake_body, snake_list)
        pygame.display.set_caption('Snek AI Game | Score: ' + score(snake_length - 1) + " | Timer: " + str(
            dt) + " | You have {} seconds to eat a moogle!".format(
            play_time))  # score(snake_length - 1)  # -1 because the snake length was initiated with value of 1
        pygame.display.update()  # update the fact that we just added a rectangle and key binds

        if (x == food_x and y == food_y):  # if the snake eats the food, its length is increased by 1
            while 1 == 1:
                tempX = round(random.randrange(0, board_x - snake_body) / 10.0) * 10.0
                tempY = round(random.randrange(0, board_y - snake_body) / 10.0) * 10.0
                good = True
                for snakePart in snake_list:
                    if tempX == snakePart[0] and tempY == snakePart[1]:
                        good = False
                        break
                if good == True:
                    break

            food_x = tempX  # new food x-coordinate
            food_y = tempY  # new food y-coordinate
            snake_length += 1

        timer.tick(snake_speed)  # frame advancements or fps

    pygame.quit()
    quit()  # terminate the screen


GameLoop()