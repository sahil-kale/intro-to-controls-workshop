import argparse
import click
from model import SpringMassDamperModel
from renderer import Renderer
import time
import random


class Simulator:
    def __init__(self, controller, model, renderer, length_m, white_noise_percent):
        self.controller = controller
        self.model = model
        self.renderer = renderer
        self.fps = 60
        self.dt = 1 / self.fps
        self.length_m = length_m
        self.white_noise_percent = white_noise_percent

    def run(self):
        try:
            time_now = 0
            while True:
                ref = self.renderer.get_selected_reference()
                gains = self.renderer.get_selected_gains()
                kp, ki, kd = gains

                actual_pos = self.model.get_position()
                noise = (
                    random.uniform(-1, 1)
                    * self.white_noise_percent
                    / 100
                    * self.length_m
                )
                actual_pos += noise
                force = self.controller.get_control_output(
                    ref, actual_pos, self.dt, kp, ki, kd
                )
                new_pos = model.compute_new_position(force, self.dt)
                self.renderer.set_object_state(new_pos, model.get_velocity)

                labels = ["Reference", "Position", "Force"]
                values = [ref, actual_pos, force]
                self.renderer.plot(labels, values, time_now)
                self.renderer.update()
                time.sleep(self.dt)
                time_now += self.dt

        except KeyboardInterrupt:
            click.secho("Exiting...", fg="red")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a PID controller")
    parser.add_argument(
        "--solution", action="store_true", help="Use the solution controller"
    )
    args = parser.parse_args()

    if args.solution:
        from controller_solution import Controller
    else:
        from controller_implemented import Controller

    controller = Controller()
    simulation_length_m = 8
    model = SpringMassDamperModel(
        mass=1.0, k_spring=0.3, b_damper=0.05, midpos_m=simulation_length_m / 2
    )
    renderer = Renderer(length_m=simulation_length_m, width=1600, height=1200)
    simulator = Simulator(
        controller, model, renderer, simulation_length_m, white_noise_percent=2
    )
    simulator.run()
