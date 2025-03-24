import numpy as np


class SpringMassDamperModel:
    def __init__(
        self, mass, k_spring, max_spring_force_N, b_damper, midpos_m, control_saturation
    ):
        self.mass = mass  # kg
        self.k_spring = k_spring  # N/m
        self.b_damper = b_damper  # N/(m/s)
        self.midpos_m = midpos_m
        self.control_saturation = control_saturation  # N
        self.max_spring_force_N = max_spring_force_N

        # state space model of a spring-mass-damper system

        self.A = np.array([[0, 1], [-k_spring / mass, -b_damper / mass]])
        self.B = np.array([[0], [1 / mass]])

        self.C = np.array([[1, 0]])

        self.x = np.array([[0], [0]])  # Position and velocity

    def compute_non_linear_spring_constant(self):
        delta_pos = np.abs(self.get_position() - self.midpos_m)
        non_clamped_spring_force = self.k_spring * delta_pos
        clamped_spring_force = np.clip(
            non_clamped_spring_force, -self.max_spring_force_N, self.max_spring_force_N
        )

        eff_spring_constant = clamped_spring_force / delta_pos if delta_pos != 0 else 0
        return eff_spring_constant

    def compute_derivative(self, force):
        force = np.clip(force, -self.control_saturation, self.control_saturation)
        force = np.array([[force]], dtype="float64")
        return self.A @ self.x + self.B @ force

    def compute_new_position(self, force, dt, num_steps=500):
        eff_spring_constant = self.compute_non_linear_spring_constant()
        self.A[1][0] = -eff_spring_constant / self.mass
        for _ in range(num_steps):
            x_dot = self.compute_derivative(force)
            self.x = self.x + (x_dot * dt / num_steps)  # Euler's method

        return self.get_position()

    def get_position(self):
        return self.x[0][0] + self.midpos_m

    def get_velocity(self):
        return self.x[1][0]
