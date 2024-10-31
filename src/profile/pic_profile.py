import base64
from io import BytesIO
from PIL import Image

def handle_profile_pic_upload(file):
    if file and allowed_file(file.filename):
        image = Image.open(file)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_binary = buffered.getvalue()
        return {'profile_pic': base64.b64encode(img_binary).decode('utf-8')}
    return {}

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
   
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS