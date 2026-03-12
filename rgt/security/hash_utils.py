from bcrypt import hashpw, checkpw, gensalt


class HashUtils:
    @staticmethod
    def hash(plain: str, rounds: int = 12) -> str:
        return hashpw(plain.encode(), gensalt(rounds=rounds)).decode()

    @staticmethod
    def verify(plain: str, hashed: str) -> bool:
        return checkpw(plain.encode(), hashed.encode())
