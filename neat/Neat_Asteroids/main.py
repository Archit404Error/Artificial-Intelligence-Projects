import neat
import pygame
import os
import sys
import math
from random import randint
from math import sqrt

screenWidth = 1200
screenHeight = 700
generation = 0

asteroids = []

def blitRotateCenter(screen, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    screen.blit(rotated_image, new_rect.topleft)

class Asteroid:
    def __init__(self, x, y, w, h, a, s, c):
        self.pos = [x, y]
        self.angle = a
        self.width = w
        self.height = h
        self.color = c
        self.velX = s * math.sin(math.radians(self.angle))
        self.velY = s * math.cos(math.radians(self.angle))
        self.hit = False

    def isHit(self, bullet, ship):
        hitBox = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        bullBox = pygame.Rect(bullet.pos[0], bullet.pos[1], bullet.width, bullet.height)
        if hitBox.colliderect(bullBox):
            self.hit = True
            if ship.hasMoved:
                ship.fitness += 100
            ship.bullets.pop(ship.bullets.index(bullet))
            return True
        return False

    def draw(self, screen):
        if not self.hit:
            self.pos[0] -= self.velX
            self.pos[1] -= self.velY
            if self.pos[0] < 0:
                self.pos[0] = screenWidth
            if self.pos[0] > screenWidth:
                self.pos[0] = 0
            if self.pos[1] < 0:
                self.pos[1] = screenHeight
            if self.pos[1] > screenHeight:
                self.pos[1] = 0
            pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

class Bullet:
    def __init__(self, x, y, velX, velY):
        self.width = 10
        self.height = 10
        self.velX = velX
        self.velY = velY
        self.pos = [x, y]

    def draw(self, screen):
        self.pos[0] -= self.velX
        self.pos[1] -= self.velY
        pygame.draw.rect(screen, (255, 255, 255), (self.pos[0], self.pos[1], self.width, self.height))

class Ship:
    def __init__(self):
        self.width = 100
        self.height = 100
        self.img = pygame.image.load("ship.png")
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        self.pos = [screenWidth / 2, screenHeight / 2]
        self.speed = 10
        self.velX = 0
        self.velY = 0
        self.angle = 0
        self.bullets = []
        self.fitness = 0

        self.hasMoved = False
        self.hasShot = False
        self.hasRotated = False

        self.alive = True

    def hitAsteroid(self, asteroid):
        hitBox = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        asBox = pygame.Rect(asteroid.pos[0], asteroid.pos[1], asteroid.width, asteroid.height)
        if hitBox.colliderect(asBox):
            self.alive = False

    def move(self, val):
        if self.alive:
            self.angle %= 360
            if val == 0:
                self.angle += 15
                if not self.hasRotated:
                    self.fitness += 100
                self.hasRotated = True
            if val == 1:
                self.angle -= 15
                if not self.hasRotated:
                    self.fitness += 100
                self.hasRotated = True
            if val == 2:
                self.velX = self.speed * math.sin(math.radians(self.angle))
                self.velY = self.speed * math.cos(math.radians(self.angle))
                if not self.hasMoved:
                    self.fitness += 100
                self.hasMoved = True
            if val == 3:
                if not self.hasShot:
                    self.fitness += 100
                if len(self.bullets) < 5:
                    self.bullets.append(Bullet(self.pos[0] + (self.width / 2.0), self.pos[1] + (self.height / 2.0), self.speed * math.sin(math.radians(self.angle)), self.speed * math.cos(math.radians(self.angle))))
                self.hasShot = True

    def decreaseVelocity(self, vel):
        if abs(vel) < 1:
            return 0
        if vel < 0:
            return vel + 1
        return vel - 1

    def draw(self, screen):
        if self.alive:
            self.pos[0] -= self.velX
            self.pos[1] -= self.velY
            if self.pos[0] < 0:
                self.pos[0] = screenWidth
            if self.pos[0] > screenWidth:
                self.pos[0] = 0
            if self.pos[1] < 0:
                self.pos[1] = screenHeight
            if self.pos[1] > screenHeight:
                self.pos[1] = 0
            self.velX = self.decreaseVelocity(self.velX)
            self.velY = self.decreaseVelocity(self.velY)
            blitRotateCenter(screen, self.img, self.pos, self.angle)
            for bullet in self.bullets:
                if bullet.pos[0] < 0 or bullet.pos[0] > screenWidth or bullet.pos[1] < 0 or bullet.pos[1] > screenHeight:
                    self.bullets.pop(self.bullets.index(bullet))
                else:
                    bullet.draw(screen)

class Player:
    def __init__(self):
        self.ship = Ship()
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.asteroids = asteroids

    def moveShip(self, val):
        self.ship.move(val)

    def getFitness(self):
        return self.ship.fitness

    def getDist(self, x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def getInfo(self):
        shortDist = self.getDist(self.ship.pos[0], self.ship.pos[1], self.asteroids[0].pos[0], self.asteroids[0].pos[1])
        shortAst = self.asteroids[0]
        for asteroid in self.asteroids:
            currD = self.getDist(self.ship.pos[0], self.ship.pos[1], asteroid.pos[0], asteroid.pos[1])
            if currD < shortDist:
                shortDist = currD
                shortAst = asteroid
        return [shortAst.pos[0], shortAst.pos[1], shortDist]

    def isAlive(self):
        return self.ship.alive

    def draw(self, screen):
        if self.isAlive():
            if len(self.asteroids) < 5:
                currAst = Asteroid(randint(0, screenWidth), randint(0, screenHeight), 50, 50, randint(0, 360), 5, (255, 255, 255))
                self.asteroids.append(currAst)
            for asteroid in self.asteroids:
                for bullet in self.ship.bullets:
                    asteroid.isHit(bullet, self.ship)
                asteroid.draw(screen)
                self.ship.hitAsteroid(asteroid)
                if asteroid.hit:
                    if not asteroid.width < 25:
                        self.asteroids.append(Asteroid(asteroid.pos[0], asteroid.pos[1], asteroid.width / 2, asteroid.height / 2, (asteroid.angle + 45) % 360, 5, asteroid.color))
                        self.asteroids.append(Asteroid(asteroid.pos[0], asteroid.pos[1], asteroid.width / 2, asteroid.height / 2, (asteroid.angle - 45) % 360, 5, asteroid.color))
                    self.asteroids.pop(self.asteroids.index(asteroid))
            self.ship.draw(screen)

def runGame(genomes, config):
    networks = []
    players = []

    asteroids.clear()
    for i in range(5):
        currAst = Asteroid(randint(0, screenWidth), randint(0, screenHeight), 50, 50, randint(0, 360), 5, (255, 255, 255))
        hitBox = pygame.Rect(screenWidth / 2, screenHeight / 2, 100, 100)
        asBox = pygame.Rect(currAst.pos[0], currAst.pos[1], currAst.width, currAst.height)
        while hitBox.colliderect(asBox):
            currAst = Asteroid(randint(0, screenWidth), randint(0, screenHeight), 50, 50, randint(0, 360), 5, (255, 255, 255))
            hitBox = pygame.Rect(screenWidth / 2, screenHeight / 2, 100, 100)
            asBox = pygame.Rect(currAst.pos[0], currAst.pos[1], currAst.width, currAst.height)
        asteroids.append(currAst)

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        networks.append(net)
        g.fitness = 0
        players.append(Player())

    pygame.init()
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        for i, player in enumerate(players):
            output = networks[i].activate(player.getInfo())
            val = output.index(max(output))
            player.moveShip(val)
        clock.tick(40)
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, screenWidth, screenHeight))
        alive = 0
        for i, player in enumerate(players):
            if player.isAlive():
                alive += 1
                genomes[i][1].fitness = player.getFitness()
        if alive == 0:
            break
        for player in players:
            player.draw(screen)
        pygame.display.update()
    pygame.display.flip()

if __name__ == "__main__":
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.run(runGame, 1000)
