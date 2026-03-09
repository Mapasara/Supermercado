[07:56, 09/03/2026] Mapasara Meta Digital: import streamlit as st
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
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            if not df.empty:
                return df
        except:
            pass
    
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
        "Produto": produtos_lista,
        "Subclasse": ["BÁSICO"] * len(produtos_lista)
    })

if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 2. INTERFACE ---
st.title("🛒 Gestor de Compras Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

with aba_config:
    st.subheader("Sua Lista de Produtos")
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={"Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES)},
        num_rows="dynamic",
        use_container_width=True,
        key="editor_config_v3"
    )
    
    if st.button("💾 SALVAR LISTA DEFINITIVAMENTE", use_container_width=True):
        st.session_state.df_mestre = df_editado
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista gravada com sucesso!")
        st.rerun()

with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR TOTAL NO CARRINHO", f"R$ {total_compra:.2f}")

    lista_busca = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    escolha = st.selectbox("Buscar Produto:", options=lista_busca, index=None)

    if escolha:
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
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        carrinho_atualizado = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
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
[08:22, 09/03/2026] Mapasara Meta Digital: Salvo subclasse na   aba "configurar lista" e não salva automaticamente na aba Mercado  no buscar produtos e no resumo  por subclasse.

Algumas das subclasses definidas na aba "configurar lista" não são salvas na aba "no mercado"



Escolha inteligente na aba configurar lista, na parte de produtos


Aplicativo trava na hora de digitar produto

Apagar o nome do produto na busca inteligente  anterior
[08:24, 09/03/2026] Mapasara Meta Digital: import streamlit as st
import pandas as pd
import os

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
    
    # Lista inicial padrão
    produtos_lista = ["Arroz", "Feijão", "Açúcar", "Café", "Leite", "Óleo", "Cebola", "Tomate"]
    return pd.DataFrame({
        "Produto": sorted(produtos_lista),
        "Subclasse": ["BÁSICO"] * len(produtos_lista)
    })

# Inicialização do estado
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 2. INTERFACE ---
st.title("🛒 Gestor de Compras Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista"])

# --- ABA DE CONFIGURAÇÃO (SALVAMENTO REAL) ---
with aba_config:
    st.subheader("⚙️ Gestão da Lista Mestra")
    st.info("⚠️ Após editar, você PRECISA clicar no botão SALVAR abaixo para atualizar o Mercado.")
    
    # Editor da tabela
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES, required=True),
            "Produto": st.column_config.TextColumn("Nome do Produto", required=True)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_config_v4"
    )
    
    if st.button("💾 SALVAR ALTERAÇÕES AGORA", use_container_width=True):
        # Atualiza a memória e o arquivo físico
        st.session_state.df_mestre = df_editado.drop_duplicates(subset=['Produto'])
        st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
        st.success("✅ Lista atualizada! Agora a aba 'No Mercado' já conhece as novas subclasses.")
        st.rerun()

# --- ABA NO MERCADO (USO PRÁTICO) ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR TOTAL NO CARRINHO", f"R$ {total_compra:.2f}")

    st.subheader("🔍 Lançar Produto")
    
    # IMPORTANTE: Pegamos os nomes SEMPRE do df_mestre atualizado
    opcoes_produtos = sorted(st.session_state.df_mestre["Produto"].tolist())
    
    # Criamos uma chave única que muda quando inserimos algo para "resetar" o campo
    if "reset_busca" not in st.session_state:
        st.session_state.reset_busca = 0

    escolha = st.selectbox(
        "Buscar na lista:", 
        options=opcoes_produtos, 
        index=None, 
        placeholder="Digite para filtrar...",
        key=f"busca_{st.session_state.reset_busca}" 
    )

    if escolha:
        # Busca a subclasse correta no df_mestre (garante sincronia)
        linha_prod = st.session_state.df_mestre[st.session_state.df_mestre["Produto"] == escolha]
        sub_identificada = linha_prod["Subclasse"].values[0] if not linha_prod.empty else "BÁSICO"
        
        st.info(f"Categoria detectada: *{sub_identificada}*")
        
        col_q, col_p = st.columns(2)
        with col_q:
            qtd_in = st.number_input("Quantidade:", min_value=0.0, value=1.0, step=0.1)
        with col_p:
            # Otimizado para não travar: o valor inicial é 0.0
            preco_in = st.number_input("Preço Unitário (R$):", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        if st.button("🛒 CONFIRMAR LANÇAMENTO", use_container_width=True):
            novo_item = pd.DataFrame([{
                "Produto": escolha, 
                "Subclasse": sub_identificada, 
                "Qtd": qtd_in, 
                "Preço": preco_in, 
                "Total": qtd_in * preco_in
            }])
            st.session_state.carrinho = pd.concat([st.session_state.carrinho, novo_item], ignore_index=True)
            
            # AQUI O SEGREDO: Mudamos a chave da busca para ela "limpar" sozinha
            st.session_state.reset_busca += 1
            st.toast(f"Adicionado: {escolha}")
            st.rerun()

    st.divider()
    
    if not st.session_state.carrinho.empty:
        st.write("### 📝 Itens no Carrinho")
        # Carrinho com opção de deletar linhas
        carrinho_final = st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True, num_rows="fixed")
        
        if not carrinho_final.equals(st.session_state.carrinho):
            st.session_state.carrinho = carrinho_final
            st.rerun()
            
        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            res = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            if total_compra > 0:
                res["%"] = ((res["Total"] / total_compra) * 100).round(1).astype(str) + "%"
            res["Total"] = res["Total"].map("R$ {:.2f}".format)
            st.table(res)

        if st.button("🗑️ Esvaziar Tudo"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun()
