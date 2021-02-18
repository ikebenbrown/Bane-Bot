import cv2


class ImageProcessor:

    imageState = None

    def __init__(self, image, name):
        self.original_name = name
        self.name = "images/" + name + "_proposed"
        self.image = image
        if image.height <= 32 and image.width <= 32:
            self.image_state = "fit"
        elif image.height is image.width:
            self.image_state = "square"
        else:
            self.image_state = "bad"

    def get_image_state(self):
        return self.imageState

    async def downscale(self):
        await self.download_image()
        self.img = cv2.imread(self.name + ".png",-1)
        self.img = cv2.resize(self.img, (32,32), interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.name + ".png", self.img)
        is_success, im_buf_arr = cv2.imencode(".png", self.img)
        self.bytes = im_buf_arr.tobytes()

    async def download_image(self):
        self.mat = await self.image.save(self.name + ".png")

    async def downscale_skew(self):
        await self.download_image()
        self.img = cv2.imread(self.name + ".png", -1)
        width = self.img.shape[1]
        height = self.img.shape[0]
        if width > height:
            ratio = height / width
            height = int(32 * ratio)
            width = 32
        else:
            ratio = width / height
            width = int(32 * ratio)
            height = 32
        self.img = cv2.resize(self.img, (width, height), interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.name + ".png", self.img)
        is_success, im_buf_arr = cv2.imencode(".png", self.img)
        self.bytes = im_buf_arr.tobytes()
