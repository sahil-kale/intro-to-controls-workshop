class Controller:
    def __init__(self):
        self.integral_term_sum = 0
        self.prev_error = 0

    def get_control_output(self, setpoint, current_position, dt, k_p, k_i, k_d):
        return 0
