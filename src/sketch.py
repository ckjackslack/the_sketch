from PIL import Image, ImageDraw


class Canvas:
    def __init__(self, width, height, background_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), background_color)
        self.draw = ImageDraw.Draw(self.image)

    def save(self, filename):
        self.image.save(filename)

    def show(self):
        self.image.show()


class Sketch:
    def __init__(self, canvas):
        self.canvas = canvas

    def setup(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass


def run_sketch(sketch, width, height, background_color=(255, 255, 255)):
    canvas = Canvas(width, height, background_color)
    sketch_instance = sketch(canvas)
    sketch_instance.setup()

    while True:
        sketch_instance.update()
        sketch_instance.draw()
        canvas.show()
