from flask import Flask, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar o flash para mensagens

# Configura as credenciais do Firebase
cred = credentials.Certificate("script/papelaria-dela-firebase-adminsdk-dvfeh-b931973ed8.json")
firebase_admin.initialize_app(cred)

# Conecta ao Firestore
db = firestore.client()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Lógica para vender produto, visualizar estoque, etc.
        pass
    else:
        return render_template('index.html')

@app.route('/index2', methods=['GET'])
def index2():
    return render_template('index2.html')

@app.route('/vender_produto', methods=['POST'])
def vender_produto():
    produto = request.form['produtoVender']
    quantidade = int(request.form['quantidadeVender'])
    valor_pago = float(request.form['valorPago'])

    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_data = produto_doc.to_dict()
        novo_estoque = produto_data['estoque'] - quantidade
        if novo_estoque >= 0:
            produto_ref.update({'estoque': novo_estoque})
            flash('Produto vendido com sucesso!', 'success')
        else:
            flash('Estoque insuficiente!', 'error')
    else:
        flash('Produto não encontrado!', 'error')

    return redirect(url_for('index'))

@app.route('/visualizar_estoque_individual', methods=['POST'])
def visualizar_estoque_individual():
    produto = request.form['produto']
    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_data = produto_doc.to_dict()
        flash(f"Estoque do produto {produto}: {produto_data['estoque']}", 'success')
    else:
        flash('Produto não encontrado!', 'error')

    return redirect(url_for('index'))

@app.route('/visualizar_estoque_geral', methods=['POST'])
def visualizar_estoque_geral():
    produtos_ref = db.collection('produtos')
    produtos = produtos_ref.stream()
    estoque_geral = {produto.id: produto.to_dict()['estoque'] for produto in produtos}
    
    flash(f"Estoque geral: {estoque_geral}", 'success')
    return redirect(url_for('index'))

@app.route('/atualizar_estoque', methods=['POST'])
def atualizar_estoque():
    produto = request.form['produtoAtualizar']
    novo_estoque = int(request.form['novoEstoque'])
    
    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_ref.update({'estoque': novo_estoque})
        flash('Estoque atualizado com sucesso!', 'success')
    else:
        flash('Produto não encontrado!', 'error')

    return redirect(url_for('index'))

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    produto = request.form['novoProduto']
    estoque = int(request.form['estoqueProduto'])
    preco = float(request.form['precoProduto'])
    
    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        flash('Produto já existe!', 'error')
    else:
        produto_ref.set({'estoque': estoque, 'preco': preco})
        flash('Produto adicionado com sucesso!', 'success')

    return redirect(url_for('index'))

@app.route('/remover_produto', methods=['POST'])
def remover_produto():
    produto = request.form['produtoRemover']
    
    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_ref.delete()
        flash('Produto removido com sucesso!', 'success')
    else:
        flash('Produto não encontrado!', 'error')

    return redirect(url_for('index'))

@app.route('/ver_lucro', methods=['POST'])
def ver_lucro():
    preco_venda = float(request.form['precoVenda'])
    preco_compra = float(request.form['precoCompra'])
    quantidade = int(request.form['quantidadeVendida'])
    
    lucro = (preco_venda - preco_compra) * quantidade
    flash(f'Lucro: {lucro:.2f}', 'success')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
