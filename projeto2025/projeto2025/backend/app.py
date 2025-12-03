from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, jwt, datetime
from models import criar_tabelas, DB_NAME

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'chave_secreta_para_token_seguro'

criar_tabelas()

# ---------------- FUNÇÕES AUXILIARES ----------------
def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def gerar_token(usuario_id):
    payload = {
        'id': usuario_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verificar_token():
    header = request.headers.get("Authorization")
    if not header:
        return None
    try:
        token = header.split(" ")[1]  # Formato: Bearer <token>
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['id']
    except:
        return None

# ---------------- ROTAS DE AUTENTICAÇÃO ----------------
@app.route('/register', methods=['POST'])
def registrar():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'erro': 'Campos obrigatórios faltando!'}), 400

    senha_hash = generate_password_hash(senha)

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
                       (nome, email, senha_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'erro': 'E-mail já cadastrado!'}), 400
    finally:
        conn.close()

    return jsonify({'mensagem': 'Usuário registrado com sucesso!'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario['senha_hash'], senha):
        token = gerar_token(usuario['id'])
        return jsonify({'token': token})
    else:
        return jsonify({'erro': 'Credenciais inválidas!'}), 401


# ---------------- ROTAS DE TAREFAS ----------------
@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    user_id = verificar_token()
    if not user_id:
        return jsonify({'erro': 'Token inválido!'}), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas WHERE usuario_id = ?", (user_id,))
    tarefas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tarefas)


@app.route("/tarefas", methods=["POST"])
def criar_tarefa():
    user_id = verificar_token()
    if not user_id:
        return jsonify({'erro': 'Token inválido!'}), 401

    data = request.get_json()
    titulo = data.get("titulo")
    if not titulo:
        return jsonify({"erro": "Título é obrigatório"}), 400

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarefas (titulo, usuario_id) VALUES (?, ?)", (titulo, user_id))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Tarefa criada com sucesso!"}), 201


@app.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    user_id = verificar_token()
    if not user_id:
        return jsonify({'erro': 'Token inválido!'}), 401

    data = request.get_json()
    titulo = data.get("titulo")
    concluida = data.get("concluida")

    conn = conectar()
    cursor = conn.cursor()
    if titulo is not None:
        cursor.execute("UPDATE tarefas SET titulo = ? WHERE id = ? AND usuario_id = ?", (titulo, id, user_id))
    if concluida is not None:
        cursor.execute("UPDATE tarefas SET concluida = ? WHERE id = ? AND usuario_id = ?", (int(concluida), id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Tarefa atualizada com sucesso!"})


@app.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    user_id = verificar_token()
    if not user_id:
        return jsonify({'erro': 'Token inválido!'}), 401

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ? AND usuario_id = ?", (id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Tarefa removida com sucesso!"})


if __name__ == "__main__":
    app.run(debug=True)
