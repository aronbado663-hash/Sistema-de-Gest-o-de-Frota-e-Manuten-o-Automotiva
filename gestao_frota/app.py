from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

# Configuração do banco de dados alterada para SQLite (utiliza o arquivo database.db na raiz)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# MODELOS (Mapeamento ORM - Entidades)
# ==============================================================================

class Motorista(db.Model):
    __tablename__ = 'motoristas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnh = db.Column(db.String(20), unique=True, nullable=False)
    categoria_cnh = db.Column(db.String(5), nullable=False)
    telefone = db.Column(db.String(20))
    veiculos = db.relationship('Veiculo', backref='motorista', lazy=True)

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    quilometragem = db.Column(db.Integer, nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=True)
    manutencoes = db.relationship('Manutencao', backref='veiculo', cascade="all, delete-orphan", lazy=True)

class Mecanico(db.Model):
    __tablename__ = 'mecanicos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(50))
    turno = db.Column(db.String(20))
    manutencoes = db.relationship('Manutencao', backref='mecanico', lazy=True)

class Peca(db.Model):
    __tablename__ = 'pecas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    fabricante = db.Column(db.String(50))
    valor_unitario = db.Column(db.Float, nullable=False)
    qtd_estoque = db.Column(db.Integer, default=0, nullable=False)

class Manutencao(db.Model):
    __tablename__ = 'manutencoes'
    id = db.Column(db.Integer, primary_key=True)
    data_manutencao = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text)
    valor_mao_de_obra = db.Column(db.Float, default=0.0)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    mecanico_id = db.Column(db.Integer, db.ForeignKey('mecanicos.id'), nullable=False)
    itens = db.relationship('ItemManutencao', backref='manutencao', cascade="all, delete-orphan", lazy=True)

class ItemManutencao(db.Model):
    __tablename__ = 'itens_manutencao'
    id = db.Column(db.Integer, primary_key=True)
    manutencao_id = db.Column(db.Integer, db.ForeignKey('manutencoes.id'), nullable=False)
    peca_id = db.Column(db.Integer, db.ForeignKey('pecas.id'), nullable=False)
    quantidade_usada = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    peca = db.relationship('Peca')

# ==============================================================================
# ROTAS DO SISTEMA
# ==============================================================================

@app.route('/')
def index():
    return render_template('index.html')

# ---------- CRUD: VEÍCULOS ----------
@app.route('/veiculos')
def listar_veiculos():
    veiculos = Veiculo.query.all()
    motoristas = Motorista.query.all()
    return render_template('veiculos.html', veiculos=veiculos, motoristas=motoristas)

@app.route('/veiculos/criar', methods=['POST'])
def criar_veiculo():
    novo = Veiculo(
        placa=request.form['placa'],
        modelo=request.form['modelo'],
        ano=int(request.form['ano']),
        quilometragem=int(request.form['quilometragem']),
        motorista_id=request.form.get('motorista_id') or None
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('listar_veiculos'))

@app.route('/veiculos/editar/<int:id>', methods=['POST'])
def editar_veiculo(id):
    v = Veiculo.query.get_or_404(id)
    v.placa = request.form['placa']
    v.modelo = request.form['modelo']
    v.ano = int(request.form['ano'])
    v.quilometragem = int(request.form['quilometragem'])
    v.motorista_id = request.form.get('motorista_id') or None
    db.session.commit()
    return redirect(url_for('listar_veiculos'))

@app.route('/veiculos/deletar/<int:id>', methods=['POST'])
def deletar_veiculo(id):
    v = Veiculo.query.get_or_404(id)
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for('listar_veiculos'))

# ---------- CRUD: MOTORISTAS ----------
@app.route('/motoristas')
def listar_motoristas():
    motoristas = Motorista.query.all()
    return render_template('motoristas.html', motoristas=motoristas)

@app.route('/motoristas/criar', methods=['POST'])
def criar_motorista():
    novo = Motorista(
        nome=request.form['nome'],
        cnh=request.form['cnh'],
        categoria_cnh=request.form['categoria_cnh'],
        telefone=request.form.get('telefone')
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('listar_motoristas'))

@app.route('/motoristas/editar/<int:id>', methods=['POST'])
def editar_motorista(id):
    m = Motorista.query.get_or_404(id)
    m.nome = request.form['nome']
    m.cnh = request.form['cnh']
    m.categoria_cnh = request.form['categoria_cnh']
    m.telefone = request.form.get('telefone')
    db.session.commit()
    return redirect(url_for('listar_motoristas'))

@app.route('/motoristas/deletar/<int:id>', methods=['POST'])
def deletar_motorista(id):
    m = Motorista.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('listar_motoristas'))

# ---------- CRUD: MECÂNICOS ----------
@app.route('/mecanicos')
def listar_mecanicos():
    mecanicos = Mecanico.query.all()
    return render_template('mecanicos.html', mecanicos=mecanicos)

@app.route('/mecanicos/criar', methods=['POST'])
def criar_mecanico():
    novo = Mecanico(
        nome=request.form['nome'],
        especialidade=request.form.get('especialidade'),
        turno=request.form.get('turno')
    )
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('listar_mecanicos'))

@app.route('/mecanicos/editar/<int:id>', methods=['POST'])
def editar_mecanico(id):
    m = Mecanico.query.get_or_404(id)
    m.nome = request.form['nome']
    m.especialidade = request.form.get('especialidade')
    m.turno = request.form.get('turno')
    db.session.commit()
    return redirect(url_for('listar_mecanicos'))

@app.route('/mecanicos/deletar/<int:id>', methods=['POST'])
def deletar_mecanico(id):
    m = Mecanico.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('listar_mecanicos'))

# ---------- CRUD: PEÇAS ----------
@app.route('/pecas')
def listar_pecas():
    pecas = Peca.query.all()
    return render_template('pecas.html', pecas=pecas)

@app.route('/pecas/criar', methods=['POST'])
def criar_peca():
    nova = Peca(
        nome=request.form['nome'],
        fabricante=request.form['fabricante'],
        valor_unitario=float(request.form['valor_unitario']),
        qtd_estoque=int(request.form['qtd_estoque'])
    )
    db.session.add(nova)
    db.session.commit()
    return redirect(url_for('listar_pecas'))

@app.route('/pecas/editar/<int:id>', methods=['POST'])
def editar_peca(id):
    p = Peca.query.get_or_404(id)
    p.nome = request.form['nome']
    p.fabricante = request.form['fabricante']
    p.valor_unitario = float(request.form['valor_unitario'])
    p.qtd_estoque = int(request.form['qtd_estoque'])
    db.session.commit()
    return redirect(url_for('listar_pecas'))

@app.route('/pecas/deletar/<int:id>', methods=['POST'])
def deletar_peca(id):
    p = Peca.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('listar_pecas'))

# ---------- CRUD: MANUTENÇÕES ----------
@app.route('/manutencoes')
def listar_manutencoes():
    manutencoes = Manutencao.query.all()
    veiculos = Veiculo.query.all()
    mecanicos = Mecanico.query.all()
    pecas = Peca.query.all()
    return render_template('manutencoes.html', manutencoes=manutencoes, veiculos=veiculos, mecanicos=mecanicos, pecas=pecas)

@app.route('/manutencoes/criar', methods=['POST'])
def criar_manutencao():
    nova = Manutencao(
        tipo=request.form['tipo'],
        descricao=request.form['descricao'],
        valor_mao_de_obra=float(request.form['valor_mao_de_obra']),
        veiculo_id=int(request.form['veiculo_id']),
        mecanico_id=int(request.form['mecanico_id'])
    )
    db.session.add(nova)
    db.session.flush()

    peca_id = request.form.get('peca_id')
    qtd_usada = int(request.form.get('quantidade_usada', 0))

    if peca_id and qtd_usada > 0:
        peca = Peca.query.get(int(peca_id))
        if peca and peca.qtd_estoque >= qtd_usada:
            item = ItemManutencao(
                manutencao_id=nova.id,
                peca_id=peca.id,
                quantidade_usada=qtd_usada,
                preco_unitario=peca.valor_unitario
            )
            peca.qtd_estoque -= qtd_usada
            db.session.add(item)
        else:
            flash("Quantidade de peças em estoque insuficiente!", "danger")

    db.session.commit()
    return redirect(url_for('listar_manutencoes'))

@app.route('/manutencoes/deletar/<int:id>', methods=['POST'])
def deletar_manutencao(id):
    m = Manutencao.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('listar_manutencoes'))

# ---------- RELATÓRIOS ----------
@app.route('/relatorios/historico-veiculo', methods=['GET', 'POST'])
def relatorio_historico_veiculo():
    veiculo_selecionado = None
    manutencoes = []
    placa_busca = ""

    if request.method == 'POST':
        placa_busca = request.form.get('placa')
        veiculo_selecionado = Veiculo.query.filter_by(placa=placa_busca).first()
        if veiculo_selecionado:
            manutencoes = Manutencao.query.filter_by(veiculo_id=veiculo_selecionado.id).all()

    return render_template('relatorios/historico_veiculo.html', 
                           veiculo=veiculo_selecionado, 
                           manutencoes=manutencoes, 
                           placa_busca=placa_busca)

@app.route('/relatorios/estoque-critico')
def relatorio_estoque_critico():
    limite_minimo = int(request.args.get('limite', 5))
    pecas_criticas = Peca.query.filter(Peca.qtd_estoque <= limite_minimo).all()
    return render_template('relatorios/estoque_critico.html', pecas=pecas_criticas, limite=limite_minimo)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco database.db e as tabelas automaticamente
    app.run(debug=True)