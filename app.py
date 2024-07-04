from cgitb import text
from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired
from forms import UnidadeForm
from flask import flash, redirect, render_template, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#teste

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condmorarbem.db'
app.config['SECRET_KEY'] = 'mysecretkey'


db = SQLAlchemy(app)

class Unidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    nome_proprietario = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Encomenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unidade_numero = db.Column(db.String(10), db.ForeignKey('unidade.numero'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    nome_porteiro_recebimento = db.Column(db.String(100), nullable=False)
    data_recebimento = db.Column(db.DateTime, nullable=False)
    nome_morador_retirada = db.Column(db.String(100))
    nome_porteiro_retirada = db.Column(db.String(100))
    data_retirada = db.Column(db.DateTime)
    retirada = db.Column(db.Boolean, default=False)  # Adicione esta linha se 'retirada' for um campo booleano

class RegistrarEncomendaForm(FlaskForm):
    unidade_numero = SelectField('Unidade', coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo de Encomenda', choices=[('carta', 'Carta'), ('envelope', 'Envelope'), ('pacote', 'Pacote'), ('caixa', 'Caixa')], validators=[DataRequired()])
    nome_porteiro_recebimento = StringField('Nome do Porteiro', validators=[DataRequired()])
    data_recebimento = DateField('Data de Recebimento', format='%Y-%m-%d', validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidade_numero.choices = [(unidade.id, f'{unidade.numero}') for unidade in Unidade.query.all()]

class DarBaixaEncomendaForm(FlaskForm):
    encomenda_id = SelectField('ID da Encomenda', coerce=int, validators=[DataRequired()])
    nome_morador_retirada = StringField('Nome do Morador', validators=[DataRequired()])
    nome_porteiro_retirada = StringField('Nome do Porteiro', validators=[DataRequired()])
    data_retirada = DateField('Data de Retirada', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Dar Baixa')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registrar_encomenda", methods=["GET", "POST"])
def registrar_encomenda():
    form = RegistrarEncomendaForm()
    if form.validate_on_submit():
        encomenda = Encomenda(
            unidade_numero=form.unidade_numero.data,
            tipo=form.tipo.data,
            nome_porteiro_recebimento=form.nome_porteiro_recebimento.data,
            data_recebimento=form.data_recebimento.data
        )
        db.session.add(encomenda)
        db.session.commit()
        
        # Obter o e-mail do proprietário da unidade
        unidade = Unidade.query.filter_by(numero=form.unidade_numero.data).first()
        destinatario = unidade.email
        assunto = 'Condomínio Morar Bem - Nova correspondência'
        corpo = (
    f"Prezado condômino da Unidade ({form.unidade_numero.data}),\n"
    "Uma nova correspondência aguarda sua retirada na portaria.\n"
    f"- Data de recebimento: {form.data_recebimento.data}\n"
    f"- Tipo: {form.tipo.data}\n"
    f"- Porteiro que recebeu: {form.nome_porteiro_recebimento.data}\n"
    "Atenciosamente,\n"
    "Administração do Condomínio Morar Bem."
) #teste#
        enviar_email(destinatario, assunto, corpo)
        flash('Encomenda registrada e e-mail enviado com sucesso!', 'success')
        
        return redirect(url_for('index'))
    
    return render_template("registrar_encomenda.html", form=form)

@app.route('/dar_baixa', methods=['GET', 'POST'])
def dar_baixa():
    form = DarBaixaEncomendaForm()
    
    # Buscar encomendas pendentes
    encomendas_pendentes = Encomenda.query.filter_by(retirada=False).all()
    
    # Preencher o SelectField com as opções de encomendas pendentes
    form.encomenda_id.choices = [(encomenda.id, f'{encomenda.id} : Unid. {encomenda.unidade_numero}') for encomenda in encomendas_pendentes]
    
    if request.method == 'POST' and form.validate_on_submit():
        # Lógica para dar baixa na encomenda
        encomenda_id = form.encomenda_id.data
        encomenda = Encomenda.query.get(encomenda_id)
        if encomenda:
            encomenda.retirada = True
            encomenda.nome_morador_retirada = form.nome_morador_retirada.data
            encomenda.nome_porteiro_retirada = form.nome_porteiro_retirada.data
            encomenda.data_retirada = form.data_retirada.data
            db.session.commit()
        
        # Redirecionar para a página inicial após a baixa da encomenda
        flash('Baixa de encomenda registrada com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('dar_baixa.html', form=form, encomendas_pendentes=encomendas_pendentes)

@app.route("/historico")
def historico():
    encomendas = Encomenda.query.filter(Encomenda.data_retirada.isnot(None)).all()
    return render_template("historico.html", encomendas=encomendas)

@app.route("/unidades")
def unidades():
    unidades = Unidade.query.all()
    return render_template("unidades.html", unidades=unidades)

@app.route("/cadastrar_unidade", methods=["GET", "POST"])
def cadastrar_unidade():
    form = UnidadeForm()
    if form.validate_on_submit():
        
        unidade_existente_numero = Unidade.query.filter_by(numero=form.numero.data).first()
        unidade_existente_email = Unidade.query.filter_by(email=form.email.data).first()
        unidade_existente_proprietario = Unidade.query.filter_by(nome_proprietario=form.nome_proprietario.data).first()
        
        if unidade_existente_numero:
            flash('Unidade com este número já cadastrada!', 'danger')
        elif unidade_existente_email:
            flash('Já existe uma unidade cadastrada com este email!', 'danger')
        elif unidade_existente_proprietario:
            flash('Já existe uma unidade cadastrada com este proprietario!', 'danger')
        else:
            # Criar e adicionar a nova unidade apenas se não houver conflito
            nova_unidade = Unidade(
                numero=form.numero.data,
                nome_proprietario=form.nome_proprietario.data,
                telefone=form.telefone.data,
                email=form.email.data
            )
            db.session.add(nova_unidade)
            db.session.commit()
            flash('Unidade cadastrada com sucesso!', 'success')
            return redirect(url_for('unidades'))
    
    return render_template("cadastrar_unidade.html", form=form)

            
@app.route("/alterar_unidade/<int:id>", methods=["GET", "POST"])
def alterar_unidade(id):
    unidade = Unidade.query.get_or_404(id)
    form = UnidadeForm(obj=unidade)
    if form.validate_on_submit():
        unidade.nome_proprietario = form.nome_proprietario.data
        unidade.telefone = form.telefone.data
        unidade.email = form.email.data
        db.session.commit()
        flash('Atualização da unidade com sucesso!', 'success')
        return redirect(url_for('unidades'))
    return render_template("alterar_unidade.html", form=form, unidade=unidade)

def enviar_email(destinatario, assunto, corpo):
    remetente = 'testemorarbem@gmail.com'
    senha = 'fvhonpowfrqdkvgx'
    
    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto

    mensagem.attach(MIMEText(corpo, 'plain'))

    try:
        servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        servidor_smtp.starttls()
        servidor_smtp.login(remetente, senha)
        servidor_smtp.sendmail(remetente, destinatario, mensagem.as_string())
        servidor_smtp.quit()
        print('E-mail enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar e-mail: {str(e)}')

@app.route('/remover_unidade/<int:id>', methods=['POST', 'DELETE'])
def remover_unidade(id):
    unidade = Unidade.query.get_or_404(id)
    
    if tem_encomendas_vinculadas(unidade):
        flash('Não é possível excluir esta unidade porque há encomendas vinculadas a ela.', 'danger')
    else:
        try:
            db.session.delete(unidade)
            db.session.commit()
            flash('Unidade removida com sucesso!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao tentar remover a unidade.', 'danger')
    
    return redirect(url_for('unidades'))

# Função para verificar se há encomendas vinculadas à unidade
def tem_encomendas_vinculadas(unidade):
    try:
        # Consulta para verificar se há encomendas vinculadas à unidade
        encomendas_vinculadas = Encomenda.query.filter_by(unidade_numero=unidade.numero).first()
        
        # Se há encomendas vinculadas, retorna True
        return encomendas_vinculadas is not None
    except Exception as e:
        # Lida com qualquer erro de consulta ou de banco de dados
        db.session.rollback()
        raise e

@app.before_request
def before_request():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
