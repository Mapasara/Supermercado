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
        return pd.read_csv(ARQUIVO_DADOS).dropna(subset=['Produto'])
    return pd.DataFrame({"Produto": ["Arroz", "Feijão"], "Subclasse": ["BÁSICO", "BÁSICO"]})

# Inicialização de Estados
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0

# --- BANNER DO TOTAL (ESTILO CARTÃO) ---
total_v = st.session_state.carrinho["Total"].sum()
st.markdown(f"""
    <div style="background-color:#1E1E1E; padding:15px; border-radius:12px; border: 2px solid #4CAF50; text-align:center; margin-bottom:10px;">
        <p style="color:#AAAAAA; margin:0; font-size:14px; text-transform:uppercase;">Total no Carrinho</p>
        <h2 style="color:#4CAF50; margin:0; font-size:36px;">R$ {total_v:.2f}</h2>
    </div>
""", unsafe_allow_html=True)

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    # Gráfico e Resumo lado a lado
    if not st.session_state.carrinho.empty:
        col_g, col_t = st.columns([1, 1])
        with col_g:
            if PLOTLY_DISPONIVEL:
                resumo = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                fig = px.pie(resumo, values='Total', names='Subclasse', hole=0.5)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=150, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        with col_t:
            st.caption("📂 *Resumo por Categoria:*")
            res_txt = st.session_state.carrinho.groupby("Subclasse")["Total"].sum()
            for c, v in res_txt.items():
                st.write(f"*{c}:* R$ {v:.2f}")
        st.divider()

    st.subheader("🔍 Lançar Produto")
    
    # BUSCA POR TEXTO
    txt_busca = st.text_input("Filtrar nome:", key=f"t_{st.session_state.reset_trigger}").strip().lower()
    
    # FILTRO DA LISTA
    lista_original = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    opcoes = [p for p in lista_original if txt_busca in p.lower()] if txt_busca else lista_original

    # SELETOR (A ESCOLHA)
    produto_sel = st.selectbox(
        f"Resultados ({len(opcoes)}):", 
        options=opcoes, 
        index=None, 
        placeholder="Selecione o produto aqui...",
        key=f"s_{st.session_state.reset_trigger}"
    )

    # BLOCO DE LANÇAMENTO (Só aparece quando o produto_sel NÃO é nulo)
    if produto_sel is not None:
        # Pega a categoria automática
        dados_p = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == produto_sel]
        cat_p = dados_p["Subclasse"].values[0] if not dados_p.empty else "OUTROS"
        
        st.info(f"📍 Selecionado: *{produto_sel}*")
        
        c_q, c_p = st.columns(2)
        with c_q:
            v_qtd = st.number_input("Qtd:", min_value=0.1, value=1.0, step=0.1, key="input_qtd")
        with c_p:
            v_pre = st.number_input("Preço Unitário R$:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="input_pre")
            
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            if v_pre > 0:
                novo_item = pd.DataFrame([{
                    "Produto": produto_sel, "Subclasse": cat_p, 
                    "Qtd": v_qtd, "Preço": v_pre, "Total": v_qtd * v_pre
                }])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
                st.session_state.reset_trigger += 1 # ISSO LIMPA TUDO PARA O PRÓXIMO
                st.rerun()
            else:
                st.error("Digite o preço antes de confirmar!")

    if not st.session_state.carrinho.empty:
        st.divider()
        st.write("### 📝 Carrinho")
        # Carrinho editável (permite apagar itens)
        car_final = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="editor_car")
        if not car_final.equals(st.session_state.carrinho):
            st.session_state.carrinho = car_final
            st.rerun()

# --- ABA 2: CONFIGURAR LISTA ---
with aba_config:
    st.subheader("⚙️ Lista Mestra de Produtos")
    mestre_ed = st.data_editor(
        st.session_state.df_mestre, 
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Categoria", options=SUBCLASSES, required=True),
            "Produto": st.column_config.TextColumn("Nome do Produto", required=True)
        }, 
        num_rows="dynamic", 
        use_container_width=True,
        key="ed_mestre"
    )
    if st.button("💾 SALVAR PRODUTOS", use_container_width=True):
        st.session_state.df_mestre = mestre_ed.dropna(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista atualizada com sucesso!")
        st.rerun()
