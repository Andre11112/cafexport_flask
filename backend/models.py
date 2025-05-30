from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.schema import Computed

import enum

db = SQLAlchemy()

# Definir Enums para tipos de café y estados de venta
class TipoCafeEnum(enum.Enum):
    Pasilla = 'Pasilla'
    Arabica = 'Arabica'

# Enum para estados de Venta (usado en tabla ventas)
class EstadoVentaEnum(enum.Enum):
    Pendiente = 'Pendiente'
    Aprobada = 'Aprobada' # Mantenemos Aprobada para Ventas
    Rechazada = 'Rechazada'
    Cancelada = 'Cancelada'
    Completada = 'Completada'

# Enum ESPECÍFICO para estados de Compra de Empresa
class EstadoCompraEnum(enum.Enum):
    Pendiente = 'Pendiente'
    Confirmadas = 'Confirmadas'
    Completada = 'Completada'

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
    total = db.Column(db.DECIMAL(12, 2), Computed('cantidad * precio_kg'), nullable=False)
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    estado = db.Column(db.Enum(EstadoVentaEnum), default=EstadoVentaEnum.Aprobada, nullable=False)

    # Definición de la relación con la empresa (comprador)
    empresa = db.relationship('Usuario', foreign_keys=[empresa_id])

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

# Modelo para las compras de las empresas a CafExport
class CompraEmpresa(db.Model):
    __tablename__ = 'compras_empresa'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='RESTRICT'), nullable=False)
    cafexport_vendedor_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='RESTRICT'), nullable=False)
    tipo_cafe = db.Column(db.Enum(TipoCafeEnum), nullable=False)
    cantidad = db.Column(db.DECIMAL(10, 2), nullable=False)
    precio_kg = db.Column(db.DECIMAL(10, 2), nullable=False)
    total = db.Column(db.DECIMAL(12, 2), Computed('cantidad * precio_kg'), nullable=False)
    fecha_orden = db.Column(db.TIMESTAMP, nullable=False)
    fecha_entrega = db.Column(db.TIMESTAMP, nullable=True)
    notas = db.Column(db.TEXT, nullable=True)
    estado = db.Column(db.Enum(EstadoCompraEnum), default=EstadoCompraEnum.Pendiente, nullable=False)

    # Relaciones (opcional, pero útil)
    empresa = db.relationship('Usuario', foreign_keys=[empresa_id])
    cafexport_vendedor = db.relationship('Usuario', foreign_keys=[cafexport_vendedor_id])

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_id': self.empresa_id,
            'cafexport_vendedor_id': self.cafexport_vendedor_id,
            'tipo_cafe': self.tipo_cafe.value,
            'cantidad': str(self.cantidad),
            'precio_kg': str(self.precio_kg),
            'total': str(self.total),
            'fecha_orden': self.fecha_orden.isoformat() if self.fecha_orden else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'notas': self.notas,
            'estado': self.estado.value,
        } 

# Modelo para los precios del café
class PrecioCafe(db.Model):
    __tablename__ = 'precios_cafe'

    id = db.Column(db.Integer, primary_key=True)
    tipo_cafe = db.Column(db.Enum(TipoCafeEnum), nullable=False)
    precio_kg = db.Column(db.DECIMAL(10, 2), nullable=False)
    precio_usd = db.Column(db.DECIMAL(10, 2), nullable=True)  # Precio en dólares de la bolsa
    tasa_cambio = db.Column(db.DECIMAL(10, 2), nullable=True) # Tasa de cambio USD/COP
    fecha_actualizacion = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    fuente = db.Column(db.String(50), nullable=False) # 'manual', 'bolsa_valores', 'api_externa'
    activo = db.Column(db.Boolean, default=True)
    referencia_externa = db.Column(db.String(100), nullable=True) # ID o referencia de la API externa
    metadata_json = db.Column(db.JSON, nullable=True) # Datos adicionales de la API

    # Asegurar que solo haya un precio activo por tipo de café (si es necesario)
    # __table_args__ = (db.UniqueConstraint('tipo_cafe', 'activo', name='uq_tipo_cafe_activo'),)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_cafe': self.tipo_cafe.value,
            'precio_kg': str(self.precio_kg),
            'precio_usd': str(self.precio_usd) if self.precio_usd is not None else None,
            'tasa_cambio': str(self.tasa_cambio) if self.tasa_cambio is not None else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'fuente': self.fuente,
            'activo': self.activo,
            'referencia_externa': self.referencia_externa,
            'metadata_json': self.metadata_json
        } 