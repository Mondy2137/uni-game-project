import pygame
import sys
import os
import math
from collections import deque

# Initialize Pygame
pygame.init()

# Window settings
GRID_SIZE = 50
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
UI_HEIGHT = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - Gra tegotypu")

towers = []
enemies = []
floating_texts = []
selected_tower_type = "arrow"
gold = 100

logo = pygame.image.load(os.path.join("assets", "logo.png"))
logo = pygame.transform.scale(logo, (800, 450))

start_button_image = pygame.image.load(os.path.join("assets", "start_button.png"))
start_button_image = pygame.transform.scale(start_button_image, (500, 300))

font = pygame.font.SysFont('Arial', 30)
tooltip_name_font = pygame.font.SysFont('Arial', 22, bold=True)
tooltip_cost_font = pygame.font.SysFont('Arial', 20)
tooltip_stats_font = pygame.font.SysFont('Arial', 18)

title_font = pygame.font.SysFont('Arial', 60)
button_font = pygame.font.SysFont('Arial', 40)

clock = pygame.time.Clock()

current_round = 0
max_rounds = 5
enemies_to_spawn = 0
spawn_interval = 0.5
spawn_timer = 0
round_timer = 10
between_round_delay = 20 
round_active = False
game_over = False


def get_grid_pos(x, y):
    return (x // GRID_SIZE) * GRID_SIZE, (y // GRID_SIZE) * GRID_SIZE

def bfs_path(start, goal, obstacles):
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path

        x, y = current
        neighbors = [
            (x + GRID_SIZE, y), (x - GRID_SIZE, y),
            (x, y + GRID_SIZE), (x, y - GRID_SIZE)
        ]

        for nx, ny in neighbors:
            if 0 <= nx < SCREEN_WIDTH and 0 <= ny < SCREEN_HEIGHT - UI_HEIGHT:
                if (nx, ny) not in visited and (nx, ny) not in obstacles:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))

    print("No path found")
    return [start]
    
def show_start_screen():
    while True:
        screen.fill((30, 30, 30))

        screen.blit(logo, (SCREEN_WIDTH // 2 - logo.get_width() // 2, 35))

        button_x = SCREEN_WIDTH // 2 - start_button_image.get_width() // 2
        button_y = 400
        mouse_x, mouse_y = pygame.mouse.get_pos()

        is_hovered = (button_x <= mouse_x <= button_x + start_button_image.get_width() and
                      button_y <= mouse_y <= button_y + start_button_image.get_height())

        if is_hovered:
            hover_offset = 5
            brightness = 1.2
        else:
            hover_offset = 0
            brightness = 1.0

        button_effect = start_button_image.copy()
        arr = pygame.surfarray.pixels3d(button_effect)
        arr[:] = (arr * brightness).clip(0, 255)
        del arr

        screen.blit(button_effect, (button_x, button_y + hover_offset))
        button_rect = pygame.Rect(button_x, button_y + hover_offset, start_button_image.get_width(), start_button_image.get_height())

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and is_hovered:
                return

def reset_game():
    global towers, enemies, floating_texts, selected_tower_type, selected_tower_image
    global gold, current_round, enemies_to_spawn, spawn_timer, round_timer
    global round_active, game_over, occupied_tiles

    towers = []
    enemies = []
    floating_texts = []
    selected_tower_type = "arrow"
    selected_tower_image = TOWERS[selected_tower_type]["image"]
    gold = 100

    current_round = 0
    enemies_to_spawn = 0
    spawn_timer = 0
    round_timer = 10
    round_active = False
    game_over = False

    occupied_tiles.clear()
    for y in range(BASE_POSITION[1], BASE_POSITION[1] + BASE_SIZE, GRID_SIZE):
        for x in range(BASE_POSITION[0], BASE_POSITION[0] + BASE_SIZE, GRID_SIZE):
            occupied_tiles.add((x, y))

def start_round(enemy_count):
    global enemies_to_spawn, spawn_timer, round_active
    enemies_to_spawn = enemy_count
    spawn_timer = 0
    round_active = True

def towerInit():
    global selected_tower_type, TOWERS, tower_arrow_icon, tower_cannon_icon, wall_icon, selected_tower_image

    wall_image = pygame.image.load(os.path.join("assets", "wall.png"))
    wall_icon = pygame.transform.scale(wall_image, (60, 60))

    tower_arrow_image = pygame.image.load(os.path.join("assets", "towerArrow.png"))
    tower_arrow_icon = pygame.transform.scale(tower_arrow_image, (60, 60))

    tower_cannon_image = pygame.image.load(os.path.join("assets", "towerCannon.png"))
    tower_cannon_icon = pygame.transform.scale(tower_cannon_image, (60, 60))

    TOWERS = {
        "arrow": {
            "name": "Arrow Tower",
            "image": tower_arrow_image,
            "icon": tower_arrow_icon,
            "cost": 10,
            "damage": 5,
            "attack_speed": 3.5,
            "range": 150
        },
        "cannon": {
            "name": "Cannon Tower",
            "image": tower_cannon_image,
            "icon": tower_cannon_icon,
            "cost": 20,
            "damage": 30,
            "attack_speed": 1,
            "range": 200
        },
        "wall": {
            "name": "Wall",
            "image": wall_image,
            "icon": wall_icon,
            "cost": 5,
            "damage": 0,
            "attack_speed": 0,
            "range": 0
        }
    }

    selected_tower_type = "arrow"
    selected_tower_image = TOWERS[selected_tower_type]["image"]

def castleInit():
    global castle_image, BASE_SIZE, BASE_POSITION, occupied_tiles
    castle_image = pygame.image.load(os.path.join("assets", "castle.png"))
    BASE_SIZE = GRID_SIZE * 2
    BASE_POSITION = (SCREEN_WIDTH // 2 - BASE_SIZE // 2, SCREEN_HEIGHT - BASE_SIZE - UI_HEIGHT)

    occupied_tiles = set()
    for y in range(BASE_POSITION[1], BASE_POSITION[1] + BASE_SIZE, GRID_SIZE):
        for x in range(BASE_POSITION[0], BASE_POSITION[0] + BASE_SIZE, GRID_SIZE):
            occupied_tiles.add((x, y))

def terrainInit():
    global grass_tile, enemy_grass_tile, SPAWN_POINTS
    grass_tile = pygame.image.load(os.path.join("assets", "grass.png")).convert_alpha()
    enemy_grass_tile = pygame.image.load(os.path.join("assets", "enemyGrass.png")).convert_alpha()

    SPAWN_POINTS = [
        (SCREEN_WIDTH // 2 - GRID_SIZE, 0),
        (SCREEN_WIDTH // 2, 0)
    ]

def enemyInit():
    global slime_image
    slime_image = pygame.image.load(os.path.join("assets", "slime.png")).convert_alpha()

def spawn_enemy():
    spawn_point = SPAWN_POINTS[0]
    start = get_grid_pos(*spawn_point)
    goal = get_grid_pos(BASE_POSITION[0], BASE_POSITION[1]-10)
    path = bfs_path(start, goal, occupied_tiles)


    enemy = {
        "x": start[0],
        "y": start[1],
        "image": slime_image,
        "hp": 100,
        "max_hp": 100,
        "path": path,
        "path_index": 0
    }
    enemies.append(enemy)

def update_enemies(dt):
    global gold, game_over
    speed = 100
    for enemy in enemies[:]:
        if enemy["hp"] <= 0:
            enemies.remove(enemy)
            gold += 10
            floating_texts.append({
                "text": "+10g",
                "x": enemy["x"],
                "y": enemy["y"],
                "timer": 1.0
            })
            continue

        if enemy["path_index"] < len(enemy["path"]):
            target_x, target_y = enemy["path"][enemy["path_index"]]
            dx = target_x - enemy["x"]
            dy = target_y - enemy["y"]
            dist = math.hypot(dx, dy)

            if dist < speed * dt:
                enemy["x"], enemy["y"] = target_x, target_y
                enemy["path_index"] += 1

                current_tile = (enemy["x"], enemy["y"])
                goal = get_grid_pos(BASE_POSITION[0], BASE_POSITION[1] - 10)
                new_path = bfs_path(current_tile, goal, occupied_tiles)

                if new_path != [current_tile]:
                    enemy["path"] = new_path
                    enemy["path_index"] = 1

            else:
                enemy["x"] += (dx / dist) * speed * dt
                enemy["y"] += (dy / dist) * speed * dt

        goal_tile = get_grid_pos(BASE_POSITION[0], BASE_POSITION[1] - 10)
        enemy_tile = get_grid_pos(enemy["x"], enemy["y"])
        if enemy_tile == goal_tile:
            game_over = True         


def update_towers(dt):
    for tower in towers:
        if tower["type"] == "wall":
            continue
        tower["cooldown"] -= dt
        if tower["cooldown"] <= 0:
            tx = tower["x"] + GRID_SIZE // 2
            ty = tower["y"] + GRID_SIZE // 2
            for enemy in enemies:
                ex = enemy["x"] + enemy["image"].get_width() // 2
                ey = enemy["y"] + enemy["image"].get_height() // 2
                distance = math.hypot(tx - ex, ty - ey)
                if distance <= tower["range"]:
                    enemy["hp"] -= tower["damage"]
                    tower["cooldown"] = 1.0 / TOWERS[tower["type"]]["attack_speed"]
                    break

def update_floating_texts(dt):
    for text in floating_texts[:]:
        text["y"] -= 30 * dt
        text["timer"] -= dt
        if text["timer"] <= 0:
            floating_texts.remove(text)

def draw_terrain():
    for y in range(0, SCREEN_HEIGHT - UI_HEIGHT, GRID_SIZE):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            tile_pos = (x, y)
            if tile_pos in SPAWN_POINTS:
                screen.blit(enemy_grass_tile, tile_pos)
            else:
                screen.blit(grass_tile, tile_pos)

    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (0, 100, 0), (x, 0), (x, SCREEN_HEIGHT - UI_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT - UI_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (0, 100, 0), (0, y), (SCREEN_WIDTH, y), 1)

def uiInit():
    global ui_buttons, warning_message, warning_timer
    ui_buttons = []
    button_x = 20
    for tower_type, tower_data in TOWERS.items():
        rect = pygame.Rect(button_x, SCREEN_HEIGHT - UI_HEIGHT + 10, 80, 80)
        icon_x = rect.x + (rect.width - tower_data["icon"].get_width()) // 2
        icon_y = rect.y + (rect.height - tower_data["icon"].get_height()) // 2
        ui_buttons.append({
            "type": tower_type,
            "rect": rect,
            "icon": tower_data["icon"],
            "icon_pos": (icon_x, icon_y)
        })
        button_x += rect.width + 40

    warning_message = ""
    warning_timer = 0

def draw_game_elements():
    draw_terrain()
    screen.blit(castle_image, (BASE_POSITION[0], BASE_POSITION[1]))

    for tower in towers:
        screen.blit(tower["image"], (tower["x"], tower["y"]))
        tower_rect = pygame.Rect(tower["x"], tower["y"], GRID_SIZE, GRID_SIZE)
        if tower_rect.collidepoint(pygame.mouse.get_pos()):
            center = (tower["x"] + GRID_SIZE // 2, tower["y"] + GRID_SIZE // 2)
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surface, (100, 100, 255, 100), center, tower["range"], 2)
            screen.blit(surface, (0, 0))

    for enemy in enemies:
        screen.blit(enemy["image"], (enemy["x"], enemy["y"]))
        bar_width = 40
        bar_height = 6
        bar_x = enemy["x"] + (enemy["image"].get_width() - bar_width) // 2
        bar_y = enemy["y"] - 10
        hp_ratio = max(0, enemy["hp"] / enemy["max_hp"])
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
    
    for text in floating_texts:
        label = font.render(text["text"], True, (255, 215, 0))
        screen.blit(label, (text["x"], text["y"]))

def draw_ui(gold, mouse_pos):
    global warning_message, warning_timer
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))

    gold_text = font.render(f'Gold: {gold}', True, (255, 215, 0))
    screen.blit(gold_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - UI_HEIGHT + 30))

    for button in ui_buttons:
        screen.blit(button["icon"], button["icon_pos"])
        if selected_tower_type == button["type"]:
            pygame.draw.rect(screen, (255, 255, 255), button["rect"], 3)

    for button in ui_buttons:
        if button["rect"].collidepoint(mouse_pos):
            tower_data = TOWERS[button["type"]]
            draw_tooltip(tower_data["name"], tower_data["cost"], tower_data["damage"], tower_data["attack_speed"], mouse_pos)

    if warning_timer > 0:
        warning_label = font.render(warning_message, True, (255, 50, 50))

        padding = 10
        bg_width = warning_label.get_width() + padding * 2
        bg_height = warning_label.get_height() + padding * 2

        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))

        pos_x = 20
        pos_y = SCREEN_HEIGHT - UI_HEIGHT - bg_height - 10

        screen.blit(bg_surface, (pos_x, pos_y))
        screen.blit(warning_label, (pos_x + padding, pos_y + padding))

        warning_timer -= dt
        
    round_text = f"Runda: {current_round}/{max_rounds}"
    status_text = f"Start za: {int(round_timer)}s" if not round_active and current_round < max_rounds else "Walka!"
    label = font.render(round_text + "  |  " + status_text, True, (255, 255, 255))
    screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, SCREEN_HEIGHT - UI_HEIGHT + 30))



def draw_tooltip(name, cost, damage, attack_speed, position):
    name_text = tooltip_name_font.render(name, True, (255, 255, 255))
    cost_text = tooltip_cost_font.render(f"{cost} Gold", True, (255, 215, 0))
    damage_text = tooltip_stats_font.render(f"Damage: {damage}", True, (200, 200, 200))
    speed_text = tooltip_stats_font.render(f"Attack Speed: {attack_speed}", True, (200, 200, 200))

    width = max(name_text.get_width(), cost_text.get_width(), damage_text.get_width(), speed_text.get_width()) + 20
    height = name_text.get_height() + cost_text.get_height() + damage_text.get_height() + speed_text.get_height() + 25
    tooltip_bg = pygame.Surface((width, height), pygame.SRCALPHA)
    tooltip_bg.fill((0, 0, 0, 150))

    tooltip_bg.blit(name_text, (10, 5))
    tooltip_bg.blit(cost_text, (10, name_text.get_height() + 5))
    tooltip_bg.blit(damage_text, (10, name_text.get_height() + cost_text.get_height() + 10))
    tooltip_bg.blit(speed_text, (10, name_text.get_height() + cost_text.get_height() + damage_text.get_height() + 15))

    screen.blit(tooltip_bg, (position[0] + 15, position[1] - height - 10))



show_start_screen()

# Initialization
towerInit()
castleInit()
terrainInit()
uiInit()
enemyInit()

running = True
while running:
    if game_over:
        screen.fill((30, 0, 0))
        lose_text = title_font.render("Przegrana!", True, (255, 50, 50))
        screen.blit(lose_text, (SCREEN_WIDTH // 2 - lose_text.get_width() // 2, 200))

        button_width, button_height = 300, 100
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = 350
        mouse_x, mouse_y = pygame.mouse.get_pos()

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovered = button_rect.collidepoint(mouse_x, mouse_y)

        pygame.draw.rect(screen, (100, 100, 255) if is_hovered else (70, 70, 200), button_rect, border_radius=12)
        reset_text = button_font.render("Zagraj ponownie", True, (255, 255, 255))
        screen.blit(reset_text, (button_x + button_width // 2 - reset_text.get_width() // 2,
                                 button_y + button_height // 2 - reset_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and is_hovered:
                reset_game()
        continue


    dt = clock.tick(20) / 1000
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for button in ui_buttons:
                if button["rect"].collidepoint(mouse_x, mouse_y):
                    selected_tower_type = button["type"]
                    selected_tower_image = TOWERS[selected_tower_type]["image"]
                elif mouse_y < SCREEN_HEIGHT - UI_HEIGHT:
                    grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE
                    grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE
                    tile_pos = (grid_x, grid_y)
                    if tile_pos not in occupied_tiles:
                        blocked_by_enemy = False
                        for enemy in enemies:
                            enemy_tile = get_grid_pos(enemy["x"], enemy["y"])
                            if tile_pos == enemy_tile:
                                blocked_by_enemy = True
                                break
                            if enemy["path_index"] < len(enemy["path"]):
                                next_tile = enemy["path"][enemy["path_index"]]
                                if tile_pos == next_tile:
                                    blocked_by_enemy = True
                                    break

                        if blocked_by_enemy:
                            warning_message = "Nie możesz budować bezpośrednio na wrogu!"
                            warning_timer = 2
                        else:
                            hypothetical_obstacles = occupied_tiles.copy()
                            hypothetical_obstacles.add(tile_pos)
                            path_blocked = False
                            for spawn_point in SPAWN_POINTS:
                                start = get_grid_pos(*spawn_point)
                                goal = get_grid_pos(BASE_POSITION[0], BASE_POSITION[1] - 10)
                                if bfs_path(start, goal, hypothetical_obstacles) == [start]:
                                    path_blocked = True
                                    break

                            if path_blocked:
                                warning_message = "Nie można zablokować drogi do zamku!"
                                warning_timer = 2
                            else:
                                tower_cost = TOWERS[selected_tower_type]["cost"]
                                if gold >= tower_cost:
                                    tower_data = TOWERS[selected_tower_type]
                                    towers.append({
                                        "x": grid_x,
                                        "y": grid_y,
                                        "type": selected_tower_type,
                                        "image": tower_data["image"],
                                        "range": tower_data.get("range", 0),
                                        "damage": tower_data.get("damage", 0),
                                        "cooldown": 0
                                    })
                                    occupied_tiles.add(tile_pos)
                                    gold -= tower_cost
                                else:
                                    warning_message = "Za mało złota!"
                                    warning_timer = 2
    # waves
    if round_active:
        if enemies_to_spawn > 0:
            spawn_timer -= dt
            if spawn_timer <= 0:
                spawn_enemy()
                enemies_to_spawn -= 1
                spawn_timer = spawn_interval
        elif len(enemies) == 0:
            round_active = False
            round_timer = between_round_delay
    else:
        round_timer -= dt
        if round_timer <= 0 and current_round < max_rounds:
            current_round += 1
            start_round(enemy_count=5 + current_round * 2)

    update_enemies(dt)
    update_floating_texts(dt)
    update_towers(dt)
    draw_game_elements()
    draw_ui(gold, mouse_pos)
    pygame.display.flip()

pygame.quit()
sys.exit()
