import numpy as np


class SpringMassDamperModel:
    def __init__(self, mass, k_spring, b_damper, midpos_m, control_saturation):
        self.mass = mass  # kg
        self.k_spring = k_spring  # N/m
        self.b_damper = b_damper  # N/(m/s)
        self.midpos_m = midpos_m
        self.control_saturation = control_saturation  # N

        # state space model of a spring-mass-damper system

        self.A = np.array([[0, 1], [-k_spring / mass, -b_damper / mass]])
        self.B = np.array([[0], [1 / mass]])

        self.C = np.array([[1, 0]])

        self.x = np.array([[0], [0]])  # Position and velocity

    def compute_derivative(self, force):
        force = np.clip(force, -self.control_saturation, self.control_saturation)
        force = np.array([[force]], dtype="float64")
        return self.A @ self.x + self.B @ force

    def compute_new_position(self, force, dt, num_steps=500):
        for _ in range(num_steps):
            x_dot = self.compute_derivative(force)
            self.x = self.x + (x_dot * dt / num_steps)  # Euler's method

        return self.get_position()

    def get_position(self):
        return self.x[0][0] + self.midpos_m

    def get_velocity(self):
        return self.x[1][0]
