import pygame
import sys
import os

pygame.init()

clock = pygame.time.Clock()

# Window settings
GRID_SIZE = 50
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
UI_HEIGHT = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - Gra tegotypu")

towers = []  # List for storing tower data
enemies = []  # List for storing enemies data

selected_tower_type = "arrow" # Initial selected UI element 
gold = 100  # Starting gold amount

# Load fonts
font = pygame.font.SysFont('Arial', 30)
tooltip_name_font = pygame.font.SysFont('Arial', 22, bold=True)
tooltip_cost_font = pygame.font.SysFont('Arial', 20)
tooltip_stats_font = pygame.font.SysFont('Arial', 18)

# Initialize game elements
def update_enemies():
    for enemy in enemies:
        enemy["y"] += 1

def spawn_enemy():
    enemy = {
        "x": SCREEN_WIDTH // 2,
        "y": 0,
        "image": slime_image,
        "hp": 100
    }
    enemies.append(enemy)

def towerInit():
    global selected_tower_type, TOWERS, tower_arrow_icon, tower_cannon_icon, selected_tower_image

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
            "damage": 10,
            "attack_speed": 2,
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
        }
    }

    selected_tower_type = "arrow"
    selected_tower_image = TOWERS[selected_tower_type]["image"]

def enemyInit():
    global slime_image
    slime_image = pygame.image.load(os.path.join("assets", "slime.png")).convert_alpha()

    spawn_enemy()

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
    global ui_buttons
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

def draw_game_elements():
    draw_terrain()
    screen.blit(castle_image, (BASE_POSITION[0], BASE_POSITION[1]))

    for tower in towers:
        screen.blit(tower["image"], (tower["x"], tower["y"]))
        tower_rect = pygame.Rect(tower["x"], tower["y"], GRID_SIZE, GRID_SIZE)
        if tower_rect.collidepoint(pygame.mouse.get_pos()):
            center = (tower["x"] + GRID_SIZE // 2, tower["y"] + GRID_SIZE // 2)
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surface, (100, 100, 255, 80), center, tower["range"], 5)
            screen.blit(surface, (0, 0))
    
    for enemy in enemies:
        screen.blit(enemy["image"], (enemy["x"], enemy["y"]))

def draw_ui(selected_tower_image, gold, mouse_pos):
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

towerInit()
castleInit()
terrainInit()
uiInit()
enemyInit()

# Main loop
running = True
while running:
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
                        tower_cost = TOWERS[selected_tower_type]["cost"]
                        if gold >= tower_cost:
                            towers.append({
                                "x": grid_x,
                                "y": grid_y,
                                "type": selected_tower_type,
                                "image": TOWERS[selected_tower_type]["image"],
                                "range": TOWERS[selected_tower_type]["range"]
                            })
                        occupied_tiles.add(tile_pos)
                        gold -= tower_cost

    draw_game_elements()
    draw_ui(selected_tower_image, gold, mouse_pos)
    update_enemies()
    pygame.display.flip()
    dt = clock.tick(20) / 1000

pygame.quit()
sys.exit()
