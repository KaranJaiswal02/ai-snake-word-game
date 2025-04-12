import pygame
import random
import string
import nltk
from nltk.corpus import words
import heapq

nltk.download('words')
valid_words = set(w.lower() for w in words.words())
short_valid_words = {
    "cat", "dog", "car", "sun", "run", "red", "man", "fun", "cup", "map", "top", "toy", "box", "fox", "log",
    "yes", "hat", "bat", "rat", "mat", "pot", "pen", "can", "win", "bus", "net", "dot", "fan", "bed", "egg",
    "four", "five", "cool", "look", "make", "game", "word", "play", "code", "read"
}

WIDTH, HEIGHT = 1200, 800
GRID_SIZE = 20
FPS = 10

pygame.init()
pygame.mixer.init()
FONT = pygame.font.SysFont("consolas", 24)
BIG_FONT = pygame.font.SysFont("consolas", 48)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")

EAT_SOUND = pygame.mixer.Sound("car_door.mp3")
WORD_SOUND = pygame.mixer.Sound("game.mp3")

WHITE = (245, 245, 245)
GREEN = (0, 200, 0)
RED = (255, 80, 80)
BLUE = (80, 150, 255)
DARK = (30, 30, 30)
YELLOW = (255, 215, 0)
GRAY = (60, 60, 60)
BLACK = (0, 0, 0)

def is_valid_word(word):
    return len(word) >= 3 and (word in valid_words or word in short_valid_words)

def get_random_word():
    return random.choice(list(short_valid_words))

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal, snake_body, width, height):
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
            neighbor = (current[0]+dx, current[1]+dy)
            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and neighbor not in snake_body):
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

def spawn_letters(word, snake, ai_snake):
    letters = []
    all_positions = snake + ai_snake
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

def draw_snake(snake, color):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        if i == 0:
            pygame.draw.circle(screen, BLACK, rect.center, 4)

def draw_game(snake, ai_snake, letters, word, player_index, ai_index, p_score, ai_score):
    screen.fill(DARK)
    draw_snake(snake, GREEN)
    draw_snake(ai_snake, BLUE)
    for x, y, ch in letters:
        pygame.draw.rect(screen, RED, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE), border_radius=3)
        screen.blit(FONT.render(ch, True, WHITE), (x + 2, y + 1))
    screen.blit(FONT.render("Target Word: " + word.upper(), True, YELLOW), (WIDTH//2 - 100, 10))
    screen.blit(FONT.render(f"Player Collected: {player_index}/{len(word)}", True, WHITE), (20, 10))
    screen.blit(FONT.render(f"AI Collected: {ai_index}/{len(word)}", True, WHITE), (20, 40))
    screen.blit(FONT.render(f"Player Score: {p_score}", True, GREEN), (950, 10))
    screen.blit(FONT.render(f"AI Score: {ai_score}", True, BLUE), (950, 40))
    pygame.display.flip()

def show_message(text, sub=""):
    screen.fill(BLACK)
    msg = BIG_FONT.render(text, True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
    if sub:
        submsg = FONT.render(sub, True, GRAY)
        screen.blit(submsg, (WIDTH//2 - submsg.get_width()//2, HEIGHT//2 + 20))
    pygame.display.flip()

def ask_play_again():
    show_message("Game Over", "Press R to Replay or ESC to Exit")
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False

def main():
    while True:
        snake = [safe_spawn([])]
        ai_snake = [safe_spawn(snake)]
        direction = (GRID_SIZE, 0)
        clock = pygame.time.Clock()
        player_index = 0
        ai_index = 0
        player_score = 0
        ai_score = 0
        word = get_random_word()
        letters = spawn_letters(word, snake, ai_snake)

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
            if keys[pygame.K_UP] and direction != (0, GRID_SIZE):
                direction = (0, -GRID_SIZE)
            elif keys[pygame.K_DOWN] and direction != (0, -GRID_SIZE):
                direction = (0, GRID_SIZE)
            elif keys[pygame.K_LEFT] and direction != (GRID_SIZE, 0):
                direction = (-GRID_SIZE, 0)
            elif keys[pygame.K_RIGHT] and direction != (-GRID_SIZE, 0):
                direction = (GRID_SIZE, 0)

            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if (new_head in snake[1:] or new_head in ai_snake or
                new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT):
                running = False
                break

            snake.insert(0, new_head)
            if not any((new_head[0], new_head[1]) == (l[0], l[1]) and l[2] == word[player_index].upper() for l in letters):
                snake.pop()
            for l in letters:
                if (l[0], l[1]) == new_head and l[2] == word[player_index].upper():
                    pygame.mixer.Sound.play(EAT_SOUND)
                    player_index += 1
                    player_score += 1
                    letters.remove(l)
                    break
            if player_index == len(word):
                pygame.mixer.Sound.play(WORD_SOUND)
                player_score += 3
                word = get_random_word()
                player_index = 0
                ai_index = 0
                letters = spawn_letters(word, snake, ai_snake)

            if letters and ai_index < len(word):
                targets = [(x, y) for x, y, c in letters if c == word[ai_index].upper()]
                if targets:
                    closest = min(targets, key=lambda pos: heuristic(ai_snake[0], pos))
                    path = astar(ai_snake[0], closest, ai_snake + snake, WIDTH, HEIGHT)
                    if path:
                        next_pos = path[0]
                        ai_snake.insert(0, next_pos)
                        if next_pos == closest:
                            pygame.mixer.Sound.play(EAT_SOUND)
                            ai_index += 1
                            ai_score += 1
                            for l in letters:
                                if (l[0], l[1]) == next_pos and l[2] == word[ai_index-1].upper():
                                    letters.remove(l)
                                    break
                        else:
                            ai_snake.pop()
                else:
                    ai_snake.pop()

            if (ai_snake[0] in ai_snake[1:] or ai_snake[0] in snake or
                ai_snake[0][0] < 0 or ai_snake[0][0] >= WIDTH or ai_snake[0][1] < 0 or ai_snake[0][1] >= HEIGHT):
                running = False
                break

            if ai_index == len(word):
                pygame.mixer.Sound.play(WORD_SOUND)
                ai_score += 3
                word = get_random_word()
                player_index = 0
                ai_index = 0
                letters = spawn_letters(word, snake, ai_snake)

            draw_game(snake, ai_snake, letters, word, player_index, ai_index, player_score, ai_score)
            clock.tick(FPS)

        if not ask_play_again():
            break
        else:
            show_message(f"Final Score - Player: {player_score}, AI: {ai_score}", "Press R to Replay or ESC to Exit")

if __name__ == "__main__":
    main()
