import pygame
import random
import string
import heapq
import nltk
from nltk.corpus import words

# Download word list if not already present
nltk.download('words')
valid_words = set(words.words())

# Constants
WIDTH, HEIGHT = 1200, 800
GRID_SIZE = 20
FPS = 10
MARGIN_X = 40
MARGIN_Y = 60
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
YELLOW = (255, 215, 0)

# Word check helpers
common_two_letter_words = {
    "as", "at", "be", "by", "do", "go", "he", "if", "in", "is", "it",
    "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we"
}

def is_valid_word(word):
    word = word.lower()
    return (len(word) > 2 and word in valid_words) or (len(word) == 2 and word in common_two_letter_words)

def check_valid_word(collected_letters):
    for i in range(len(collected_letters)):
        word_to_check = collected_letters[i:]
        if is_valid_word(word_to_check):
            return word_to_check
    return None

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_path(start, goal, ai_snake, width, height):
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
            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and neighbor not in ai_snake):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def get_closest_letter(position, letters):
    return min(letters, key=lambda l: heuristic(position, (l[0], l[1])))

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

def draw_snake(screen, snake, color):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] + MARGIN_X, segment[1] + MARGIN_Y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        if i == 0:
            eye_size = 4
            cx, cy = rect.center
            pygame.draw.circle(screen, BLACK, (cx - 4, cy - 4), eye_size)
            pygame.draw.circle(screen, BLACK, (cx + 4, cy - 4), eye_size)

def draw_game(screen, snake, ai_snake, letters, collected_letters, ai_collected_letters, FONT):
    screen.fill(DARK_GRAY)
    pygame.draw.rect(screen, GRAY, (MARGIN_X - 2, MARGIN_Y - 2, WIDTH - 2 * MARGIN_X + 4, HEIGHT - 2 * MARGIN_Y + 4), 2)
    draw_snake(screen, snake, GREEN)
    draw_snake(screen, ai_snake, BLUE)
    for letter in letters:
        lx, ly = letter[0] + MARGIN_X, letter[1] + MARGIN_Y
        rect = pygame.Rect(lx, ly, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect, border_radius=3)
        char_surface = FONT.render(letter[2], True, WHITE)
        screen.blit(char_surface, (lx + (GRID_SIZE - char_surface.get_width()) // 2, ly + (GRID_SIZE - char_surface.get_height()) // 2))
    player_text = FONT.render(f"Player: {collected_letters}", True, YELLOW)
    ai_text = FONT.render(f"AI: {ai_collected_letters}", True, YELLOW)
    screen.blit(player_text, (MARGIN_X, 20))
    screen.blit(ai_text, (MARGIN_X + 300, 20))
    pygame.display.flip()

def show_start_screen(screen, FONT):
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

def show_game_over(screen, FONT):
    screen.fill((0, 0, 0))
    msg = FONT.render("Game Over! Press ESC to Quit.", True, (255, 255, 255))
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()

# Game Start
pygame.init()
FONT = pygame.font.Font(None, 32)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")

show_start_screen(screen, FONT)

# Game Setup
snake = [safe_spawn([])]
ai_snake = [safe_spawn(snake)]
direction = (GRID_SIZE, 0)
ai_frozen = 0
ai_collected_letters = ""
collected_letters = ""
letters = [spawn_letter(snake, ai_snake) for _ in range(3)]

def check_collision(body, head):
    return (head in body or head in ai_snake or head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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
        show_game_over(screen, FONT)

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
                letters.extend([spawn_letter(snake, ai_snake) for _ in range(3)])
            break

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
