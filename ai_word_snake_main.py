import math
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

WIDTH, HEIGHT = 1550, 775
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
BACKGROUND_COLOR = (0, 0, 0)  # Black background


# Add to initialization
particles = []
for _ in range(50):
    particles.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'size': random.randint(1, 3),
        'speed': random.uniform(0.1, 0.5)
    })

def choose_mode():
    import math
    screen_rect = screen.get_rect()
    msg = BIG_FONT.render("Choose Game Mode", True, WHITE)
    opt_texts = ["AI vs Human", "AI vs Human vs Human"]
    selected = 0
    clock = pygame.time.Clock()
    t = 0  # time variable for animation

    def draw_gradient_background(tick):
        top_color = (40, 0, 80)    # deep indigo
        mid_color = (128, 0, 128)  # vibrant purple
        bottom_color = (30, 144, 255)  # soft sky blue

        height = screen_rect.height
        for y in range(height):
            blend = y / height
            wave = math.sin(tick + y * 0.01) * 0.1  # gentle animation
            blend += wave
            blend = max(0, min(blend, 1))  # clamp to [0,1]

            if blend < 0.5:
                ratio = blend * 2
                r = int(top_color[0] * (1 - ratio) + mid_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + mid_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + mid_color[2] * ratio)
            else:
                ratio = (blend - 0.5) * 2
                r = int(mid_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(mid_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(mid_color[2] * (1 - ratio) + bottom_color[2] * ratio)

            pygame.draw.line(screen, (r, g, b), (0, y), (screen_rect.width, y))


    while True:
        clock.tick(60)
        t += 0.05
        draw_gradient_background(t)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))

        for i, text in enumerate(opt_texts):
            is_selected = (i == selected)
            font = BIG_FONT if is_selected else FONT
            color = YELLOW
            rendered = font.render(text, True, color)
            rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 60))

            if is_selected:
                # Draw highlight background
                pygame.draw.rect(screen, (50, 50, 50), rect.inflate(40, 20), border_radius=10)
                # Fake glow
                glow_color = (255, 255, 150)
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    glow = font.render(text, True, glow_color)
                    screen.blit(glow, rect.move(dx, dy))
                # Draw arrow
                arrow = FONT.render(">", True, WHITE)
                arrow_rect = arrow.get_rect(midright=(rect.left - 10, rect.centery))
                screen.blit(arrow, arrow_rect)

            screen.blit(rendered, rect)

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opt_texts)
                elif e.key == pygame.K_UP:
                    selected = (selected - 1) % len(opt_texts)
                elif e.key == pygame.K_RETURN:
                    return "vs_ai" if selected == 0 else "vs_ai_human2"


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

def draw_snake(snake, color, direction):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
        
        # Gradient body - darker towards tail
        shade = max(50, 255 - i*3)
        body_color = (min(color[0], shade), min(color[1], shade), min(color[2], shade))
        pygame.draw.rect(screen, body_color, rect, border_radius=5)
        
        # Head with eyes looking in movement direction
        if i == 0:
            pygame.draw.rect(screen, color, rect, border_radius=5)
            eye_offset_x = 5 if direction[0] > 0 else -5 if direction[0] < 0 else 0
            eye_offset_y = -5 if direction[1] == 0 else (5 if direction[1] > 0 else -5)
            pygame.draw.circle(screen, WHITE, (rect.centerx + eye_offset_x, rect.centery + eye_offset_y), 4)
            pygame.draw.circle(screen, BLACK, (rect.centerx + eye_offset_x, rect.centery + eye_offset_y), 2)

def draw_game(snake, ai_snake, letters, word, player_index, ai_index, p_score, ai_score, obstacles, mode, snake2=None, player2_index=0):
    screen.fill(DARK)
    #deepseek
    #it was commented till before for loop forgot why commented so uncommented it
    # for p in particles:
    #     pygame.draw.circle(screen, (80, 80, 80), (int(p['x']), int(p['y'])), p['size'])
    #     p['x'] -= p['speed']
    #     if p['x'] < 0:
    #         p['x'] = WIDTH
    #         p['y'] = random.randint(0, HEIGHT)
    for p in particles:
        if 'speed' in p:
            # Background floating particle
            pygame.draw.circle(screen, (80, 80, 80), (int(p['x']), int(p['y'])), p['size'])
            p['x'] -= p['speed']
            if p['x'] < 0:
                p['x'] = WIDTH
                p['y'] = random.randint(0, HEIGHT)
        else:
            # Burst particles from letter collection
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            p['life'] -= 50
        #can remove if we dont like it
        #   
    # Semi-transparent score panel
    score_panel = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    score_panel.fill((30, 30, 30, 180))
    screen.blit(score_panel, (0, 0))
    
    # Progress bar for word completion
    pygame.draw.rect(screen, (60, 60, 60), (WIDTH//2 - 150, 50, 300, 10), border_radius=5)
    progress = player_index/len(word) * 300
    pygame.draw.rect(screen, GREEN, (WIDTH//2 - 150, 50, progress, 10), border_radius=5)
    
    # Score with icons
    screen.blit(EMOJI_FONT.render("🐍", True, WHITE), (20, 15))
    screen.blit(FONT.render(f"{p_score}", True, GREEN), (50, 15))
    
    screen.blit(EMOJI_FONT.render("🤖", True, WHITE), (120, 15))
    screen.blit(FONT.render(f"{ai_score}", True, BLUE), (150, 15))
    
    # Word display with background
    word_bg = pygame.Surface((FONT.size(word.upper())[0] + 20, 40), pygame.SRCALPHA)
    word_bg.fill((0, 0, 0, 150))
    screen.blit(word_bg, (WIDTH//2 - word_bg.get_width()//2, 10))
    screen.blit(FONT.render(word.upper(), True, YELLOW), (WIDTH//2 - FONT.size(word.upper())[0]//2, 15))


    draw_snake(snake, GREEN, direction=(GRID_SIZE, 0))
    draw_snake(ai_snake, BLUE, direction=(GRID_SIZE, 0))
    if mode == "vs_ai_human2" and snake2:
        draw_snake(snake2, YELLOW, direction=(GRID_SIZE, 0))

    for x, y, ch in letters:
        pygame.draw.rect(screen, RED, pygame.Rect(x, y, GRID_SIZE, GRID_SIZE), border_radius=3)
        screen.blit(EMOJI_FONT.render(ch, True, WHITE), (x + 2, y + 1))
    
   # screen.blit(EMOJI_FONT.render("Target Word: " + word.upper(), True, YELLOW), (WIDTH//2 - 100, 10))
    
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
    tick = pygame.time.get_ticks() / 500  # animate the gradient over time

    # --- Gradient background like menu ---
    top_color = (40, 0, 80)
    mid_color = (128, 0, 128)
    bottom_color = (30, 144, 255)
    height = screen.get_height()

    for y in range(height):
        blend = y / height
        wave = math.sin(tick + y * 0.01) * 0.1
        blend += wave
        blend = max(0, min(blend, 1))

        if blend < 0.5:
            ratio = blend * 2
            r = int(top_color[0] * (1 - ratio) + mid_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + mid_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + mid_color[2] * ratio)
        else:
            ratio = (blend - 0.5) * 2
            r = int(mid_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(mid_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(mid_color[2] * (1 - ratio) + bottom_color[2] * ratio)

        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # --- Render message text ---
    msg = BIG_FONT.render(text, True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))

    if sub:
        submsg = EMOJI_FONT.render(sub, True, GRAY)
        screen.blit(submsg, (WIDTH//2 - submsg.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

def show_scorecard(player_score, ai_score, player2_score=None):
    def draw_gradient_background(tick):
        top_color = (40, 0, 80)    # deep indigo
        mid_color = (128, 0, 128)  # vibrant purple
        bottom_color = (30, 144, 255)  # soft sky blue

        height = screen.get_height()
        for y in range(height):
            blend = y / height
            wave = math.sin(tick + y * 0.01) * 0.05  # more subtle animation
            blend += wave
            blend = max(0, min(blend, 1))  # clamp to [0,1]

            if blend < 0.5:
                ratio = blend * 2
                r = int(top_color[0] * (1 - ratio) + mid_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + mid_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + mid_color[2] * ratio)
            else:
                ratio = (blend - 0.5) * 2
                r = int(mid_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(mid_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(mid_color[2] * (1 - ratio) + bottom_color[2] * ratio)

            pygame.draw.line(screen, (r, g, b), (0, y), (screen.get_width(), y))
    tick = 0
    while True:
        draw_gradient_background(tick)
        tick += 0.05

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
                    # Countdown before starting
                    for count in range(5, 0, -1):
                        screen.fill(BACKGROUND_COLOR)
                        draw_game(snake, ai_snake, letters, word, player_index, ai_index, player_score, ai_score, obstacles, mode, snake2, player2_index)
                        text = FONT.render(str(count), True, (255, 255, 255))
                        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(text, rect)
                        pygame.display.flip()
                        pygame.time.delay(1000)

                    # Optional 'GO!' flash
                    screen.fill(BACKGROUND_COLOR)
                    draw_game(snake, ai_snake, letters, word, player_index, ai_index, player_score, ai_score, obstacles, mode, snake2, player2_index)
                    go_text = FONT.render("GO!", True, (0, 255, 0))
                    go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    screen.blit(go_text, go_rect)
                    pygame.display.flip()
                    pygame.time.delay(500)
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
                    # Add to letter collection logic
                    if letter_collected:
                        # Create particle effect
                        for _ in range(10):
                            particles.append({
                                'x': new_head[0] + GRID_SIZE//2,
                                'y': new_head[1] + GRID_SIZE//2,
                                'size': random.randint(2, 4),
                                'speed_x': random.uniform(-2, 2),
                                'speed_y': random.uniform(-2, 2),
                                'color': (random.randint(200, 255), random.randint(100, 200), random.randint(50, 150)),
                                'life': 30
                            })
                    break

            if not letter_collected:
                snake.pop()

            if player_index == len(word):
                pygame.mixer.Sound.play(WORD_SOUND)
                player_score += 3
                ai_freeze_timer = 50
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
                        # Add to letter collection logic
                        if letter_collected2:
                            # Create particle effect
                            for _ in range(10):
                                particles.append({
                                    'x': new_head[0] + GRID_SIZE//2,
                                    'y': new_head[1] + GRID_SIZE//2,
                                    'size': random.randint(2, 4),
                                    'speed_x': random.uniform(-2, 2),
                                    'speed_y': random.uniform(-2, 2),
                                    'color': (random.randint(200, 255), random.randint(100, 200), random.randint(50, 150)),
                                    'life': 50
                                })
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