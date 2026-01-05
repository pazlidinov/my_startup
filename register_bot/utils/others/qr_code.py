import os
import qrcode
from pathlib import Path





BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "qr_code_img" 
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def save_qr(img, name: str):
    path = MEDIA_DIR / name
    img.save(path)
    return str(path)


# QR kodni yaratish
def generate_qr_code(telegram_id, secret_code):
    qr = qrcode.QRCode(
        version=5,  # kod o'lchami (1–40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # xatolarni tuzatish darajasi
        box_size=10,  # har bir kvadratning o'lchami
        border=4,  # chekka qalinligi
    )

    # QR kodga aylantirmoqchi bo'lgan ma'lumot
    qr.add_data(f"{telegram_id}/{secret_code}")
    qr.make(fit=True)

    # QR kodni rasm sifatida saqlash
    img = qr.make_image(fill_color="black", back_color="white")
    return save_qr(img, f"{telegram_id}.png")
