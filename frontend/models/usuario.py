from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# Importar db desde el frontend
from frontend import db # Asumiendo que db estará en frontend/__init__.py

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))  # 'campesino' o 'empresa'
    cedula = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=True)
    direccion_finca = db.Column(db.String(200))
    password_hash = db.Column(db.String(128))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Usuario, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'email': self.email,
            'direccion_finca': self.direccion_finca,
            'fecha_registro': self.fecha_registro.isoformat()
        } 