import streamlit as st
import pandas as pd
import os

# Tentativa de importação segura do Plotly
try:
    import plotly.express as px
except ImportError:
    st.error("O módulo 'plotly' ainda está sendo instalado pelo GitHub. Por favor, aguarde 1 minuto e atualize a página.")
    st.stop()

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. CONFIGURAÇÕES E BANCO DE DADOS ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", "VERDURAS", "LEGUMES", "FRUTAS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    return pd.DataFrame({"Produto": ["Arroz", "Feijão"], "Subclasse": ["BÁSICO", "BÁSICO"]})

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

st.title("🛒 Gestor de Compras Master")
aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA DE CONFIGURAÇÃO ---
with aba_config:
    st.subheader("⚙️ Lista Mestra")
    df_editado = st.data_editor(st.session_state.df_mestre, column_config={"Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES)}, num_rows="dynamic", use_container_width=True)
    if st.button("💾 SALVAR LISTA", use_container_width=True):
        st.session_state.df_mestre = df_editado.drop_duplicates(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Salvo!")
        st.rerun()

# --- ABA NO MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.markdown(f"<div style='background-color:#1E1E1E; padding:15px; border-radius:10px; border: 2px solid #4CAF50; text-align:center;'><h1 style='color:#4CAF50; margin:0;'>Total: R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

    if not st.session_state.carrinho.empty:
        resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
        fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Lançar")
    
    # Reset da busca para limpar o texto automaticamente
    if "reset_key" not in st.session_state: st.session_state.reset_key = 0
    
    # Campo de busca por texto
    busca = st.text_input("Filtrar produto:", key=f"txt_{st.session_state.reset_key}").strip().lower()
    
    lista_p = sorted(st.session_state.df_mestre["Produto"].tolist())
    opcoes = [p for p in lista_p if busca in p.lower()] if busca else lista_p

    escolha = st.selectbox(f"Resultados ({len(opcoes)}):", options=opcoes, index=None, key=f"sel_{st.session_state.reset_key}")

    if escolha:
        sub = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        st.info(f"Subclasse: {sub}")
        c1, c2 = st.columns(2)
        q = c1.number_input("Qtd:", min_value=0.0, value=1.0, step=0.1, key="q")
        p = c2.number_input("Preço:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="p")
        
        if st.button("🛒 CONFIRMAR", use_container_width=True):
            novo = pd.DataFrame([{"Produto": escolha, "Subclasse": sub, "Qtd": q, "Preço": p, "Total": q * p}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
            st.session_state.reset_key += 1 # Isso limpa os campos de busca
            st.rerun()

    st.divider()
    if not st.session_state.carrinho.empty:
        st.write("### 📝 Carrinho")
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        if st.button("🗑️ Esvaziar", use_container_width=True):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
