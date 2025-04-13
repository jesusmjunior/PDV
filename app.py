import streamlit as st
import pandas as pd
import requests

# ========================
# PDV OLIVEIRA - APP BASE
# ========================

# 🔑 Chave de API (para integração futura com Auth0 / Sheets / Drive)
API_KEY = "AIzaSyDJNAf_HhkW5vJ_tsHvjMi9sQ6Woxvfmis"

# 🌐 Fonte de dados principal (planilha CSV pública do Google Sheets)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?output=csv"

# ============================
# FUNÇÕES DE SUPORTE E CARGA
# ============================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.upper().str.strip()  # Normaliza nomes de colunas
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

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

# ================
# TELA DE VENDAS
# ================
def vendas_page():
    st.title("🛒 PDV Oliveira - Registro de Vendas")
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhum dado carregado da planilha.")
    elif 'DESCRICAO' not in df.columns or 'PRECO' not in df.columns:
        st.error("Planilha inválida: colunas 'DESCRICAO' ou 'PRECO' ausentes.")
    else:
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
    df = carregar_dados()
    if df.empty:
        st.warning("Sem dados para exibir.")
    elif 'TOTAL' not in df.columns or 'DESCRICAO' not in df.columns:
        st.info("Colunas necessárias para relatório não encontradas.")
    else:
        st.subheader("📈 Estatísticas")
        st.metric("Total de Vendas", f"R$ {df['TOTAL'].sum():.2f}")
        st.bar_chart(df.groupby("DESCRICAO")["TOTAL"].sum())

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
