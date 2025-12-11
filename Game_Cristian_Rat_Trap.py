import pygame, sys, os
from collections import deque

pygame.init()

# ------------------ INT-НАСТРОЙКИ  ------------------
WIDTH, HEIGHT = 640,448

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rat Trap")

clock = pygame.time.Clock()
FPS = 10

TILE = 64

# --- Rutas ---
base_path = r"C:\Users\Пользователь\Desktop\cris_rat_trap"
sprite_path = os.path.join(base_path, "sprite_rat01.png")
cheese_path = os.path.join(base_path, "cheese_small.png")

# ------------------ CHARGING OF SPRITES- ЗАГРУЗКА СПРАЙТОВ ------------------
# RATA
spritesheet = pygame.image.load(sprite_path).convert_alpha()
frame_width, frame_height = 64, 64
num_frames = spritesheet.get_width() // frame_width
frames = [
    spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    for i in range(num_frames)
]
current_frame = 0

# QUESO ANIMADO
spritesheet_cheese = pygame.image.load(cheese_path).convert_alpha()
cheese_frame_width, cheese_frame_height = 64, 64
cheese_num_frames = spritesheet_cheese.get_width() // cheese_frame_width

cheese_frames = [
    spritesheet_cheese.subsurface(pygame.Rect(i * cheese_frame_width, 0, cheese_frame_width, cheese_frame_height))
    for i in range(cheese_num_frames)
]
cheese_current_frame = 0

# ------------------ЛАБИРИНТ ------------------
maze = [
    "1111111111",  # Fila 0
    "1R00001001",  # Fila 1 - Rata en (1,1)
    "1011010101",  # Fila 2
    "1000000101",  # Fila 3
    "1010110101",  # Fila 4
    "1000000001",  # Fila 5
    "1111111111"   # Fila 6
]


# Buscar posición inicial de la rata
rat_cx = rat_cy = 0
for y, row in enumerate(maze):
    for x, val in enumerate(row):
        if val == "R":
            rat_cx, rat_cy = x, y

# ------------------ ПОИСК САМОЙ ДАЛЕКОЙ ТОЧКИ  ------------------
def find_farthest_point(start_x, start_y):
    rows = len(maze)
    cols = len(maze[0])
    
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    queue = deque()
    queue.append((start_x, start_y, 0))
    visited[start_y][start_x] = True
    
    farthest_x, farthest_y = start_x, start_y
    max_distance = 0
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    while queue:
        x, y, dist = queue.popleft()
        
        if dist > max_distance and maze[y][x] != "1":
            max_distance = dist
            farthest_x, farthest_y = x, y
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if (0 <= nx < cols and 0 <= ny < rows and 
                not visited[ny][nx] and maze[ny][nx] != "1"):
                visited[ny][nx] = True
                queue.append((nx, ny, dist + 1))
    
    return farthest_x, farthest_y

# Encontrar posición para el queso
cheese_cx, cheese_cy = find_farthest_point(rat_cx, rat_cy)

# Asegurarse de que no sea la misma posición inicial
while cheese_cx == rat_cx and cheese_cy == rat_cy:
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for dx, dy in directions:
        nx, ny = cheese_cx + dx, cheese_cy + dy
        if maze[ny][nx] != "1":
            cheese_cx, cheese_cy = nx, ny
            break

# ------------------ ФУНКЦИИ  ------------------
def draw_maze():
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
            if tile == "1":
                pygame.draw.rect(screen, (120, 80, 40), rect)
            else:
                pygame.draw.rect(screen, (195, 195, 195), rect)

def is_walkable(x, y):
    if maze[y][x] in ("0", "R"):
        return True
    return False

# ------------------ ГЛАВНЫЙ ЦИКЛ ------------------
running = True
won = False

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    new_cx, new_cy = rat_cx, rat_cy

    # Movimiento
    if keys[pygame.K_UP]:
        new_cy -= 1
    if keys[pygame.K_DOWN]:
        new_cy += 1
    if keys[pygame.K_LEFT]:
        new_cx -= 1
    if keys[pygame.K_RIGHT]:
        new_cx += 1

    # Solo moverse si es camino
    if is_walkable(new_cx, new_cy):
        rat_cx, rat_cy = new_cx, new_cy
        current_frame += 0.5
        if current_frame >= num_frames:
            current_frame = 0
    else:
        current_frame = 0

    # ¿Ganó?
    if rat_cx == cheese_cx and rat_cy == cheese_cy:
        won = True

    # ------------------ DIBUJAR ------------------
    screen.fill((0, 0, 0))
    draw_maze()

    # Dibujar queso animado (CORREGIDO)
    if len(cheese_frames) > 0:
        # Animación del queso
        cheese_current_frame += 0.3
        if cheese_current_frame >= len(cheese_frames):
            cheese_current_frame = 0
            
        current_cheese_frame = cheese_frames[int(cheese_current_frame)]
        cheese_px = cheese_cx*TILE + TILE//2 - current_cheese_frame.get_width()//2
        cheese_py = cheese_cy*TILE + TILE//2 - current_cheese_frame.get_height()//2
        screen.blit(current_cheese_frame, (cheese_px, cheese_py))

    # Dibujar rata animada
    rat_px = rat_cx*TILE + TILE//2 - frame_width//2
    rat_py = rat_cy*TILE + TILE//2 - frame_height//2
    screen.blit(frames[int(current_frame)], (rat_px, rat_py))

    if won:
        font = pygame.font.SysFont(None, 60)
        text = font.render("¡Ganaste!", True, (255, 255, 0))
        screen.blit(text, (WIDTH//2 - 120, HEIGHT//2 - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()