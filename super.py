import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra", layout="wide")

# 1. MEMÓRIA DO APLICATIVO
if 'lista_mestra' not in st.session_state:
    st.session_state.lista_mestra = ["Arroz", "Feijão", "Açúcar"] # Itens padrão

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Qtd", "Preço", "Total"])

st.title("🛒 Supermercado Inteligente")

# --- SEÇÃO 1: BOTÃO PARA INSERIR NOVOS NOMES NA LISTA ---
with st.expander("➕ CLIQUE AQUI PARA CADASTRAR PRODUTO NOVO", expanded=False):
    novo_nome = st.text_input("Escreva o nome do produto (ex: Cebola):")
    if st.button("SALVAR NOME NA LISTA"):
        if novo_nome:
            if novo_nome not in st.session_state.lista_mestra:
                st.session_state.lista_mestra.append(novo_nome)
                st.session_state.lista_mestra.sort()
                st.success(f"'{novo_nome}' agora está na sua busca inteligente!")
            else:
                st.warning("Este produto já existe na lista.")

st.divider()

# --- SEÇÃO 2: BUSCA E LANÇAMENTO NO CARRINHO ---
st.write("### 🔍 LOCALIZAR E LANÇAR")
# Aqui é a busca inteligente que você queria
escolha = st.selectbox(
    "Digite o nome para buscar:", 
    st.session_state.lista_mestra, 
    index=None, 
    placeholder="Ex: ceb..."
)

if escolha:
    col_q, col_b = st.columns([1, 1])
    with col_q:
        qnt = st.number_input("Quantidade:", min_value=1.0, step=1.0, key="qtd_lançar")
    with col_b:
        st.write(" ") # Espaçador
        if st.button("INSERIR NO CARRINHO"):
            novo_item = pd.DataFrame([{"Produto": escolha, "Qtd": qnt, "Preço": 0.0, "Total": 0.0}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
            st.rerun()

st.divider()

# --- SEÇÃO 3: TABELA DE PREÇOS ---
total_geral = st.session_state.carrinho["Total"].sum()
st.metric("TOTAL DA COMPRA", f"R$ {total_geral:.2f}")

if not st.session_state.carrinho.empty:
    st.write("📝 Digite o preço abaixo:")
    df_editado = st.data_editor(
        st.session_state.carrinho,
        column_config={
            "Preço": st.column_config.NumberColumn("Preço (R$)", format="%.2f"),
            "Total": st.column_config.NumberColumn("Subtotal", format="R$ %.2f", disabled=True),
        },
        disabled=["Produto", "Total"],
        hide_index=True,
        use_container_width=True
    )
    
    # Recalcula se o preço mudar
    df_editado["Total"] = df_editado["Qtd"] * df_editado["Preço"]
    if not df_editado.equals(st.session_state.carrinho):
        st.session_state.carrinho = df_editado
        st.rerun()

if st.button("Limpar Tudo"):
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Qtd", "Preço", "Total"])
    st.rerun()
