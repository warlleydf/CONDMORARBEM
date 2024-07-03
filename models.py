from app import db
from datetime import datetime

class Encomenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unidade_numero = db.Column(db.String(10), db.ForeignKey('unidade.numero'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nome_porteiro_recebimento = db.Column(db.String(100), nullable=False)
    data_recebimento = db.Column(db.DateTime, nullable=False)
    nome_morador_retirada = db.Column(db.String(100))
    nome_porteiro_retirada = db.Column(db.String(100))
    data_retirada = db.Column(db.DateTime)
    retirada = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Encomenda {self.id} - Unidade {self.unidade}"

class Unidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nome_proprietario = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
