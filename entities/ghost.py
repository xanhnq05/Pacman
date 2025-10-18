class ghost:
    def __init__(self, x, y, color, direction, leftLimit, rightLimit):
        self.x = x
        self.y = y
        self.direction = direction #rotate follow the direction degrees 90 or -90
        self.leftLimit = leftLimit
        self.rightLimit = rightLimit
        self.speed = 1
        self.radius = 10
        self.color = color

    def load_graphic(self):
        path = f'assets/ghost_image/{self.color}.png' #path to the images
        self.image = pygame.image.load(path).convert_alpha() # load the image following the color value
        self.image = pygame.transform.scale(self.image, (self.radius, self.radius)) # scale the image to the radius
        self.image = pygame.transform.rotate(self.image, self.direction) #load graphic that rotating follow the direction
        self.rect = self.image.get_rect() # init the rect
        self.rect.center = (self.x, self.y)# set x,y to the rect that has been initialized

    def update(self, maze):
        new_x = self.x + self.speed * self.direction
        # Nếu phía trước là tường → quay đầu lại
        if maze.is_wall(new_x, self.y):
            self.direction *= -1
        else:
        # Không phải tường → di chuyển bình thường
            self.x = new_x
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)