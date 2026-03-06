import streamlit as st
import pandas as pd

# 1. Configuração da página para celular
st.set_page_config(page_title="Compras Família", layout="centered")

# 2. Título visual
st.title("🛒 Controle de Compras")

# 3. Criando um espaço na memória para os itens (temporário)
if 'lista_compras' not in st.session_state:
    st.session_state['lista_compras'] = []

# 4. Cálculos Automáticos
df = pd.DataFrame(st.session_state['lista_compras'])

if not df.empty:
    valor_total_geral = df['Total'].sum()
else:
    valor_total_geral = 0.0

# 5. MOSTRAR VALOR NO TOPO (O que você pediu)
st.metric(label="Gasto Total até agora", value=f"R$ {valor_total_geral:.2f}")

st.divider()

# 6. FORMULÁRIO DE ENTRADA
with st.form("adicionar_item", clear_on_submit=True):
    nome_prod = st.text_input("Produto (ex: Arroz 5kg)")
    
    col1, col2 = st.columns(2)
    with col1:
        classe = st.selectbox("Classe", ["Básico", "Café/Lanches", "Limpeza", "Higiene", "Diversos", "CARNES", "HORTI-FRUTI"])
    
    with col2:
        # Lógica de Subclasses que você pediu
        if classe == "CARNES":
            subclasse = st.selectbox("Subclasse", ["Frango", "Vaca", "Porco", "Peixes"])
        elif classe == "HORTI-FRUTI":
            subclasse = st.selectbox("Subclasse", ["Verduras", "Legumes", "Frutas"])
        else:
            subclasse = st.selectbox("Subclasse", ["Geral"])

    col3, col4 = st.columns(2)
    with col3:
        qtd = st.number_input("Quantidade", min_value=0.1, step=0.1, value=1.0)
    with col4:
        preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")

    botao = st.form_submit_button("➕ Adicionar na Lista")

# 7. Lógica para salvar o item na tabela ao clicar no botão
if botao:
    novo_item = {
        "Produto": nome_prod,
        "Classe": classe,
        "Subclasse": subclasse,
        "Qtd": qtd,
        "Unitario": preco,
        "Total": qtd * preco
    }
    st.session_state['lista_compras'].append(novo_item)
    st.rerun()

# 8. TABELA DE RESUMO E PORCENTAGEM (Sua solicitação)
if not df.empty:
    st.subheader("Resumo por Categoria")
    # Agrupando por subclasse
    resumo = df.groupby('Subclasse')['Total'].sum().reset_index()
    # Calculando a porcentagem do total
    resumo['% do Total'] = (resumo['Total'] / valor_total_geral * 100).round(1).astype(str) + '%'
    
    st.table(resumo)
    
    # Botão para limpar a lista
    if st.button("Limpar Tudo"):
        st.session_state['lista_compras'] = []
        st.rerun()
