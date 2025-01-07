import pygame
import sys


# A minimal slider class for demonstration
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.label = label
        # A small "handle" to indicate the current position on the slider
        self.handle_width = 10
        self.handle_rect = pygame.Rect(x, y, self.handle_width, h)

        self.update_handle_position()

    def update_handle_position(self):
        # Convert self.value -> handle x position
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.x = self.rect.x + int(
            ratio * (self.rect.width - self.handle_width)
        )

    def draw(self, surface, font):
        # Draw slider track (the bar)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, border_radius=3)
        # Draw handle
        pygame.draw.rect(surface, (120, 120, 120), self.handle_rect, border_radius=3)
        # Draw label and value
        text_surface = font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x, self.rect.y - 20))

    def handle_event(self, event):
        # Only handle mouse events for simplicity
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.update_value_from_mouse(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] == 1:  # Mouse dragged
                if self.rect.collidepoint(event.pos):
                    self.update_value_from_mouse(event.pos)

    def update_value_from_mouse(self, mouse_pos):
        # Map mouse x -> slider value
        x = mouse_pos[0]
        if x < self.rect.x:
            x = self.rect.x
        if x > self.rect.right - self.handle_width:
            x = self.rect.right - self.handle_width
        ratio = (x - self.rect.x) / float(self.rect.width - self.handle_width)
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_position()

    def get_value(self):
        return self.value


class Renderer:
    def __init__(self, length_m, width=800, height=400):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("PID Controller Visualization")

        self.meters_to_pixels_gain = width / length_m
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()

        # Set up font
        self.font = pygame.font.SysFont(None, 24)

        # Create sliders for kp, ki, kd
        max_gain = 3
        self.slider_kp = Slider(50, 50, 200, 20, 0.0, max_gain, 1.0, label="Kp")
        self.slider_ki = Slider(50, 100, 200, 20, 0.0, max_gain, 0.0, label="Ki")
        self.slider_kd = Slider(50, 150, 200, 20, 0.0, max_gain, 0.0, label="Kd")

        # Create slider for reference
        max_ref = width / self.meters_to_pixels_gain
        self.slider_ref = Slider(
            50, 250, 300, 20, 1, max_ref - 1, max_ref / 2, label="Reference"
        )

        # Object position
        self.object_pos_pixels = 0.0
        self.object_vel = 0.0

    def update(self):
        """Updates the display. Call this once per frame."""
        self.clock.tick(60)
        self.screen.fill((255, 255, 255))

        # Draw the sliders
        self.slider_kp.draw(self.screen, self.font)
        self.slider_ki.draw(self.screen, self.font)
        self.slider_kd.draw(self.screen, self.font)
        self.slider_ref.draw(self.screen, self.font)

        # Draw the reference (cyan circle)
        ref_x_m = self.get_selected_reference()
        pygame.draw.circle(
            self.screen,
            (0, 255, 255),
            (int(ref_x_m * self.meters_to_pixels_gain), self.height // 2),
            8,
        )

        # Draw the object (green circle)
        pygame.draw.circle(
            self.screen,
            (0, 255, 0),
            (int(self.object_pos_pixels), self.height // 2),
            12,
        )

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Let the sliders handle events
            self.slider_kp.handle_event(event)
            self.slider_ki.handle_event(event)
            self.slider_kd.handle_event(event)
            self.slider_ref.handle_event(event)

    def set_object_state(self, position, velocity=0.0):
        """Sets the object's current state in the 1D space."""
        self.object_pos_pixels = position * self.meters_to_pixels_gain
        self.object_vel = velocity

    def get_selected_gains(self):
        """Returns the current Kp, Ki, Kd from the sliders."""
        kp = self.slider_kp.get_value()
        ki = self.slider_ki.get_value()
        kd = self.slider_kd.get_value()
        return kp, ki, kd

    def get_selected_reference(self):
        """Returns the reference position from the slider."""
        return self.slider_ref.get_value()
