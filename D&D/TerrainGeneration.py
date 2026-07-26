import pygame
from perlin_noise import PerlinNoise
import random
import math
import time

WIDTH = 2400
HEIGHT = 1300
IMAGE_PATH = "C:/Users/rhys6/OneDrive/Desktop/D&D/models/village.png"
# Isometric tile size
TILE_WIDTH = 12
TILE_HEIGHT = 7

# World size
MAP_WIDTH = 200
MAP_HEIGHT = 200
camera_x = 0
camera_y = 200
SEED = random.randint(0, 999999)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("D&D game")
clock = pygame.time.Clock()
village_image = pygame.image.load(IMAGE_PATH).convert()
village_image = pygame.transform.scale(
    village_image,
    (80, 80)
)



class Tile:

    def __init__(self):

        self.elevation = 0
        self.moisture = 0

        self.biome = "unknown"
        self.river = False
        self.town = False

        self.explored = False

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[Tile() for x in range(width)]

            for y in range(height)
        ]
    def generate(self):
        maximum = 0
        offsetA = 0.2
        offsetM = 1
        print("Generating world...")
        large_land_noise = PerlinNoise(octaves=2,seed=SEED)
        detail_noise = PerlinNoise(octaves=6,seed=SEED + 1)
        
        moisture_noise = PerlinNoise(octaves=4,seed=SEED + 100)
        
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                nx = x / self.width
                ny = y / self.height
                elevation = (large_land_noise([nx * 2,ny * 2]) * 0.7 + detail_noise([nx * 8,ny * 8]) * 0.3)
                distance = math.sqrt(
                    (nx-0.5)**2 +
                    (ny-0.5)**2
                )
                falloff = distance * 0.8
                elevation -= falloff - offsetA
                if elevation > 0.3:
                    elevation = elevation * 1.2
                tile.elevation = elevation * offsetM
                
                moisture = moisture_noise(
                    [
                        nx*4,
                        ny*4
                    ]
                )
                tile.moisture = moisture
                tile.biome = self.get_biome(
                    elevation,
                    moisture
                )
                if tile.elevation > maximum:
                    #print(tile.elevation)
                    maximum = tile.elevation
                if tile.elevation <= 0:
                    tile.elevation = 0
                else:
                    if random.randint(0,10):
                        tile.town = True

        print("World generated!")

    def get_biome(self, elevation, moisture):
        if elevation < -0.35:
            return "deep ocean"
        elif elevation < -0.3:
            return "semi deep water"
        elif elevation < -0.2:
            return "semi shallow water"
        elif elevation < -0.1:
            return "shallow water"
        elif elevation < -0.05:
            return "beach"
        elif elevation > 0.3:
            if elevation > 0.4:
                return "snow mountain"
            return "mountain"
        else:
            if moisture < -0.25:
                return "desert"
            elif moisture < 0.15:
                return "grassland"
            elif moisture < 0.45:
                return "forest"
            else:
                return "dense forest"

    def colour(self, biome):

        colours = {
            "deep ocean":
            (0,40,120),
            "semi deep water":
            (10,70,150),
            "semi shallow water":
            (30,100,180),
            "shallow water":
            (40,120,220),
            "beach":
            (240,220,130),
            "desert":
            (220,200,120),
            "grassland":
            (80,180,80),
            "forest":
            (30,130,50),
            "dense forest":
            (10,90,30),
            "mountain":
            (110,110,110),
            "snow mountain":
            (240,240,240)
        }

        return colours[biome]


    def iso_to_screen(self, x, y):
        screen_x = (
            (x-y)*TILE_WIDTH//2
            + WIDTH//2
            + camera_x
        )

        screen_y = (
            (x+y)*TILE_HEIGHT//2
            + camera_y
        )
        return screen_x, screen_y

    def draw3D(self,surface):
        for diagonal in range(self.width + self.height):
            for y in range(self.height):
                x = diagonal - y
                if x < 0 or x >= self.width:
                    continue
                tile = self.tiles[y][x]
                colour = self.colour(tile.biome)
                screen_x, screen_y = self.iso_to_screen(
                    x,
                    y
                )
                height = tile.elevation * 80
                screen_y -= height
                if tile.biome == 'mountain' or tile.biome == 'snow mountain':
                    points = [(screen_x,screen_y-tile.elevation - 12),(screen_x + TILE_WIDTH//2,screen_y + TILE_HEIGHT//2),(screen_x,screen_y + TILE_HEIGHT),(screen_x - TILE_WIDTH//2,screen_y + TILE_HEIGHT//2)]
                else: points = [(screen_x,screen_y-tile.elevation),(screen_x + TILE_WIDTH//2,screen_y + TILE_HEIGHT//2),(screen_x,screen_y + TILE_HEIGHT),(screen_x - TILE_WIDTH//2,screen_y + TILE_HEIGHT//2)]
                
                
                pygame.draw.polygon(surface,colour,points)
                #if tile.town:
                if False:
                    surface.blit(
                        village_image,
                        (
                            screen_x - village_image.get_width()//2,
                            screen_y - village_image.get_height() + TILE_HEIGHT//2
                        )
                    )
                
                
    def draw2D(self, surface):
        TILE_SIZE = 10
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                colour = self.colour( tile.biome )
                pygame.draw.rect( surface, colour, ( x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE ) )
world = World(
    MAP_WIDTH,
    MAP_HEIGHT
)
world.generate()
running = True
view = '2D'
def toggle(view):
    if view == '2D':
        view = '3D'
    elif view == '3D':
        view = '2D'
    return view
        
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            speed = 100

            if keys[pygame.K_LEFT]:
                camera_x += speed

            if keys[pygame.K_RIGHT]:
                camera_x -= speed

            if keys[pygame.K_UP]:
                camera_y += speed

            if keys[pygame.K_DOWN]:
                camera_y -= speed
            if event.key == pygame.K_c:
                view = toggle(view)
                time.sleep(0.3)
        if event.type == pygame.QUIT:
            running = False
    screen.fill((20,20,40))
    if view == '3D':
        world.draw3D(screen)
    else:
        world.draw2D(screen)
    pygame.display.update()
    clock.tick(60)
pygame.quit()