import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Window settings
GRID_SIZE = 50
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
UI_HEIGHT = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - Gra tegotypu")

towers = []  # List to store tower positions
selected_tower_type = "arrow"
gold = 100  # Starting gold amount

# Load fonts
font = pygame.font.SysFont('Arial', 30)
tooltip_name_font = pygame.font.SysFont('Arial', 22, bold=True)
tooltip_cost_font = pygame.font.SysFont('Arial', 20)
tooltip_stats_font = pygame.font.SysFont('Arial', 18)

# Initialize game elements
def towerInit():
    global selected_tower_type, TOWERS, tower_arrow_icon, tower_cannon_icon, selected_tower_image
    
    # Load tower images
    tower_arrow_image = pygame.image.load(os.path.join("assets", "towerArrow.png"))
    tower_arrow_icon = pygame.transform.scale(tower_arrow_image, (60, 60))

    tower_cannon_image = pygame.image.load(os.path.join("assets", "towerCannon.png"))
    tower_cannon_icon = pygame.transform.scale(tower_cannon_image, (60, 60))

    # Tower settings
    TOWERS = {
        "arrow": {
            "name": "Arrow Tower",
            "image": tower_arrow_image,
            "icon": tower_arrow_icon,
            "cost": 10,
            "damage": 10,
            "attack_speed": 2  # shots per second
        },
        "cannon": {
            "name": "Cannon Tower",
            "image": tower_cannon_image,
            "icon": tower_cannon_icon,
            "cost": 20,
            "damage": 30,
            "attack_speed": 1  # shots per second
        }
    }

    # Set default selected tower
    selected_tower_type = "arrow"
    selected_tower_image = TOWERS[selected_tower_type]["image"]

def castleInit():
    global castle_image, BASE_SIZE, BASE_POSITION, occupied_tiles
    # Load castle image
    castle_image = pygame.image.load(os.path.join("assets", "castle.png"))
    BASE_SIZE = GRID_SIZE * 2
    BASE_POSITION = (SCREEN_WIDTH // 2 - BASE_SIZE // 2, SCREEN_HEIGHT - BASE_SIZE - UI_HEIGHT)
    
    # Mark castle area as occupied
    occupied_tiles = set()
    for y in range(BASE_POSITION[1], BASE_POSITION[1] + BASE_SIZE, GRID_SIZE):
        for x in range(BASE_POSITION[0], BASE_POSITION[0] + BASE_SIZE, GRID_SIZE):
            occupied_tiles.add((x, y))

def terrainInit():
    global grass_tile, enemy_grass_tile, SPAWN_POINTS
    # Load grass tiles
    grass_tile = pygame.image.load(os.path.join("assets", "grass.png")).convert_alpha()
    enemy_grass_tile = pygame.image.load(os.path.join("assets", "enemyGrass.png")).convert_alpha()

    # Define enemy spawn points (2 tiles in the middle of the top)
    SPAWN_POINTS = [
        (SCREEN_WIDTH // 2 - GRID_SIZE, 0),
        (SCREEN_WIDTH // 2, 0)
    ]

def draw_terrain():
    # Fill the background with the grass tile
    for y in range(0, SCREEN_HEIGHT - UI_HEIGHT, GRID_SIZE):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            tile_pos = (x, y)
            if tile_pos in SPAWN_POINTS:
                screen.blit(enemy_grass_tile, tile_pos)
            else:
                screen.blit(grass_tile, tile_pos)
    
    # Draw grid lines on top of grass
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (0, 100, 0), (x, 0), (x, SCREEN_HEIGHT - UI_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT - UI_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (0, 100, 0), (0, y), (SCREEN_WIDTH, y), 1)

def uiInit():
    global ui_buttons
    ui_buttons = []
    button_x = 20  # Initial x position
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
        button_x += rect.width + 40  # Spacing between buttons

towerInit()
castleInit()
terrainInit()
uiInit()

def draw_game_elements():
    # Draw terrain and grid
    draw_terrain()
    
    # Draw the base
    screen.blit(castle_image, (BASE_POSITION[0], BASE_POSITION[1]))
    
    # Draw all towers
    for tower in towers:
        screen.blit(tower[2], (tower[0], tower[1]))

def draw_ui(selected_tower_image, gold, mouse_pos):
    # Draw UI background
    pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))
    
    # Display gold amount in the bottom left corner
    gold_text = font.render(f'Gold: {gold}', True, (255, 215, 0))  # Gold color
    screen.blit(gold_text, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - UI_HEIGHT + 30))
    
    # Draw UI buttons
    for button in ui_buttons:
        screen.blit(button["icon"], button["icon_pos"])
        # Draw selection outline if this tower is selected
        if selected_tower_type == button["type"]:
            pygame.draw.rect(screen, (255, 255, 255), button["rect"], 3)
    
    # Show tooltips
    for button in ui_buttons:
        if button["rect"].collidepoint(mouse_pos):
            tower_data = TOWERS[button["type"]]
            draw_tooltip(tower_data["name"], tower_data["cost"], tower_data["damage"], tower_data["attack_speed"], mouse_pos)

def draw_tooltip(name, cost, damage, attack_speed, position):
    # Render the tooltip text
    name_text = tooltip_name_font.render(name, True, (255, 255, 255))
    cost_text = tooltip_cost_font.render(f"{cost} Gold", True, (255, 215, 0))
    damage_text = tooltip_stats_font.render(f"Damage: {damage}", True, (200, 200, 200))
    speed_text = tooltip_stats_font.render(f"Attack Speed: {attack_speed}", True, (200, 200, 200))
    
    # Create background surface
    width = max(name_text.get_width(), cost_text.get_width(), damage_text.get_width(), speed_text.get_width()) + 20
    height = name_text.get_height() + cost_text.get_height() + damage_text.get_height() + speed_text.get_height() + 25
    tooltip_bg = pygame.Surface((width, height), pygame.SRCALPHA)
    tooltip_bg.fill((0, 0, 0, 150))  # Semi-transparent background
    
    # Position the texts
    tooltip_bg.blit(name_text, (10, 5))
    tooltip_bg.blit(cost_text, (10, name_text.get_height() + 5))
    tooltip_bg.blit(damage_text, (10, name_text.get_height() + cost_text.get_height() + 10))
    tooltip_bg.blit(speed_text, (10, name_text.get_height() + cost_text.get_height() + damage_text.get_height() + 15))
    
    # Draw the background and the text
    screen.blit(tooltip_bg, (position[0] + 15, position[1] - height - 10))

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if clicking on UI buttons
            for button in ui_buttons:
                if button["rect"].collidepoint(mouse_x, mouse_y):
                    selected_tower_type = button["type"]
                    selected_tower_image = TOWERS[selected_tower_type]["image"]
            # Check if placing tower on the grid
                elif mouse_y < SCREEN_HEIGHT - UI_HEIGHT:
                    grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE
                    grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE
                    tile_pos = (grid_x, grid_y)
                    if tile_pos not in occupied_tiles:
                        tower_cost = TOWERS[selected_tower_type]["cost"]
                        if gold >= tower_cost:
                            towers.append((grid_x, grid_y, selected_tower_image))
                            occupied_tiles.add(tile_pos)
                            gold -= tower_cost
    
    # Draw game elements
    draw_game_elements()
    
    # Draw UI with tooltip
    draw_ui(selected_tower_image, gold, mouse_pos)
    
    # Update screen
    pygame.display.flip()

# Close the game
pygame.quit()
sys.exit()
