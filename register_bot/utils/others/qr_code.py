import os
import qrcode


# QR kodni yaratish
def generate_qr_code(telegram_id, secret_code, file):
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
    img.save(f"../../qr_code_img/{file}/{telegram_id}.jpg")

    return os.path.abspath(f"../../qr_code_img/{file}/{telegram_id}.jpg")
