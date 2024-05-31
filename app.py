from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore

app = Flask(__name__)
CORS(app)

carrinho = []

def init_firebase():
    cred = firebase_admin.credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)

if not firebase_admin._apps: 
    init_firebase()

# Conecta ao Firestore
db = firestore.client()

from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')


@app.route('/mostrar_formulario/<form_id>', methods=['GET'])
def mostrar_formulario(form_id):
    global carrinho
    
    forms = ['formVenderProduto', 'formAdicionarProduto', 'formRemoverProduto']
    for form in forms:
        if form == form_id:
            continue
        carrinho = []
        
    return jsonify({'message': f'Formulário {form_id} mostrado com sucesso.'}), 200

@app.route('/atualizar_estoque', methods=['POST'])
def atualizar_estoque():
    data = request.get_json()
    produto = data['produto']
    novo_estoque = int(data['novo_estoque'])

    produto_ref = db.collection('produtos').document(produto)
    produto_ref.update({'estoque': novo_estoque})

    return jsonify({'message': 'Estoque atualizado com sucesso!'}), 200


@app.route('/vender_produto', methods=['POST'])
def vender_produto():
    global carrinho
    
    data = request.get_json()
    carrinho = data['carrinho']
    valor_pago = float(data['valor_pago'])

    total_compra = sum(item['quantidade'] * item['preco'] for item in carrinho)
    lucro = total_compra * 0.1

    troco = valor_pago - total_compra

    # Atualizar estoque no banco de dados Firebase
    for item in carrinho:
        produto_ref = db.collection('produtos').document(item['produto'])
        produto_doc = produto_ref.get()
        estoque_atual = produto_doc.to_dict()['estoque']
        novo_estoque = estoque_atual - item['quantidade']
        produto_ref.update({'estoque': novo_estoque})

    carrinho = []  # Limpar carrinho após finalizar compra

    return jsonify({'message': 'Compra finalizada com sucesso!', 'total_compra': total_compra, 'troco': troco, 'lucro': lucro}), 200

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    data = request.get_json()
    produto = data['produto']
    estoque = int(data['estoque'])
    preco = float(data['preco'])

    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if not produto_doc.exists:
        produto_ref.set({'estoque': estoque, 'preco': preco})
        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200
    else:
        return jsonify({'error': 'Produto já existe!'}), 400

# Rota para remover um produto
@app.route('/remover_produto', methods=['DELETE'])
def remover_produto():
    data = request.get_json()
    produto = data['produto']

    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_ref.delete()
        return jsonify({'message': 'Produto removido com sucesso!'}), 200
    else:
        return jsonify({'error': 'Produto não encontrado!'}), 404

@app.route('/visualizar_estoque_individual', methods=['POST'])
def visualizar_estoque_individual():
    data = request.get_json()
    produto = data['produto']
    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_data = produto_doc.to_dict()
        return jsonify({'estoque': produto_data['estoque'], 'preco': produto_data['preco']}), 200
    else:
        return jsonify({'error': 'Produto não encontrado!'}), 404

@app.route('/visualizar_estoque_geral', methods=['GET'])
def visualizar_estoque_geral():
    produtos_ref = db.collection('produtos')
    produtos = produtos_ref.stream()
    estoque_geral = {}
    for produto in produtos:
        produto_data = produto.to_dict()
        estoque_geral[produto.id] = {'estoque': produto_data['estoque'], 'preco': produto_data['preco']}
    
    return jsonify({'estoque_geral': estoque_geral}), 200
@app.route('/calcular_lucro_total', methods=['GET'])
def calcular_lucro_total():
    produtos_ref = db.collection('produtos').stream()
    lucro_total = 0

    for produto in produtos_ref:
        produto_data = produto.to_dict()
        preco_compra = produto_data.get('preco_compra', 0)  # Preço de compra padrão é 0 se não definido
        preco_venda = produto_data.get('preco_venda', 0)    # Preço de venda padrão é 0 se não definido
        lucro_total += (preco_venda - preco_compra)

    return jsonify({'lucro_total': lucro_total}), 200
if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '_main_':
    app.run(debug=True)