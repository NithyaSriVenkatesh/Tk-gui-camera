import tkinter as tk

class Joystick(tk.Canvas):
    def __init__(self, master, control_callback, width=200, height=200, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.control_callback = control_callback
        self.outer_circle_radius = 80
        self.inner_circle_radius = 30
        self.center = (self.winfo_reqwidth() / 2, self.winfo_reqheight() / 2)
        self.inner_circle_position = self.center
        self.outer_circle_color = "#000080"
        self.inner_circle_color = "#0000FF"

        self.create_oval(self.get_outer_circle_pos(), outline=self.outer_circle_color, width=2)
        self.inner_circle = self.create_oval(self.get_inner_circle_pos(), fill=self.inner_circle_color)

        self.bind("<Configure>", self.update_canvas)
        self.bind("<B1-Motion>", self.on_touch_move)

    def get_outer_circle_pos(self):
        return (
            self.center[0] - self.outer_circle_radius,
            self.center[1] - self.outer_circle_radius,
            self.center[0] + self.outer_circle_radius,
            self.center[1] + self.outer_circle_radius
        )

    def get_inner_circle_pos(self):
        return (
            self.inner_circle_position[0] - self.inner_circle_radius,
            self.inner_circle_position[1] - self.inner_circle_radius,
            self.inner_circle_position[0] + self.inner_circle_radius,
            self.inner_circle_position[1] + self.inner_circle_radius
        )

    def update_canvas(self, event=None):
        self.center = (self.winfo_width() / 2, self.winfo_height() / 2)
        self.coords(self.inner_circle, self.get_inner_circle_pos())

    def on_touch_move(self, event):
        distance = ((self.center[0] - event.x) ** 2 + (self.center[1] - event.y) ** 2) ** 0.5
        if distance <= self.outer_circle_radius:
            self.inner_circle_position = (event.x, event.y)
            self.coords(self.inner_circle, self.get_inner_circle_pos())
            self.control_callback(self.calculate_direction(event.x, event.y))

    def calculate_direction(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

