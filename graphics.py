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
