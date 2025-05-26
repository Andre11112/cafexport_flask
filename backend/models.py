from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import enum

db = SQLAlchemy()

# Definir Enums para tipos de café y estados de venta
class TipoCafeEnum(enum.Enum):
    Pasilla = 'Pasilla'
    Arabica = 'Arabica'

class EstadoVentaEnum(enum.Enum):
    Pendiente = 'Pendiente'
    Aprobada = 'Aprobada'
    Rechazada = 'Rechazada'
    Cancelada = 'Cancelada'

# Modelos
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'campesino', 'empresa', 'admin'
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=True)         # Solo para campesinos
    nit = db.Column(db.String(20), unique=True, nullable=True)            # Solo para empresas
    email = db.Column(db.String(120), nullable=True)                
    password_hash = db.Column(db.String(255), nullable=False) # Aumentamos el tamaño para el hash
    direccion_finca = db.Column(db.String(200), nullable=True)      
    direccion_empresa = db.Column(db.String(200), nullable=True)    
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Ventas (opcional, pero útil para acceder a las ventas de un campesino)
    ventas = db.relationship('Venta', backref='campesino', lazy=True, foreign_keys='Venta.campesino_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'nit': self.nit,
            'email': self.email,
            'direccion_finca': self.direccion_finca,
            'direccion_empresa': self.direccion_empresa,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        } 

class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    campesino_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='RESTRICT'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='RESTRICT'), nullable=True)
    tipo_cafe = db.Column(db.Enum(TipoCafeEnum), nullable=False)
    cantidad = db.Column(db.DECIMAL(10, 2), nullable=False)
    precio_kg = db.Column(db.DECIMAL(10, 2), nullable=False)
    total = db.Column(db.DECIMAL(12, 2), nullable=False) # SQLAlchemy puede calcular esto o puedes calcularlo tú
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    estado = db.Column(db.Enum(EstadoVentaEnum), default=EstadoVentaEnum.Pendiente, nullable=False)

    # Puedes añadir un evento para calcular el total antes de guardar si no usas GENERATED ALWAYS AS
    # from sqlalchemy.event import listens_for
    # @listens_for(Venta, 'before_insert')
    # @listens_for(Venta, 'before_update')
    # def calculate_total(mapper, connection, target):
    #     target.total = target.cantidad * target.precio_kg if target.cantidad and target.precio_kg else 0

    def to_dict(self):
        return {
            'id': self.id,
            'campesino_id': self.campesino_id,
            'empresa_id': self.empresa_id,
            'tipo_cafe': self.tipo_cafe.value, # Obtener el valor string del Enum
            'cantidad': str(self.cantidad), # Convertir Decimal a string para JSON
            'precio_kg': str(self.precio_kg), # Convertir Decimal a string para JSON
            'total': str(self.total), # Convertir Decimal a string para JSON
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado.value, # Obtener el valor string del Enum
        } 