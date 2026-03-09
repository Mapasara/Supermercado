import streamlit as st

import pandas as pd
import os

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. CONFIGURAÇÕES DE MEMÓRIA PERMANENTE ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = [
    "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
    "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
    "VERDURAS", "LEGUMES", "FRUTAS"
]

# Função para carregar a lista de produtos
def carregar_dados():
    # Tenta ler o arquivo salvo primeiro
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            if not df.empty:
                return df
        except:
            pass
    
    # Se o arquivo não existir ou falhar, usa a lista inicial
    produtos_lista = [
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
    
    # O SEGREDO: Criamos a tabela garantindo que as duas colunas tenham o MESMO tamanho
    df_inicial = pd.DataFrame({
        "Produto": produtos_lista,
        "Subclasse": ["BÁSICO"] * len(produtos_lista) # O computador conta o tamanho aqui
    })
    return df_inicial

# Inicializa o estado da sessão
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 2. INTERFACE ---
st.title("🛒 Gestor de Compras Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA DE CONFIGURAÇÃO ---
with aba_config:
    st.subheader("Sua Lista de Produtos")
    st.info("Ajuste as subclasses abaixo e clique em SALVAR para gravar permanentemente.")
    
    # Editor da tabela mestra
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_config_v2"
    )
    
    if st.button("💾 SALVAR LISTA DEFINITIVAMENTE", use_container_width=True):
        st.session_state.df_mestre = df_editado
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista gravada com sucesso!")
        st.rerun()

# --- ABA NO MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR TOTAL NO CARRINHO", f"R$ {total_compra:.2f}")

    # Busca inteligente
    lista_busca = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    escolha = st.selectbox("Buscar Produto:", options=lista_busca, index=None, placeholder="Digite o nome...")

    if escolha:
        # Puxa a subclasse salva
        sub_item = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        st.caption(f"Categoria: {sub_item}")
        
        col_q, col_p = st.columns(2)
        with col_q:
            q_in = st.number_input("Qtd:", min_value=0.0, value=1.0, step=0.1)
        with col_p:
            p_in = st.number_input("Preço Unitário:", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        if st.button("🛒 LANÇAR NO CARRINHO", use_container_width=True):
            novo = pd.DataFrame([{"Produto": escolha, "Subclasse": sub_item, "Qtd": q_in, "Preço": p_in, "Total": q_in * p_in}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
            st.toast(f"{escolha} adicionado!")
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### Itens no Carrinho")
        carrinho_atualizado = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="carrinho_editor")
        
        if not carrinho_atualizado.equals(st.session_state.carrinho):
            carrinho_atualizado["Total"] = carrinho_atualizado["Qtd"] * carrinho_atualizado["Preço"]
            st.session_state.carrinho = carrinho_atualizado
            st.rerun()
            
        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            res = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            if total_compra > 0:
                res["%"] = ((res["Total"] / total_compra) * 100).round(1).astype(str) + "%"
            res["Total"] = res["Total"].map("R$ {:.2f}".format)
            st.table(res)

        if st.button("🗑️ Limpar Carrinho Completo"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
