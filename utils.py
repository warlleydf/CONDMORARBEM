import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import flash
from models import Unidade, Encomenda

def enviar_email(db, destinatario, assunto, corpo):
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

def obter_email_proprietario(db, numero_unidade):
    unidade = db.session.query(Unidade).filter_by(numero=numero_unidade).first()
    return unidade.email if unidade else None

def tem_encomendas_vinculadas(db, unidade):
    try:
        encomendas_vinculadas = db.session.query(Encomenda).filter_by(unidade_numero=unidade.numero).first()
        return encomendas_vinculadas is not None
    except Exception as e:
        db.session.rollback()
        raise e

def validar_numero_unidade(numero):
    try:
        andar = int(numero[:-2])
        unidade = int(numero[-2:])
        if andar < 1 or andar > 5 or unidade not in (1, 2):
            return False
        return True
    except ValueError:
        return False