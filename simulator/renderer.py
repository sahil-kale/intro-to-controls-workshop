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

        # -----------------------------
        # PLOT-RELATED ATTRIBUTES
        # -----------------------------
        self.plot_data = {}  # dictionary: label -> list of (time, value)
        self.plot_colors = {}  # label -> (r,g,b)
        self.time_window = 10.0  # seconds to show on the plot
        # Some distinct colors we’ll cycle through when a new label appears:
        self.color_bank = [
            (200, 0, 0),
            (0, 200, 0),
            (0, 0, 200),
            (200, 200, 0),
            (200, 0, 200),
            (0, 200, 200),
            (100, 100, 100),
        ]

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

        # Draw the real-time plot in the top portion (example region)
        self._draw_plot()

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

    def plot(self, labels: list, data: list, time_now: float):
        """
        Store data for plotting.
        :param labels: list of string labels (e.g. ["error", "output"])
        :param data: list of float values corresponding to these labels
        :param time_now: current time in seconds
        """
        # Make sure we have an entry in self.plot_data for each label
        for i, label in enumerate(labels):
            if label not in self.plot_data:
                self.plot_data[label] = []
                # Assign a color from the bank
                color_idx = len(self.plot_colors) % len(self.color_bank)
                self.plot_colors[label] = self.color_bank[color_idx]

            # Append the (time, value) pair
            self.plot_data[label].append((time_now, data[i]))

            # Remove old data outside the time window
            min_time = time_now - self.time_window
            # Keep only points where t >= min_time
            self.plot_data[label] = [
                (t, val) for (t, val) in self.plot_data[label] if t >= min_time
            ]

    def _draw_plot(self):
        """Draws each signal in its own subplot at the bottom of the screen."""
        # How tall we want all plots combined to be
        plot_height = 400
        # Rectangle for the combined plot area at the bottom
        plot_rect = pygame.Rect(0, self.height - plot_height, self.width, plot_height)

        # Fill with a light background
        pygame.draw.rect(self.screen, (230, 230, 230), plot_rect)

        # If there is no data, just return
        if not self.plot_data:
            return

        # ------------------------------------------------------------
        # 1. Find the total time range (shared across all subplots)
        # ------------------------------------------------------------
        # Determine the latest time from all series:
        max_time = 0.0
        for label, series in self.plot_data.items():
            if series:
                last_t = series[-1][0]
                max_time = max(max_time, last_t)

        # The minimum time in the window
        min_time = max_time - self.time_window

        # We'll use these for horizontally scaling across all subplots
        time_range = max_time - min_time
        if time_range < 1e-6:
            # Avoid dividing by zero if everything is constant in time
            time_range = 1e-6

        # ------------------------------------------------------------
        # 2. Prepare for subplots
        # ------------------------------------------------------------
        # One subplot per label
        num_signals = len(self.plot_data)

        # Height of each individual subplot
        subplot_height = plot_height / max(num_signals, 1)

        # We'll define a small margin inside each subplot
        margin_left = 45
        margin_right = 10
        margin_top = 10
        margin_bottom = 20  # Also room for X-axis on bottom subplot

        # We'll define the number of Y-ticks and (optionally) X-ticks
        num_y_ticks = 3
        num_x_ticks = 4  # on the bottom subplot

        # Pre-compute the font height for labels
        font_height = self.font.get_linesize()

        # A helper function to draw a single subplot
        def draw_subplot(index, label, series, color):
            """
            index: which subplot (0-based)
            label: the name of the signal
            series: list of (t, val) for this signal
            color: (R,G,B) for the line
            """
            # Subplot rectangle:
            sub_rect_y = plot_rect.y + index * subplot_height
            sub_rect = pygame.Rect(
                plot_rect.x, sub_rect_y, plot_rect.width, subplot_height
            )

            # Fill background just for clarity (optional)
            pygame.draw.rect(self.screen, (240, 240, 240), sub_rect)

            # If there's not enough data, just label it and return
            if len(series) < 1:
                # Draw label text (signal name) near top-left
                label_surface = self.font.render(label, True, (0, 0, 0))
                self.screen.blit(label_surface, (sub_rect.x + 5, sub_rect.y + 5))
                return

            # --------------------------------------------------------
            # 2A. Determine min/max of this signal for Y auto-scaling
            # --------------------------------------------------------
            values = [val for (t, val) in series]
            min_val = min(values)
            max_val = max(values)

            if abs(max_val - min_val) < 1e-6:
                max_val += 1e-6

            # Add padding
            padding = 0.05 * (max_val - min_val)
            min_val -= padding
            max_val += padding

            # The “content” area inside the subplot
            content_width = sub_rect.width - margin_left - margin_right
            content_height = sub_rect.height - margin_top - margin_bottom

            # Y-axis scaling
            y_range = max_val - min_val
            # Avoid / 0
            if y_range < 1e-6:
                y_range = 1e-6

            # A helper to scale (time, value) -> (x, y) in the subplot
            def to_screen_coords(t, v):
                # X: linear from [min_time, max_time] -> [left_margin, left_margin + content_width]
                x = (
                    sub_rect.x
                    + margin_left
                    + (t - min_time) * (content_width / time_range)
                )
                # Y: invert so higher values appear “higher” in the plot
                y = (sub_rect.y + margin_top + content_height) - (v - min_val) * (
                    content_height / y_range
                )
                return x, y

            # --------------------------------------------------------
            # 2B. Draw axes lines
            # --------------------------------------------------------
            axis_color = (50, 50, 50)
            # Vertical axis
            pygame.draw.line(
                self.screen,
                axis_color,
                (sub_rect.x + margin_left, sub_rect.y + margin_top),
                (sub_rect.x + margin_left, sub_rect.y + margin_top + content_height),
                2,
            )
            # Horizontal axis (along the bottom of this subplot)
            pygame.draw.line(
                self.screen,
                axis_color,
                (sub_rect.x + margin_left, sub_rect.y + margin_top + content_height),
                (
                    sub_rect.x + margin_left + content_width,
                    sub_rect.y + margin_top + content_height,
                ),
                2,
            )

            # --------------------------------------------------------
            # 2C. Draw the data line
            # --------------------------------------------------------
            points = [to_screen_coords(t, v) for (t, v) in series]
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, color, points[i], points[i + 1], 2)

            # --------------------------------------------------------
            # 2D. Y-axis ticks/labels
            # --------------------------------------------------------
            # We'll place num_y_ticks ticks linearly between min_val and max_val
            for i_tick in range(num_y_ticks):
                frac = i_tick / float(num_y_ticks - 1) if num_y_ticks > 1 else 0.5
                y_val = min_val + frac * (max_val - min_val)
                # Convert y_val -> screen Y
                x_tick = sub_rect.x + margin_left
                y_tick = (
                    sub_rect.y
                    + margin_top
                    + content_height
                    - (y_val - min_val) * (content_height / (max_val - min_val))
                )

                # Draw a small horizontal tick
                pygame.draw.line(
                    self.screen, axis_color, (x_tick - 5, y_tick), (x_tick, y_tick), 2
                )

                # Draw label to the left
                tick_label = f"{y_val:.2f}"
                label_surface = self.font.render(tick_label, True, (0, 0, 0))
                # Right-align this text so it doesn't collide with the axis
                self.screen.blit(
                    label_surface,
                    (x_tick - 5 - label_surface.get_width(), y_tick - font_height / 2),
                )

            # --------------------------------------------------------
            # 2E. X-axis ticks/labels (only on the bottom subplot)
            # --------------------------------------------------------
            # If this is the last subplot (index == num_signals - 1), add time ticks
            if index == num_signals - 1:
                for i_tick in range(num_x_ticks):
                    frac = i_tick / float(num_x_ticks - 1) if num_x_ticks > 1 else 0.5
                    t_val = min_time + frac * (time_range)
                    x_tick = (
                        sub_rect.x
                        + margin_left
                        + (t_val - min_time) * (content_width / time_range)
                    )
                    y_axis_bottom = sub_rect.y + margin_top + content_height

                    # Draw a small vertical tick
                    pygame.draw.line(
                        self.screen,
                        axis_color,
                        (x_tick, y_axis_bottom),
                        (x_tick, y_axis_bottom + 5),
                        2,
                    )

                    # Draw label below the tick
                    tick_label = f"{t_val:.1f}"
                    label_surface = self.font.render(tick_label, True, (0, 0, 0))
                    self.screen.blit(
                        label_surface,
                        (x_tick - label_surface.get_width() / 2, y_axis_bottom + 6),
                    )

                # Optionally, label the bottom axis as “Time [s]”
                time_label = "Time [s]"
                time_label_surf = self.font.render(time_label, True, (0, 0, 0))
                self.screen.blit(
                    time_label_surf,
                    (
                        sub_rect.x
                        + margin_left
                        + content_width
                        - time_label_surf.get_width(),
                        y_axis_bottom + 6 + font_height,
                    ),
                )

            # --------------------------------------------------------
            # 2F. Draw the signal label in the top-left corner
            # --------------------------------------------------------
            label_surface = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(
                label_surface, (sub_rect.x + self.width * 1 / 6, sub_rect.y + 5)
            )

        # ------------------------------------------------------------
        # 3. Loop over each signal and draw its subplot
        # ------------------------------------------------------------
        # Sort or just iterate in insertion order. For readability,
        # we'll use sorted(self.plot_data.keys()), but you can omit sorting if you prefer.
        for i, label in enumerate(sorted(self.plot_data.keys())):
            series = self.plot_data[label]
            color = self.plot_colors.get(label, (0, 0, 0))
            draw_subplot(i, label, series, color)

        # ------------------------------------------------------------
        # 4. Draw an additional info text (optional)
        # ------------------------------------------------------------
        info_text = f"Time window: {min_time:.1f}s to {max_time:.1f}s"
        text_surf = self.font.render(info_text, True, (0, 0, 0))
        # Place it just above the entire plot area, or wherever you like
        self.screen.blit(text_surf, (plot_rect.x + 5, plot_rect.y - font_height - 2))
