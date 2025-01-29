import pyved_engine as pyv


class Animation:
    def __init__(self, image, name, f_size):
        self.image = image.convert()
        self.name = name
        self.frames = []
        self.f_size = f_size
        self.f_width = self.f_size[0]
        self.f_height = self.f_size[1]
        self.populate_frames()

    def populate_frames(self):
        for y in range(0, int(self.image.get_height() / self.f_height)):
            row = []
            for x in range(0, int(self.image.get_width() / self.f_width)):
                frame = pyv.surface_create((self.f_width, self.f_height))  # .convert()
                frame.blit(self.image, (0, 0), (x * self.f_width, y * self.f_height, self.f_width, self.f_height))
                frame.set_colorkey((0, 255, 0))
                row.append(frame)
            self.frames.append(row)
