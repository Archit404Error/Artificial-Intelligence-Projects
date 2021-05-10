import neat
import pygame

screenHeight = 600
screenWidth = 600

class Snake:
    def __init__(self):
        self.pos = []
        self.len = 1

    def draw(self, screen):
        for i in range(self.len):
            pygame.drawRect(#implement bounds here)

class Food:
    def __init__(self):
        self.pos = [randint(0, screenWidth), randint(0, screenHeight)]

def runGame():
    player = Snake()
    foods = [Food()]

if __name__ == "__main__"
  runGame()
