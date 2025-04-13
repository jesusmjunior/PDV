# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib

# ============ Autenticação Nativa ============
USUARIOS = {
    "admjesus": {
        "nome": "ADM Jesus",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

def autenticar(usuario, senha):
    if usuario in USUARIOS:
        hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
        return hash_inserida == USUARIOS[usuario]["senha_hash"]
    return False

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Login - ORION PDV")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ============ URLs REAIS (extraídas do PDF original) ============
urls = {
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv",
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv",
    "forma_pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv",
    "itens_saida": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1245383590&single=true&output=csv"
}

try:
    cliente_df = pd.read_csv(urls["cliente"])
    produto_df = pd.read_csv(urls["produto"])
    grupo_df = pd.read_csv(urls["grupo"])
    marcas_df = pd.read_csv(urls["marcas"])
    forma_pgto_df = pd.read_csv(urls["forma_pgto"])
    venda_df = pd.read_csv(urls["venda"])
    venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
except Exception as e:
    st.error(f"Erro ao carregar planilhas: {e}")

# ============ Menu PDV ============
st.sidebar.title("🔹 Menu PDV")
if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False

menu = st.sidebar.radio("Escolha a opção:", ["Cadastro Produto", "Cadastro Cliente", "Registrar Venda", "Relatórios", "Painel"])

if menu == "Cadastro Produto":
    st.title("📦 Cadastro de Produto")
    with st.form("cad_prod"):
        nome = st.text_input("Nome do Produto")
        grupo = st.selectbox("Grupo", grupo_df["DESCRICAO"].dropna() if 'grupo_df' in locals() else [])
        marca = st.selectbox("Marca", marcas_df["DESCRICAO"].dropna() if 'marcas_df' in locals() else [])
        preco = st.number_input("Preço", min_value=0.0)
        estoque = st.number_input("Estoque", min_value=0)
        enviar = st.form_submit_button("Salvar")
        if enviar:
            st.success("Produto cadastrado com sucesso!")
