from flask import Flask, app, render_template, request, redirect, url_for, flash
import firebase_admin
from firebase_admin import firestore
from teste_firebase import init_firebase


if not firebase_admin._apps: 
    init_firebase()
# Conecta ao Firestore
db = firestore.client()




@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/visualizar_estoque_geral', methods=['POST', 'GET'])
def visualizar_estoque_geral():
    produtos_ref = db.collection('produtos')
    produtos = produtos_ref.stream()
    estoque_geral = {}
    for produto in produtos:
        produto_data = produto.to_dict()
        estoque_geral[produto.id] = produto_data['estoque']
    
    flash(f"Estoque geral: {estoque_geral}", 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)