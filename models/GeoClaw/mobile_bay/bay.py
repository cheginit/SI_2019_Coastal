class Bay():
    def __init__(self, info):
        from reader import read_data

        config = read_data(info)

        self.shape = config['shape']
        self.x_o1, self.y0, self.z_r = config['x_o1'], config['y0'], config[
            'z_r']
        self.z_o, self.z_r = config['z_o'], config['z_r']
        self.S_o, self.S_b = config['S_o'], config['S_b']
        self.w_b = config['w_b']
        self.R_br, self.R_lb, self.R_bt = config['R_br'], config[
            'R_lb'], config['R_bt']
        self.cell_size = config['cell_size']

        self.set_params()

    def set_params(self):
        self.w_r = self.w_b / self.R_br
        self.w_t = self.w_b / self.R_bt if self.shape == 'trapezoid' else self.w_r
        self.w_o = 5e0 * self.w_b

        self.l_o = 30e3
        self.l_b = self.R_lb * self.w_b
        self.l_r = 50e3

        self.z_b = self.z_o + self.S_b * self.l_b
        self.z0 = self.z_o - self.S_o * self.l_o

        self.x_o2 = self.x_o1 + self.w_o

        self.x_b1 = self.x_o1 + 0.5 * (self.w_o - self.w_b)
        self.x_b2 = self.x_b1 + self.w_b
        self.x_b3 = self.x_b1 + 0.5 * (self.w_b - self.w_t)
        self.x_b4 = self.x_b3 + self.w_t

        self.x_r1 = self.x_b1 + 0.5 * (self.w_b - self.w_r)
        self.x_r2 = self.x_r1 + self.w_r

        self.r_width = self.x_r2 - self.x_r1
        self.min_ref = int(self.cell_size / self.r_width * 0.5) + 1

        self.y_o = self.y0 + self.l_o
        self.y_b = self.y_o + self.l_b
        self.y_r = self.y_b + self.l_r
