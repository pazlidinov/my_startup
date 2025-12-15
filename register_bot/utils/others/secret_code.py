import secrets
import string

from loader import client_db


async def generate_code(length=10):
    alphabet = string.ascii_letters + string.digits

    while True:
        new_code = "".join(secrets.choice(alphabet) for _ in range(length))
        client = await client_db.select_client(secret_code=new_code)
        if not client:
            return new_code
    # new_code = "".join(secrets.choice(alphabet) for _ in range(10))
    # return new_code
