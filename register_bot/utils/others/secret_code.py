import secrets
import string

# from loader import client_db


def generate_code():
    alphabet = string.ascii_letters + string.digits

    # while True:
    #     new_code = "".join(secrets.choice(alphabet) for _ in range(10))
    #     client = await client_db.select_client(secret_code=new_code)
    #     if not client:
    #         return new_code
    new_code = "".join(secrets.choice(alphabet) for _ in range(10))
    return new_code
