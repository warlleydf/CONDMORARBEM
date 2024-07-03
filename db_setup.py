from app import app, db  # Certifique-se de importar 'app' e 'db'
from app import Unidade

# Dados fictícios para as unidades
unidades = [
    {'numero': '101', 'nome_proprietario': 'João Silva', 'telefone': '123456789', 'email': 'joao@example.com'},
    {'numero': '102', 'nome_proprietario': 'Maria Souza', 'telefone': '987654321', 'email': 'maria@example.com'},
    {'numero': '201', 'nome_proprietario': 'Pedro Santos', 'telefone': '123123123', 'email': 'pedro@example.com'},
    {'numero': '301', 'nome_proprietario': 'Ana Oliveira', 'telefone': '321321321', 'email': 'ana@example.com'},
    {'numero': '302', 'nome_proprietario': 'Carlos Pereira', 'telefone': '456456456', 'email': 'carlos@example.com'},
    {'numero': '401', 'nome_proprietario': 'Paula Costa', 'telefone': '654654654', 'email': 'paula@example.com'},
    {'numero': '402', 'nome_proprietario': 'Marcos Lima', 'telefone': '789789789', 'email': 'marcos@example.com'},
    {'numero': '501', 'nome_proprietario': 'Julia Martins', 'telefone': '987987987', 'email': 'julia@example.com'},
    {'numero': '502', 'nome_proprietario': 'Lucas Alves', 'telefone': '321654987', 'email': 'lucas@example.com'}
]

# Inicializar o banco de dados e adicionar os dados fictícios
with app.app_context():
    db.create_all()
    for unidade in unidades:
        nova_unidade = Unidade(numero=unidade['numero'], nome_proprietario=unidade['nome_proprietario'], telefone=unidade['telefone'], email=unidade['email'])
        db.session.add(nova_unidade)
    db.session.commit()
    print("Banco de dados inicializado com sucesso")
