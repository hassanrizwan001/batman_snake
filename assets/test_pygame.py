# test_pygame.py
import pygame, sys

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Batman Snake Core Test")

# Try to load an image from assets
try:
    img = pygame.image.load("assets/batman.png")
    print("✅ Image loaded successfully!")
except Exception as e:
    print("⚠️ Could not load image:", e)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
sys.exit()
