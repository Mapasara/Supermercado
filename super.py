import streamlit as st
import pandas as pd

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# 1. INICIALIZAÇÃO DA LISTA MESTRA (Seus produtos)
if 'df_mestre' not in st.session_state:
    # Transformando sua lista de texto em uma tabela (DataFrame)
    lista_inicial = [
        "Arroz", "Feijão", "Açúcar cristal", "Açucar refinado", "Farofa", "Trigo", 
        "Farinha de rosca", "Farinha de milho", "Aveia", "Fubá", "Ovos cart 30", 
        "Ovos cart 20", "Azeite", "Óleo de soja", "Óleo de milho", "Tapioca", 
        "Azeitonas", "Molho Tom Quero", "Molho Tom Pomarola", "Milho", "Café", 
        "Pão integral", "Leite condensado", "Requeijão", "Adoçante Zero cal", 
        "Muçarela", "Mortadela", "Presunto", "Pizza", "Coador Evoluto", "Lentilha", 
        "Grão de bico", "Água sanitária", "Amaciante", "Detergente", "Toalha papel", 
        "Papel Higiênico", "Papel alumínio", "Plástico filme", "Saco de lixo 100", 
        "Saco de lixo 50", "Desodorante", "Sabonete", "Cotonete", "Shampoo", 
        "Absorvente", "Buchechol", "Alface", "Chicória", "Escarola", "Acelga", 
        "Mostarda", "Tomate", "Cebola", "Chuchu", "Berinjela", "Jiló", "Cenoura", 
        "Abacate", "Banana", "Maçã", "Kiui", "Jaboticaba", "Pêra", "Mixirica", 
        "Abacaxi", "Frango à passarinho", "Filé de peito", "Linguiça", "Acém", 
        "Patinho", "Alcatra suína", "Tilápia"
    ]
    # Criando a tabela com colunas de Classe e Marca/Capacidade vazias para você preencher
    st.session_state.df_mestre = pd.DataFrame({
        "Produto": sorted(list(set(lista_inicial))),
        "Classe": "GERAL",
        "Detalhe": "Padrão"
    })

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Classe", "Qtd", "Preço", "Total"])

# --- INTERFACE ---
st.title("🛒 Gestor de Compras Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista e Classes"])

# --- ABA DE CONFIGURAÇÃO (Onde você organiza sua vida) ---
with aba_config:
    st.subheader("Gerencie seus Produtos e Categorias")
    st.write("Nesta tabela, você pode alterar o nome do produto, definir a Classe (BÁSICO, LIMPEZA...) e adicionar detalhes (Marca/Peso).")
    
    # Editor da lista mestra
    df_mestre_editado = st.data_editor(
        st.session_state.df_mestre,
        num_rows="dynamic", # Permite que você adicione linhas novas no final da tabela
        use_container_width=True,
        key="editor_mestre"
    )
    if not df_mestre_editado.equals(st.session_state.df_mestre):
        st.session_state.df_mestre = df_mestre_editado
        st.rerun()

# --- ABA DO MERCADO (O uso real) ---
with aba_mercado:
    total_geral = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR TOTAL", f"R$ {total_geral:.2f}")

    st.write("### Adicionar ao Carrinho")
    
    # Criamos uma lista de exibição que combina Nome + Detalhe
    opcoes = st.session_state.df_mestre["Produto"] + " (" + st.session_state.df_mestre["Detalhe"] + ")"
    
    escolha_idx = st.selectbox(
        "Busca Inteligente (digite o nome):",
        options=range(len(opcoes)),
        format_func=lambda x: opcoes.iloc[x],
        index=None,
        placeholder="Ex: Arroz..."
    )

    if escolha_idx is not None:
        item_sel = st.session_state.df_mestre.iloc[escolha_idx]
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            qtd = st.number_input("Qtd:", min_value=0.1, step=0.1, value=1.0)
        with col2:
            preco = st.number_input("Preço Unitário (R$):", min_value=0.0, step=0.5)
        with col3:
            st.write("---")
            if st.button("🛒 Lançar Item"):
                novo = pd.DataFrame([{
                    "Produto": f"{item_sel['Produto']} ({item_sel['Detalhe']})",
                    "Classe": item_sel['Classe'],
                    "Qtd": qtd,
                    "Preço": preco,
                    "Total": qtd * preco
                }])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
                st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### Itens no Carrinho")
        # Agrupar por classe para facilitar visualização
        carrinho_editado = st.data_editor(
            st.session_state.carrinho,
            column_config={
                "Preço": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total": st.column_config.NumberColumn(format="R$ %.2f", disabled=True)
            },
            use_container_width=True,
            hide_index=True
        )
        # Atualizar cálculos se mudar Qtd ou Preço na tabela
        carrinho_editado["Total"] = carrinho_editado["Qtd"] * carrinho_editado["Preço"]
        if not carrinho_editado.equals(st.session_state.carrinho):
            st.session_state.carrinho = carrinho_editado
            st.rerun()

        if st.button("Limpar Tudo"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Classe", "Qtd", "Preço", "Total"])
            st.rerun()
