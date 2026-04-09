import pygame
from constants import *

# Check if pygame is initialized (for testing without display)
_pygame_init = hasattr(pygame, "init")


def create_robot_icon(size, color=BLUE):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, color, (size // 4, size // 4, size // 2, size // 2))
    # Head
    pygame.draw.rect(icon, color, (size // 3, size // 8, size // 3, size // 4))
    # Eyes
    pygame.draw.circle(icon, WHITE, (size // 3 + 2, size // 8 + 4), 2)
    pygame.draw.circle(icon, WHITE, (size // 3 * 2 - 2, size // 8 + 4), 2)
    return icon


def create_battery_icon(size):
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(icon, GREEN, (size // 4, size // 4, size // 2, size // 2))
    # Cap
    pygame.draw.rect(icon, GRAY, (size // 3 + 2, size // 8, size // 4, size // 8))
    # Symbol
    pygame.draw.line(
        icon, BLACK, (size // 2 - 4, size // 2), (size // 2 + 4, size // 2), 2
    )
    pygame.draw.line(
        icon, BLACK, (size // 2, size // 2 - 4), (size // 2, size // 2 + 4), 2
    )
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


def create_mirror_icon(size):
    """Creates a light purple reflective surface icon for the mirror."""
    icon = pygame.Surface((size, size))
    # Light purple/magenta for mirror surface
    mirror_color = (180, 140, 200)
    icon.fill(mirror_color)
    # Add reflective border
    pygame.draw.rect(icon, (220, 180, 240), (0, 0, size, size), 2)
    # Add "shiny" diagonal line
    pygame.draw.line(icon, (255, 255, 255), (size // 4, 0), (size, size * 3 // 4), 1)
    return icon


def create_reset_button_icon(size):
    """Creates a bright green reset button icon (psychosis cure tile)."""
    icon = pygame.Surface((size, size))
    # Bright green fill (distinct from battery green)
    icon.fill((50, 200, 50))
    # Darker green border
    pygame.draw.rect(icon, (30, 150, 30), (0, 0, size, size), 3)
    # Center circle (button appearance)
    pygame.draw.circle(icon, (30, 150, 30), (size // 2, size // 2), size // 4)
    # Inner circle
    pygame.draw.circle(icon, (80, 220, 80), (size // 2, size // 2), size // 6)
    return icon


class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 18)
        self._text_surface = self.font.render(text, True, text_color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        txt_rect = self._text_surface.get_rect(center=self.rect.center)
        screen.blit(self._text_surface, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class TextBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.font = pygame.font.SysFont("Arial", 18)

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
    pygame.draw.rect(screen, (20, 20, 25), rect)  # Dark background for the chart
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)  # Container border

    font = pygame.font.SysFont("Arial", 14)
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
        x = rect.x + margin + (i / (len(data) - 1)) * plot_w
        # Invert Y for screen coordinates
        y = (
            rect.y
            + rect.height
            - margin
            - ((val - min_val) / (max_val - min_val + 1e-5)) * plot_h
        )
        points.append((x, y))

    if len(points) >= 2:
        pygame.draw.lines(screen, color, False, points, 2)

    # Draw Y labels
    min_surf = font.render(str(int(min_val)), True, DARK_GRAY)
    max_surf = font.render(str(int(max_val)), True, DARK_GRAY)
    screen.blit(min_surf, (rect.x + 5, rect.y + rect.height - 18))
    screen.blit(max_surf, (rect.x + 5, rect.y + 20))


def draw_resource_monitor(screen, rect, mem_data, cpu_data):
    """
    Draws a resource monitor showing memory (MB) and CPU (%) usage over time.
    """
    pygame.draw.rect(screen, (20, 20, 25), rect)
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)

    font = pygame.font.SysFont("Arial", 14)
    tit_surf = font.render("RESOURCE MONITOR", True, WHITE)
    screen.blit(tit_surf, (rect.x + 5, rect.y + 5))

    if len(mem_data) < 2:
        return

    # Memory line (blue)
    max_mem = max(mem_data) if max(mem_data) > 0 else 1
    plot_w = rect.width - 40
    plot_h = rect.height - 30
    margin_x = 20
    margin_y = 15

    mem_points = []
    for i, val in enumerate(mem_data):
        x = rect.x + margin_x + (i / (len(mem_data) - 1)) * plot_w
        y = rect.y + rect.height - margin_y - (val / max_mem) * plot_h
        mem_points.append((x, y))

    if len(mem_points) >= 2:
        pygame.draw.lines(screen, BLUE, False, mem_points, 2)

    # CPU line (orange)
    max_cpu = max(cpu_data) if max(cpu_data) > 0 else 1
    cpu_points = []
    for i, val in enumerate(cpu_data):
        x = rect.x + margin_x + (i / (len(cpu_data) - 1)) * plot_w
        y = rect.y + rect.height - margin_y - (val / max_cpu) * plot_h
        cpu_points.append((x, y))

    if len(cpu_points) >= 2:
        pygame.draw.lines(screen, ORANGE, False, cpu_points, 2)

    # Legend
    leg_y = rect.y + rect.height - 12
    mem_leg = font.render("Mem (MB)", True, BLUE)
    cpu_leg = font.render("CPU (%)", True, ORANGE)
    screen.blit(mem_leg, (rect.x + 5, leg_y))
    screen.blit(cpu_leg, (rect.x + 80, leg_y))


def draw_mini_perception(screen, x, y, size, fuzzy_perc_id):
    """Renders a simplified view of the fuzzy perception vector."""
    import json

    pygame.draw.rect(screen, BLACK, (x, y, size, size))
    pygame.draw.rect(screen, DARK_GRAY, (x, y, size, size), 1)

    font = pygame.font.SysFont("Arial", 10)

    # Handle action nodes (fallback visualization)
    if fuzzy_perc_id and fuzzy_perc_id.startswith("ACTION_"):
        action_num = fuzzy_perc_id.replace("ACTION_", "")
        action_names = {0: "A0", 1: "A1", 2: "A2", 3: "A3"}
        label = action_names.get(int(action_num), f"A{action_num}")
        txt = font.render(label, True, YELLOW)
        screen.blit(txt, (x + 2, y + 12))
        return

    try:
        vector = json.loads(fuzzy_perc_id)
        # Show top 2-3 features as text
        for i, feat in enumerate(vector[:3]):
            txt = font.render(feat[:15], True, WHITE)
            screen.blit(txt, (x + 2, y + 2 + i * 10))
    except (json.JSONDecodeError, KeyError, TypeError):
        pass


def draw_territory_map(screen, rect, territory_data):
    """Draws the global world map from visited (x, y) coordinates."""
    pygame.draw.rect(screen, (10, 10, 15), rect)
    pygame.draw.rect(screen, BLUE, rect, 2)

    if not territory_data:
        font = pygame.font.SysFont("Arial", 18)
        msg = font.render("No territory explored yet.", True, GRAY)
        screen.blit(msg, (rect.centerx - 100, rect.centery))
        return

    # Scaling cell size to fit the rect
    cell_w = rect.width / GRID_W
    cell_h = rect.height / GRID_H

    for entry in territory_data:
        tx, ty = entry["x"], entry["y"]
        visits = entry["visits"]
        importance = entry.get("importance", 1.0)

        draw_x = rect.x + tx * cell_w
        draw_y = rect.y + ty * cell_h

        # Color based on visits/importance
        intensity = min(255, 50 + visits * 20)
        color = (
            (0, intensity // 2, intensity)
            if importance <= 1.0
            else (intensity, intensity // 2, 0)
        )

        pygame.draw.rect(screen, color, (draw_x, draw_y, cell_w, cell_h))
        pygame.draw.rect(screen, (0, 0, 40), (draw_x, draw_y, cell_w, cell_h), 1)

    # Label
    font = pygame.font.SysFont("Arial", 14)
    lbl = font.render("GLOBAL TERRITORY MAP", True, WHITE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))


def draw_situational_network(
    screen, rect, nodes, edges, memory_obj=None, cmd_cache=None
):
    """Draws the situational graph as a relational network with symbolic tokens."""
    import math

    pygame.draw.rect(screen, (15, 15, 20), rect)
    pygame.draw.rect(screen, CYAN, rect, 2)

    if not nodes:
        return

    center_x, center_y = rect.center
    radius = min(rect.width, rect.height) // 3
    node_pos = {}

    font = pygame.font.SysFont("Arial", 12)

    # Pre-build command cache if not provided
    if cmd_cache is None and memory_obj:
        cmd_cache = {}
        try:
            cur = memory_obj.conn.cursor()
            cur.execute("SELECT id, value FROM conceptual_ids")
            for row in cur.fetchall():
                cmd_cache[row["id"]] = row["value"]
        except sqlite3.Error:
            pass

    for i, node_id in enumerate(nodes):
        angle = (i / len(nodes)) * 2 * math.pi
        nx = center_x + radius * math.cos(angle)
        ny = center_y + radius * math.sin(angle)
        node_pos[node_id] = (nx, ny)

    # Draw edges with labels
    for s1, action, s2, weight, cmd_id in edges:
        if s1 in node_pos and s2 in node_pos:
            start, end = node_pos[s1], node_pos[s2]
            color = (max(50, min(255, 100 + int(weight * 20))), 100, 200)
            pygame.draw.line(screen, color, start, end, 2)

            # Midpoint label for action/concept
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2

            label_text = f"A:{action}"
            if cmd_id and cmd_cache:
                val = cmd_cache.get(cmd_id)
                if val:
                    label_text = f"'{val}'" if val != " " else "[SPACE]"

            lbl = font.render(label_text, True, YELLOW)
            screen.blit(lbl, (mid_x, mid_y))

    # Draw nodes as mini-perceptions
    node_size = 40
    for node_id, (nx, ny) in node_pos.items():
        draw_mini_perception(
            screen, nx - node_size // 2, ny - node_size // 2, node_size, node_id
        )


def draw_raycast_view(
    screen, rect, robot, env, learner=None, other_bot=None, active_bot=1
):
    """
    Renders a pseudo-3D scene using Ray Casting from the robot's perspective.
    GL5: Shows mirror reflection with robot's self-ID when facing mirror.
    GL5 Dual-Bot: Shows other robot in perspective-appropriate colors.
    SURFACES: Adds procedural brick texture to walls (Wolfenstein-style).

    Color Logic:
    - Bot viewing POV sees itself in its own color in mirror
    - Other robot appears in the opposite bot's color (blue/orange)

    Texture Implementation (Wolfenstein-style):
    - Vertical walls: use ray Y position for texture coordinate
    - Horizontal walls: use ray X position for texture coordinate
    - Uses Doom textures loaded from assets (1.png to 5.png)
    """
    import math

    # SURFACES: Load Doom textures from assets folder
    _doom_textures = []
    try:
        for tex_num in range(1, 6):
            tex_path = os.path.join(
                os.path.dirname(__file__), "..", "assets", f"{tex_num}.png"
            )
            tex = pygame.image.load(tex_path)
            # Store as list of color rows for fast lookup
            tex_data = []
            for y in range(tex.get_height()):
                row = []
                for x in range(tex.get_width()):
                    pixel = tex.get_at((x, y))
                    # Convert to grayscale brightness
                    brightness = int(
                        0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
                    )
                    row.append(brightness)
                tex_data.append(row)
            _doom_textures.append(tex_data)
    except Exception as e:
        print(f"Could not load Doom textures: {e}")
        # Fallback to procedural if textures not found
        _doom_textures = None

    # If textures loaded, select one as default (stone wall)
    _default_tex_index = 0

    pygame.draw.rect(screen, BLACK, rect)  # Ceiling/Background

    # Solid dark ground (no grid - looks cleaner)
    ground_y = rect.y + rect.height // 2
    ground_h = rect.height // 2
    pygame.draw.rect(
        screen,
        (25, 25, 30),
        (rect.x, ground_y, rect.width, ground_h),
    )

    pygame.draw.rect(screen, CYAN, rect, 2)  # Border

    # 1. Map direction to Radians
    # DIR_N: -pi/2, DIR_E: 0, DIR_S: pi/2, DIR_W: pi
    base_angle = 0
    if robot.direction == DIR_N:
        base_angle = -math.pi / 2
    elif robot.direction == DIR_E:
        base_angle = 0
    elif robot.direction == DIR_S:
        base_angle = math.pi / 2
    elif robot.direction == DIR_W:
        base_angle = math.pi

    fov = math.pi / 3  # 60 degrees
    half_fov = fov / 2
    num_rays = rect.width // 2  # Original resolution
    delta_angle = fov / num_rays

    # Column width to fill the entire rect
    col_width = rect.width // num_rays

    # Starting ray angle
    ray_angle = base_angle - half_fov

    # GL5: Track if mirror is visible
    mirror_visible = False
    mirror_distance = 0

    # 2. Iterate through screen horizontal columns
    for i in range(num_rays):
        # Step small increments along the ray
        step = 0.08  # Smaller step for better accuracy
        max_dist = 12.0
        dist = 0
        hit = False
        hit_obj = EMPTY_ID
        hit_side = 0  # 0 for vertical, 1 for horizontal

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
                # GL5 Dual-Bot: Check for other robot
                if other_bot and int(rx) == other_bot.x and int(ry) == other_bot.y:
                    hit = True
                    hit_obj = 99  # Other bot ID
                elif obj == WALL_ID or obj == BATTERY_ID:
                    hit = True
                    hit_obj = obj
                    # Side detection (simple fractional check)
                    dx = abs(rx - round(rx))
                    dy = abs(ry - round(ry))
                    hit_side = 1 if dy < dx else 0
                elif obj == MIRROR_ID:
                    # Mirror detected - could be reflection
                    if dist < max_dist:
                        hit = True
                        hit_obj = MIRROR_ID
                        if not mirror_visible:
                            mirror_visible = True
                            mirror_distance = dist
            else:
                hit = True  # Out of bounds is wall-like
                hit_obj = WALL_ID
                hit_side = 0

        # 3. Project to 2D
        # Fisheye correction
        dist = dist * math.cos(ray_angle - base_angle)

        # Line height calculation
        proj_h = (1.0 / (dist + 0.1)) * rect.height * 0.8
        if proj_h > rect.height:
            proj_h = rect.height

        # Vertical column rendering
        y1 = rect.y + rect.height // 2 - proj_h // 2
        y2 = rect.y + rect.height // 2 + proj_h // 2

        # Color & Shading
        brightness = max(0, 255 - int(dist * 20))
        if hit_side == 1:
            brightness = int(brightness * 0.7)  # Side-shading

        # SURFACES: Apply Doom texture to walls
        wall_brightness = brightness
        # Texture coordinate based on wall position and side
        if hit_obj == WALL_ID:
            # Calculate texture coordinate properly
            # Texture X = fractional part of hit position
            if _doom_textures is not None:
                # Use Doom textures
                if hit_side == 0:
                    # Vertical wall - use Y fractional for tex Y, X for tex X
                    tex_x = int((ry - int(ry)) * 256) % 256
                    tex_y = int((rx - int(rx)) * 256) % 256
                else:
                    # Horizontal wall
                    tex_x = int((rx - int(rx)) * 256) % 256
                    tex_y = int((ry - int(ry)) * 256) % 256

                # Get pixel from texture (with bounds check)
                tex_h = len(_doom_textures[_default_tex_index])
                tex_w = len(_doom_textures[_default_tex_index][0]) if tex_h > 0 else 256
                if tex_y < tex_h and tex_x < tex_w:
                    tex_val = _doom_textures[_default_tex_index][tex_y][tex_x]
                else:
                    tex_val = 128
            else:
                # Fallback to procedural
                if hit_side == 0:
                    tex_x = int((ry - int(ry)) * 64)
                else:
                    tex_x = int((rx - int(rx)) * 64)

                tex_coord = (tex_x % 64) + (
                    (int(ry * 8) % 64) if hit_side == 0 else (int(rx * 8) % 64)
                )
                tex_coord = tex_coord % 256
                tex_val = (
                    _brick_fallback[tex_coord] if "_brick_fallback" in dir() else 128
                )

            wall_brightness = max(0, min(255, (brightness * tex_val) // 128))

        color = (wall_brightness, wall_brightness, wall_brightness)
        if hit_obj == BATTERY_ID:
            color = (0, brightness, 0)  # Green battery pillars
        elif hit_obj == MIRROR_ID:
            # Mirror shows reflection - simplified blue/purple tint
            mirror_color = (100, 80, 150)
            color = mirror_color
        elif hit_obj == 99:
            # GL5 Dual-Bot: Other robot appears in opposite color to viewer
            # If active_bot is 1 (blue), other appears orange; if 2 (orange), appears blue
            if active_bot == 1:
                other_color = (
                    brightness,
                    brightness // 2,
                    0,
                )  # Orange for bot1 viewing
            else:
                other_color = (0, brightness // 2, brightness)  # Blue for bot2 viewing
            color = other_color

        # Make sure color is valid RGB tuple
        if not isinstance(color, tuple) or len(color) != 3:
            color = (brightness, brightness, brightness)
        color = tuple(max(0, min(255, c)) for c in color)

        # Draw filled rectangle for the column
        pygame.draw.rect(
            screen, color, (rect.x + i * col_width, y1, col_width, y2 - y1)
        )

        ray_angle += delta_angle

    # GL5: Draw robot reflection in mirror ONLY when directly facing it
    # (not in periphery) - reflection on the front face of the cube
    if mirror_visible and learner:
        # Only show reflection if mirror is close and near center of view
        # (direct front view, not peripheral)
        if mirror_distance < 6:  # Close enough to see detailed reflection
            # Draw reflection in center of view (direct front reflection)
            ref_x = rect.x + rect.width // 2 - 30
            ref_y = rect.y + rect.height // 2 - 40
            ref_w = 60
            ref_h = 70

            # Reflection body - color matches the viewing robot (self-recognition)
            if active_bot == 1:
                # Bot 1 sees itself as blue
                reflection_body = (50, 80, 150)
                reflection_border = (80, 120, 200)
            else:
                # Bot 2 sees itself as orange
                reflection_body = (150, 80, 30)
                reflection_border = (200, 120, 50)

            pygame.draw.rect(screen, reflection_body, (ref_x, ref_y, ref_w, ref_h))
            pygame.draw.rect(screen, reflection_border, (ref_x, ref_y, ref_w, ref_h), 2)

            # Two white eyes
            eye_y = ref_y + 20
            pygame.draw.circle(screen, WHITE, (ref_x + 18, eye_y), 6)
            pygame.draw.circle(screen, WHITE, (ref_x + ref_w - 18, eye_y), 6)
            # Pupils
            pygame.draw.circle(screen, BLACK, (ref_x + 20, eye_y), 2)
            pygame.draw.circle(screen, BLACK, (ref_x + ref_w - 16, eye_y), 2)

            # Red nose/ID emitter
            nose_x = ref_x + ref_w // 2
            nose_y = ref_y + 45
            pygame.draw.circle(screen, (255, 50, 50), (nose_x, nose_y), 5)
            pygame.draw.circle(screen, (255, 200, 200), (nose_x, nose_y), 3)

            # ID display
            font = pygame.font.SysFont("Arial", 11, bold=True)
            id_str = str(robot.self_id)
            id_text = f"ID:{id_str}"
            id_surf = font.render(id_text, True, (255, 150, 150))
            screen.blit(id_surf, (ref_x + 5, ref_y + ref_h + 5))

    # HUD label
    font = pygame.font.SysFont("Arial", 14)
    lbl = font.render(" POV - ROBOT VISION", True, WHITE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))


def draw_inferences_window(screen, rect, learner, robot=None):
    """Draws the real-time cognitive inferences of the Learner."""
    pygame.draw.rect(screen, (20, 20, 25), rect)
    pygame.draw.rect(screen, ORANGE, rect, 2)

    font_title = pygame.font.SysFont("Arial", 14, bold=True)
    font_body = pygame.font.SysFont("Arial", 12)

    lbl = font_title.render("INFERENCES (Real-time Processing)", True, ORANGE)
    screen.blit(lbl, (rect.x + 5, rect.y + 5))

    y_off = rect.y + 30

    inf_type = learner.last_inference_info.get("type", "N/A")
    inf_det = learner.last_inference_info.get("details", "")

    type_surf = font_body.render(f"Decision Logic: {inf_type}", True, CYAN)
    screen.blit(type_surf, (rect.x + 10, y_off))
    y_off += 18

    det_surf = font_body.render(f"Details: {inf_det}", True, (200, 200, 200))
    screen.blit(det_surf, (rect.x + 10, y_off))
    y_off += 25

    plan_text = (
        f"Active Sequence: {learner.active_plan}"
        if learner.active_plan
        else "Active Sequence: [EMPTY]"
    )
    plan_color = GREEN if learner.active_plan else DARK_GRAY
    plan_surf = font_body.render(plan_text, True, plan_color)
    screen.blit(plan_surf, (rect.x + 10, y_off))
    y_off += 18

    agenda_len = len(learner.agenda)
    ag_surf = font_body.render(
        f"Expected Agenda Nodes: {agenda_len}",
        True,
        PURPLE if agenda_len > 0 else DARK_GRAY,
    )
    screen.blit(ag_surf, (rect.x + 10, y_off))
    y_off += 18

    stag_surf = font_body.render(
        f"Stagnation Borer: {'DETECTED' if learner.stagnant else 'CLEAR'}",
        True,
        RED if learner.stagnant else (100, 100, 100),
    )
    screen.blit(stag_surf, (rect.x + 10, y_off))
    y_off += 18

    # GL5: Command Learning Debug Panel
    # =================================
    # Always show last command info (if any) + current state

    # Show current command if being processed
    current_cmd = getattr(learner, "last_command_processed", None)
    has_cmd = current_cmd is not None and current_cmd.strip() != ""

    if has_cmd:
        cmd_surf = font_body.render(f"Command: '{current_cmd}'", True, YELLOW)
        screen.blit(cmd_surf, (rect.x + 10, y_off))
        y_off += 16

        # Show tokens
        tokens = getattr(learner, "_last_tokens", [])
        if tokens:
            tokens_str = " | ".join([str(t) for t in tokens])
            tok_surf = font_body.render(f"Tokens: {tokens_str}", True, CYAN)
            screen.blit(tok_surf, (rect.x + 10, y_off))
            y_off += 16

        # Check learned rules for this command
        if hasattr(learner, "memory"):
            try:
                from constants import ACT_LEFT, ACT_RIGHT, ACT_FORWARD, ACT_BACKWARD

                action_names = {
                    ACT_LEFT: "A0",
                    ACT_RIGHT: "A1",
                    ACT_FORWARD: "A2",
                    ACT_BACKWARD: "A3",
                }

                cmd_upper = current_cmd.upper()
                cmd_id = learner.memory.get_or_create_concept_id(cmd_upper)
                rules = learner.memory.get_rules(limit=500)
                cmd_rules = [r for r in rules if r["command_id"] == cmd_id]

                if cmd_rules:
                    for r in cmd_rules[:2]:
                        if r.get("is_composite"):
                            act_str = f"MACRO ({len(r.get('macro_actions', []))} acts)"
                        else:
                            act = r.get("target_action", 0)
                            act_str = action_names.get(act, str(act))
                        rule_surf = font_body.render(
                            f"→ Learned: {act_str} (w={r.get('weight', 0):.1f})",
                            True,
                            GREEN,
                        )
                        screen.blit(rule_surf, (rect.x + 10, y_off))
                        y_off += 14
                else:
                    notfound = font_body.render("→ NOT YET LEARNED", True, RED)
                    screen.blit(notfound, (rect.x + 10, y_off))
                    y_off += 16
            except (json.JSONDecodeError, KeyError, TypeError, sqlite3.Error):
                pass
    else:
        # No command - show autonomous mode info
        mode_surf = font_body.render("Mode: AUTONOMOUS", True, DARK_GRAY)
        screen.blit(mode_surf, (rect.x + 10, y_off))
        y_off += 16

        # Show what perception the robot has
        if hasattr(learner, "_last_perception"):
            perc = learner._last_perception
            if perc and len(perc) > 0:
                perc_short = perc[:4] if len(perc) > 4 else perc
                perc_surf = font_body.render(
                    f"Perception: {perc_short}", True, DARK_GRAY
                )
                screen.blit(perc_surf, (rect.x + 10, y_off))
                y_off += 16

    # GL5: Show learned objectives
    obj_count = len(getattr(learner, "objective_values", {}))
    goals = sum(
        1 for v in getattr(learner, "objective_values", {}).values() if v >= 3.0
    )
    pains = sum(
        1 for v in getattr(learner, "objective_values", {}).values() if v <= -3.0
    )
    obj_surf = font_body.render(
        f"Learned Goals: {goals} | Pains: {pains} | Total: {obj_count}",
        True,
        GREEN if goals > 0 else (RED if pains > 0 else DARK_GRAY),
    )
    screen.blit(obj_surf, (rect.x + 10, y_off))
    y_off += 18

    frames = learner.memory.get_all_frames() if hasattr(learner, "memory") else []
    coord_count = sum(1 for f in frames if f["relation_type"] == "COORD")
    opp_count = sum(1 for f in frames if f["relation_type"] == "OPP")
    rft_surf = font_body.render(
        f"RFT Frames: {len(frames)} (COORD:{coord_count} OPP:{opp_count})",
        True,
        PURPLE if frames else DARK_GRAY,
    )
    screen.blit(rft_surf, (rect.x + 10, y_off))
    y_off += 18

    # GL5: Show autobiographical self-ID
    self_id = 0
    if robot and hasattr(robot, "self_id"):
        self_id = robot.self_id
    elif hasattr(learner, "robot") and hasattr(learner.robot, "self_id"):
        self_id = learner.robot.self_id

    id_surf = font_body.render(
        f"Self-ID: {self_id} (Autobiographical)",
        True,
        CYAN if self_id else GRAY,
    )
    screen.blit(id_surf, (rect.x + 10, y_off))
