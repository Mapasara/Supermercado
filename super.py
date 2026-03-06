import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. DEFINIÇÃO FIXA DAS SUBCLASSES ---
if 'opcoes_subclasses' not in st.session_state:
    st.session_state.opcoes_subclasses = [
        "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
        "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
        "VERDURAS", "LEGUMES", "FRUTAS"
    ]

# --- 2. INICIALIZAÇÃO ROBUSTA DA LISTA MESTRA ---
if 'df_mestre' not in st.session_state:
    # Sua lista inicial de segurança
    dados_iniciais = {
        "Produto": ["Arroz", "Feijão", "Açúcar", "Café", "Leite", "Óleo", "Cebola", "Tomate"],
        "Subclasse": ["BÁSICO", "BÁSICO", "BÁSICO", "BÁSICO", "BÁSICO", "BÁSICO", "LEGUMES", "LEGUMES"],
        "Detalhe": ["Padrão"] * 8
    }
    st.session_state.df_mestre = pd.DataFrame(dados_iniciais)

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 3. INTERFACE ---
st.title("🛒 Gestor de Compras")

aba_mercado, aba_cadastro = st.tabs(["🛍️ No Mercado", "📝 Cadastrar/Editar"])

# --- ABA DE CADASTRO (ONDE ALIMENTA A LISTA) ---
with aba_cadastro:
    st.subheader("Adicionar Novo Item")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            n_nome = st.text_input("Nome do Produto:", key="n_nome_input")
        with c2:
            n_sub = st.selectbox("Subclasse:", st.session_state.opcoes_subclasses, key="n_sub_select")
        
        if st.button("➕ SALVAR NA LISTA"):
            if n_nome:
                novo_item = pd.DataFrame([{"Produto": n_nome.strip(), "Subclasse": n_sub, "Detalhe": "Padrão"}])
                st.session_state.df_mestre = pd.concat([st.session_state.df_mestre, novo_item], ignore_index=True)
                # Remove duplicados e ordena
                st.session_state.df_mestre = st.session_state.df_mestre.drop_duplicates(subset=['Produto']).sort_values('Produto')
                st.success(f"✅ {n_nome} guardado!")
                st.rerun()

    st.divider()
    st.subheader("Sua Lista de Produtos")
    # Editor da lista para você mudar as subclasses ou nomes
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=st.session_state.opcoes_subclasses)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_lista_mestre"
    )
    if not df_editado.equals(st.session_state.df_mestre):
        st.session_state.df_mestre = df_editado
        st.rerun()

# --- ABA NO MERCADO (USO REAL) ---
with aba_mercado:
    total_carrinho = st.session_state.carrinho["Total"].sum()
    st.metric("TOTAL NO CARRINHO", f"R$ {total_carrinho:.2f}")

    st.subheader("Lançar Item")
    
    # GARANTIA: Recriar a lista de busca toda vez que carregar a aba
    lista_opcoes = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    
    escolha = st.selectbox(
        "Buscar Produto:", 
        options=lista_opcoes, 
        index=None, 
        placeholder="Digite para buscar...",
        key="busca_realtime"
    )

    if escolha:
        # Puxa a subclasse que está salva para este produto
        try:
            sub_vinculada = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        except:
            sub_vinculada = "BÁSICO"
            
        st.info(f"Categoria: {sub_vinculada}")

        col_q, col_p = st.columns(2)
        with col_q:
            qtd_m = st.number_input("Quantidade:", min_value=0.01, value=1.0, step=0.1, key="qtd_m_input")
        with col_p:
            # Preço começando em 0.00
            preco_m = st.number_input("Preço Unitário:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="preco_m_input")
        
        # O botão de lançar agora força o Enter indiretamente
        if st.button("🛒 INSERIR NO CARRINHO", use_container_width=True):
            novo_carrinho = pd.DataFrame([{
                "Produto": escolha,
                "Subclasse": sub_vinculada,
                "Qtd": qtd_m,
                "Preço": preco_m,
                "Total": qtd_m * preco_m
            }])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_carrinho], ignore_index=True)
            st.toast(f"Adicionado: {escolha}")
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### Itens Lançados")
        # Carrinho editável caso erre o preço na hora
        car_edit = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="edit_car_real")
        
        if not car_edit.equals(st.session_state.carrinho):
            car_edit["Total"] = car_edit["Qtd"] * car_edit["Preço"]
            st.session_state.carrinho = car_edit
            st.rerun()

        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            if total_carrinho > 0:
                resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                resumo["%"] = ((resumo["Total"] / total_carrinho) * 100).round(1).astype(str) + "%"
                resumo["Total"] = resumo["Total"].map("R$ {:.2f}".format)
                st.table(resumo)

        if st.button("🗑️ Esvaziar Carrinho"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
