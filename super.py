import streamlit as st
import pandas as pd
import os

# Tenta carregar o gráfico (Plotly)
try:
    import plotly.express as px
    PLOTLY_DISPONIVEL = True
except ImportError:
    PLOTLY_DISPONIVEL = False

st.set_page_config(page_title="Gestor de Compras", layout="wide")

# --- 1. BANCO DE DADOS E CONFIGURAÇÃO ---
ARQUIVO_DADOS = "produtos_cadastrados.csv"
SUBCLASSES = ["BÁSICO", "CAFÉ E LANCHE", "BOLACHAS", "HIGIENE", "LIMPEZA", "EU MEREÇO", "CARNES", "FRUTAS/LEGUMES", "OUTROS"]

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    # Lista inicial compacta para exemplo
    return pd.DataFrame({"Produto": ["Arroz", "Feijão", "Açúcar"], "Subclasse": ["BÁSICO", "BÁSICO", "BÁSICO"]})

# Inicialização do estado do App
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
if 'key_index' not in st.session_state:
    st.session_state.key_index = 0

st.title("🛒 Minha Compra")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA 2: CONFIGURAR LISTA (BOTÃO DE INSERIR VOLTOU) ---
with aba_config:
    st.subheader("⚙️ Gerenciar Meus Produtos")
    st.write("Dica: Role até o final da tabela para adicionar novos itens ou clique duas vezes para editar.")
    
    # O data_editor com num_rows="dynamic" permite inserir novas linhas (botão +)
    df_editado = st.data_editor(
        st.session_state.df_mestre, 
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Categoria", options=SUBCLASSES, required=True),
            "Produto": st.column_config.TextColumn("Nome do Produto", required=True)
        }, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_mestre"
    )
    
    if st.button("💾 SALVAR ALTERAÇÕES NA LISTA", use_container_width=True):
        st.session_state.df_mestre = df_editado.dropna(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista de produtos salva!")
        st.rerun()

# --- ABA 1: NO MERCADO ---
with aba_mercado:
    # 1. Valor Total (Mais discreto)
    total_compra = st.session_state.carrinho["Total"].sum()
    st.markdown(f"""
        <div style="background-color:#0E1117; padding:10px; border-radius:10px; border: 1px solid #4CAF50; text-align:center;">
            <span style="color:#4CAF50; font-size:18px; font-weight:bold;">Total no Carrinho: R$ {total_compra:.2f}</span>
        </div>
    """, unsafe_allow_html=True)

    # 2. Gráfico e Resumo (SÓ APARECEM SE HOUVER ITENS)
    if not st.session_state.carrinho.empty:
        st.divider()
        c_graf, c_resumo = st.columns([1.5, 1])
        
        with c_graf:
            if PLOTLY_DISPONIVEL:
                resumo_df = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
                fig = px.pie(resumo_df, values='Total', names='Subclasse', hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with c_resumo:
            st.write("*Gasto por Categoria:*")
            resumo_texto = st.session_state.carrinho.groupby("Subclasse")["Total"].sum()
            for cat, valor in resumo_texto.items():
                st.write(f"• {cat}: R$ {valor:.2f}")

    st.divider()
    
    # 3. Busca e Lançamento (CAMPOS DE PREÇO E QTD APARECEM APÓS SELECIONAR)
    st.subheader("🔍 Localizar Produto")
    
    texto_busca = st.text_input("Digite o nome:", key=f"bus_{st.session_state.key_index}").strip().lower()
    
    lista_nomes = sorted(st.session_state.df_mestre["Produto"].tolist())
    filtro = [p for p in lista_nomes if texto_busca in p.lower()] if texto_busca else lista_nomes
    
    escolha = st.selectbox(f"Resultados ({len(filtro)}):", options=filtro, index=None, 
                          placeholder="Clique para escolher...", key=f"sel_{st.session_state.key_index}")

    if escolha:
        # Pega a categoria do produto escolhido
        linha = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        cat_escolhida = linha["Subclasse"].values[0] if not linha.empty else "OUTROS"
        
        st.info(f"📍 Categoria: {cat_escolhida}")
        
        # CAMPOS DE DIGITAÇÃO QUE VOCÊ SENTIU FALTA:
        col_q, col_p = st.columns(2)
        with col_q:
            qtd = st.number_input("Quantidade:", min_value=0.01, value=1.0, step=0.1)
        with col_p:
            preco = st.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        if st.button("🛒 ADICIONAR AO CARRINHO", use_container_width=True):
            if preco > 0:
                novo_item = pd.DataFrame([{
                    "Produto": escolha, "Subclasse": cat_escolhida, 
                    "Qtd": qtd, "Preço": preco, "Total": qtd * preco
                }])
                st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
                st.session_state.key_index += 1 # Reseta a busca
                st.rerun()
            else:
                st.warning("Insira o preço antes de confirmar!")

    # 4. Lista do Carrinho
    if not st.session_state.carrinho.empty:
        st.divider()
        st.write("### 📝 Itens Lançados")
        # Editor para o carrinho (permite deletar linhas selecionando e apertando 'Delete')
        car_editado = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, key="edit_carrinho")
        
        if not car_editado.equals(st.session_state.carrinho):
            st.session_state.carrinho = car_editado
            st.rerun()

        if st.button("🗑️ LIMPAR TODA A COMPRA", use_container_width=True):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
