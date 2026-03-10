import streamlit as st
import pandas as pd
import os
import time

try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

st.set_page_config(page_title="Minha Compra", layout="wide")

# --- 1. CONFIGURAÇÕES E CATEGORIAS ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ/LANCHE", "BOLACHA", "HIGIENE", "LIMPEZA", "FRANGO", "VACA", "PEIXES", "LEGUMES", "VERDURAS", "FRUTAS", "EU MEREÇO", "OUTROS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        if not df.empty:
            # Remove duplicados e ordena por nome ao carregar
            return df.drop_duplicates(subset=['Produto']).sort_values(by='Produto').reset_index(drop=True)
    return pd.DataFrame({"Produto": ["Arroz"], "Subclasse": ["BÁSICO"]})

# Inicialização de Estados
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
if 'contador_reset' not in st.session_state:
    st.session_state.contador_reset = 0

# --- 2. BANNER DO TOTAL ---
total_v = st.session_state.carrinho["Total"].sum()
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:15px; border-radius:12px; border: 2px solid #4CAF50; text-align:center; margin-bottom:10px;">
        <p style="color:#AAAAAA; margin:0; font-size:14px;">TOTAL NO CARRINHO</p>
        <h2 style="color:#4CAF50; margin:0; font-size:36px;">R$ {total_v:.2f}</h2>
    </div>
""", unsafe_allow_html=True)

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    if not st.session_state.carrinho.empty:
        c1, c2 = st.columns([1, 1])
        with c1:
            if PLOTLY_DISPONIVEL:
                resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.5)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=140, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.caption("📂 Resumo por Categoria:")
            res_txt = st.session_state.carrinho.groupby("Subclasse")["Total"].sum()
            for c, v in res_txt.items():
                st.write(f"*{c}:* R$ {v:.2f}")
        st.divider()

    st.subheader("🔍 Lançar Produto")
    lista_nomes = sorted(st.session_state.df_mestre["Produto"].unique().tolist())

    produto_sel = st.selectbox(
        "Selecione ou digite o produto:",
        options=lista_nomes,
        index=None,
        placeholder="Clique para buscar...",
        key=f"sel_{st.session_state.contador_reset}"
    )

    if produto_sel:
        df_p = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == produto_sel]
        cat_p = df_p["Subclasse"].values[0] if not df_p.empty else "OUTROS"
        st.info(f"📍 Selecionado: *{produto_sel}* | Categoria: *{cat_p}*")

        col_q, col_p = st.columns(2)
        v_qtd = col_q.number_input("Qtd:", min_value=0.1, value=1.0, step=0.1, key=f"q_{st.session_state.contador_reset}")
        v_pre = col_p.number_input("Preço R$:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key=f"p_{st.session_state.contador_reset}")
        
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            if v_pre > 0:
                novo = pd.DataFrame([{"Produto": produto_sel, "Subclasse": cat_p, "Qtd": v_qtd, "Preço": v_pre, "Total": v_qtd * v_pre}])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
                st.toast(f"✅ {produto_sel} adicionado!")
                st.session_state.contador_reset += 1
                time.sleep(0.3)
                st.rerun()
            else:
                st.error("Insira o preço!")

    if not st.session_state.carrinho.empty:
        st.divider()
        st.write("### 📝 Carrinho Atual")
        car_ed = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        if not car_ed.equals(st.session_state.carrinho):
            st.session_state.carrinho = car_ed
            st.rerun()

# --- ABA 2: CONFIGURAR LISTA ---
with aba_config:
    st.subheader("⚙️ Gerenciar Lista de Produtos")
    
    # Preparar DF para exibição com contagem começando em 1
    df_exibir = st.session_state.df_mestre.copy()
    df_exibir.index = df_exibir.index + 1
    
    st.write(f"Total de produtos cadastrados: *{len(df_exibir)}*")
    
    mestre_ed = st.data_editor(
        df_exibir, 
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Categoria", options=SUBCLASSES, required=True),
            "Produto": st.column_config.TextColumn("Nome do Produto", required=True)
        }, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_mestre"
    )
    
    if st.button("💾 SALVAR LISTA PERMANENTE", use_container_width=True):
        # 1. Remove linhas onde o nome do produto é nulo ou vazio
        novo_df = mestre_ed.dropna(subset=['Produto'])
        novo_df = novo_df[novo_df['Produto'].str.strip() != ""]
        
        # 2. Remove duplicatas para evitar o bug de "sumir um ao cadastrar outro"
        novo_df = novo_df.drop_duplicates(subset=['Produto'])
        
        # 3. Ordena alfabeticamente para organização
        novo_df = novo_df.sort_values(by='Produto').reset_index(drop=True)
        
        # 4. Salva no Estado e no Arquivo
        st.session_state.df_mestre = novo_df
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success(f"✅ Lista atualizada! Agora temos {len(novo_df)} produtos.")
        time.sleep(1)
        st.rerun()
