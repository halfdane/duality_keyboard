class Debouncer:
    def __init__(self, debounce_samples=3):
        self.last_x_samples = [0] * debounce_samples
        self.last_y_samples = [0] * debounce_samples
        self.debounce_index = 0

    def start_debounce(self, x, y):
        self.last_x_samples = [x] * len(self.last_x_samples)  # Initialize with first value
        self.last_y_samples = [y] * len(self.last_y_samples)  # Initialize with first value
        self.debounce_index = 0
    
    def debounce(self, x, y):
        self.last_x_samples[self.debounce_index] = x
        self.last_y_samples[self.debounce_index] = y
        self.debounce_index = (self.debounce_index + 1) % len(self.last_x_samples)

        x = sum(self.last_x_samples) // len(self.last_x_samples)
        y = sum(self.last_y_samples) // len(self.last_y_samples)

        return x, y