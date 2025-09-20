import cloudinary.uploader
import cloudinary.api
from cloudinary import CloudinaryImage

def uploadImage(image):

  # Upload the image and get its URL
  # ==============================

  # Upload the image.
  # Set the asset's public ID and allow overwriting the asset with new versions
  cloudinary.uploader.upload(image, secure=True)

  # Build the URL for the image and save it in the variable 'srcURL'
  srcURL = CloudinaryImage(f"quickstart_{image}").build_url()

  # Log the image URL to the console. 
  # Copy this URL in a browser tab to generate the image on the fly.
  print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")


