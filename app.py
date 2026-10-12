import streamlit as st
import pandas as pd
import random
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA E PWA ---
st.set_page_config(
    page_title="Circuito de Estudos - Rumos à Aprovação! 🚀", 
    page_icon="🔥", 
    layout="wide"
)

st.markdown(
    """
    <link rel="manifest" href="app/static/manifest.json">
    <meta name="theme-color" content="#1E1E2E">
    """,
    unsafe_allow_html=True
)

# --- ESTILIZAÇÃO CSS CUSTOMIZADA (VISUAL ALEGRE, MODERNO E ANIMADO) ---
st.markdown("""
    <style>
    /* Fundo e tipografia geral */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    /* Titulos vibrantes */
    h1 {
        background: linear-gradient(90deg, #FF7E5F, #FEB47B, #8A2387);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Cartões interativos com efeito hover */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(138, 35, 135, 0.4);
        border-color: #FEB47B;
    }
    
    /* Botões vibrantes e animados */
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(37, 117, 252, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 20px rgba(37, 117, 252, 0.6) !important;
    }
    
    /* Banners informativos motivacionais */
    .stAlert {
        border-radius: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://hweawyyqnzavrhejaotv.supabase.co"
SUPABASE_KEY = "COLE_AQUI_A_SUA_ANON_KEY"  # <-- Insira a sua anon key aqui

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase: Client = init_supabase()

# --- FRASES MOTIVACIONAIS ALEATÓRIAS ---
FRASES_MOTIVACIONAIS = [
    "🔥 Cada questão resolvida é um passo mais perto do seu cargo!",
    "🚀 A consistência supera o talento. Continue no ritmo!",
    "🛡️ A Defensoria Pública espera por si. Mantenha o foco!",
    "💡 O erro de hoje é a sua questão certa na prova de amanhã!",
    "🏆 A sua aprovação constrói-se bloco a bloco. Força!"
]

# --- AUTENTICAÇÃO / LOGIN ---
st.sidebar.title("🔑 Acesso do Concursando")

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
            if st.sidebar.button("Cadastrar 🚀"):
                try:
                    res = supabase.auth.sign_up({"email": email_input, "password": senha_input})
                    st.sidebar.success("Conta criada! Faça login.")
                except Exception as e:
                    st.sidebar.error(f"Erro: {e}")
        else:
            if st.sidebar.button("Entrar ✨"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
                    st.session_state["user"] = res.user
                    st.sidebar.success("Bem-vindo de volta! 🎯")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error("Credenciais inválidas.")
    else:
        st.sidebar.success(f"⚡ Conectado: {st.session_state['user'].email}")
        if st.sidebar.button("Terminar Sessão 👋"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()

# --- CABEÇALHO PRINCIPAL ANIMADO ---
st.title("⚡ Circuito de Estudos de Alta Performance")
st.caption(f"💬 *{random.choice(FRASES_MOTIVACIONAIS)}*")

menu_principal = st.radio(
    "Navegação", 
    [
        "🏋️‍♂️ Executar Circuito", 
        "📊 Painel de Desempenho", 
        "🧠 Flashcards & Recorrências", 
        "⚙️ Gerenciar Disciplinas"
    ],
    horizontal=True
)

# --- DISCIPLINAS PADRÃO ---
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
        st.warning("⚠️ Operando em modo visitante. Faça login na barra lateral para salvar seu progresso permanentemente!")

    if st.session_state.disciplinas:
        disc_atual = st.session_state.disciplinas[st.session_state.indice_atual]
        serie_atual = st.session_state.series_concluidas[disc_atual]

        st.info(f"🎯 **Aparelho / Matéria Atual:** `{disc_atual}`  |  🔥 **Série Atual:** `{serie_atual}`")

        with st.form("form_bloco"):
            st.subheader("📝 Registrar Bloco de Questões")
            col1, col2 = st.columns(2)
            with col1:
                feitas = st.number_input("Questões Feitas", min_value=1, value=15, step=1)
            with col2:
                acertos = st.number_input("Questões Acertadas", min_value=0, max_value=feitas, value=12, step=1)

            enviar_bloco = st.form_submit_button("✅ Concluir Série e Avançar! 🚀")

            if enviar_bloco:
                aproveitamento_bloco = (acertos / feitas) * 100
                
                # Efeito animado festivo se tiver ótimo desempenho
                if aproveitamento_bloco >= 80:
                    st.balloons()
                    st.success(f"🎉 SENSACIONAL! Rendimento de **{aproveitamento_bloco:.0f}%**! Você está voando!")
                elif aproveitamento_bloco >= 60:
                    st.success(f"👏 Muito bem! **{aproveitamento_bloco:.0f}%** de aproveitamento. Mantém o ritmo!")
                else:
                    st.warning(f"💪 **{aproveitamento_bloco:.0f}%** de aproveitamento. Hora de revisar os erros e ajustar!")

                # Salvar no Supabase
                if st.session_state["user"] and supabase:
                    try:
                        dados = {
                            "user_id": st.session_state["user"].id,
                            "disciplina": disc_atual,
                            "feitas": feitas,
                            "acertos": acertos
                        }
                        supabase.table("historico_estudos").insert(dados).execute()
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

                st.session_state.series_concluidas[disc_atual] += 1
                st.session_state.indice_atual = (st.session_state.indice_atual + 1) % len(st.session_state.disciplinas)

        st.markdown("---")
        st.markdown("### 📋 Sequência do Circuito")
        for i, d in enumerate(st.session_state.disciplinas):
            marcador = "🔥 [A TREINAR AGORA]" if i == st.session_state.indice_atual else "✅"
            st.text(f"{marcador} {d} — Série {st.session_state.series_concluidas.get(d, 1)}")

    else:
        st.warning("Cadastre disciplinas na aba de configurações para iniciar!")


# ==========================================
# ABA 2: PAINEL DE DESEMPENHO
# ==========================================
elif menu_principal == "📊 Painel de Desempenho":
    st.subheader("📈 Painel de Evolução & Conquistas")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login para carregar seu painel de estatísticas salvas.")
    else:
        if supabase:
            try:
                res = supabase.table("historico_estudos").select("*").eq("user_id", st.session_state["user"].id).execute()
                dados = res.data

                if not dados:
                    st.info("📭 Nenhum treino registrado ainda. Complete sua primeira série na aba inicial!")
                else:
                    df = pd.DataFrame(dados)
                    
                    total_feitas = df["feitas"].sum()
                    total_acertos = df["acertos"].sum()
                    aproveitamento_geral = (total_acertos / total_feitas) * 100 if total_feitas > 0 else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("📚 Questões Resolvidas", f"{total_feitas:,}")
                    c2.metric("🎯 Total de Acertos", f"{total_acertos:,}")
                    c3.metric("🔥 Rendimento Global", f"{aproveitamento_geral:.1f}%")

                    # Barra de progresso visual
                    st.progress(min(int(aproveitamento_geral), 100))

                    st.markdown("---")
                    st.subheader("📊 Aproveitamento por Disciplina")

                    resumo_disc = df.groupby("disciplina")[["feitas", "acertos"]].sum().reset_index()
                    resumo_disc["Aproveitamento (%)"] = (resumo_disc["acertos"] / resumo_disc["feitas"] * 100).round(1)
                    resumo_disc = resumo_disc.sort_values(by="Aproveitamento (%)", ascending=False)

                    st.dataframe(resumo_disc, use_container_width=True)

                    st.markdown("### 💡 Diagnóstico Motivacional")
                    melhor = resumo_disc.iloc[0] if not resumo_disc.empty else None
                    pior = resumo_disc.iloc[-1] if not resumo_disc.empty else None

                    if melhor is not None and pior is not None:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.success(f"🏆 **Seu Maior Domínio:** `{melhor['disciplina']}`\n\nRendimento fantástico de **{melhor['Aproveitamento (%)']}%**!")
                        with col_b:
                            st.error(f"⚠️ **Oportunidade de Crescimento:** `{pior['disciplina']}`\n\nRendimento de **{pior['Aproveitamento (%)']}%**. Vamos turbinar os flashcards desta matéria!")

            except Exception as e:
                st.error(f"Erro ao carregar o painel: {e}")


# ==========================================
# ABA 3: FLASHCARDS & RECORRÊNCIAS
# ==========================================
elif menu_principal == "🧠 Flashcards & Recorrências":
    st.subheader("🧠 Caderno de Erros Inteligente")
    st.markdown("Transforme falhas em pontos fortes com organização de 3 níveis.")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login para salvar seus flashcards na nuvem.")
    else:
        with st.expander("➕ Adicionar Novo Flashcard / Erro", expanded=False):
            with st.form("form_fc"):
                disc_escolhida = st.selectbox("1️⃣ Disciplina:", st.session_state.disciplinas)
                assunto_livre = st.text_input("2️⃣ Assunto Especifico:", placeholder="Ex: Prisão Preventiva, ITD, Usucapião Familial...")
                comentario_erro = st.text_area("3️⃣ Comentário / Fundamento do Erro:", placeholder="O que pegou na questão? Qual o entendimento do STJ/STF?")
                
                if st.form_submit_button("Salvar Flashcard 💾"):
                    if assunto_livre.strip() and comentario_erro.strip() and supabase:
                        try:
                            dados_fc = {
                                "user_id": st.session_state["user"].id,
                                "disciplina": disc_escolhida,
                                "assunto": assunto_livre.strip(),
                                "pergunta_erro": assunto_livre.strip(),
                                "resposta_fundamento": comentario_erro
                            }
                            supabase.table("flashcards_erros").insert(dados_fc).execute()
                            st.success("🧠 Flashcard salvo com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")

        st.markdown("---")

        if supabase:
            try:
                res_fc = supabase.table("flashcards_erros").select("*").eq("user_id", st.session_state["user"].id).execute()
                lista_fc = res_fc.data

                if lista_fc:
                    df_fc = pd.DataFrame(lista_fc)
                    
                    st.subheader("🎯 Radar de Assuntos Mais Recorrentes")
                    if "assunto" in df_fc.columns:
                        df_fc["assunto_clean"] = df_fc["assunto"].fillna("Geral").str.strip().str.title()
                        recorrencia = df_fc.groupby(["disciplina", "assunto_clean"]).size().reset_index(name="Frequência")
                        recorrencia = recorrencia.sort_values(by="Frequência", ascending=False)

                        for _, row_g in recorrencia.head(3).iterrows():
                            st.warning(f"🔥 **{row_g['assunto_clean']}** ({row_g['disciplina']}) — Erro registrado `{row_g['Frequência']}x`. Reforce a leitura do texto legal e jurisprudência!")

                    st.markdown("---")
                    st.subheader("📚 Seus Flashcards")
                    
                    filtro_disc = st.selectbox("Filtrar Disciplina:", ["Todas"] + list(df_fc["disciplina"].unique()))
                    df_filtrado = df_fc if filtro_disc == "Todas" else df_fc[df_fc["disciplina"] == filtro_disc]

                    for idx, row in df_filtrado.iterrows():
                        assunto_txt = row.get('assunto', 'Geral')
                        with st.expander(f"📌 [{row['disciplina']}] — Assunto: {assunto_txt}"):
                            st.write(f"**Fundamento do Erro:**\n\n> {row['resposta_fundamento']}")
                            if st.button("🗑️ Excluir", key=f"del_{row['id']}"):
                                supabase.table("flashcards_erros").delete().eq("id", row['id']).execute()
                                st.rerun()
                else:
                    st.info("📭 Nenhum flashcard cadastrado ainda.")

            except Exception as e:
                st.error(f"Erro ao carregar flashcards: {e}")


# ==========================================
# ABA 4: GERENCIAR DISCIPLINAS
# ==========================================
else:
    st.subheader("⚙️ Configurar Circuito")
    
    nova_disc = st.text_input("Adicionar nova disciplina jurídica:")
    if st.button("Adicionar ao Circuito ✨") and nova_disc:
        if nova_disc not in st.session_state.disciplinas:
            st.session_state.disciplinas.append(nova_disc)
            st.session_state.series_concluidas[nova_disc] = 1
            st.success(f"'{nova_disc}' adicionada!")
            st.rerun()

    st.markdown("### Disciplinas Ativas:")
    for d in st.session_state.disciplinas:
        col1, col2 = st.columns([4, 1])
        col1.write(f"• **{d}** (Série: {st.session_state.series_concluidas.get(d, 1)})")
        if col2.button("Remover", key=f"rem_{d}"):
            st.session_state.disciplinas.remove(d)
            st.rerun()
