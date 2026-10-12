import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA E PWA ---
st.set_page_config(
    page_title="Circuito de Estudos - Defensoria & Carreiras Jurídicas", 
    page_icon="⚖️", 
    layout="wide"
)

st.markdown(
    """
    <link rel="manifest" href="app/static/manifest.json">
    <meta name="theme-color" content="#0e1117">
    """,
    unsafe_allow_html=True
)

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://hweawyyqnzavrhejaotv.supabase.co"
SUPABASE_KEY = "COLE_AQUI_A_SUA_ANON_KEY"  # <-- Certifique-se de que a sua chave está aqui

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase: Client = init_supabase()

# --- AUTENTICAÇÃO / LOGIN NA BARRA LATERAL ---
st.sidebar.title("🔑 Acesso do Aluno")

if "user" not in st.session_state:
    st.session_state["user"] = None

if supabase is None:
    st.sidebar.error("Erro ao conectar com o Supabase. Verifique as credenciais.")
else:
    if st.session_state["user"] is None:
        aba_auth = st.sidebar.radio("Conta:", ["Entrar", "Criar Conta"])
        
        email_input = st.sidebar.text_input("E-mail")
        senha_input = st.sidebar.text_input("Senha", type="password")
        
        if aba_auth == "Criar Conta":
            if st.sidebar.button("Cadastrar"):
                try:
                    res = supabase.auth.sign_up({"email": email_input, "password": senha_input})
                    st.sidebar.success("Conta criada! Faça login.")
                except Exception as e:
                    st.sidebar.error(f"Erro: {e}")
        else:
            if st.sidebar.button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
                    st.session_state["user"] = res.user
                    st.sidebar.success("Login efetuado!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error("Credenciais inválidas.")
    else:
        st.sidebar.success(f"Conectado: {st.session_state['user'].email}")
        if st.sidebar.button("Terminar Sessão"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()

# --- MENU DE NAVEGAÇÃO PRINCIPAL ---
st.title("⚖️ Circuito de Estudos de Alto Rendimento")
st.markdown("*Foco na aprovação: Disciplina, volume de questões, percentual de acertos, painel e flashcards independentes.*")

menu_principal = st.radio(
    "Navegação", 
    [
        "🏋️‍♂️ Executar Circuito", 
        "📊 Painel de Desempenho", 
        "🧠 Flashcards & Caderno de Erros", 
        "⚙️ Gerenciar Disciplinas"
    ],
    horizontal=True
)

# --- DISCIPLINAS PADRÃO PARA CONCURSOS ---
if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = [
        "Direito Constitucional", "Direito Administrativo", "Processo Civil", 
        "Direito Civil", "Direito Penal", "Processo Penal", "E.C.A.", 
        "Execução Penal", "Direitos Humanos", "Empresarial", "Direito do Consumidor"
    ]

if "indice_atual" not in st.session_state:
    st.session_state.indice_atual = 0

if "series_concluidas" not in st.session_state:
    st.session_state.series_concluidas = {d: 1 for d in st.session_state.disciplinas}


# ==========================================
# ABA 1: EXECUTAR CIRCUITO
# ==========================================
if menu_principal == "🏋️‍♂️ Executar Circuito":
    if st.session_state["user"] is None:
        st.warning("⚠️ Você está operando no modo local. Faça login na barra lateral para salvar seu progresso permanentemente na nuvem.")

    if st.session_state.disciplinas:
        disc_atual = st.session_state.disciplinas[st.session_state.indice_atual]
        serie_atual = st.session_state.series_concluidas[disc_atual]

        st.info(f"👉 **Aparelho / Matéria Atual:** `{disc_atual}`  |  📌 **Série:** `{serie_atual}`")

        with st.form("form_bloco"):
            st.subheader("📝 Registrar Bloco de Questões Concluído")
            col1, col2 = st.columns(2)
            with col1:
                feitas = st.number_input("Questões Feitas neste Bloco", min_value=1, value=15, step=1)
            with col2:
                acertos = st.number_input("Questões Acertadas", min_value=0, max_value=feitas, value=12, step=1)

            enviar_bloco = st.form_submit_button("✅ Concluir Série e Avançar no Circuito ➡️")

            if enviar_bloco:
                if st.session_state["user"] and supabase:
                    try:
                        dados = {
                            "user_id": st.session_state["user"].id,
                            "disciplina": disc_atual,
                            "feitas": feitas,
                            "acertos": acertos,
                            "erros": None
                        }
                        supabase.table("historico_estudos").insert(dados).execute()
                        st.success("🎯 Desempenho gravado com sucesso na nuvem!")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco: {e}")
                else:
                    st.success("🎯 Bloco concluído (faça login para persistir dados na nuvem)!")

                st.session_state.series_concluidas[disc_atual] += 1
                st.session_state.indice_atual = (st.session_state.indice_atual + 1) % len(st.session_state.disciplinas)
                st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Status Atual do Circuito")
        for i, d in enumerate(st.session_state.disciplinas):
            marcador = "🔥 [TREINO ATUAL]" if i == st.session_state.indice_atual else "✅"
            st.text(f"{marcador} {d} — Série {st.session_state.series_concluidas.get(d, 1)}")

    else:
        st.warning("Adicione disciplinas na aba de configurações para iniciar o circuito.")


# ==========================================
# ABA 2: PAINEL DE DESEMPENHO
# ==========================================
elif menu_principal == "📊 Painel de Desempenho":
    st.subheader("📈 Painel Analítico de Evolução")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login na barra lateral para visualizar o seu histórico salvo na nuvem.")
    else:
        if supabase:
            try:
                res = supabase.table("historico_estudos").select("*").eq("user_id", st.session_state["user"].id).execute()
                dados = res.data

                if not dados:
                    st.info("📭 Nenhum bloco de estudos registado até ao momento. Conclua algumas séries na aba inicial!")
                else:
                    df = pd.DataFrame(dados)
                    
                    total_feitas = df["feitas"].sum()
                    total_acertos = df["acertos"].sum()
                    aproveitamento_geral = (total_acertos / total_feitas) * 100 if total_feitas > 0 else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("📚 Total de Questões Feitas", total_feitas)
                    c2.metric("🎯 Acertos Totais", total_acertos)
                    c3.metric("📊 Aproveitamento Global", f"{aproveitamento_geral:.1f}%")

                    st.markdown("---")
                    st.subheader("📊 Desempenho por Disciplina")

                    resumo_disc = df.groupby("disciplina")[["feitas", "acertos"]].sum().reset_index()
                    resumo_disc["Aproveitamento (%)"] = (resumo_disc["acertos"] / resumo_disc["feitas"] * 100).round(1)
                    resumo_disc = resumo_disc.sort_values(by="Aproveitamento (%)", ascending=False)

                    st.dataframe(resumo_disc, use_container_width=True)

                    st.markdown("### 💡 Diagnóstico de Alta Performance")
                    melhor = resumo_disc.iloc[0] if not resumo_disc.empty else None
                    pior = resumo_disc.iloc[-1] if not resumo_disc.empty else None

                    if melhor is not None and pior is not None:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.success(f"🏆 **Ponto Forte:** `{melhor['disciplina']}`\n\nAproveitamento de **{melhor['Aproveitamento (%)']}%**.")
                        with col_b:
                            st.error(f"⚠️ **Atenção (Maior Dificuldade):** `{pior['disciplina']}`\n\nAproveitamento de **{pior['Aproveitamento (%)']}%**. Foque nos Flashcards desta matéria!")

            except Exception as e:
                st.error(f"Erro ao carregar dados do painel: {e}")


# ==========================================
# ABA 3: FLASHCARDS & CADERNO DE ERROS (INDEPENDENTE)
# ==========================================
elif menu_principal == "🧠 Flashcards & Caderno de Erros":
    st.subheader("🧠 Gestão Independente de Flashcards e Caderno de Erros")
    st.markdown("Cadastre de forma livre os pontos de atenção, súmulas, jurisprudências ou pegadinhas que errou em simulados externos, e consulte-os por disciplina.")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login na barra lateral para criar e sincronizar os seus flashcards na nuvem.")
    else:
        # Seção de Cadastro Independente
        with st.expander("➕ Adicionar Novo Flashcard / Erro", expanded=True):
            with st.form("form_flashcard"):
                disc_fc = st.selectbox("Disciplina:", st.session_state.disciplinas)
                pergunta_fc = st.text_input("Pegadinha / Pergunta / Tema do Erro:", placeholder="Ex: Prazo para embargos infringentes no CPC...")
                resposta_fc = st.text_area("Explicação / Fundamento Legal / Jurisprudência correta:", placeholder="Ex: Art. 1.009 do CPC... Súmula X do STJ...")
                
                salvar_fc = st.form_submit_button("Salvar Flashcard 💾")

                if salvar_fc:
                    if pergunta_fc.strip() and resposta_fc.strip() and supabase:
                        try:
                            dados_fc = {
                                "user_id": st.session_state["user"].id,
                                "disciplina": disc_fc,
                                "pergunta_erro": pergunta_fc,
                                "resposta_fundamento": resposta_fc
                            }
                            supabase.table("flashcards_erros").insert(dados_fc).execute()
                            st.success("🧠 Flashcard guardado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar flashcard: {e}")
                    else:
                        st.error("Preencha todos os campos obrigatórios.")

        st.markdown("---")
        st.subheader("📚 Meus Flashcards Cadastrados")

        if supabase:
            try:
                res_fc = supabase.table("flashcards_erros").select("*").eq("user_id", st.session_state["user"].id).execute()
                lista_fc = res_fc.data

                if not lista_fc:
                    st.info("📭 Nenhum flashcard cadastrado ainda. Use o formulário acima para adicionar os seus erros e revisões!")
                else:
                    df_fc = pd.DataFrame(lista_fc)
                    
                    filtro_fc_disc = st.selectbox("Filtrar Flashcards por Disciplina:", ["Todas"] + list(df_fc["disciplina"].unique()))
                    if filtro_fc_disc != "Todas":
                        df_fc_filtrado = df_fc[df_fc["disciplina"] == filtro_fc_disc]
                    else:
                        df_fc_filtrado = df_fc

                    for idx, row in df_fc_filtrado.iterrows():
                        with st.expander(f"📌 [{row['disciplina']}] {row['pergunta_erro']}"):
                            st.markdown(f"**Fundamento / Resposta Correta:**\n> {row['resposta_fundamento']}")
                            
                            if st.button("🗑️ Excluir Flashcard", key=f"del_fc_{row['id']}"):
                                try:
                                    supabase.table("flashcards_erros").delete().eq("id", row['id']).execute()
                                    st.success("Flashcard removido!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {e}")

            except Exception as e:
                st.error(f"Erro ao carregar flashcards: {e}")


# ==========================================
# ABA 4: GERENCIAR DISCIPLINAS
# ==========================================
else:
    st.subheader("⚙️ Personalizar Circuito de Estudos")
    
    nova_disc = st.text_input("Adicionar nova disciplina jurídica:")
    if st.button("Adicionar ao Circuito") and nova_disc:
        if nova_disc not in st.session_state.disciplinas:
            st.session_state.disciplinas.append(nova_disc)
            st.session_state.series_concluidas[nova_disc] = 1
            st.success(f"'{nova_disc}' adicionada com sucesso!")
            st.rerun()

    st.markdown("### Disciplinas Atuais no Sistema:")
    for d in st.session_state.disciplinas:
        col_d1, col_d2 = st.columns([4, 1])
        col_d1.markdown(f"• **{d}** (Série atual: {st.session_state.series_concluidas.get(d, 1)})")
        if col_d2.button("Remover", key=f"rem_{d}"):
            st.session_state.disciplinas.remove(d)
            st.rerun()
