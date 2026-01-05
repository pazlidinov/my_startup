import secrets
import string
from utils.db_api.database import all_tables as db



async def generate_code(length=10):
    alphabet = string.ascii_letters + string.digits

    while True:
        new_code = "".join(secrets.choice(alphabet) for _ in range(length))
        client = await db.select_client(secret_code=new_code)
        gym = await db.select_gym(secret_code=new_code)
        if not client and not gym:
            return new_code
