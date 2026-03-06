import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra", layout="wide")

# 1. ESTOQUE DE DADOS (Sua lista padrão inicial)
if 'dados' not in st.session_state:
    lista_inicial = [
        {"Produto": "Arroz 5kg", "Classe": "Básico", "Qtd": 1.0, "Preço": 0.0},
        {"Produto": "Feijão 1kg", "Classe": "Básico", "Qtd": 2.0, "Preço": 0.0},
        {"Produto": "Café 500g", "Classe": "Café", "Qtd": 1.0, "Preço": 0.0},
        {"Produto": "Detergente", "Classe": "Limpeza", "Qtd": 1.0, "Preço": 0.0},
        {"Produto": "Frango (kg)", "Classe": "Carnes", "Qtd": 1.0, "Preço": 0.0},
    ]
    st.session_state.dados = pd.DataFrame(lista_inicial)

# CÁLCULOS AUTOMÁTICOS
st.session_state.dados["Total"] = st.session_state.dados["Qtd"] * st.session_state.dados["Preço"]
total_geral = st.session_state.dados["Total"].sum()

# --- INTERFACE DO TOPO ---
st.title("🛒 Minha Compra")
st.metric(label="VALOR ACUMULADO", value=f"R$ {total_geral:.2f}")

# Botão de Resumo que abre e fecha
with st.expander("📊 Clique para ver o Resumo por Classe"):
    if total_geral > 0:
        resumo = st.session_state.dados.groupby('Classe')['Total'].sum().reset_index()
        resumo['%'] = (resumo['Total'] / total_geral * 100).round(1).astype(str) + '%'
        st.table(resumo)
    else:
        st.info("O resumo aparecerá aqui quando você digitar os preços.")

st.divider()

# --- BUSCA E TABELA ---
busca = st.text_input("🔍 Procurar produto na lista...", "")

# Filtrar a lista com base na busca
df_exibir = st.session_state.dados[st.session_state.dados['Produto'].str.contains(busca, case=False)]

st.write("💡 Clique no Preço ou Qtd para editar:")

# Tabela interativa
editado = st.data_editor(
    df_exibir,
    column_config={
        "Preço": st.column_config.NumberColumn("Preço (R$)", format="%.2f", min_value=0.0),
        "Qtd": st.column_config.NumberColumn("Qtd", step=0.1, min_value=0.0),
        "Total": st.column_config.NumberColumn("Subtotal", format="R$ %.2f", disabled=True),
    },
    disabled=["Produto", "Classe", "Total"],
    hide_index=True,
    use_container_width=True
)

# Salva as alterações
st.session_state.dados.update(editado)
