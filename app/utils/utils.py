# Utility functions (e.g., for Excel parsing) will be implemented here in later steps.
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_bcrypt_hash(password: str) -> str:
    """
    Generate a bcrypt hash for the given password.
    Usage:
        from app.utils.utils import generate_bcrypt_hash
        print(generate_bcrypt_hash("your_password"))
    """
    return pwd_context.hash(password)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(generate_bcrypt_hash(sys.argv[1]))
    else:
        print("Usage: python utils.py <password>")