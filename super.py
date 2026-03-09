import streamlit as st
import pandas as pd
import os

# Tenta carregar o Plotly para o gráfico
try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

st.set_page_config(page_title="Minha Compra", layout="wide")

# --- BANCO DE DADOS ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ/LANCHE", "HIGIENE", "LIMPEZA", "CARNES", "FRUTAS/LEGUMES", "OUTROS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        return df.dropna(subset=['Produto'])
    return pd.DataFrame({"Produto": ["Arroz", "Feijão"], "Subclasse": ["BÁSICO", "BÁSICO"]})

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
if 'key_index' not in st.session_state:
    st.session_state.key_index = 0

# --- ESTILO DO BANNER (TAMANHO MÉDIO) ---
total_compra = st.session_state.carrinho["Total"].sum()
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border: 3px solid #4CAF50; text-align:center; margin-bottom:20px;">
        <span style="color:white; font-size:20px; font-weight:normal; display:block;">Valor no Carrinho</span>
        <span style="color:#4CAF50; font-size:42px; font-weight:bold;">R$ {total_compra:.2f}</span>
    </div>
""", unsafe_allow_html=True)

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    # Gráfico e Resumo lateral
    if not st.session_state.carrinho.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            if PLOTLY_DISPONIVEL:
                resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.5)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=180, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("📊 *Resumo:*")
            resumo_txt = st.session_state.carrinho.groupby("Subclasse")["Total"].sum()
            for cat, val in resumo_txt.items():
                st.caption(f"{cat}: R$ {val:.2f}")

    st.subheader("🔍 Lançar Produto")
    
    # BUSCA INTELIGENTE MELHORADA
    busca_texto = st.text_input("Comece a digitar o nome:", key=f"txt_{st.session_state.key_index}").strip().lower()
    
    lista_total = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    # Filtra os nomes conforme a digitação
    opcoes_filtradas = [p for p in lista_total if busca_texto in p.lower()] if busca_texto else lista_total

    escolha = st.selectbox(
        f"Encontrados ({len(opcoes_filtradas)}):", 
        options=opcoes_filtradas, 
        index=None, 
        placeholder="Selecione aqui...",
        key=f"sel_{st.session_state.key_index}"
    )

    # Só mostra os campos se o produto for selecionado
    if escolha:
        linha_prod = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        cat_p = linha_prod["Subclasse"].values[0] if not linha_prod.empty else "OUTROS"
        
        st.success(f"🛒 *{escolha}* ({cat_p})")
        
        col_q, col_p = st.columns(2)
        with col_q:
            qtd = st.number_input("Qtd:", min_value=0.1, value=1.0, step=0.1)
        with col_p:
            preco = st.number_input("Preço R$:", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        if st.button("✅ CONFIRMAR LANÇAMENTO", use_container_width=True):
            if preco > 0:
                novo = pd.DataFrame([{"Produto": escolha, "Subclasse": cat_p, "Qtd": qtd, "Preço": preco, "Total": qtd * preco}])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
                st.session_state.key_index += 1 # Limpa a busca e os campos
                st.rerun()
            else:
                st.error("Por favor, coloque o preço!")

    if not st.session_state.carrinho.empty:
        st.divider()
        st.write("### 📝 Carrinho Atual")
        # Editor para o carrinho - Permite deletar linhas selecionando-as e apertando Delete
        car_ed = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        if not car_ed.equals(st.session_state.carrinho):
            st.session_state.carrinho = car_ed
            st.rerun()

# --- ABA 2: CONFIGURAR LISTA ---
with aba_config:
    st.subheader("⚙️ Meus Produtos")
    st.write("Para adicionar novos, use a última linha da tabela ou cole uma lista.")
    
    df_mestre_ed = st.data_editor(
        st.session_state.df_mestre, 
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Categoria", options=SUBCLASSES, required=True),
            "Produto": st.column_config.TextColumn("Nome", required=True)
        }, 
        num_rows="dynamic", 
        use_container_width=True
    )
    
    if st.button("💾 SALVAR LISTA MESTRA", use_container_width=True):
        st.session_state.df_mestre = df_mestre_ed.dropna(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista salva!")
        st.rerun()
