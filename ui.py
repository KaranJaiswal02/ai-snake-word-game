import pygame

# Colors
WHITE = (30, 30, 30)
GREEN = (0, 200, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 215, 0)

GRID_SIZE = 20
GAME_AREA_WIDTH = 1120
GAME_AREA_HEIGHT = 720
MARGIN_X = 40
MARGIN_Y = 60

def draw_snake(screen, snake, color):
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] + MARGIN_X, segment[1] + MARGIN_Y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        if i == 0:  # eyes on head
            eye_size = 4
            cx, cy = rect.center
            pygame.draw.circle(screen, BLACK, (cx - 4, cy - 4), eye_size)
            pygame.draw.circle(screen, BLACK, (cx + 4, cy - 4), eye_size)

def draw_game(screen, snake, ai_snake, letters, collected_letters, ai_collected_letters, FONT):
    screen.fill(DARK_GRAY)

    # Draw game boundary
    pygame.draw.rect(screen, GRAY, (MARGIN_X - 2, MARGIN_Y - 2, GAME_AREA_WIDTH + 4, GAME_AREA_HEIGHT + 4), 2)

    # Draw snakes
    draw_snake(screen, snake, GREEN)
    draw_snake(screen, ai_snake, BLUE)

    # Draw letters
    for letter in letters:
        lx, ly = letter[0] + MARGIN_X, letter[1] + MARGIN_Y
        rect = pygame.Rect(lx, ly, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect, border_radius=3)
        char_surface = FONT.render(letter[2], True, WHITE)
        screen.blit(char_surface, (lx + (GRID_SIZE - char_surface.get_width()) // 2, ly + (GRID_SIZE - char_surface.get_height()) // 2))

    # Info bar on top
    player_text = FONT.render(f"Player: {collected_letters}", True, YELLOW)
    ai_text = FONT.render(f"AI: {ai_collected_letters}", True, YELLOW)
    screen.blit(player_text, (MARGIN_X, 20))
    screen.blit(ai_text, (MARGIN_X + 300, 20))

    pygame.display.flip()
