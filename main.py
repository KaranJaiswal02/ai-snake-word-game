import pygame
import random
import string
from ui import draw_game
from ai import astar_path, get_closest_letter, check_valid_word

# Game Constants
WIDTH, HEIGHT = 1200, 800
GRID_SIZE = 20
FPS = 10

# Initialize
pygame.init()
FONT = pygame.font.Font(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")

# Spawning
def safe_spawn(exclude):
    while True:
        x = random.randint(2, (WIDTH // GRID_SIZE) - 3) * GRID_SIZE
        y = random.randint(2, (HEIGHT // GRID_SIZE) - 3) * GRID_SIZE
        if (x, y) not in exclude:
            return (x, y)

def spawn_letter(snake, ai_snake):
    while True:
        x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        if (x, y) not in snake and (x, y) not in ai_snake:
            return (x, y, random.choice(string.ascii_uppercase))

# Setup
snake = [safe_spawn([])]
ai_snake = [safe_spawn(snake)]
direction = (GRID_SIZE, 0)
ai_frozen = 0
ai_collected_letters = ""
collected_letters = ""
letters = [spawn_letter(snake, ai_snake) for _ in range(3)]

def check_collision(body, head):
    return (head in body or head in ai_snake or
            head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT)

# === Waiting for SPACE to start ===
waiting = True
while waiting:
    screen.fill((255, 255, 255))
    msg = FONT.render("Press SPACE to Start", True, (0, 0, 0))
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting = False

# Game Loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and direction != (0, GRID_SIZE):
        direction = (0, -GRID_SIZE)
    elif keys[pygame.K_DOWN] and direction != (0, -GRID_SIZE):
        direction = (0, GRID_SIZE)
    elif keys[pygame.K_LEFT] and direction != (GRID_SIZE, 0):
        direction = (-GRID_SIZE, 0)
    elif keys[pygame.K_RIGHT] and direction != (-GRID_SIZE, 0):
        direction = (GRID_SIZE, 0)

    # Move Player
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    if check_collision(snake[1:], new_head):
        running = False
    else:
        snake.insert(0, new_head)
        if new_head not in [(l[0], l[1]) for l in letters]:
            snake.pop()
        for letter in letters:
            if (letter[0], letter[1]) == new_head:
                collected_letters += letter[2]
                letters.remove(letter)
                letters.append(spawn_letter(snake, ai_snake))
                valid = check_valid_word(collected_letters)
                if valid:
                    print(f"Player formed word: {valid}")
                    collected_letters = ""
                    ai_frozen = 100
                    letters.extend([spawn_letter(snake, ai_snake) for _ in range(5)])
                break

    # AI Movement
    if ai_frozen > 0:
        ai_frozen -= 1
    elif letters:
        target = get_closest_letter(ai_snake[0], letters)
        path = astar_path(ai_snake[0], (target[0], target[1]), ai_snake, WIDTH, HEIGHT)
        if path:
            next_move = path[0]
            ai_snake.insert(0, next_move)
            if ai_snake[0] == (target[0], target[1]):
                ai_collected_letters += target[2]
                letters.remove(target)
                letters.append(spawn_letter(snake, ai_snake))
                valid = check_valid_word(ai_collected_letters)
                if valid:
                    print(f"AI formed word: {valid}")
                    ai_collected_letters = ""
            else:
                ai_snake.pop()
        else:
            # AI fallback movement
            moves = [(ai_snake[0][0] + dx, ai_snake[0][1] + dy)
                     for dx, dy in [(0, -GRID_SIZE), (0, GRID_SIZE), (-GRID_SIZE, 0), (GRID_SIZE, 0)]
                     if 0 <= ai_snake[0][0] + dx < WIDTH and 0 <= ai_snake[0][1] + dy < HEIGHT and
                     (ai_snake[0][0] + dx, ai_snake[0][1] + dy) not in ai_snake]
            if moves:
                ai_snake.insert(0, random.choice(moves))
                ai_snake.pop()

    draw_game(screen, snake, ai_snake, letters, collected_letters, ai_collected_letters, FONT)
    clock.tick(FPS)

pygame.quit()