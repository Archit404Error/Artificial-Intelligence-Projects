import pygame
import os
import sys
from random import *
from math import *
import neat

screen_width = 600
screen_height = 600
generation = 0

class Brick:
    def __init__(self, x, y, c):
        self.width = 75
        self.height = 20
        self.hit = False
        self.pos = [x, y]
        self.color = c

    def isHit(self, ball):
        brickBox = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        ballBox = pygame.Rect(ball.pos[0], ball.pos[1], ball.width, ball.height)
        if brickBox.colliderect(ballBox):
            self.hit = True
            ball.setVel(ball.velX, ball.velY * -1)

    def draw(self, screen):
        if not self.hit:
            pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

class BrickWall:
    def __init__(self, c):
        self.bricks = []
        self.color = c
        for i in range(0, 600 - 75, 85):
            for j in range(0, 300 - 20, 30):
                self.bricks.append(Brick(i, j, self.color))

    def draw(self, screen, ball):
        for b in self.bricks:
            if not b.hit:
                b.isHit(ball)
            else:
                self.bricks.pop(self.bricks.index(b))
                continue
            b.draw(screen)

class Ball:
    def __init__(self, c):
        self.pos = [300, 400]
        self.height = 20
        self.width = 20
        self.color = c
        self.velX = -10
        self.velY = -10

    def paddleHit(self, pad):
        ballBox = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        padBox = pygame.Rect(pad.pos[0], pad.pos[1], pad.width, pad.height)
        if(ballBox.colliderect(padBox)):
            self.velY *= -1
            if self.pos[0] > pad.pos[0] + pad.width or self.pos[0] < pad.pos[0]:
                self.pos[1] += 50
            elif self.pos[0] < (pad.pos[0] + pad.width / 2):
                self.velX = -1 * abs(self.velX)
            else:
                self.velX = abs(self.velX)

    def setVel(self, x, y):
        self.velX = x
        self.velY = y

    def draw(self, screen, pad):
        self.pos = [self.pos[0] + self.velX, self.pos[1] + self.velY]
        if self.pos[0] >= 600 - self.width or self.pos[0] <= 0:
            self.velX *= -1
        if self.pos[1] <= 0:
            self.velY *= -1
        self.paddleHit(pad)
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

class Paddle:
    def __init__(self, c):
        self.height = 20
        self.width = 150
        self.color = c
        self.velX = 10
        self.pos = [300 - self.width / 2, 500 - self.height]

    def move(self, val):
        if val == 1 and self.pos[0] <= screen_width - self.width - self.velX:
            self.pos[0] += self.velX
        elif val == 2 and self.pos[0] >= 0:
            self.pos[0] -= self.velX

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

class BrickPair:
    def __init__(self):
        col = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.paddle = Paddle(col)
        self.ball = Ball(col)
        self.wall = BrickWall(col)
        self.currBricks = len(self.wall.bricks)
        self.timeSinceHit = 0
        self.alive = True

    def isAlive(self):
        if self.ball.pos[1] >= screen_height - self.ball.height:
            self.alive = False
        if len(self.wall.bricks) < self.currBricks:
            self.currBricks = len(self.wall.bricks)
        else:
            self.timeSinceHit += 1
            if self.timeSinceHit == 10000:
                self.alive = false
        print(self.timeSinceHit)
        return self.alive

    def getInfo(self):
        return [self.ball.pos[0], self.ball.pos[1], self.paddle.pos[0], self.paddle.pos[1], self.wall.bricks[len(self.wall.bricks) - 1].pos[0], self.wall.bricks[len(self.wall.bricks) - 1].pos[1]]

    def getFitness(self):
        return (70 - len(self.wall.bricks)) + (sqrt((self.ball.pos[0] - self.paddle.pos[0]) ** 2 + (self.ball.pos[1] - self.paddle.pos[1]) ** 2))/10

    def draw(self, screen):
        if self.alive:
            self.isAlive()
            self.paddle.draw(screen)
            self.ball.draw(screen, self.paddle)
            self.wall.draw(screen, self.ball)

def runGame():
    player = BrickPair()

    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.paddle.move(2)
                if event.key == pygame.K_RIGHT:
                    player.paddle.move(1)
        clock.tick(40)
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 600, 600))

        print(player.getFitness())

        player.draw(screen)
        pygame.display.update()
    pygame.display.flip()

if __name__ == "__main__":
    runGame()
