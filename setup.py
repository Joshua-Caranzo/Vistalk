import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
    cloud_name = "due4hbbar", 
    api_key = "232339977941922", 
    api_secret = "Ngx09hHe4FAkKNHoBnwGGILYf4E"
)

def upload_media(file_path):
    response = cloudinary.uploader.upload(file_path, resource_type="auto")
    return response['url']
