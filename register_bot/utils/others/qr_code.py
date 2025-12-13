import qrcode
from secret_code import generate_code


# QR kodni yaratish
def generate_qr_code(telegram_id):
    qr = qrcode.QRCode(
        version=5,  # kod o'lchami (1–40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # xatolarni tuzatish darajasi
        box_size=10,  # har bir kvadratning o'lchami
        border=4,  # chekka qalinligi
    )

    # QR kodga aylantirmoqchi bo'lgan ma'lumot
    qr.add_data(f"{telegram_id}/{generate_code()}")
    qr.make(fit=True)

    # QR kodni rasm sifatida saqlash
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f"../../qr_code_img/client_img/{telegram_id}.jpg")


if __name__ == "__main__":
    generate_qr_code(6)
