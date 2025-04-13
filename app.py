import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit_auth0 as stauth

# ========================
# CONFIGURAÇÃO AUTH0
# ========================
AUTH0_CLIENT_ID = "145009781337-065tk1gp2jbo5rl7m18klch1s4m5t1ir.apps.googleusercontent.com"
AUTH0_DOMAIN = "zeta-bonbon-424022-b5.us.auth0.com"
AUTH0_CLIENT_SECRET = "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"

# ========================
# GOOGLE DRIVE CONFIG
# ========================
CRED_PATH = "client_secret_145009781337-065tk1gp2jbo5rl7m18klch1s4m5t1ir.apps.googleusercontent.com (1).json"
NOME_PLANILHA = "SIS_PDV_PLANILHA"

# ============================
# FUNÇÃO: AUTENTICAR USUÁRIO VIA AUTH0
# ============================
def autenticar_usuario():
    auth0 = stauth.Auth0(
        client_id=AUTH0_CLIENT_ID,
        domain=AUTH0_DOMAIN,
        client_secret=AUTH0_CLIENT_SECRET,
        redirect_uri="http://localhost:8501",
        scope="openid profile email"
    )
    user_info = auth0.login_button("🔐 Entrar com Auth0")
    return user_info

# ============================
# FUNÇÃO: LER DADOS DO GOOGLE SHEETS
# ============================
def carregar_abas_drive():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, scope)
    client = gspread.authorize(creds)
    planilha = client.open(NOME_PLANILHA)

    abas = {aba.title.upper(): pd.DataFrame(aba.get_all_records()) for aba in planilha.worksheets()}
    for nome, df in abas.items():
        abas[nome].columns = [col.upper().strip() for col in df.columns]
    return abas

# ============================
# TELA DE VENDAS
# ============================
def vendas_page():
    st.title("🛒 PDV Oliveira - Registro de Vendas")
    tabelas = carregar_abas_drive()
    df = tabelas.get("PRODUTO", pd.DataFrame())

    if df.empty:
        st.error("A aba 'PRODUTO' não foi encontrada ou está vazia.")
        return

    if 'DESCRICAO' not in df.columns or 'PRECO' not in df.columns:
        st.error("Coluna 'DESCRICAO' ou 'PRECO' ausente em PRODUTO.")
        return

    st.subheader("📦 Produtos disponíveis")
    st.dataframe(df)

    st.subheader("🧾 Nova Venda")
    produto = st.selectbox("Produto", df['DESCRICAO'].unique())
    qtd = st.number_input("Quantidade", min_value=1, value=1)
    preco = df[df['DESCRICAO'] == produto]['PRECO'].values[0]
    total = qtd * preco
    st.write(f"💰 Total: R$ {total:.2f}")

    if st.button("Registrar Venda"):
        st.success("Venda registrada (simulada).")

# ============================
# TELA DE RELATÓRIOS
# ============================
def relatorios_page():
    st.title("📊 Relatórios de Vendas")
    tabelas = carregar_abas_drive()
    df = tabelas.get("VENDA", pd.DataFrame())

    if df.empty or 'TOTAL' not in df.columns:
        st.warning("Coluna 'TOTAL' não encontrada em VENDA.")
        return

    st.metric("Total de Vendas", f"R$ {df['TOTAL'].sum():.2f}")
    if 'ID_CLIENTE' in df.columns:
        st.bar_chart(df.groupby("ID_CLIENTE")["TOTAL"].sum())

# ============================
# TELA DE CLIENTES
# ============================
def clientes_page():
    st.title("👥 Clientes Cadastrados")
    tabelas = carregar_abas_drive()
    df = tabelas.get("CLIENTE", pd.DataFrame())

    if df.empty:
        st.warning("A aba CLIENTE não foi encontrada.")
        return

    st.dataframe(df)
    st.text_input("🔍 Buscar cliente por nome")
    st.button("➕ Adicionar novo cliente (em breve)")

# ============================
# INTERFACE PRINCIPAL
# ============================
st.set_page_config(page_title="PDV Oliveira", layout="centered")
st.sidebar.title("📌 Navegação")
pagina = st.sidebar.radio("Escolha a tela", ["Vendas", "Relatórios", "Clientes"])

# ============================
# AUTENTICAÇÃO E CONTROLE DE ACESSO
# ============================
if "usuario" not in st.session_state:
    user = autenticar_usuario()
    if user:
        st.session_state["usuario"] = user["email"]
    else:
        st.stop()

# ============================
# ROTEAMENTO DE PÁGINAS
# ============================
if pagina == "Vendas":
    vendas_page()
elif pagina == "Relatórios":
    relatorios_page()
elif pagina == "Clientes":
    clientes_page()
