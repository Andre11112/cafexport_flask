from werkzeug.security import generate_password_hash

password = "654321"
hash = generate_password_hash(password)
print(f"-- Hash generado para todas las empresas: {hash}") 