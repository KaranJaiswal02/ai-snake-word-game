import pygame
import random
import string
import heapq
import nltk
from nltk.corpus import words

# Download words dataset if not available
nltk.download('words')
valid_words = set(words.words())

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 1300, 750
GRID_SIZE = 20
FPS = 10
FONT = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Initialize Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")

# Safe Snake Spawn Function
def safe_spawn(existing_positions):
    while True:
        x = random.randint(2, (WIDTH // GRID_SIZE) - 3) * GRID_SIZE
        y = random.randint(2, (HEIGHT // GRID_SIZE) - 3) * GRID_SIZE
        if (x, y) not in existing_positions:
            return (x, y)

# Initialize Snakes Safely
snake = [safe_spawn([])]  # Player snake
ai_snake = [safe_spawn(snake)]  # AI snake ensures it doesn't overlap
direction = (GRID_SIZE, 0)
ai_direction = (GRID_SIZE, 0)

# Letter Spawning Function
def spawn_letter():
    return (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
            random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE,
            random.choice(string.ascii_uppercase))

letters = [spawn_letter() for _ in range(3)]  # Start with 3 letters
collected_letters = ""
ai_collected_letters = ""

# Word Validation Function
def is_valid_word(word):
    return len(word) > 2 and word.lower() in valid_words  # Ensure minimum 3 letters

# A* Pathfinding for AI
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_path(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for dx, dy in [(0, -GRID_SIZE), (0, GRID_SIZE), (-GRID_SIZE, 0), (GRID_SIZE, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < WIDTH and 0 <= neighbor[1] < HEIGHT and neighbor not in ai_snake:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def get_closest_letter(position):
    return min(letters, key=lambda l: heuristic(position, (l[0], l[1])))

# Collision Detection
def check_collision(snake_body, new_head):
    return (new_head in snake_body or new_head in ai_snake or 
            new_head[0] < 0 or new_head[0] >= WIDTH or 
            new_head[1] < 0 or new_head[1] >= HEIGHT)

# Game Loop
running = True
while running:
    screen.fill(WHITE)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Move Player Snake
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and direction != (0, GRID_SIZE):
        direction = (0, -GRID_SIZE)
    elif keys[pygame.K_DOWN] and direction != (0, -GRID_SIZE):
        direction = (0, GRID_SIZE)
    elif keys[pygame.K_LEFT] and direction != (GRID_SIZE, 0):
        direction = (-GRID_SIZE, 0)
    elif keys[pygame.K_RIGHT] and direction != (-GRID_SIZE, 0):
        direction = (GRID_SIZE, 0)
    
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    if check_collision(snake[1:], new_head):
        running = False
    else:
        snake.insert(0, new_head)
        for letter in letters:
            if (letter[0], letter[1]) == new_head:
                collected_letters += letter[2]
                letters.remove(letter)
                letters.append(spawn_letter())
                if is_valid_word(collected_letters):
                    print(f"Valid Word Formed: {collected_letters}")
                    collected_letters = ""  # Reset only for valid words
                break
        else:
            snake.pop()
    
    # AI Movement
    if letters:
        target_letter = get_closest_letter(ai_snake[0])
        path = astar_path(ai_snake[0], (target_letter[0], target_letter[1]))
        if path:
            next_move = path[0]
            if check_collision(ai_snake[1:], next_move):
                running = False
            else:
                ai_snake.insert(0, next_move)
                if ai_snake[0] == (target_letter[0], target_letter[1]):
                    ai_collected_letters += target_letter[2]
                    letters.remove(target_letter)
                    letters.append(spawn_letter())
                    if is_valid_word(ai_collected_letters):
                        print(f"AI Formed Valid Word: {ai_collected_letters}")
                        ai_collected_letters = ""
                else:
                    ai_snake.pop()
    
    # Draw Player Snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
    
    # Draw AI Snake
    for segment in ai_snake:
        pygame.draw.rect(screen, BLUE, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
    
    # Draw Letters
    for letter in letters:
        pygame.draw.rect(screen, RED, (letter[0], letter[1], GRID_SIZE, GRID_SIZE))
        screen.blit(FONT.render(letter[2], True, WHITE), (letter[0] + 5, letter[1] + 5))
    
    # Display Collected Letters
    text_surface = FONT.render(f"Player: {collected_letters} | AI: {ai_collected_letters}", True, BLACK)
    screen.blit(text_surface, (10, 10))
    
    pygame.display.flip()
    pygame.time.Clock().tick(FPS)

pygame.quit()
