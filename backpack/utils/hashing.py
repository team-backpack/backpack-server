import bcrypt

def hash(senha: str):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def check(senha: str, hashed: str):
    return bcrypt.checkpw(senha.encode(), hashed.encode())