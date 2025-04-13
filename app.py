import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit_authenticator as stauth

# =============================
# CONFIGURAÇÃO GOOGLE SHEETS
# =============================
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'client_secret.json'  # Suba esse arquivo junto ao app.py no GitHub
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KsMt9JFkTZfRSj0POfHNg07NFb56aA-GJyb3KnkHQbc/edit?usp=sharing'

# Autenticando com Google
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url(SPREADSHEET_URL)
sheet_produto = spreadsheet.worksheet("PRODUTO")
data_produto = sheet_produto.get_all_records()
produtos_df = pd.DataFrame(data_produto)

# =============================
# BANCO LOCAL (SQLITE)
# =============================
conn = sqlite3.connect('pdv.db')
cursor = conn.cursor()

# Inicializar tabelas
cursor.execute('''CREATE TABLE IF NOT EXISTS USUARIO (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS CLIENTE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS PRODUTO (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    grupo TEXT,
    marca TEXT,
    preco REAL NOT NULL,
    estoque INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS VENDA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    usuario_id INTEGER,
    data TEXT,
    forma_pgto TEXT,
    total REAL,
    FOREIGN KEY (cliente_id) REFERENCES CLIENTE(id),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS ITENS_SAIDA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER,
    produto_id INTEGER,
    quantidade INTEGER,
    preco_unitario REAL,
    FOREIGN KEY (venda_id) REFERENCES VENDA(id),
    FOREIGN KEY (produto_id) REFERENCES PRODUTO(id))''')
conn.commit()

# =============================
# AUTENTICAÇÃO
# =============================
config = {
    'credentials': {
        'usernames': {
            'admjesus': {
                'name': 'ADM Jesus',
                'password': stauth.Hasher(['senha123']).generate()[0]
            },
            'vendedor1': {
                'name': 'Vendedor 1',
                'password': stauth.Hasher(['venda2025']).generate()[0]
            },
        }
    },
    'cookie': {
        'name': 'pdv_login_cookie',
        'key': 'assinatura_segura',
        'expiry_days': 1
    },
    'preauthorized': {
        'emails': ["admin@email.com"]
    }
}
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    st.success(f"Bem-vindo, {name}!")
    authenticator.logout("Sair", "sidebar")

    aba = st.sidebar.radio("📌 Menu", ["Cadastrar Produto", "Nova Venda", "Relatório"])

    if aba == "Cadastrar Produto":
        st.header("📦 Cadastro de Produto")
        nome = st.text_input("Nome")
        grupo = st.text_input("Grupo")
        marca = st.text_input("Marca")
        preco = st.number_input("Preço", min_value=0.0)
        estoque = st.number_input("Estoque", min_value=0)
        if st.button("Salvar"):
            cursor.execute("INSERT INTO PRODUTO (nome, grupo, marca, preco, estoque) VALUES (?, ?, ?, ?, ?)", (nome, grupo, marca, preco, estoque))
            conn.commit()
            st.success("Produto salvo!")

    elif aba == "Nova Venda":
        st.header("🧾 Nova Venda")
        clientes = cursor.execute("SELECT id, nome FROM CLIENTE").fetchall()
        produtos = cursor.execute("SELECT id, nome, preco, estoque FROM PRODUTO").fetchall()
        cliente = st.selectbox("Cliente", [f"{c[0]} - {c[1]}" for c in clientes])
        forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "PIX"])

        itens = []
        for i in range(3):
            p = st.selectbox(f"Produto {i+1}", [f"{x[0]} - {x[1]}" for x in produtos], key=f"prod{i}")
            qtd = st.number_input(f"Qtd {i+1}", min_value=0, key=f"qtd{i}")
            if qtd > 0:
                prod = next(x for x in produtos if f"{x[0]} - {x[1]}" == p)
                itens.append((prod[0], qtd, prod[2]))

        if st.button("Finalizar Venda") and itens:
            cliente_id = int(cliente.split(" - ")[0])
            usuario_id = 1
            data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total = sum([q * v for _, q, v in itens])
            cursor.execute("INSERT INTO VENDA (cliente_id, usuario_id, data, forma_pgto, total) VALUES (?, ?, ?, ?, ?)",
                           (cliente_id, usuario_id, data_venda, forma_pgto, total))
            venda_id = cursor.lastrowid
            for pid, qtd, preco in itens:
                cursor.execute("INSERT INTO ITENS_SAIDA (venda_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)", (venda_id, pid, qtd, preco))
                cursor.execute("UPDATE PRODUTO SET estoque = estoque - ? WHERE id = ?", (qtd, pid))
            conn.commit()
            st.success("Venda concluída!")

    elif aba == "Relatório":
        st.header("📊 Relatórios de Venda")
        di = st.date_input("Data Inicial", datetime.now())
        df = st.date_input("Data Final", datetime.now())
        if st.button("Gerar"):
            query = f"SELECT V.id, C.nome AS cliente, U.nome AS usuario, V.data, V.forma_pgto, V.total FROM VENDA V LEFT JOIN CLIENTE C ON V.cliente_id = C.id LEFT JOIN USUARIO U ON V.usuario_id = U.id WHERE date(V.data) BETWEEN '{di}' AND '{df}' ORDER BY V.data DESC"
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                st.dataframe(df)
                total = df['total'].sum()
                st.success(f"Total do período: R$ {total:.2f}")
                st.download_button("📥 Baixar CSV", df.to_csv(index=False).encode(), "relatorio.csv")
            else:
                st.warning("Nenhuma venda no período.")

elif auth_status is False:
    st.error("Credenciais inválidas")
elif auth_status is None:
    st.info("Digite suas credenciais")
