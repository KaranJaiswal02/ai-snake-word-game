import random
import heapq
import string
import nltk
from nltk.corpus import words

nltk.download('words')
valid_words = set(words.words())

GRID_SIZE = 20

common_two_letter_words = {
    "as", "at", "be", "by", "do", "go", "he", "if", "in", "is", "it",
    "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we"
}

def is_valid_word(word):
    word = word.lower()
    return (len(word) > 2 and word in valid_words) or (len(word) == 2 and word in common_two_letter_words)

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
            if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height and neighbor not in ai_snake:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []

def get_closest_letter(position, letters):
    return min(letters, key=lambda l: heuristic(position, (l[0], l[1])))

def check_valid_word(collected_letters):
    for i in range(len(collected_letters)):
        word_to_check = collected_letters[i:]
        if is_valid_word(word_to_check):
            return word_to_check
    return None

def spawn_letter(snake, ai_snake, width, height):
    while True:
        x = random.randint(0, (width // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (height // GRID_SIZE) - 1) * GRID_SIZE
        if (x, y) not in snake and (x, y) not in ai_snake:
            return (x, y, random.choice(string.ascii_uppercase))
