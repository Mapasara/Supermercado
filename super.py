import streamlit as st
import pandas as pd
import os
import plotly.express as px  # Nova biblioteca para o gráfico

st.set_page_config(page_title="Minha Compra Master", layout="wide")

# --- 1. CONFIGURAÇÕES E BANCO DE DADOS ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = [
    "BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", 
    "EU MEREÇO", "FRANGO", "VACA", "PORCO", "PEIXE", 
    "VERDURAS", "LEGUMES", "FRUTAS"
]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    produtos_lista = ["Arroz", "Feijão", "Açúcar", "Café", "Leite", "Óleo", "Cebola", "Tomate"]
    return pd.DataFrame({
        "Produto": sorted(produtos_lista),
        "Subclasse": ["BÁSICO"] * len(produtos_lista)
    })

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

st.title("🛒 Gestor de Compras Master")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA DE CONFIGURAÇÃO ---
with aba_config:
    st.subheader("⚙️ Gestão da Lista Mestra")
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES, required=True),
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_config_v5"
    )
    if st.button("💾 SALVAR ALTERAÇÕES AGORA", use_container_width=True):
        st.session_state.df_mestre = df_editado.drop_duplicates(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista atualizada!")
        st.rerun()

# --- ABA NO MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    
    # Destaque para o valor total
    st.markdown(f"""
        <div style="background-color:#1E1E1E; padding:10px; border-radius:10px; border: 2px solid #4CAF50; text-align:center;">
            <h1 style="color:#4CAF50; margin:0;">Total: R$ {total_compra:.2f}</h1>
        </div>
    """, unsafe_index=True)

    # --- GRÁFICO DE PIZZA EM TEMPO REAL ---
    if not st.session_state.carrinho.empty:
        # Criando o gráfico com Plotly
        resumo_grafico = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
        fig = px.pie(
            resumo_grafico, 
            values='Total', 
            names='Subclasse', 
            title='Distribuição de Gastos',
            hole=0.4, # Estilo Donut
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Lançar Produto")
    opcoes_produtos = sorted(st.session_state.df_mestre["Produto"].tolist())
    
    if "reset_busca" not in st.session_state:
        st.session_state.reset_busca = 0

    escolha = st.selectbox(
        "Buscar na lista:", options=opcoes_produtos, index=None, 
        placeholder="Digite o nome do produto...",
        key=f"busca_{st.session_state.reset_busca}" 
    )

    if escolha:
        linha_prod = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        sub_identificada = linha_prod["Subclasse"].values[0] if not linha_prod.empty else "BÁSICO"
        
        st.info(f"Subclasse: *{sub_identificada}*")
        
        col_q, col_p = st.columns(2)
        with col_q:
            qtd_in = st.number_input("Quantidade:", min_value=0.0, value=1.0, step=0.1)
        with col_p:
            preco_in = st.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            novo_item = pd.DataFrame([{"Produto": escolha, "Subclasse": sub_identificada, "Qtd": qtd_in, "Preço": preco_in, "Total": qtd_in * preco_in}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
            st.session_state.reset_busca += 1
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### 📝 Carrinho")
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Esvaziar Tudo", use_container_width=True):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
