import pygame
import random
import heapq
import nltk
from nltk.corpus import words
import sys

nltk.download('words')
valid_words = set(w.lower() for w in words.words())
short_valid_words = {
    "cat", "dog", "car", "sun", "run", "red", "man", "fun", "cup", "map", "top", "toy", "box", "fox", "log",
    "yes", "hat", "bat", "rat", "mat", "pot", "pen", "can", "win", "bus", "net", "dot", "fan", "bed", "egg",
    "four", "five", "cool", "look", "make", "game", "word", "play", "code", "read"
}

WIDTH, HEIGHT = 1500, 750
GRID_SIZE = 20
FPS = 7

obstacle_color = {
    "water": (0, 120, 255),
    "fire": (255, 80, 0),
    "pit": (50, 50, 50),
    "eagle": (200, 200, 200)
}

obstacle_symbol = {
    "water": "💧",
    "fire": "🔥",
    "pit": "⛳",
    "eagle": "🦅"
}

pygame.init()
pygame.mixer.init()
try:
    EMOJI_FONT = pygame.font.Font("seguiemj.ttf", 24)
except:
    EMOJI_FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("consolas", 48)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")

try:
    EAT_SOUND = pygame.mixer.Sound("car_door.mp3")
    WORD_SOUND = pygame.mixer.Sound("game.mp3")
except:
    EAT_SOUND = pygame.mixer.Sound(buffer=bytearray(44))
    WORD_SOUND = pygame.mixer.Sound(buffer=bytearray(44))

FONT = pygame.font.SysFont("consolas", 36)

WHITE = (245, 245, 245)
GREEN = (0, 200, 0)
RED = (255, 80, 80)
BLUE = (80, 150, 255)
DARK = (30, 30, 30)
YELLOW = (255, 215, 0)
GRAY = (60, 60, 60)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)

def choose_mode():
    screen.fill(BLACK)
    msg = BIG_FONT.render("Choose Game Mode", True, WHITE)
    opt1 = FONT.render("1. AI vs Human", True, YELLOW)
    opt2 = FONT.render("2. AI vs Human vs Human", True, YELLOW)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 100))
    screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, HEIGHT//2 - 20))
    screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, HEIGHT//2 + 40))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return "vs_ai"
                elif e.key == pygame.K_2:
                    return "vs_ai_human2"

def is_valid_word(word):
    return len(word) >= 3 and (word in valid_words or word in short_valid_words)

def get_random_word():
    return random.choice(list(short_valid_words))

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal, snake_body, width, height, obstacles=[]):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    obstacle_positions = {(o[0], o[1]) for o in obstacles}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for dx, dy in [(0, -GRID_SIZE), (0, GRID_SIZE), (-GRID_SIZE, 0), (GRID_SIZE, 0)]:
            neighbor = (current[0]+dx, current[1]+dy)
            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and 
                neighbor not in snake_body and neighbor not in obstacle_positions):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def safe_spawn(exclude):
    while True:
        x = random.randint(2, WIDTH//GRID_SIZE - 3) * GRID_SIZE
        y = random.randint(2, HEIGHT//GRID_SIZE - 3) * GRID_SIZE
        if (x, y) not in exclude:
            return (x, y)

def spawn_letters(word, snake, ai_snake, snake2=None):
    letters = []
    all_positions = snake + ai_snake
    if snake2:
        all_positions += snake2
    for letter in word:
        for _ in range(3):
            while True:
                x = random.randint(0, WIDTH//GRID_SIZE - 1) * GRID_SIZE
                y = random.randint(0, HEIGHT//GRID_SIZE - 1) * GRID_SIZE
                if (x, y) not in all_positions:
                    letters.append((x, y, letter.upper()))
                    all_positions.append((x, y))
                    break
    return letters

def spawn_obstacles(num, exclude):
    types = list(obstacle_symbol.keys())
    obstacles = []
    while len(obstacles) < num:
        x = random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE
        y = random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE
        if (x, y) not in exclude:
            obstacle_type = random.choice(types)
            obstacles.append((x, y, obstacle_type))
            exclude.append((x, y))
    return obstacles

def draw_snake(snake, color):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        if i == 0:
            pygame.draw.circle(screen, BLACK, rect.center, 4)

def draw_game(snake, ai_snake, letters, word, player_index, ai_index, p_score, ai_score, obstacles, mode, snake2=None, player2_index=0):
    screen.fill(DARK)
    draw_snake(snake, GREEN)
    draw_snake(ai_snake, BLUE)
    if mode == "vs_ai_human2" and snake2:
        draw_snake(snake2, YELLOW)

    for x, y, ch in letters:
        pygame.draw.rect(screen, RED, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE), border_radius=3)
        screen.blit(EMOJI_FONT.render(ch, True, WHITE), (x + 2, y + 1))
    
    screen.blit(EMOJI_FONT.render("Target Word: " + word.upper(), True, YELLOW), (WIDTH//2 - 100, 10))
    
    if mode == "vs_ai_human2":
        screen.blit(EMOJI_FONT.render(f"Player 1: {player_index}/{len(word)}", True, GREEN), (20, 10))
        screen.blit(EMOJI_FONT.render(f"Player 2: {player2_index}/{len(word)}", True, YELLOW), (20, 40))
        screen.blit(EMOJI_FONT.render(f"AI: {ai_index}/{len(word)}", True, BLUE), (20, 70))
    else:
        screen.blit(EMOJI_FONT.render(f"Player: {player_index}/{len(word)}", True, GREEN), (20, 10))
        screen.blit(EMOJI_FONT.render(f"AI: {ai_index}/{len(word)}", True, BLUE), (20, 40))
    
    screen.blit(EMOJI_FONT.render(f"Player Score: {p_score}", True, GREEN), (950, 10))
    screen.blit(EMOJI_FONT.render(f"AI Score: {ai_score}", True, BLUE), (950, 40))
    
    for x, y, t in obstacles:
        pygame.draw.rect(screen, obstacle_color[t], pygame.Rect(x, y, GRID_SIZE, GRID_SIZE), border_radius=3)
        screen.blit(EMOJI_FONT.render(obstacle_symbol[t], True, WHITE), (x + 2, y + 2))
    
    pygame.display.flip()

def show_message(text, sub=""):
    screen.fill(BLACK)
    msg = BIG_FONT.render(text, True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
    if sub:
        submsg = EMOJI_FONT.render(sub, True, GRAY)
        screen.blit(submsg, (WIDTH//2 - submsg.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()

def show_scorecard(player_score, ai_score, player2_score=None):
    screen.fill(BLACK)
    game_over_text = BIG_FONT.render("Game Over", True, RED)
    player_text = FONT.render(f"Player Score: {player_score}", True, GREEN)
    ai_text = FONT.render(f"AI Score: {ai_score}", True, BLUE)
    
    if player2_score is not None:
        player2_text = FONT.render(f"Player 2 Score: {player2_score}", True, YELLOW)
        texts = [game_over_text, player_text, player2_text, ai_text]
    else:
        texts = [game_over_text, player_text, ai_text]
    
    for i, text in enumerate(texts):
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100 + i * 40))
    
    replay_text = FONT.render("Press R to Replay or ESC to Quit", True, GRAY)
    screen.blit(replay_text, (WIDTH // 2 - replay_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    while True:
        mode = choose_mode()
        snake = [safe_spawn([])]
        ai_snake = [safe_spawn(snake)]
        snake2 = None
        direction2 = None
        player2_index = 0
        player2_score = 0

        if mode == "vs_ai_human2":
            snake2 = [safe_spawn(snake + ai_snake)]
            direction2 = (-GRID_SIZE, 0)

        obstacles = []
        direction = (GRID_SIZE, 0)
        clock = pygame.time.Clock()
        player_index = 0
        ai_index = 0
        player_score = 0
        ai_score = 0
        ai_freeze_timer = 0
        slow_timer = 0
        ai_slow_timer = 0
        eagle_pos = None
        eagle_tick = 0

        word = get_random_word()
        letters = spawn_letters(word, snake, ai_snake, snake2)
        occupied = snake + ai_snake + [(l[0], l[1]) for l in letters]
        if snake2:
            occupied += snake2
        obstacles = spawn_obstacles(5 + player_score // 5, occupied)
        eagle_list = [o for o in obstacles if o[2] == 'eagle']
        if eagle_list:
            eagle_pos = [eagle_list[0][0], eagle_list[0][1]]

        show_message("Press SPACE to start")
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    break
            else:
                continue
            break

        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return

            keys = pygame.key.get_pressed()
            
            # Player 1 controls
            if keys[pygame.K_UP] and direction != (0, GRID_SIZE):
                direction = (0, -GRID_SIZE)
            elif keys[pygame.K_DOWN] and direction != (0, -GRID_SIZE):
                direction = (0, GRID_SIZE)
            elif keys[pygame.K_LEFT] and direction != (GRID_SIZE, 0):
                direction = (-GRID_SIZE, 0)
            elif keys[pygame.K_RIGHT] and direction != (-GRID_SIZE, 0):
                direction = (GRID_SIZE, 0)

            # Player 1 movement
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if (new_head in snake[1:] or new_head in ai_snake or
                new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                any(new_head == (o[0], o[1]) for o in obstacles)):  # Obstacle collision
                running = False
                break

            if mode == "vs_ai_human2" and new_head in snake2:
                running = False
                break

            snake.insert(0, new_head)
            letter_collected = False
            for l in letters[:]:
                if (l[0], l[1]) == new_head and l[2] == word[player_index].upper():
                    pygame.mixer.Sound.play(EAT_SOUND)
                    player_index += 1
                    player_score += 1
                    letters.remove(l)
                    letter_collected = True
                    break

            if not letter_collected:
                snake.pop()

            if player_index == len(word):
                pygame.mixer.Sound.play(WORD_SOUND)
                player_score += 3
                ai_freeze_timer = 30
                word = get_random_word()
                player_index = 0
                ai_index = 0
                letters = spawn_letters(word, snake, ai_snake, snake2)
                occupied = snake + ai_snake + [(l[0], l[1]) for l in letters]
                if snake2:
                    occupied += snake2
                obstacles = spawn_obstacles(5 + max(player_score, player2_score if mode == "vs_ai_human2" else player_score) // 5, occupied)
                eagle_list = [o for o in obstacles if o[2] == 'eagle']
                if eagle_list:
                    eagle_pos = [eagle_list[0][0], eagle_list[0][1]]

            # Player 2 controls and movement (if in vs_ai_human2 mode)
            if mode == "vs_ai_human2":
                if keys[pygame.K_w] and direction2 != (0, GRID_SIZE):
                    direction2 = (0, -GRID_SIZE)
                elif keys[pygame.K_s] and direction2 != (0, -GRID_SIZE):
                    direction2 = (0, GRID_SIZE)
                elif keys[pygame.K_a] and direction2 != (GRID_SIZE, 0):
                    direction2 = (-GRID_SIZE, 0)
                elif keys[pygame.K_d] and direction2 != (-GRID_SIZE, 0):
                    direction2 = (GRID_SIZE, 0)

                new_head2 = (snake2[0][0] + direction2[0], snake2[0][1] + direction2[1])
                if (new_head2 in snake2[1:] or new_head2 in snake or new_head2 in ai_snake or
                    new_head2[0] < 0 or new_head2[0] >= WIDTH or
                    new_head2[1] < 0 or new_head2[1] >= HEIGHT or
                    any(new_head2 == (o[0], o[1]) for o in obstacles)):  # Obstacle collision
                    running = False
                    break

                snake2.insert(0, new_head2)
                letter_collected2 = False
                for l in letters[:]:
                    if (l[0], l[1]) == new_head2 and l[2] == word[player2_index].upper():
                        pygame.mixer.Sound.play(EAT_SOUND)
                        player2_index += 1
                        player2_score += 1
                        letters.remove(l)
                        letter_collected2 = True
                        break
                if not letter_collected2:
                    snake2.pop()

                if player2_index == len(word):
                    pygame.mixer.Sound.play(WORD_SOUND)
                    player2_score += 3
                    ai_freeze_timer = 30
                    word = get_random_word()
                    player_index = 0
                    player2_index = 0
                    ai_index = 0
                    letters = spawn_letters(word, snake, ai_snake, snake2)
                    occupied = snake + ai_snake + snake2 + [(l[0], l[1]) for l in letters]
                    obstacles = spawn_obstacles(5 + max(player_score, player2_score) // 5, occupied)
                    eagle_list = [o for o in obstacles if o[2] == 'eagle']
                    if eagle_list:
                        eagle_pos = [eagle_list[0][0], eagle_list[0][1]]

            # AI Movement
            if ai_freeze_timer <= 0:
                if letters and ai_index < len(word):
                    targets = [(x, y) for x, y, c in letters if c == word[ai_index].upper()]
                    if targets:
                        closest = min(targets, key=lambda pos: heuristic(ai_snake[0], pos))
                        path = astar(ai_snake[0], closest, ai_snake + snake + (snake2 if snake2 else []), WIDTH, HEIGHT, obstacles)
                        if path:
                            next_pos = path[0]
                            ai_snake.insert(0, next_pos)
                            if next_pos == closest:
                                pygame.mixer.Sound.play(EAT_SOUND)
                                ai_index += 1
                                ai_score += 1
                                for l in letters[:]:
                                    if (l[0], l[1]) == next_pos and l[2] == word[ai_index - 1].upper():
                                        letters.remove(l)
                                        break
                            else:
                                ai_snake.pop()
                    else:
                        ai_snake.pop()
            else:
                ai_freeze_timer -= 1

            if (ai_snake[0] in ai_snake[1:] or ai_snake[0] in snake or
                ai_snake[0][0] < 0 or ai_snake[0][0] >= WIDTH or
                ai_snake[0][1] < 0 or ai_snake[0][1] >= HEIGHT or
                any(ai_snake[0] == (o[0], o[1]) for o in obstacles)):  # Obstacle collision
                running = False
                break

            if mode == "vs_ai_human2" and ai_snake[0] in snake2:
                running = False
                break

            if ai_index == len(word):
                pygame.mixer.Sound.play(WORD_SOUND)
                ai_score += 3
                word = get_random_word()
                player_index = 0
                ai_index = 0
                if mode == "vs_ai_human2":
                    player2_index = 0
                letters = spawn_letters(word, snake, ai_snake, snake2)
                occupied = snake + ai_snake + [(l[0], l[1]) for l in letters]
                if snake2:
                    occupied += snake2
                obstacles = spawn_obstacles(5 + max(player_score, player2_score if mode == "vs_ai_human2" else player_score) // 5, occupied)
                eagle_list = [o for o in obstacles if o[2] == 'eagle']
                if eagle_list:
                    eagle_pos = [eagle_list[0][0], eagle_list[0][1]]

            # Eagle logic
            if eagle_pos:
                eagle_tick += 1
                if eagle_tick % 5 == 0:
                    path = astar((eagle_pos[0], eagle_pos[1]), snake[0], [], WIDTH, HEIGHT, obstacles)
                    if path:
                        eagle_pos[0], eagle_pos[1] = path[0]
                        if (eagle_pos[0], eagle_pos[1]) == snake[0]:
                            running = False
                            break
                for i, o in enumerate(obstacles):
                    if o[2] == 'eagle':
                        obstacles[i] = (eagle_pos[0], eagle_pos[1], 'eagle')

            draw_game(snake, ai_snake, letters, word, player_index, ai_index, player_score, ai_score, obstacles, mode, snake2, player2_index)

            # Apply slowdown
            delay = 0.05 if slow_timer > 0 else 0
            ai_delay = 0.05 if ai_slow_timer > 0 else 0
            if slow_timer > 0: slow_timer -= 1
            if ai_slow_timer > 0: ai_slow_timer -= 1
            pygame.time.delay(int(delay * 1000))
            clock.tick(FPS)

        if mode == "vs_ai_human2":
            if not show_scorecard(player_score, ai_score, player2_score):
                break
        else:
            if not show_scorecard(player_score, ai_score):
                break

if __name__ == "__main__":
    main()