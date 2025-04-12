import pygame
import random
import string

# Constants
WIDTH, HEIGHT = 1200, 800
GRID_SIZE = 20
MARGIN_X = 40
MARGIN_Y = 60
FPS = 10

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
YELLOW = (255, 215, 0)

# Pygame setup
pygame.init()
FONT = pygame.font.Font(None, 28)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Word Snake")


def draw_snake(screen, snake, color):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] + MARGIN_X, segment[1] + MARGIN_Y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        if i == 0:
            eye_size = 4
            cx, cy = rect.center
            pygame.draw.circle(screen, BLACK, (cx - 4, cy - 4), eye_size)
            pygame.draw.circle(screen, BLACK, (cx + 4, cy - 4), eye_size)


def draw_game(screen, snake, ai_snake, letters, collected_letters, ai_collected_letters):
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


def show_start_screen():
    screen.fill(WHITE)
    title = FONT.render("AI Word Snake", True, BLACK)
    msg = FONT.render("Press SPACE to Start", True, (100, 100, 100))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()


def show_game_over(score):
    screen.fill((20, 20, 20))
    over_text = FONT.render("Game Over!", True, RED)
    score_text = FONT.render(f"Words formed: {score}", True, YELLOW)
    exit_text = FONT.render("Press ESC to Quit", True, GRAY)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.flip()


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
