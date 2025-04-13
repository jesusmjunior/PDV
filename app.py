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
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# ===================
# TELA DE LOGIN FAKE
# ===================
def login_page():
    st.title("🔐 Acesso ao PDV Oliveira")
    st.markdown("""
        ⚠️ Autenticação desativada para modo de demonstração.
        
        Sistema em desenvolvimento para integrar com **Auth0** e segurança baseada em token OAuth2.
    """)
    if st.button("Entrar no sistema (demo)"):
        st.session_state["logado"] = True
        st.session_state["usuario"] = "Administrador"

# ================
# TELA DE VENDAS
# ================
def vendas_page():
    st.title("🛒 PDV Oliveira - Registro de Vendas")
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhum dado carregado da planilha.")
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
    else:
        st.subheader("📈 Estatísticas")
        if 'TOTAL' in df.columns:
            st.metric("Total de Vendas", f"R$ {df['TOTAL'].sum():.2f}")
            st.bar_chart(df.groupby("DESCRICAO")["TOTAL"].sum())
        else:
            st.info("Coluna 'TOTAL' não encontrada para relatório.")

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
