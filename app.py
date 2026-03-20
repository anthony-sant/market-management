from flask import Flask, render_template, request, redirect
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
import enum

app = Flask(__name__)
Scss(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

class Unidade(enum.Enum):
    KG = "kg"
    UN = "un"

class Produto(db.Model):
    MARGEM_LUCRO = 0.25
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(14), nullable=False)
    vol_estoque = db.Column(db.Float, default=0)
    preco_custo = db.Column(db.Numeric(precision = 9, scale = 2), nullable=False)
    unidade = db.Column(db.Enum(Unidade), nullable=False)

    def get_valor_venda(self):
        return float(self.preco_custo) * (1+float(self.MARGEM_LUCRO))


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/estoque", methods=["GET"])
def estoque():
    produtos = Produto.query.order_by(Produto.nome).all()
    return render_template('estoque.html', produtos=produtos)

@app.route("/estoque/cadastrar-produto", methods=["GET","POST"])
def cadastrar_produto():
    if request.method == "POST":
        nome_produto = request.form['nome']
        codigo_produto = request.form['codigo']
        vol_estoque_produto = request.form['vol_estoque']
        unidade_medida_produto = request.form['unidade_medida']
        preco_produto = request.form['preco_custo']
        new_produto = Produto(
            nome = nome_produto, 
            preco_custo = preco_produto,
            codigo = codigo_produto, 
            vol_estoque = vol_estoque_produto, 
            unidade = unidade_medida_produto)
        try:
            db.session.add(new_produto)
            db.session.commit()
            return redirect("/estoque")
        except Exception as e:
            return f"Error{e}"
    else:
        return render_template("cadastrar-produto.html")
    
@app.route("/estoque/editar-produto/<int:id>", methods = ["GET", "POST"])
def update_produto(id):
    produto = Produto.query.get_or_404(id)
    if request.method == "POST":
            produto.nome = request.form['nome']
            produto.vol_estoque = request.form['vol_estoque']
            produto.preco_custo = request.form['preco_custo']
            try:
                db.session.commit()
                return redirect("/estoque")
            except Exception as e:
                print(f"Error{e}")
                return "Error"
    else:
        return render_template("editar.html", produto=produto)
    
@app.route("/estoque/remover-produto/<int:id>", methods = ["GET", "POST"])
def delete_produto(id):
    produto_to_delete = Produto.query.get_or_404(id)
    try:
        db.session.delete(produto_to_delete)
        db.session.commit()
        return redirect("/estoque")
    except Exception as e:
        return f"Error{e}"


if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)