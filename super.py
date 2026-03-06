import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- LISTA DE SUBCLASSES PRÉ-DEFINIDAS ---
OPCOES_SUBCLASSES = [
    "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
    "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
    "VERDURAS", "LEGUMES", "FRUTAS"
]

# 1. INICIALIZAÇÃO DO BANCO DE DADOS
if 'df_mestre' not in st.session_state:
    lista_inicial = [
        "Arroz", "Feijão", "Açúcar cristal", "Açucar refinado", "Farofa", "Trigo", 
        "Farinha de rosca", "Farinha de milho", "Aveia", "Fubá", "Ovos", "Azeite", 
        "Óleo de soja", "Óleo de milho", "Tapioca", "Azeitonas", "Molho Tomate", 
        "Milho", "Café", "Pão integral", "Leite condensado", "Requeijão", 
        "Adoçante", "Muçarela", "Mortadela", "Presunto", "Pizza", "Coador", 
        "Lentilha", "Grão de bico", "Água sanitária", "Amaciante", "Detergente", 
        "Toalha papel", "Papel Higiênico", "Desodorante", "Sabonete", "Shampoo", 
        "Alface", "Tomate", "Cebola", "Cenoura", "Banana", "Maçã", "Frango", 
        "Acém", "Patinho", "Linguiça", "Tilápia"
    ]
    st.session_state.df_mestre = pd.DataFrame({
        "Produto": sorted(list(set(lista_inicial))),
        "Subclasse": "BÁSICO",
        "Detalhe": "Padrão"
    })

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- FUNÇÃO PARA LIMPAR CAMPOS APÓS LANÇAR ---
def lancar_produto(produto_nome, sub, q, p):
    novo = pd.DataFrame([{
        "Produto": produto_nome,
        "Subclasse": sub,
        "Qtd": q,
        "Preço": p,
        "Total": q * p
    }])
    st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
    # O rerun limpa os inputs automaticamente devido ao estado do widget
    st.rerun()

st.title("🛒 Gestor de Compras Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Subclasses"])

# --- ABA 2: CONFIGURAÇÃO ---
with aba_config:
    st.subheader("Organize seus Produtos")
    st.write("Dica: Clique em 'Subclasse' para escolher a categoria de cada item.")
    
    # Editor da lista mestra com menu suspenso para Subclasses
    df_mestre_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn(
                "Subclasse",
                help="Escolha a categoria",
                options=OPCOES_SUBCLASSES,
                required=True,
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_mestre"
    )
    if not df_mestre_editado.equals(st.session_state.df_mestre):
        st.session_state.df_mestre = df_mestre_editado
        st.rerun()

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    # Cálculo do total apenas dos itens do carrinho (Subclasses)
    total_geral = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR TOTAL CARRINHO", f"R$ {total_geral:.2f}")

    st.write("### Adicionar ao Carrinho")
    
    # Formulário para garantir a limpeza dos campos ao enviar
    with st.form("form_inserir", clear_on_submit=True):
        opcoes = st.session_state.df_mestre["Produto"] + " (" + st.session_state.df_mestre["Detalhe"] + ")"
        
        escolha_busca = st.selectbox(
            "Busca Inteligente:",
            options=range(len(opcoes)),
            format_func=lambda x: opcoes.iloc[x],
            index=None,
            placeholder="Digite o produto..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            qtd = st.number_input("Quantidade:", min_value=0.01, step=0.1, value=1.0)
        with col2:
            preco = st.number_input("Preço Unitário (R$):", min_value=0.0, step=0.01)
        
        botao_enviar = st.form_submit_button("🛒 LANÇAR NO CARRINHO")
        
        if botao_enviar and escolha_busca is not None:
            item_sel = st.session_state.df_mestre.iloc[escolha_busca]
            nome_final = f"{item_sel['Produto']} ({item_sel['Detalhe']})"
            lancar_produto(nome_final, item_sel['Subclasse'], qtd, preco)

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### Itens Lançados")
        carrinho_editado = st.data_editor(
            st.session_state.carrinho,
            column_config={
                "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total": st.column_config.NumberColumn(format="R$ %.2f", disabled=True)
            },
            use_container_width=True,
            hide_index=True,
            key="editor_carrinho"
        )
        
        # Resumo por Subclasse (Visualização sem somar ao total principal)
        with st.expander("📊 Ver resumo por Subclasse"):
            resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            st.table(resumo.style.format({"Total": "R$ {:.2f}"}))

        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
