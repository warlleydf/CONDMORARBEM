from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, DateTimeField, SubmitField, ValidationError
from wtforms.validators import DataRequired
import re

from models import Unidade

def email_check(form, field):
    email = field.data
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Endereço de email inválido.')

class EncomendaForm(FlaskForm):
    unidade = SelectField('Unidade', choices=[(101, '101'), (102, '102'), (201, '201'), (301, '301'), (302, '302'), (401, '401'), (402, '402'), (501, '501'), (502, '502')], validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('Carta', 'Carta'), ('Envelope', 'Envelope'), ('Pacote', 'Pacote'), ('Caixa', 'Caixa')], validators=[DataRequired()])
    porteiro = StringField('Porteiro', validators=[DataRequired()])
    data_recebimento = DateTimeField('Data de Recebimento', validators=[DataRequired()])
    submit = SubmitField('Registrar Encomenda')

class BaixaForm(FlaskForm):
    id_encomenda = SelectField('ID da Encomenda', coerce=int, validators=[DataRequired()])
    nome_morador = StringField('Nome do Morador', validators=[DataRequired()])
    porteiro_retirada = StringField('Porteiro que Entregou', validators=[DataRequired()])
    data_retirada = DateTimeField('Data de Retirada', validators=[DataRequired()])
    submit = SubmitField('Dar Baixa')

class UnidadeForm(FlaskForm):
    numero = StringField('Unidade', validators=[DataRequired()])
    nome_proprietario = StringField('Nome do Proprietário', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), email_check])
    submit = SubmitField('Atualizar')
    
class RegistrarEncomendaForm(FlaskForm):
    unidade_numero = SelectField('Unidade', coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo de Encomenda', choices=[('carta', 'Carta'), ('envelope', 'Envelope'), ('pacote', 'Pacote'), ('caixa', 'Caixa')], validators=[DataRequired()])
    nome_porteiro_recebimento = StringField('Nome do Porteiro', validators=[DataRequired()])
    data_recebimento = DateField('Data de Recebimento', format='%Y-%m-%d', validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidade_numero.choices = [(str(unidade.numero), f'{unidade.numero}') for unidade in Unidade.query.all()]

class DarBaixaEncomendaForm(FlaskForm):
    encomenda_id = SelectField('ID da Encomenda', coerce=int, validators=[DataRequired()])
    nome_morador_retirada = StringField('Nome do Morador', validators=[DataRequired()])
    nome_porteiro_retirada = StringField('Nome do Porteiro', validators=[DataRequired()])
    data_retirada = DateField('Data de Retirada', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Dar Baixa')