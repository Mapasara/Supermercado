import streamlit as st
import pandas as pd
import os
import plotly.express as px

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
        key="editor_config_final"
    )
    if st.button("💾 SALVAR ALTERAÇÕES AGORA", use_container_width=True):
        st.session_state.df_mestre = df_editado.drop_duplicates(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista atualizada!")
        st.rerun()

# --- ABA NO MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    
    st.markdown(f"""
        <div style="background-color:#1E1E1E; padding:15px; border-radius:10px; border: 2px solid #4CAF50; text-align:center; margin-bottom:20px;">
            <h1 style="color:#4CAF50; margin:0; font-size:28px;">Total: R$ {total_compra:.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.carrinho.empty:
        resumo_grafico = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
        fig = px.pie(resumo_grafico, values='Total', names='Subclasse', hole=0.4, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Localizar e Lançar")
    
    # BUSCA POR PALAVRA (Seu Ctrl+F integrado)
    busca_palavra = st.text_input("Digite para filtrar (ex: Arroz, Papel):", key="filtro_palavra").strip().lower()
    
    lista_completa = sorted(st.session_state.df_mestre["Produto"].tolist())
    if busca_palavra:
        opcoes_filtradas = [p for p in lista_completa if busca_palavra in p.lower()]
    else:
        opcoes_filtradas = lista_completa

    if "reset_busca" not in st.session_state: st.session_state.reset_busca = 0
    
    escolha = st.selectbox(
        f"Resultados ({len(opcoes_filtradas)}):", 
        options=opcoes_filtradas, 
        index=None, 
        placeholder="Selecione o produto...",
        key=f"sel_{st.session_state.reset_busca}"
    )

    if escolha:
        linha = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        sub_identificada = linha["Subclasse"].values[0] if not linha.empty else "BÁSICO"
        
        st.info(f"Selecionado: *{escolha}*")
        
        c1, c2 = st.columns(2)
        with c1:
            qtd_in = st.number_input("Qtd:", min_value=0.0, value=1.0, step=0.1, key="q_in")
        with c2:
            preco_in = st.number_input("Preço Unitário:", min_value=0.0, value=0.0, step=0.01, format="%.2f", key="p_in")
            
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            novo = pd.DataFrame([{"Produto": escolha, "Subclasse": sub_identificada, "Qtd": qtd_in, "Preço": preco_in, "Total": qtd_in * preco_in}])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo], ignore_index=True)
            st.session_state.reset_busca += 1
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### 📝 Carrinho")
        # Editor para remover ou ajustar itens lançados
        car_edit = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="edit_car")
        
        if not car_edit.equals(st.session_state.carrinho):
            st.session_state.carrinho = car_edit
            st.rerun()

        if st.button("🗑️ Esvaziar Tudo", use_container_width=True):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
