import cloudinary.uploader
import cloudinary.api

def uploadImage(image):
    try:
        upload_result = cloudinary.uploader.upload(
            image,
            overwrite=True,
            resource_type="image"
        )
    except Exception as e:
        print(str(e))
        return str(e)
    return upload_result

def getImage(public_id):
    try:
        response = cloudinary.api.resource(public_id)
    except Exception as e:
        print(str(e))
        return False
    return response

def updateImage(public_id):
    try:
        response = cloudinary.uploader.explicit(
            public_id=public_id,
            type="upload"
        )
    except Exception as e:
        return False
    return response