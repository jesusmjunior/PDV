import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib

# ============ Função de Autenticação Simples ============
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
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ============ Dados ============
urls = {
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "forma_pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv",
    "itens_saida": "https://docs.google.com/spreadsheets/d/e/2PACX-1v...&output=csv"
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

# ============ Menu Principal ============
st.sidebar.title("🔹 Menu PDV")
if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.experimental_rerun()

menu = st.sidebar.radio("Escolha a opção:", ["Cadastro Produto", "Cadastro Cliente", "Registrar Venda", "Relatórios", "Painel"])

if menu == "Cadastro Produto":
    st.title("📦 Cadastro de Produto")
    with st.form("cad_prod"):
        nome = st.text_input("Nome do Produto")
        grupo = st.selectbox("Grupo", grupo_df["DESCRICAO"].dropna())
        marca = st.selectbox("Marca", marcas_df["DESCRICAO"].dropna())
        preco = st.number_input("Preço", min_value=0.0)
        estoque = st.number_input("Estoque", min_value=0)
        if st.form_submit_button("Salvar"):
            st.success("Produto cadastrado com sucesso!")

elif menu == "Cadastro Cliente":
    st.title("👤 Cadastro de Cliente")
    with st.form("cad_cliente"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        if st.form_submit_button("Salvar"):
            st.success("Cliente cadastrado com sucesso!")

elif menu == "Registrar Venda":
    st.title("🧾 Nova Venda")
    with st.form("venda"):
        cliente = st.selectbox("Cliente", cliente_df["NOME"].dropna())
        pgto = st.selectbox("Forma de Pagamento", forma_pgto_df["DESCRICAO"].dropna())
        st.markdown("---")
        itens = []
        for i in range(3):
            prod = st.selectbox(f"Produto {i+1}", produto_df["DESCRICAO"], key=f"prod_{i}")
            qtd = st.number_input(f"Qtd {i+1}", min_value=0, key=f"qtd_{i}")
            if qtd > 0:
                preco = float(produto_df.loc[produto_df["DESCRICAO"] == prod, "PRECO"].values[0])
                itens.append({"produto": prod, "qtd": qtd, "preco": preco, "total": qtd * preco})
        if st.form_submit_button("Finalizar Venda") and itens:
            total = sum(i["total"] for i in itens)
            st.success(f"Venda registrada com total de R$ {total:.2f}")

elif menu == "Relatórios":
    st.title("📊 Relatório de Vendas")
    col1, col2 = st.columns(2)
    ini = col1.date_input("Início", datetime.today())
    fim = col2.date_input("Fim", datetime.today())
    filtro = (venda_df['DATA'].dt.date >= ini) & (venda_df['DATA'].dt.date <= fim)
    rel = venda_df[filtro]
    if not rel.empty:
        st.dataframe(rel)
        total = rel["TOTAL"].sum()
        st.metric("Total do Período", f"R$ {total:,.2f}")
    else:
        st.warning("Nenhuma venda encontrada no período.")

elif menu == "Painel":
    st.title("📈 Painel Financeiro")
    try:
        import plotly.express as px
        pgto_group = venda_df.groupby("ID_FORMA_PGTO")["TOTAL"].sum().reset_index()
        fig_pgto = px.bar(pgto_group, x="ID_FORMA_PGTO", y="TOTAL", title="Total por Forma de Pagamento")
        st.plotly_chart(fig_pgto)

        diario = venda_df.groupby(venda_df["DATA"].dt.date)["TOTAL"].sum().reset_index()
        fig_dia = px.line(diario, x="DATA", y="TOTAL", title="Evolução Diária")
        st.plotly_chart(fig_dia)

        st.metric("Total Geral de Vendas", f"R$ {venda_df['TOTAL'].sum():,.2f}")
    except Exception as e:
        st.error("Erro ao gerar gráficos. Execute: pip install plotly")
