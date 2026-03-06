import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. DEFINIÇÃO FIXA DAS SUBCLASSES ---
OPCOES_SUBCLASSES = [
    "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
    "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
    "VERDURAS", "LEGUMES", "FRUTAS"
]

# --- 2. INICIALIZAÇÃO DA MEMÓRIA (SÓ RODA 1 VEZ) ---
if 'df_mestre' not in st.session_state:
    # Seus itens iniciais
    itens_padrao = ["Arroz", "Feijão", "Açúcar", "Café", "Leite", "Óleo", "Cebola", "Tomate"]
    st.session_state.df_mestre = pd.DataFrame({
        "Produto": sorted(itens_padrao),
        "Subclasse": ["BÁSICO"] * len(itens_padrao),
        "Detalhe": ["Padrão"] * len(itens_padrao)
    })

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 3. ESTRUTURA DO APP ---
st.title("🛒 Gestor de Compras")

aba_mercado, aba_cadastro = st.tabs(["🛍️ No Mercado", "📝 Cadastrar/Editar"])

# --- ABA 2: CADASTRO (ONDE VOCÊ ALIMENTA A LISTA) ---
with aba_cadastro:
    st.subheader("Adicionar NOVO item")
    
    # Campos de entrada simples (sem form aqui para não travar)
    c1, c2 = st.columns(2)
    with c1:
        n_nome = st.text_input("Nome do Produto (ex: Maionese):", key="input_nome_novo")
    with c2:
        n_sub = st.selectbox("Escolha a Subclasse:", OPCOES_SUBCLASSES, key="select_sub_nova")
    
    if st.button("➕ SALVAR NA LISTA MESTRA"):
        if n_nome:
            novo_item = pd.DataFrame([{"Produto": n_nome, "Subclasse": n_sub, "Detalhe": "Padrão"}])
            # Adiciona e remove duplicados
            st.session_state.df_mestre = pd.concat([st.session_state.df_mestre, novo_item], ignore_index=True)
            st.session_state.df_mestre = st.session_state.df_mestre.drop_duplicates(subset=['Produto']).sort_values('Produto')
            st.success(f"✅ {n_nome} cadastrado com sucesso!")
            st.rerun()
        else:
            st.error("Digite o nome do produto!")

    st.divider()
    st.subheader("Sua Lista Cadastrada")
    # Tabela editável para ajustes finos
    df_temp = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=OPCOES_SUBCLASSES)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_lista_mestra"
    )
    if not df_temp.equals(st.session_state.df_mestre):
        st.session_state.df_mestre = df_temp
        st.rerun()

# --- ABA 1: NO MERCADO (USO REAL) ---
with aba_mercado:
    total_venda = st.session_state.carrinho["Total"].sum()
    st.metric("TOTAL NO CARRINHO", f"R$ {total_venda:.2f}")

    st.subheader("Lançar Item")
    
    # Puxa a lista atualizada da memória
    lista_para_busca = st.session_state.df_mestre["Produto"].tolist()
    
    escolha = st.selectbox(
        "Buscar Produto:", 
        options=lista_para_busca, 
        index=None, 
        placeholder="Digite para buscar...",
        key="busca_mercado"
    )

    if escolha:
        # Pega a subclasse que você definiu no cadastro
        sub_atual = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        st.caption(f"Categoria: {sub_atual}")

        col_q, col_p = st.columns(2)
        with col_q:
            qtd_in = st.number_input("Qtd:", min_value=0.01, value=1.0, step=0.1, key="qtd_m")
        with col_p:
            # Colocamos o valor como 0.00 mas permitimos a edição rápida
            preco_in = st.number_input("Preço Unitário:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="preco_m")
        
        # Botão de lançar fora de formulário para evitar bugs de Enter
        if st.button("🛒 INSERIR NO CARRINHO", use_container_width=True):
            novo_no_carrinho = pd.DataFrame([{
                "Produto": escolha,
                "Subclasse": sub_atual,
                "Qtd": qtd_in,
                "Preço": preco_in,
                "Total": qtd_in * preco_in
            }])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_no_carrinho], ignore_index=True)
            st.toast(f"{escolha} adicionado!")
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### Itens Lançados")
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="edit_carrinho")
        
        # RESUMO COM PERCENTUAL
        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            res_df = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            if total_venda > 0:
                res_df["%"] = ((res_df["Total"] / total_venda) * 100).round(1).astype(str) + "%"
            
            # Formatação de Moeda para a tabela
            res_df["Total"] = res_df["Total"].map("R$ {:.2f}".format)
            st.table(res_df)

        if st.button("🗑️ Esvaziar Carrinho"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
