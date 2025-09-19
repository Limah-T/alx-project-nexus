import cloudinary.uploader
def upload_to_the_cloud(image, **options):
    cloudinary.uploader.upload(image)

