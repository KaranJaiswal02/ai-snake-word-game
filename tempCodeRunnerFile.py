for p in particles:
        pygame.draw.circle(screen, (80, 80, 80), (int(p['x']), int(p['y'])), p['size'])
        p['x'] -= p['speed']
        if p['x'] < 0:
            p['x'] = WIDTH
            p['y'] = random.randint(0, HEIGHT)