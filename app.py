from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrarEncomendaForm, DarBaixaEncomendaForm, UnidadeForm
from models import db, Unidade, Encomenda
from utils import enviar_email, obter_email_proprietario, tem_encomendas_vinculadas, validar_numero_unidade


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///condmorarbem.db'
app.config['SECRET_KEY'] = 'mysecretkey'

db.init_app(app)


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
        
        destinatario = obter_email_proprietario(db,form.unidade_numero.data)
        
        if destinatario:
            assunto = 'Condomínio Morar Bem - Nova correspondência'
            corpo = (
                f"Prezado condômino da Unidade ({form.unidade_numero.data}),\n"
                "Uma nova correspondência aguarda sua retirada na portaria.\n"
                f"- Data de recebimento: {form.data_recebimento.data}\n"
                f"- Tipo: {form.tipo.data}\n"
                f"- Porteiro que recebeu: {form.nome_porteiro_recebimento.data}\n"
                "Atenciosamente,\n"
                "Administração do Condomínio Morar Bem."
            )
            enviar_email(db, destinatario, assunto, corpo)
        
        flash('Encomenda registrada e e-mail enviado com sucesso!', 'success')
        
        return redirect(url_for('index'))
    
    return render_template("registrar_encomenda.html", form=form)

@app.route('/dar_baixa', methods=['GET', 'POST'])
def dar_baixa():
    form = DarBaixaEncomendaForm()
    
    encomendas_pendentes = Encomenda.query.filter_by(retirada=False).all()
    form.encomenda_id.choices = [(encomenda.id, f'{encomenda.id} : Unid. {encomenda.unidade_numero}') for encomenda in encomendas_pendentes]
    
    if request.method == 'POST' and form.validate_on_submit():
        encomenda_id = form.encomenda_id.data
        encomenda = Encomenda.query.get(encomenda_id)
        if encomenda:
            encomenda.retirada = True
            encomenda.nome_morador_retirada = form.nome_morador_retirada.data
            encomenda.nome_porteiro_retirada = form.nome_porteiro_retirada.data
            encomenda.data_retirada = form.data_retirada.data
            db.session.commit()
        
        flash('Baixa de encomenda registrada com sucesso!', 'success')
        return redirect(url_for('index'))
    
    return render_template('dar_baixa.html', form=form, encomendas_pendentes=encomendas_pendentes)

@app.route("/historico")
def historico():
    encomendas = Encomenda.query.filter(Encomenda.data_retirada.isnot(None)).all()
    return render_template("historico.html", encomendas=encomendas)

@app.route("/unidades")
def unidades():
    unidades = Unidade.query.order_by(Unidade.numero).all()
    return render_template("unidades.html", unidades=unidades)

@app.route("/cadastrar_unidade", methods=["GET", "POST"])
def cadastrar_unidade():
    form = UnidadeForm()
    
    if form.validate_on_submit():
        if not validar_numero_unidade(form.numero.data):
            flash('Número de unidade inválido! Use o formato correto (por exemplo, 101, 102, 201, 202 até 502).', 'danger')
        else:
            unidade_existente_numero = Unidade.query.filter_by(numero=form.numero.data).first()
            unidade_existente_email = Unidade.query.filter_by(email=form.email.data).first()
            unidade_existente_proprietario = Unidade.query.filter_by(nome_proprietario=form.nome_proprietario.data).first()
            
            if unidade_existente_numero:
                flash('Unidade com este número já cadastrada!', 'danger')
            elif unidade_existente_email:
                flash('Já existe uma unidade cadastrada com este email!', 'danger')
            elif unidade_existente_proprietario:
                flash('Já existe uma unidade cadastrada com este proprietário!', 'danger')
            else:
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

@app.route('/remover_unidade/<int:id>', methods=['GET', 'POST'])
def remover_unidade(id):
    unidade = Unidade.query.get_or_404(id)
    
    if tem_encomendas_vinculadas(db,unidade):
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

@app.before_request
def before_request():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
