#!/usr/bin/env python3

import sys
import random
import curses
from enum import Enum
from curses import wrapper
import time
import _curses

# Constants
WINDOW_WIDTH = 144
WINDOW_HEIGHT = 40

# Initialize curses library.
stdscr = curses.initscr()


def main(stdscr):
    # Curses settings.
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.noecho()

    # Create and draw a frame.
    walls = Walls(WINDOW_WIDTH, WINDOW_HEIGHT)
    walls.Draw()

    # Create a point.
    y_coordinate = 20
    x_coordinate = 50
    point = Point(y_coordinate, x_coordinate, "*")

    # Create and draw a snake.
    snake_lenght = 5
    snake = Snake(point, snake_lenght, Direction.RIGHT)
    snake.Draw()

    # Create and draw a food.
    food_creator = Food_creator(WINDOW_WIDTH, WINDOW_HEIGHT, "$")
    food = food_creator.Create_food()
    food.Draw()

    scores = 0

    # Run a game process.
    while True:
        # Remove a waiting for input.
        stdscr.nodelay(True)

        # Get and process a button click.
        key = stdscr.getch()
        snake.Handle_key(key)

        # If the snake is collided with a wall or her tail the game is over.
        if walls.Is_hit(snake) or snake.Is_hit_tail():
            game_over(scores)
            break

        # If the snake is collided food, it eats it.
        if snake.Eat(food):
            scores = scores + 1
            food = food_creator.Create_food()
            food.Draw()

        # If the snake is not collided with anything, it keeps moving forward.
        else:
            snake.Move()
            time.sleep(0.09)

    # Back to the default terminal settings.
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()

    # Deinitialize curses library.
    curses.endwin()


# Tell a user that game is over.
def game_over(scores):
    y_coordinate = 20
    x_coordinate = 70
    stdscr.addstr(y_coordinate, x_coordinate,
                  "Игра окончена! Для продолжения нажмите любую клавишу...")

    # Print am amount of scores.
    score_amount(scores)


# Print an amount of scores on the screen.
def score_amount(scores):
    y_coordinate = 25
    x_coordinate = 70

    stdscr.addstr(y_coordinate, x_coordinate, "Количество ваших очков:")
    stdscr.addstr(str(scores))
    stdscr.nodelay(False)
    stdscr.getch()


class Figure:
    def __init__(self, point_list=[]):
        self.point_list = point_list

    # Draw a line.
    def Drow(self):
        for i in self.point_list:
            i.Draw()

    # Detect a collision.
    def Is_hit(self, figure):
        for p in self.point_list:
            if figure.Is_hit(p):
                return True
        return False


class Point:
    def __init__(self, y, x, sym):
        self.y = y
        self.x = x
        self.sym = sym

    # Draw point.
    def Draw(self):
        stdscr.move(self.y, self.x)
        stdscr.addch(self.y, self.x, self.sym)
        stdscr.timeout(1)
        stdscr.getch()

    # Shift coordinates of point.
    def Shift(self, offset, direction):
        if direction == Direction.RIGHT:
            self.x = self.x + offset

        if direction == Direction.LEFT:
            self.x = self.x - offset

        if direction == Direction.UP:
            self.y = self.y - offset

        if direction == Direction.DOWN:
            self.y = self.y + offset

    # Clear point symbol.
    def Clear(self):
        self.sym = ' '
        self.Draw()

    # Detect a collision.
    def Is_hit(self, p):
        return p.x == self.x and p.y == self.y


class Walls:
    def __init__(self, window_width, window_height, wall_list=[]):
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.wall_list = wall_list

        width = self.window_width
        height = self.window_height

        # Create lines.
        up_line = Horizontal_line(0, width - 2, 0, "+")
        down_line = Horizontal_line(0, width - 2, height - 1, "+")
        left_line = Vertical_line(0, height - 1, 0, "+")
        right_line = Vertical_line(0, height - 1, width - 2, "+")

        # Append lines to the list.
        self.wall_list.append(up_line)
        self.wall_list.append(down_line)
        self.wall_list.append(left_line)
        self.wall_list.append(right_line)

    # Draw lines.
    def Draw(self):
        for i in self.wall_list:
            i.Drow()

    # Detect collistion.
    def Is_hit(self, figure):
        for wall in self.wall_list:
            if wall.Is_hit(figure):
                return True
        return False


class Horizontal_line(Figure):
    def __init__(self, x_left, x_right, y, sym, point_list=[]):
        self.x_left = x_left
        self.x_right = x_right
        self.y = y
        self.sym = sym
        self.point_list = point_list

        # Append points to the list.
        while x_left < x_right:
            point = Point(y, x_left, sym)
            self.point_list.append(point)
            x_left = x_left + 1


class Vertical_line(Figure):
    def __init__(self, y_up, y_down, x, sym, point_list=[]):
        self.y_up = y_up
        self.y_down = y_down
        self.x = x
        self.sym = sym
        self.point_list = point_list

        # добавляем точки в список
        while y_up < y_down:
            point = Point(y_up, x, sym)
            self.point_list.append(point)
            y_up = y_up + 1


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Direction(AutoNumber):
        LEFT = ()
        RIGHT = ()
        UP = ()
        DOWN = ()


# Count an amount of items in a list.
def count(item):
    number = 0
    for i in item:
        number = number + 1
    return number


class Snake(Figure):
    def __init__(self, tail, length, direction, snake_list=[]):
        self.tail = tail
        self.length = length
        self.direction = direction
        self.snake_list = snake_list

        # Append points to the list.
        i = 0
        while i < length:
            p = Point(self.tail.y, self.tail.x, self.tail.sym)
            p.Shift(i, self.direction)
            self.snake_list.append(p)
            i = i + 1

    # Move the snake.
    def Move(self):
        # Delete a tail.
        tail = self.snake_list[0]
        self.snake_list.remove(tail)

        # Create new head.
        head = self.Get_next_point()
        self.snake_list.append(head)

        # Clear a tail and draw a new head.
        tail.Clear()
        head.Draw()

    # Get a new head.
    def Get_next_point(self):
        # Count an amount of items in the list.
        number = count(self.snake_list)

        # Create a new point based on the head.
        last_element = number - 1
        head = self.snake_list[last_element]
        next_point = Point(head.y, head.x, head.sym)

        # Shift a new point cooordinates.
        next_point.Shift(1, self.direction)

        return next_point

    # Draw the snake.
    def Draw(self):
        for i in self.snake_list:
            i.Draw()

    # Control of the snake.
    def Handle_key(self, key):
        if key == curses.KEY_RIGHT:
            if self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT

        if key == curses.KEY_LEFT:
            if self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT

        if key == curses.KEY_UP:
            if self.direction != Direction.DOWN:
                self.direction = Direction.UP

        if key == curses.KEY_DOWN:
            if self.direction != Direction.UP:
                self.direction = Direction.DOWN

    # Eat a food.
    def Eat(self, food):

        head = self.Get_next_point()

        if head.Is_hit(food):
            food.sym = head.sym
            self.snake_list.append(food)
            return True
        else:
            return False

    # Detect a collision.
    def Is_hit(self, point):
        for p in self.snake_list:
            if p.Is_hit(point):
                return True
        return False

    # Detect a collision with the tail.
    def Is_hit_tail(self):
        # Count an amount of items in the list.
        number = count(self.snake_list)

        # Identify the head position.
        last_element = number - 1
        head = self.snake_list[last_element]

        # Identify a number of body points, except the head.
        body_points = number - 2

        # Identify a collision of body to the head.
        i = 0
        while i < body_points:
            if head.Is_hit(self.snake_list[i]):
                return True
            i = i + 1
        return False


class Food_creator:
    def __init__(self, window_width, window_height, sym):
        self.sym = sym
        self.window_width = window_width
        self.window_height = window_height

    def Create_food(self):
        # Generate random coordinates in the particular borders.
        y_coordinate = random.randint(2, self.window_height - 2)
        x_coordinate = random.randint(2, self.window_width - 3)

        point = Point(y_coordinate, x_coordinate, self.sym)

        return point


if __name__ == "__main__":
    curses.wrapper(main)

