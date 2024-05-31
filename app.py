from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import firestore

from teste_firebase import init_firebase

app = Flask(__name__)

if not firebase_admin._apps: 
    init_firebase()

# Conecta ao Firestore
db = firestore.client()
app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return "API está online."

@app.route('/vender_produto', methods=['POST'])
def vender_produto():
    data = request.get_json()
    produto = data['produto']
    quantidade = int(data['quantidade'])
    valor_pago = float(data['valor_pago'])

    produto_ref = db.collection('produtos').document(produto)
    produto_doc = produto_ref.get()

    if produto_doc.exists:
        produto_data = produto_doc.to_dict()
        novo_estoque = produto_data['estoque'] - quantidade
        if novo_estoque >= 0:
            produto_ref.update({'estoque': novo_estoque})
            return jsonify({'message': 'Produto vendido com sucesso!'}), 200
        else:
            return jsonify({'error': 'Estoque insuficiente!'}), 400
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
        return jsonify({'estoque': produto_data['estoque']}), 200
    else:
        return jsonify({'error': 'Produto não encontrado!'}), 404

@app.route('/visualizar_estoque_geral', methods=['GET'])
def visualizar_estoque_geral():
    produtos_ref = db.collection('produtos')
    produtos = produtos_ref.stream()
    estoque_geral = {}
    for produto in produtos:
        produto_data = produto.to_dict()
        estoque_geral[produto.id] = produto_data['estoque']
    
    return jsonify({'estoque_geral': estoque_geral}), 200


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



if __name__ == '__main__':
    app.run(debug=True)
