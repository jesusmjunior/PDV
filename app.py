import streamlit as st
import pandas as pd
import requests

# ========================
# PDV OLIVEIRA - APP BASE
# ========================

# 🔑 Chave de API (para integração futura com Auth0 / Sheets / Drive)
API_KEY = "AIzaSyDJNAf_HhkW5vJ_tsHvjMi9sQ6Woxvfmis"

# 📄 Planilha .xlsx com múltiplas tabelas relacionais (já enviada)
EXCEL_PATH = "/mnt/data/SIS_PDV_PLANILHA (1).xlsx"

# ============================
# FUNÇÕES DE SUPORTE E CARGA
# ============================
@st.cache_data
def carregar_planilhas():
    try:
        dados = pd.read_excel(EXCEL_PATH, sheet_name=None)
        for nome, df in dados.items():
            dados[nome] = df.copy()
            dados[nome].columns = df.columns.str.upper().str.strip()
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return {}

# ===================
# TELA DE LOGIN COM VALIDAÇÃO FIXA
# ===================
def login_page():
    st.title("🔐 Acesso ao PDV Oliveira")
    st.markdown("Entre com suas credenciais para continuar.")

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
    data = carregar_planilhas()
    if not data:
        st.warning("Planilha não carregada.")
        return

    df_prod = data.get("PRODUTO", pd.DataFrame())
    if df_prod.empty or 'DESCRICAO' not in df_prod.columns or 'PRECO' not in df_prod.columns:
        st.error("Planilha inválida: coluna 'DESCRICAO' ou 'PRECO' ausente em PRODUTO.")
        return

    st.subheader("📦 Produtos disponíveis")
    st.dataframe(df_prod)

    st.subheader("🧾 Nova Venda")
    produto = st.selectbox("Produto", df_prod['DESCRICAO'].unique())
    qtd = st.number_input("Quantidade", min_value=1, value=1)
    preco = df_prod[df_prod['DESCRICAO'] == produto]['PRECO'].values[0]
    total = qtd * preco
    st.write(f"💰 Total: R$ {total:.2f}")

    if st.button("Registrar Venda"):
        st.success("Venda registrada (simulada).")

# ==================
# TELA DE RELATÓRIOS
# ==================
def relatorios_page():
    st.title("📊 Relatórios de Vendas - PDV Oliveira")
    data = carregar_planilhas()
    if not data:
        st.warning("Sem dados para exibir.")
        return

    df_vendas = data.get("VENDA", pd.DataFrame())
    df_prod = data.get("PRODUTO", pd.DataFrame())

    if df_vendas.empty or 'TOTAL' not in df_vendas.columns:
        st.info("Coluna 'TOTAL' não encontrada na planilha VENDA.")
    else:
        st.subheader("📈 Estatísticas")
        st.metric("Total de Vendas", f"R$ {df_vendas['TOTAL'].sum():.2f}")
        if 'ID_PRODUTO' in df_prod.columns and 'DESCRICAO' in df_prod.columns:
            st.bar_chart(df_prod.set_index("DESCRICAO")["PRECO"])

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
