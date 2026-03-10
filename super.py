import streamlit as st
import pandas as pd
import os

# Tenta carregar o Plotly
try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

st.set_page_config(page_title="Minha Compra", layout="wide")

# --- 1. BANCO DE DADOS (COM TRAVA DE SEGURANÇA) ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ/LANCHE", "HIGIENE", "LIMPEZA", "CARNES", "FRUTAS/LEGUMES", "OUTROS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        if not df.empty:
            return df.dropna(subset=['Produto'])
    # Se o arquivo sumiu, ele inicia com estes básicos (você pode colar sua lista de 72 aqui depois)
    return pd.DataFrame({"Produto": ["Arroz", "Feijão", "Açúcar"], "Subclasse": ["BÁSICO", "BÁSICO", "BÁSICO"]})

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 2. BANNER DO TOTAL ---
total_v = st.session_state.carrinho["Total"].sum()
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:15px; border-radius:12px; border: 2px solid #4CAF50; text-align:center; margin-bottom:10px;">
        <p style="color:#AAAAAA; margin:0; font-size:14px;">TOTAL NO CARRINHO</p>
        <h2 style="color:#4CAF50; margin:0; font-size:36px;">R$ {total_v:.2f}</h2>
    </div>
""", unsafe_allow_html=True)

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA 1: NO MERCADO (SEM FORMULÁRIO PARA O ENTER FUNCIONAR) ---
with aba_mercado:
    if not st.session_state.carrinho.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            if PLOTLY_DISPONIVEL:
                resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.5)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=150, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.caption("📂 Resumo:")
            res_txt = st.session_state.carrinho.groupby("Subclasse")["Total"].sum()
            for c, v in res_txt.items():
                st.write(f"*{c}:* R$ {v:.2f}")
        st.divider()

    st.subheader("🔍 Lançar Produto")
    
    lista_produtos = sorted(st.session_state.df_mestre["Produto"].unique().tolist())

    # Escolha do produto (Fora do formulário)
    escolha = st.selectbox("Selecione o Produto:", options=lista_produtos, index=None, placeholder="Digite o nome...")

    if escolha:
        # Pega a categoria automática
        df_p = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        cat_p = df_p["Subclasse"].values[0] if not df_p.empty else "OUTROS"
        
        st.info(f"📍 Categoria: {cat_p}")

        col_q, col_p = st.columns(2)
        # O ENTER nesses campos agora atualizará o estado imediatamente
        v_qtd = col_q.number_input("Qtd:", min_value=0.1, value=1.0, step=0.1)
        v_pre = col_p.number_input("Preço R$:", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        
        # Botão de confirmação isolado
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            if v_pre > 0:
                novo = pd.DataFrame([{"Produto": escolha, "Subclasse": cat_p, "Qtd": v_qtd, "Preço": v_pre, "Total": v_qtd * v_pre}])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
                st.success(f"Adicionado: {escolha}")
                st.rerun()
            else:
                st.error("Coloque o preço!")

    if not st.session_state.carrinho.empty:
        st.divider()
        st.write("### 📝 Carrinho")
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        if st.button("🗑️ Esvaziar Tudo"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()

# --- ABA 2: CONFIGURAR LISTA ---
with aba_config:
    st.subheader("⚙️ Configurar Meus Produtos")
    # Mostra quantos produtos existem
    st.write(f"Produtos na memória: {len(st.session_state.df_mestre)}")
    
    mestre_ed = st.data_editor(
        st.session_state.df_mestre, 
        column_config={"Subclasse": st.column_config.SelectboxColumn("Categoria", options=SUBCLASSES, required=True)}, 
        num_rows="dynamic", 
        use_container_width=True
    )
    if st.button("💾 SALVAR LISTA"):
        st.session_state.df_mestre = mestre_ed.dropna(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista salva! Se os 72 sumiram, você pode colá-los aqui novamente.")
        st.rerun()
