import streamlit as st
import pandas as pd
import requests

# ========================
# PDV OLIVEIRA - APP ONLINE
# ========================

# 🔑 Chave de API (Google API Key + integração futura Auth0)
API_KEY = "AIzaSyDJNAf_HhkW5vJ_tsHvjMi9sQ6Woxvfmis"

# 🌐 Fonte de dados (planilha pública Google Sheets - exportada como XLSX online, simulando múltiplas abas)
PLANILHA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?output=xlsx"

# ============================
# FUNÇÕES DE SUPORTE E CARGA
# ============================
@st.cache_data
def carregar_abas_planilha():
    try:
        dados = pd.read_excel(PLANILHA_URL, sheet_name=None)
        tabelas = {}
        for nome, df in dados.items():
            df.columns = df.columns.str.upper().str.strip()
            tabelas[nome.upper()] = df
        return tabelas
    except Exception as e:
        st.error(f"Erro ao acessar planilha online com múltiplas abas: {e}")
        return {}

# ===================
# TELA DE LOGIN COM VALIDAÇÃO FIXA
# ===================
def login_page():
    st.title("🔐 Acesso ao PDV Oliveira")
    st.markdown("Login baseado em sessão. Integração futura com Auth0 e OAuth2.")

    login_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if login_input == "Oliveira" and senha_input == "PDV":
            st.session_state["logado"] = True
            st.session_state["usuario"] = login_input
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")

# =============
# TELA DE VENDAS
# =============
def vendas_page():
    st.title("🛒 PDV Oliveira - Registro de Vendas")
    tabelas = carregar_abas_planilha()
    df = tabelas.get("PRODUTO", pd.DataFrame())

    if df.empty:
        st.error("A aba 'PRODUTO' não foi encontrada ou está vazia.")
        return

    if 'DESCRICAO' not in df.columns or 'PRECO' not in df.columns:
        st.error("Planilha inválida: coluna 'DESCRICAO' ou 'PRECO' ausente na aba PRODUTO.")
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

# ==================
# TELA DE RELATÓRIOS
# ==================
def relatorios_page():
    st.title("📊 Relatórios de Vendas - PDV Oliveira")
    tabelas = carregar_abas_planilha()
    df = tabelas.get("VENDA", pd.DataFrame())

    if df.empty or 'TOTAL' not in df.columns:
        st.info("Coluna 'TOTAL' não encontrada na aba VENDA.")
        return

    st.subheader("📈 Estatísticas")
    st.metric("Total de Vendas", f"R$ {df['TOTAL'].sum():.2f}")
    if 'ID_CLIENTE' in df.columns:
        st.bar_chart(df.groupby("ID_CLIENTE")["TOTAL"].sum())

# ===================
# INTERFACE PRINCIPAL
# ===================
st.set_page_config(page_title="PDV Oliveira", layout="centered")
st.sidebar.title("📌 Navegação")
pagina = st.sidebar.radio("Escolha a tela", ["Login", "Vendas", "Relatórios"])

# Controle de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Controle de páginas
if pagina == "Login":
    login_page()
elif pagina == "Vendas":
    if st.session_state["logado"]:
        vendas_page()
    else:
        st.warning("Por favor, acesse a tela de login primeiro.")
elif pagina == "Relatórios":
    if st.session_state["logado"]:
        relatorios_page()
    else:
        st.warning("Por favor, acesse a tela de login primeiro.")
