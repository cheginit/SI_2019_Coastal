class Bay():
    def __init__(self,
                 shape,
                 w_b,
                 R_br,
                 R_lb,
                 R_bt,
                 z_o,
                 z_r=-1e3,
                 x_o1=0e0,
                 y0=0e0,
                 S_o=2e-3,
                 S_b=2e-4,
                 cell_size=2e3):

        self.shape = shape
        self.x_o1, self.y0, self.z_r = x_o1, y0, z_r
        self.z_o, self.z_r = z_o, z_r
        self.S_o, self.S_b = S_o, S_b
        self.w_b = w_b
        self.R_br, self.R_lb, self.R_bt = R_br, R_lb, R_bt
        self.cell_size = cell_size

        self.set_params()

    def set_params(self):
        self.w_r = self.w_b / self.R_br
        self.w_t = self.w_b / self.R_bt if self.shape == 'trapezoid' else self.w_r
        self.w_o = 3e0 * self.w_b

        self.l_o = 50e3
        self.l_b = self.R_lb * self.w_b
        self.l_r = 100e3

        self.z_b = self.z_o + self.S_b * self.l_b
        self.z0 = self.z_o - self.S_o * self.l_o

        self.x_o2 = self.x_o1 + self.w_o

        self.x_b1 = self.x_o1 + 0.5 * (self.w_o - self.w_b)
        self.x_b2 = self.x_b1 + self.w_b
        self.x_b3 = self.x_b1 + 0.5 * (self.w_b - self.w_t)
        self.x_b4 = self.x_b3 + self.w_t

        self.x_r1 = self.x_b1 + 0.5 * (self.w_b - self.w_r)
        self.x_r2 = self.x_r1 + self.w_r

        self.y_o = self.y0 + self.l_o
        self.y_b = self.y_o + self.l_b
        self.y_r = self.y_b + self.l_r

        self.r_area = (self.x_r2 - self.x_r1) * self.z_r
