from passlib.hash import bcrypt


def generate_admin_user() -> dict:
    """
    Genera un diccionario con los datos del usuario administrador inicial.
    """
    return {
        "name": "Administrador General",
        "email": "admin.saluia5@gmail.com",
        "rut": "10800850-8",
        "hashed_password": bcrypt.hash("admin.saluia5.123"),
        "is_admin": True,
        "is_doctor": True,
        "is_chief_doctor": True,
        "turn": "all",
    }
