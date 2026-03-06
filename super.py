import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra", layout="wide")

# 1. LISTA DE PRODUTOS PARA BUSCA (AQUI ESTÁ O SEGREDO)
if 'lista_mestra' not in st.session_state:
    st.session_state.lista_mestra = sorted([
        "Arroz 5kg", "Feijão 1kg", "Açúcar 1kg", "Café 500g", "Leite Integral",
        "Óleo de Soja", "Detergente", "Sabão em Pó", "Carne Moída (kg)"
    ])

# 2. O CARRINHO
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Qtd", "Preço", "Total"])

st.title("🛒 Minha Compra Inteligente")

# 3. MOSTRAR O TOTAL NO TOPO
total_geral = st.session_state.carrinho["Total"].sum()
st.metric(label="VALOR ACUMULADO", value=f"R$ {total_geral:.2f}")

# 4. A BUSCA QUE VOCÊ PROCURAVA (st.selectbox)
st.write("### Localizar Produto")
escolha = st.selectbox(
    "Clique e digite o nome:", 
    st.session_state.lista_mestra, 
    index=None, 
    placeholder="Ex: Arroz..."
)

if escolha:
    qtd_input = st.number_input(f"Quantidade de {escolha}:", min_value=1.0, step=1.0)
    if st.button("➕ Adicionar ao Carrinho"):
        novo_item = pd.DataFrame([{"Produto": escolha, "Qtd": qtd_input, "Preço": 0.0, "Total": 0.0}])
        st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
        st.rerun()

st.divider()

# 5. EXIBIÇÃO DA TABELA
if not st.session_state.carrinho.empty:
    st.write("### 📝 Itens Lançados:")
    df_editado = st.data_editor(
        st.session_state.carrinho,
        column_config={
            "Preço": st.column_config.NumberColumn("Preço Unitário (R$)", format="%.2f"),
            "Total": st.column_config.NumberColumn("Subtotal", format="R$ %.2f", disabled=True),
        },
        disabled=["Produto", "Total"],
        hide_index=True,
        use_container_width=True
    )
    
    # Recalcula e salva se você mudar o preço
    df_editado["Total"] = df_editado["Qtd"] * df_editado["Preço"]
    if not df_editado.equals(st.session_state.carrinho):
        st.session_state.carrinho = df_editado
        st.rerun()
