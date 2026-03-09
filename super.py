# Função para carregar dados salvos
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        # Se o arquivo não existir, carrega sua lista inicial de 74 itens
        dados_iniciais = {
            "Produto": [
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
            ],
            "Subclasse": ["BÁSICO"] * 74  # Inicialmente tudo como BÁSICO para você editar
        }
        return pd.DataFrame(dados_iniciais)

# Inicializa o estado do app
if 'df_mestre' not in st.session_state:
    st.session_state.df_mestre = carregar_dados()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])

# --- 2. INTERFACE ---
st.title("🛒 Supermercado Inteligente")

aba_mercado, aba_config = st.tabs(["🛍️ No Mercado", "⚙️ Configurar Lista Permanentemente"])

# --- ABA DE CONFIGURAÇÃO (MEMÓRIA PERMANENTE) ---
with aba_config:
    st.subheader("Configuração da sua Lista Mestra")
    st.info("As alterações feitas aqui serão salvas no arquivo definitivo.")
    
    # Editor da tabela
    df_editado = st.data_editor(
        st.session_state.df_mestre,
        column_config={
            "Subclasse": st.column_config.SelectboxColumn("Subclasse", options=SUBCLASSES)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_permanente"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 SALVAR ALTERAÇÕES DEFINITIVAMENTE"):
            st.session_state.df_mestre = df_editado
            st.session_state.df_mestre.to_csv(ARQUIVO_DADOS, index=False)
            st.success("Lista salva com sucesso no arquivo!")
            st.rerun()
            
    with col_btn2:
        st.warning("Aperte o botão acima após editar para não perder as mudanças.")

# --- ABA NO MERCADO ---
with aba_mercado:
    total_compra = st.session_state.carrinho["Total"].sum()
    st.metric("VALOR NO CARRINHO", f"R$ {total_compra:.2f}")

    # Seleção do produto
    lista_busca = sorted(st.session_state.df_mestre["Produto"].unique().tolist())
    escolha = st.selectbox("Localizar Produto:", options=lista_busca, index=None, placeholder="Digite o nome...")

    if escolha:
        sub_item = st.session_state.df_mestre.loc[st.session_state.df_mestre["Produto"] == escolha, "Subclasse"].values[0]
        st.caption(f"Subclasse: {sub_item}")
        
        col_q, col_p = st.columns(2)
        with col_q:
            q_in = st.number_input("Qtd:", min_value=0.01, value=1.0, step=0.1)
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
        st.data_editor(st.session_state.carrinho, use_container_width=True, hide_index=True)
        
        # Resumo com %
        with st.expander("📊 RESUMO POR SUBCLASSE", expanded=True):
            res = st.session_state.carrinho.groupby("Subclasse")["Total"].sum().reset_index()
            res["%"] = ((res["Total"] / total_compra) * 100).round(1).astype(str) + "%"
            res["Total"] = res["Total"].map("R$ {:.2f}".format)
            st.table(res)

        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = pd.DataFrame(columns=["Produto", "Subclasse", "Qtd", "Preço", "Total"])
            st.rerun() continuar outro
            <!--end list_
