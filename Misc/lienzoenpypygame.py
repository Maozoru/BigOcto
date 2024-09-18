import pygame
from pygame.locals import *

class DrawingCanvas:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Prototipo BigOcto")
        
        # Initial brush settings
        self.brush_color = (0, 0, 0)  # Black color
        self.brush_size = 5
        self.last_point = None
        self.pen_is_down = False
        self.eraser_mode = False
        
        # Create a surface for drawing
        self.canvas = pygame.Surface((800, 800))
        self.canvas.fill((255, 255, 255))  # White background

        # Main loop
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.pen_is_down = True
                    self.last_point = event.pos
                elif event.type == MOUSEBUTTONUP:
                    self.pen_is_down = False
                    self.last_point = None
                elif event.type == MOUSEMOTION:
                    if self.pen_is_down:
                        self.draw_line(self.last_point, event.pos)
                        self.last_point = event.pos
                elif event.type == KEYDOWN:
                    if event.key == K_c and event.mod & KMOD_CTRL:
                        self.clear_canvas()

            self.screen.fill((0, 0, 0))  # Clear screen
            self.screen.blit(self.canvas, (0, 0))  # Draw canvas surface onto screen
            pygame.display.flip()  # Update display

        pygame.quit()

    def draw_line(self, start_point, end_point):
        pygame.draw.line(self.canvas, self.brush_color, start_point, end_point, self.brush_size)

    def clear_canvas(self):
        self.canvas.fill((255, 255, 255))  # White background

if __name__ == "__main__":
    canvas = DrawingCanvas()
