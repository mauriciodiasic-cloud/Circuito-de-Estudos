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
st.title("⚖️ Circuito de Estudos de Alto Rendimiento")
st.markdown("*Foco na aprovação: Disciplina, volume de questões, percentual de acertos e caderno de erros integrado.*")

menu_principal = st.radio(
    "Navegação", 
    ["🏋️‍♂️ Executar Circuito de Questões", "📊 Painel de Desempenho & Histórico", "⚙️ Gerenciar Disciplinas"],
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
if menu_principal == "🏋️‍♂️ Executar Circuito de Questões":
    if st.session_state["user"] is None:
        st.warning("⚠️ Você está operando no modo local. Faça login na barra lateral para salvar seu histórico e desempenho permanentemente na nuvem.")

    if st.session_state.disciplinas:
        disc_atual = st.session_state.disciplinas[st.session_state.indice_atual]
        serie_atual = st.session_state.series_concluidas[disc_atual]

        # Caixa de destaque visual para o treino atual
        st.info(f"👉 **Aparelho / Matéria Atual:** `{disc_atual}`  |  📌 **Série:** `{serie_atual}`")

        with st.form("form_bloco"):
            st.subheader("📝 Registrar Bloco de Questões Concluído")
            col1, col2 = st.columns(2)
            with col1:
                feitas = st.number_input("Questões Feitas neste Bloco", min_value=1, value=15, step=1)
            with col2:
                acertos = st.number_input("Questões Acertadas", min_value=0, max_value=feitas, value=12, step=1)

            erros_txt = st.text_area("📌 Caderno de Erros (O que errou e por quê? Ex: Jurisprudência do STJ, pegadinha de prazo):", placeholder="Anote o fundamento legal ou jurisprudencial que caiu...")

            enviar_bloco = st.form_submit_button("✅ Concluir Série e Avançar no Circuito ➡️")

            if enviar_bloco:
                # Salva no Supabase se logado
                if st.session_state["user"] and supabase:
                    try:
                        dados = {
                            "user_id": st.session_state["user"].id,
                            "disciplina": disc_atual,
                            "feitas": feitas,
                            "acertos": acertos,
                            "erros": erros_txt if erros_txt.strip() else None
                        }
                        supabase.table("historico_estudos").insert(dados).execute()
                        st.success("🎯 Desempenho gravado com sucesso na nuvem!")
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco: {e}")
                else:
                    st.success("🎯 Bloco concluído (faça login para persistir dados na nuvem)!")

                # Atualiza o circuito rotativo
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
# ABA 2: PAINEL DE DESEMPENHO & HISTÓRICO
# ==========================================
elif menu_principal == "📊 Painel de Desempenho & Histórico":
    st.subheader("📈 Painel Analítico de Evolução")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login na barra lateral para visualizar o seu histórico salvo na nuvem.")
    else:
        if supabase:
            try:
                # Buscar dados do usuário logado
                res = supabase.table("historico_estudos").select("*").eq("user_id", st.session_state["user"].id).execute()
                dados = res.data

                if not dados:
                    st.info("📭 Nenhum bloco de estudos registado até ao momento. Conclua algumas séries na aba inicial para ver as estatísticas!")
                else:
                    df = pd.DataFrame(dados)
                    
                    # Métricas Gerais
                    total_feitas = df["feitas"].sum()
                    total_acertos = df["acertos"].sum()
                    aproveitamento_geral = (total_acertos / total_feitas) * 100 if total_feitas > 0 else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("📚 Total de Questões Feitas", total_feitas)
                    c2.metric("🎯 Acertos Totais", total_acertos)
                    c3.metric("📊 Aproveitamento Global", f"{aproveitamento_geral:.1f}%")

                    st.markdown("---")
                    st.subheader("📊 Desempenho por Disciplina")

                    # Agrupar por disciplina
                    resumo_disc = df.groupby("disciplina")[["feitas", "acertos"]].sum().reset_index()
                    resumo_disc["Aproveitamento (%)"] = (resumo_disc["acertos"] / resumo_disc["feitas"] * 100).round(1)
                    resumo_disc = resumo_disc.sort_values(by="Aproveitamento (%)", ascending=False)

                    # Exibir tabela formatada
                    st.dataframe(resumo_disc, use_container_width=True)

                    # Alertas de Dificuldade vs Evolução
                    st.markdown("### 💡 Diagnóstico de Alta Performance")
                    melhor = resumo_disc.iloc[0] if not resumo_disc.empty else None
                    pior = resumo_disc.iloc[-1] if not resumo_disc.empty else None

                    if melhor is not None and pior is not None:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.success(f"🏆 **Ponto Forte:** `{melhor['disciplina']}`\n\nAproveitamento excelente de **{melhor['Aproveitamento (%)']}%**. Continue mantendo o ritmo!")
                        with col_b:
                            st.error(f"⚠️ **Atenção (Maior Dificuldade):** `{pior['disciplina']}`\n\nAproveitamento de **{pior['Aproveitamento (%)']}%**. Recomenda-se focar mais tempo no Caderno de Erros desta matéria.")

                    st.markdown("---")
                    st.subheader("📓 Caderno de Erros & Histórico Completo")
                    
                    # Filtrar por disciplina se desejar
                    filtro_disc = st.selectbox("Filtrar Histórico por Disciplina:", ["Todas"] + list(df["disciplina"].unique()))
                    if filtro_disc != "Todas":
                        df_filtrado = df[df["disciplina"] == filtro_disc]
                    else:
                        df_filtrado = df

                    # Exibir tabela detalhada
                    for index, row in df_filtrado.iterrows():
                        porc = (row["acertos"] / row["feitas"]) * 100 if row["feitas"] > 0 else 0
                        with st.expander(f"📌 {row['data'][:10]} | {row['disciplina']} — Acertos: {row['acertos']}/{row['feitas']} ({porc:.0f}%)"):
                            if row["erros"]:
                                st.markdown(f"**Motivo do Erro / Anotação:**\n> {row['erros']}")
                            else:
                                st.markdown("*Nenhum registo de erro específico para este bloco.*")

            except Exception as e:
                st.error(f"Erro ao carregar dados do painel: {e}")


# ==========================================
# ABA 3: GERENCIAR DISCIPLINAS
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
