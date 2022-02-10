
class Vector2:
    # TODO pygame.Vector2 doesn't seem to be supported yet. So I made my own >:(

    def __init__(self, x, y=0.0):
        if isinstance(x, Vector2):
            self.x = x.x
            self.y = x.y
        else:
            self.x = x
            self.y = y

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        else:
            return self.y

    def __len__(self):
        return 2

    def __iter__(self):
        return (v for v in (self.x, self.y))

    def __add__(self, other: 'Vector2'):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2'):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Vector2(self.x * other, self.y * other)

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: 'Vector2'):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def rotate_ip(self, degrees):
        theta = math.radians(degrees)
        cs = math.cos(theta)
        sn = math.sin(theta)
        x = self.x * cs - self.y * sn
        y = self.x * sn + self.y * cs
        self.x = x
        self.y = y

    def rotate(self, degrees):
        res = Vector2(self)
        res.rotate_ip(degrees)
        return res

    def to_ints(self):
        return Vector2(int(self.x), int(self.y))

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def scale_to_length(self, length):
        cur_length = self.length()
        if cur_length == 0 and length != 0:
            raise ValueError("Cannot scale vector with length 0")
        else:
            mult = length / cur_length
            self.x *= mult
            self.y *= mult
