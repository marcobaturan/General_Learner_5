import pygame
from constants import *

def create_robot_icon(size):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, BLUE, (size//4, size//4, size//2, size//2))
    # Head
    pygame.draw.rect(icon, BLUE, (size//3, size//8, size//3, size//4))
    # Eyes
    pygame.draw.circle(icon, WHITE, (size//3 + 2, size//8 + 4), 2)
    pygame.draw.circle(icon, WHITE, (size//3*2 - 2, size//8 + 4), 2)
    return icon

def create_battery_icon(size):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, GREEN, (size//4, size//4, size//2, size//2))
    # Cap
    pygame.draw.rect(icon, GRAY, (size//3+2, size//8, size//4, size//8))
    # Symbol
    pygame.draw.line(icon, BLACK, (size//2-4, size//2), (size//2+4, size//2), 2)
    pygame.draw.line(icon, BLACK, (size//2, size//2-4), (size//2, size//2+4), 2)
    return icon

def create_wall_icon(size):
    icon = pygame.Surface((size, size))
    icon.fill(GRAY)
    # Small stone details
    for i in range(4):
        x = (i * 7) % size
        y = (i * 11) % size
        pygame.draw.rect(icon, DARK_GRAY, (x, y, 4, 4))
    return icon

class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', 18)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TextBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.font = pygame.font.SysFont('Arial', 18)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                self.text += event.unicode
        return False

    def draw(self, screen):
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_surf = self.font.render(self.text, True, BLACK)
        screen.blit(txt_surf, (self.rect.x + 5, self.rect.y + 10))

def draw_scaled_plot(screen, rect, data, color, title, label_y):
    """
    Draws a simple line chart within a given Rect based on a list of numeric data.
    """
    pygame.draw.rect(screen, (20, 20, 25), rect) # Dark background for the chart
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)  # Container border
    
    font = pygame.font.SysFont('Arial', 14)
    tit_surf = font.render(title, True, WHITE)
    screen.blit(tit_surf, (rect.x + 5, rect.y + 5))

    if len(data) < 2:
        return

    # Scaling logic
    max_val = max(data) if max(data) > 0 else 1
    min_val = min(data)
    
    points = []
    margin = 20
    plot_w = rect.width - (margin * 2)
    plot_h = rect.height - (margin * 2) - 10
    
    for i, val in enumerate(data):
        x = rect.x + margin + (i / (len(data)-1)) * plot_w
        # Invert Y for screen coordinates
        y = rect.y + rect.height - margin - ((val - min_val) / (max_val - min_val + 1e-5)) * plot_h
        points.append((x, y))

    if len(points) >= 2:
        pygame.draw.lines(screen, color, False, points, 2)
    
    # Draw Y labels
    min_surf = font.render(str(int(min_val)), True, DARK_GRAY)
    max_surf = font.render(str(int(max_val)), True, DARK_GRAY)
    screen.blit(min_surf, (rect.x + 5, rect.y + rect.height - 18))
    screen.blit(max_surf, (rect.x + 5, rect.y + 20))

def draw_mini_perception(screen, x, y, size, perception_str):
    """Renders a small 3x3 visualization of a situational node."""
    import json
    try:
        grid = json.loads(perception_str)
        cell = size // 3
        for r in range(3):
            for c in range(3):
                rect = pygame.Rect(x + c*cell, y + r*cell, cell, cell)
                val = grid[r][c]
                color = BLACK
                if val == WALL_ID: color = GRAY
                elif val == BATTERY_ID: color = GREEN
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, DARK_GRAY, rect, 1)
    except:
        pygame.draw.rect(screen, DARK_GRAY, (x, y, size, size))

def draw_situational_network(screen, rect, nodes, edges):
    """Draws the situational graph as a relational network."""
    import math
    pygame.draw.rect(screen, (15, 15, 20), rect)
    pygame.draw.rect(screen, CYAN, rect, 2)
    
    if not nodes: return
    
    # Simple radial layout for nodes
    center_x, center_y = rect.center
    radius = min(rect.width, rect.height) // 3
    node_pos = {}
    
    for i, node_id in enumerate(nodes):
        angle = (i / len(nodes)) * 2 * math.pi
        nx = center_x + radius * math.cos(angle)
        ny = center_y + radius * math.sin(angle)
        node_pos[node_id] = (nx, ny)
        
    # Draw edges
    for s1, action, s2 in edges:
        if s1 in node_pos and s2 in node_pos:
            pygame.draw.line(screen, DARK_GRAY, node_pos[s1], node_pos[s2], 1)
            
    # Draw nodes as mini-perceptions
    node_size = 30
    for node_id, (nx, ny) in node_pos.items():
        draw_mini_perception(screen, nx - node_size//2, ny - node_size//2, node_size, node_id)

def draw_raycast_view(screen, rect, robot, env):
    """
    Renders a pseudo-3D scene using Ray Casting from the robot's perspective.
    """
    import math
    pygame.draw.rect(screen, BLACK, rect) # Ceiling/Background
    # Ground color
    pygame.draw.rect(screen, (30, 30, 35), (rect.x, rect.y + rect.height//2, rect.width, rect.height//2))
    pygame.draw.rect(screen, CYAN, rect, 2) # Border

    # 1. Map direction to Radians
    # DIR_N: -pi/2, DIR_E: 0, DIR_S: pi/2, DIR_W: pi
    base_angle = 0
    if robot.direction == DIR_N: base_angle = -math.pi/2
    elif robot.direction == DIR_E: base_angle = 0
    elif robot.direction == DIR_S: base_angle = math.pi/2
    elif robot.direction == DIR_W: base_angle = math.pi

    fov = math.pi / 3 # 60 degrees
    half_fov = fov / 2
    num_rays = rect.width // 2 # Resolution skip for performance
    delta_angle = fov / num_rays
    
    # Starting ray angle
    ray_angle = base_angle - half_fov
    
    # 2. Iterate through screen horizontal columns
    for i in range(num_rays):
        # Step small increments along the ray
        step = 0.05
        max_dist = 12.0
        dist = 0
        hit = False
        hit_obj = EMPTY_ID

        # Ray Vector
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        while dist < max_dist and not hit:
            dist += step
            # Projection in grid coords
            rx = robot.x + 0.5 + cos_a * dist
            ry = robot.y + 0.5 + sin_a * dist
            
            # Boundary/Collision check
            if 0 <= rx < GRID_W and 0 <= ry < GRID_H:
                obj = env.get_at(int(rx), int(ry))
                if obj == WALL_ID or obj == BATTERY_ID:
                    hit = True
                    hit_obj = obj
            else:
                hit = True # Out of bounds is wall-like
                hit_obj = WALL_ID

        # 3. Project to 2D
        # Fisheye correction
        dist = dist * math.cos(ray_angle - base_angle)
        
        # Line height calculation
        proj_h = (1.0 / (dist + 0.1)) * rect.height * 0.8
        if proj_h > rect.height: proj_h = rect.height
        
        # Vertical column rendering
        y1 = rect.y + rect.height // 2 - proj_h // 2
        
        # Color & Shading
        brightness = max(0, 255 - int(dist * 20))
        color = (brightness, brightness, brightness)
        if hit_obj == BATTERY_ID:
            color = (0, brightness, 0) # Green battery pillars

        pygame.draw.rect(screen, color, (rect.x + i*2, y1, 2, proj_h))
        
        ray_angle += delta_angle

    # HUD label
    font = pygame.font.SysFont('Arial', 14)
    lbl = font.render(" POV - ROBOT VISION", True, WHITE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))
