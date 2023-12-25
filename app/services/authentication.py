from werkzeug.security import check_password_hash, generate_password_hash


def confirm_password(hashed_password: str, plain_password: str):
    return check_password_hash(hashed_password, plain_password)


def hash_user_password(password: str):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
