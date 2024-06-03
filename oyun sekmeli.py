import pygame
import math
import random

# Pygame'i başlat
pygame.init()

# Oyun ekranı boyutları
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platform Oyunu")

# Renkler
NIGHT_BLUE = (25, 25, 112)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# PNG resimlerini yükle
background_img = pygame.image.load('background.png')
player1_img = pygame.image.load('player1.png')
player2_img = pygame.image.load('player2.png')

# PNG resimlerini 10 kat küçült
player1_img = pygame.transform.scale(player1_img, (player1_img.get_width() // 10, player1_img.get_height() // 10))
player2_img = pygame.transform.scale(player2_img, (player2_img.get_width() // 10, player2_img.get_height() // 10))

# Oyuncu boyutları ve başlangıç pozisyonları
player1_size = player1_img.get_rect().size
player2_size = player2_img.get_rect().size
player1_pos = [50 + 210, HEIGHT // 2 - player1_size[1] // 2 + 270]
player2_pos = [WIDTH - 50 - 210 - player2_size[0], HEIGHT // 2 - player2_size[1] // 2 + 270]

# Havai fişek animasyonu için ayarlar
fireworks = []

# Görünmez dikdörtgenlerin konumu ve boyutları
left_rect = pygame.Rect(0,836, 320, 244)
right_rect = pygame.Rect(1600 , 836 , 320, 244)

# Çizim fonksiyonu
def draw_game():
    screen.blit(background_img, (0, 0))
    screen.blit(player1_img, player1_pos)
    screen.blit(player2_img, player2_pos)

    if ball_pos:
        pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), 5)
    if winner:
        draw_winner(winner)
    else:
        draw_turn()
    pygame.display.flip()

font = pygame.font.Font(None, 36)
input_active = 'angle'
input_angle = ''
input_speed = ''
player_turn = 1
ball_pos = None
ball_vel = None
gravity = 9.8
mass = 100
winner = None
player1_name = ""
player2_name = ""
player1_input_active = True
player2_input_active = False
game_started = False

def draw_input():
    global input_angle, input_speed, input_active

    input_box = pygame.Rect(20, 20, 140, 32)
    color_active = pygame.Color('black')
    color_inactive = pygame.Color('orange')
    angle_color = color_active if input_active == 'angle' else color_inactive
    speed_color = color_active if input_active == 'speed' else color_inactive

    text_surface = font.render(f"Açı giriniz: {input_angle}", True, angle_color)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    input_box.y += 40
    text_surface = font.render(f"Hız giriniz: {input_speed}", True, speed_color)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    button_rect = pygame.Rect(20, input_box.y + 40, 100, 32)
    pygame.draw.rect(screen, WHITE, button_rect)
    text_surface = font.render("VUR", True, NIGHT_BLUE)
    screen.blit(text_surface, (button_rect.x + 5, button_rect.y + 5))

    pygame.display.flip()
    return button_rect

def calculate_trajectory(angle, speed):
    radian_angle = math.radians(angle)
    vx = speed * math.cos(radian_angle)
    vy = -speed * math.sin(radian_angle)
    return vx, vy

def update_ball_position(ball_pos, ball_vel, dt):
    ball_pos[0] += ball_vel[0] * dt
    ball_pos[1] += ball_vel[1] * dt
    ball_vel[1] += gravity * dt

    # Ekran dışına çıkan topu geri getirmeme
    if ball_pos[0] < 0 or ball_pos[0] > WIDTH or ball_pos[1] > HEIGHT:
        ball_pos = None  # Top ekran dışına çıkarsa sonsuza gider
    if ball_pos and ball_pos[1] < 0:
        ball_pos[1] = 0
        ball_vel[1] = abs(ball_vel[1])  # Yukarıdan gelen top geri dönsün

    # Görünmez dikdörtgenlere çarpma kontrolü
    if ball_pos and left_rect.collidepoint(ball_pos):
        if ball_vel[0] < 0:
            ball_vel[0] = abs(ball_vel[0])  # Sol duvara çarpan top sağa seker
    if ball_pos and right_rect.collidepoint(ball_pos):
        if ball_vel[0] > 0:
            ball_vel[0] = -abs(ball_vel[0])  # Sağ duvara çarpan top sola seker

    return ball_pos, ball_vel

def check_collision(ball_pos, player_pos, player_size):
    px, py = player_pos
    bx, by = ball_pos
    if px <= bx <= px + player_size[0] and py <= by <= py + player_size[1]:
        return True
    return False

def draw_winner(winner):
    text_surface = font.render(f"K.O (KAZANDIN OĞLUUUM) - {winner} Kazandı!", True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
    draw_fireworks()
    pygame.display.flip()

def draw_fireworks():
    for firework in fireworks:
        for particle in firework['particles']:
            pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), int(particle['radius']))

def update_fireworks():
    for firework in fireworks:
        for particle in firework['particles']:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += gravity * 0.1  # Yer çekimi etkisi
            particle['radius'] -= 0.03  # Daha yavaş küçülsün
        firework['particles'] = [p for p in firework['particles'] if p['radius'] > 0]
    fireworks[:] = [f for f in fireworks if f['particles']]

def create_firework(x, y):
    colors = [RED, YELLOW, WHITE]
    particles = []
    for _ in range(100):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        color = random.choice(colors)
        particles.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'color': color, 'radius': 9})  # 3 kat büyük
    fireworks.append({'particles': particles})

def draw_name_input():
    screen.fill(NIGHT_BLUE)
    if player1_input_active:
        prompt = "Oyuncu 1 ismi:"
        text_surface = font.render(prompt + player1_name, True, WHITE)
    else:
        prompt = "Oyuncu 2 ismi:"
        text_surface = font.render(prompt + player2_name, True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - text_surface.get_height() // 2))
    pygame.display.flip()

def draw_turn():
    turn_text = f"{player1_name if player_turn == 1 else player2_name} sıra sende!"
    text_surface = font.render(turn_text, True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 50))

running = True
fireworks_timer = 0
while running:
    dt = pygame.time.Clock().tick(60) / 1000  # Delta time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not game_started:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player1_input_active:
                        player1_input_active = False
                        player2_input_active = True
                    elif player2_input_active:
                        game_started = True
                        player2_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    if player1_input_active:
                        player1_name = player1_name[:-1]
                    elif player2_input_active:
                        player2_name = player2_name[:-1]
                else:
                    if player1_input_active:
                        player1_name += event.unicode
                    elif player2_input_active:
                        player2_name += event.unicode
        elif game_started:
            if event.type == pygame.MOUSEBUTTONDOWN and not winner:
                if button_rect.collidepoint(event.pos):
                    if input_angle and input_speed:
                        angle = float(input_angle)
                        speed = float(input_speed)
                        vx, vy = calculate_trajectory(angle, speed)
                        ball_pos = list(player1_pos if player_turn == 1 else player2_pos)
                        ball_vel = [vx, vy]
                        player_turn = 2 if player_turn == 1 else 1
                        input_angle, input_speed = '', ''
                        input_active = 'angle'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if input_active == 'angle':
                        input_active = 'speed'
                    else:
                        input_active = 'angle'
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == 'angle':
                        input_angle = input_angle[:-1]
                    elif input_active == 'speed':
                        input_speed = input_speed[:-1]
                elif event.key == pygame.K_RETURN:
                    if input_active == 'angle':
                        input_active = 'speed'
                    elif input_active == 'speed':
                        if input_angle and input_speed:
                            angle = float(input_angle)
                            speed = float(input_speed)
                            vx, vy = calculate_trajectory(angle, speed)
                            ball_pos = list(player1_pos if player_turn == 1 else player2_pos)
                            ball_vel = [vx, vy]
                            player_turn = 2 if player_turn == 1 else 1
                            input_angle, input_speed = '', ''
                            input_active = 'angle'
                elif event.unicode.isdigit() or event.unicode == '.':
                    if input_active == 'angle':
                        input_angle += event.unicode
                    elif input_active == 'speed':
                        input_speed += event.unicode

    if game_started:
        draw_game()
        if not winner:
            button_rect = draw_input()

        if ball_pos and ball_vel:
            ball_pos, ball_vel = update_ball_position(ball_pos, ball_vel, dt)

            if ball_pos and check_collision(ball_pos, player1_pos, player1_size):
                winner = player2_name
                create_firework(WIDTH // 2, HEIGHT // 2)
                fireworks_timer = 0
            elif ball_pos and check_collision(ball_pos, player2_pos, player2_size):
                winner = player1_name
                create_firework(WIDTH // 2, HEIGHT // 2)
                fireworks_timer = 0

        if winner:
            update_fireworks()
            if fireworks_timer > 20:
                running = False
    else:
        draw_name_input()

pygame.quit()
