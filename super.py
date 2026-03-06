import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- SUBCLASSES ---
OPCOES_SUBCLASSES = [
    "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
    "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
    "VERDURAS", "LEGUMES", "FRUTAS"
]

# 1. BANCO DE DATOS
if 'df_mestre' not in st.session_state:
    lista_inicial = ["Arroz", "Feijão", "Açúcar", "Café", "Leite", "Óleo", "Cebola", "Tomate"]
    st.session_state.df_mestre = pd.DataFrame({
        "Produto": sorted(lista_inicial),
        "Subclasse": "BÁSICO",
        "Detalhe": "Padrão"
    })

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

st.title("🛒 Gestor de Compras")

aba_mercado, aba_cadastro = st.tabs(["🛍️ No Mercado", "📝 Cadastrar/Editar"])

# --- ABA 2: CADASTRO ---
with aba_cadastro:
    st.subheader("Adicionar NOVO item")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1: n_nome = st.text_input("Produto:")
        with c2: n_sub = st.selectbox("Subclasse:", OPCOES_SUBCLASSES)
        if st.button("➕ SALVAR NA LISTA"):
            if n_nome:
                novo_df = pd.DataFrame([{"Produto": n_nome, "Subclasse": n_sub, "Detalhe": "Padrão"}])
                st.session_state.df_mestre = pd.concat([st.session_state.df_mestre, novo_df], ignore_index=True).drop_duplicates(subset=['Produto'])
                st.rerun()

    st.data_editor(st.session_state.df_mestre, column_config={"Subclasse": st.column_config.SelectboxColumn(options=OPCOES_SUBCLASSES)}, num_rows="dynamic", use_container_width=True)

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    total_geral = st.session_state.carrinho["Total"].sum()
    st.metric("TOTAL NO CARRINHO", f"R$ {total_geral:.2f}")

    # FORMULÁRIO PARA PERMITIR O "ENTER"
    with st.form("insercao_rapida", clear_on_submit=True):
        st.subheader("Lançar Item")
        opcoes_nomes = st.session_state.df_mestre["Produto"].tolist()
        escolha = st.selectbox("Produto:", options=opcoes_nomes, index=None)

        col_q, col_p = st.columns(2)
        with col_q:
            # Quantidade como texto para facilitar a limpeza ou numero simples
            qtd_input = st.number_input("Qtd:", min_value=0.0, value=1.0, step=0.1)
        with col_p:
            # O truque do valor 0.00: deixamos ele como "value=0.0" 
            preco_input = st.number_input("Preço Unitário:", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        
        # O botão submit permite que o ENTER do teclado funcione
        botao_inserir = st.form_submit_button("🛒 INSERIR (OU APERTE ENTER)")

        if botao_inserir and escolha:
            sub_auto = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
            novo_item = pd.DataFrame([{
                "Produto": escolha, "Subclasse": sub_auto, "Qtd": qtd_input, "Preço": preco_input, "Total": qtd_input * preco_input
            }])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        # TABELA DO CARRINHO
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        
        # QUADRO DE RESUMO COM PERCENTUAL
        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            # Cálculo da Porcentagem
            resumo["%"] = (resumo["Total"] / total_geral * 100).round(1)
            
            # Formatação para exibição
            resumo_copy = resumo.copy()
            resumo_copy["Total"] = resumo_copy["Total"].apply(lambda x: f"R$ {x:,.2f}")
            resumo_copy["%"] = resumo_copy["%"].apply(lambda x: f"{x}%")
            
            st.table(resumo_copy)

        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
