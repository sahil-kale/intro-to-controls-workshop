class Controller:
    def __init__(self):
        self.integral_term_sum = 0
        self.prev_error = 0

    def get_control_output(self, setpoint, current_position, dt, k_p, k_i, k_d):
        error = setpoint - current_position
        self.integral_term_sum += k_i * error * dt
        derivative = (error - self.prev_error) / dt

        p_term = k_p * error
        i_term = self.integral_term_sum
        d_term = k_d * derivative

        self.prev_error = error

        return p_term + i_term + d_term
