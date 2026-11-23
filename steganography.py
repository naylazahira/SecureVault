from stegano import lsb
from io import BytesIO
from PIL import Image

def hide_message(image_bytes,message):
    img=Image.open(BytesIO(image_bytes)).convert("RGB")
    out=lsb.hide(img,message)
    b=BytesIO(); out.save(b,format="PNG"); return b.getvalue()

def reveal_message(image_bytes):
    img=Image.open(BytesIO(image_bytes))
    return lsb.reveal(img)
