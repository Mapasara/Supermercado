import streamlit as st
import pandas as pd
import os

# Tenta carregar o gráfico, se não der, o app avisa sem travar
try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. BANCO DE DADOS ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", "VERDURAS", "LEGUMES", "FRUTAS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    # Se o arquivo não existir, cria a lista padrão
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
    return pd.DataFrame({
        "Produto": sorted(produtos_lista),
        "Subclasse": ["BÁSICO"] * len(produtos_lista)
    })

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

st.title("🛒 Gestor Master")
aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA CONFIGURAÇÃO ---
with aba_config:
    st.subheader("⚙️ Configuração")
    st.info("Ajuste as categorias e clique em SALVAR.")
    df_editado = st.data_editor(st.session_state.df_mestre, column_config={"Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES)}, num_rows="dynamic", use_container_width=True)
    if st.button("💾 SALVAR LISTA", use_container_width=True):
        st.session_state.df_mestre = df_editado.drop_duplicates(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Salvo com sucesso!")
        st.rerun()

# --- ABA MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.markdown(f"<div style='background-color:#1E1E1E; padding:15px; border-radius:10px; border: 2px solid #4CAF50; text-align:center;'><h1 style='color:#4CAF50; margin:0;'>Total: R$ {total_compra:.2f}</h1></div>", unsafe_allow_html=True)

    if not st.session_state.carrinho.empty:
        if PLOTLY_DISPONIVEL:
            resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Lançar")
    if "key_index" not in st.session_state: st.session_state.key_index = 0
    
    # Busca com filtro
    busca = st.text_input("Filtrar produto:", key=f"input_{st.session_state.key_index}").strip().lower()
    lista_p = sorted(st.session_state.df_mestre["Produto"].tolist())
    opcoes = [p for p in lista_p if busca in p.lower()] if busca else lista_p
    escolha = st.selectbox(f"Resultados ({len(opcoes)}):", options=opcoes, index=None, key=f"select_{st.session_state.key_index}")

    if escolha:
        sub = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        st.info(f"Subclasse: {sub}")
        c1, c2 = st.columns(2)
        q = c1.number_input("Qtd:", min_value=0.0, value=1.0, step=0.1, key=f"q_{st.session_state.key_index}")
        p = c2.number_input("Preço:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"p_{st.session_state.key_index}")
        
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            novo = pd.DataFrame([{"Produto": escolha, "Subclasse": sub, "Qtd": q, "Preço": p, "Total": q * p}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
            st.session_state.key_index += 1 # Limpa a busca
            st.rerun()

    st.divider()
    if not st.session_state.carrinho.empty:
        st.write("### 📝 Carrinho")
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        if st.button("🗑️ Esvaziar Tudo", use_container_width=True):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
