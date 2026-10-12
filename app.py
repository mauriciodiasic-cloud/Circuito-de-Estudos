import streamlit as st
import pandas as pd
import random
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA E PWA ---
st.set_page_config(
    page_title="Circuito de Estudos - Rumo à Aprovação! 🚀", 
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

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
    <style>
    /* Fundo e tipografia geral */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    /* Títulos vibrantes */
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

# --- INICIALIZAÇÃO SEGURA DO SESSION STATE ---
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

if "user" not in st.session_state:
    st.session_state["user"] = None

if "nome_preferido" not in st.session_state:
    st.session_state["nome_preferido"] = None

if "abrir_popup_nome" not in st.session_state:
    st.session_state["abrir_popup_nome"] = True

# Ajuste preventivo de índice para evitar erros de limites
if st.session_state.disciplinas:
    st.session_state.indice_atual = st.session_state.indice_atual % len(st.session_state.disciplinas)

# --- POPUP MODAL PARA DEFINIR O NOME ---
@st.dialog("👋 Boas-vindas ao Circuito de Estudos!")
def modal_definir_nome():
    st.write("Como você gostaria de ser chamado(a) durante a sua preparação?")
    nome_digitado = st.text_input("Seu nome ou apelido:", placeholder="Ex: Dr. Silva, Maria, DPE-RJ...")
    
    if st.button("Confirmar e Começar 🚀", use_container_width=True):
        if nome_digitado.strip():
            st.session_state["nome_preferido"] = nome_digitado.strip()
            st.session_state["abrir_popup_nome"] = False
            
            # Se estiver logado, atualiza o nome no perfil do Supabase
            if st.session_state["user"] and supabase:
                try:
                    supabase.auth.update_user({"data": {"full_name": nome_digitado.strip()}})
                except:
                    pass
            st.rerun()
        else:
            st.error("Por favor, digite um nome ou apelido para continuar.")

# Abrir popup se ainda não tiver nome definido
if st.session_state["nome_preferido"] is None and st.session_state["abrir_popup_nome"]:
    modal_definir_nome()

# Definição do nome do aluno
nome_aluno = st.session_state.get("nome_preferido") or "Concursando"

# --- NAVEGAÇÃO E AUTENTICAÇÃO NA BARRA LATERAL ---
st.sidebar.title("📌 Menu Principal")

menu_principal = st.sidebar.radio(
    "Navegue pelas telas:", 
    [
        "🏠 Início",
        "🏋️‍♂️ Executar Circuito", 
        "📊 Painel de Desempenho", 
        "🧠 Flashcards & Recorrências", 
        "⚙️ Gerenciar Disciplinas"
    ]
)

st.sidebar.markdown("---")
st.sidebar.title("🔑 Área do Usuário")

if supabase is None:
    st.sidebar.error("Erro ao conectar com o Supabase. Verifique as credenciais.")
else:
    if st.session_state["user"] is None:
        aba_auth = st.sidebar.radio("Sua Conta:", ["Entrar", "Criar Conta", "Esqueci a Senha"])
        
        if aba_auth == "Criar Conta":
            nome_input = st.sidebar.text_input("Seu Nome ou Apelido")
            email_input = st.sidebar.text_input("E-mail")
            senha_input = st.sidebar.text_input("Senha", type="password")
            
            if st.sidebar.button("Cadastrar 🚀"):
                if not nome_input.strip():
                    st.sidebar.error("Por favor, informe o seu nome para personalizar seus estudos.")
                elif len(senha_input) < 6:
                    st.sidebar.error("A senha deve ter pelo menos 6 caracteres.")
                else:
                    try:
                        res = supabase.auth.sign_up({
                            "email": email_input, 
                            "password": senha_input,
                            "options": {
                                "data": {
                                    "full_name": nome_input.strip()
                                }
                            }
                        })
                        st.session_state["nome_preferido"] = nome_input.strip()
                        st.sidebar.success("Conta criada com sucesso! Faça login para continuar.")
                    except Exception as e:
                        st.sidebar.error(f"Erro no cadastro: {e}")

        elif aba_auth == "Entrar":
            email_input = st.sidebar.text_input("E-mail")
            senha_input = st.sidebar.text_input("Senha", type="password")
            
            if st.sidebar.button("Entrar ✨"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
                    st.session_state["user"] = res.user
                    
                    user_metadata = getattr(res.user, "user_metadata", {}) or {}
                    nome_usuario = user_metadata.get("full_name", email_input.split("@")[0])
                    st.session_state["nome_preferido"] = nome_usuario
                    
                    st.sidebar.success(f"Bem-vindo(a) de volta, {nome_usuario}! 🎯")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error("E-mail ou senha incorretos. Tente novamente.")

        elif aba_auth == "Esqueci a Senha":
            st.sidebar.markdown("##### 🔑 Redefinição de Senha")
            email_recuperacao = st.sidebar.text_input("E-mail cadastrado")
            
            if st.sidebar.button("Enviar E-mail de Recuperação 📩"):
                if email_recuperacao.strip():
                    try:
                        supabase.auth.reset_password_for_email(email_recuperacao.strip())
                        st.sidebar.success("Enviamos um link de redefinição para o seu e-mail! Verifique sua caixa de entrada e spam.")
                    except Exception as e:
                        st.sidebar.error(f"Erro ao enviar e-mail: {e}")
                else:
                    st.sidebar.error("Digite o seu e-mail cadastrado.")
    else:
        st.sidebar.success(f"⚡ Conectado como: **{nome_aluno}**")
        if st.sidebar.button("Sair da Conta 👋"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.session_state["nome_preferido"] = None
            st.session_state["abrir_popup_nome"] = True
            st.rerun()

# --- FRASES MOTIVACIONAIS PERSONALIZADAS ---
FRASES_MOTIVACIONAIS = [
    f"🔥 Olá, {nome_aluno}! Cada questão resolvida é um passo a mais rumo ao seu cargo!",
    f"🚀 Bora estudar, {nome_aluno}! A constância vence qualquer desafio.",
    f"🛡️ A Defensoria Pública espera por você, {nome_aluno}! Mantenha o foco!",
    f"💡 Vamos com tudo, {nome_aluno}! O erro de hoje é a sua questão certa na prova!",
    f"🏆 Força nos estudos, {nome_aluno}! Sua aprovação está sendo construída agora."
]


# ==========================================
# TELA INITIAL: 🏠 INÍCIO
# ==========================================
if menu_principal == "🏠 Início":
    st.title(f"👋 Olá, {nome_aluno}!")
    st.caption(f"💬 *{random.choice(FRASES_MOTIVACIONAIS)}*")
    
    st.markdown("---")
    
    col_bem_vindo, col_config = st.columns([2, 1])
    
    with col_bem_vindo:
        st.subheader("🚀 Bem-vindo(a) ao seu Circuito de Estudos!")
        st.write("""
        Esta plataforma foi desenvolvida para potencializar a sua preparação para concursos públicos de alto nível:
        
        * 🏋️‍♂️ **Circuito Rotativo:** Mantenha um ritmo dinâmico e equilibrado passando por todas as disciplinas.
        * 📊 **Painel Analítico:** Acompanhe a sua porcentagem de acertos geral e por matéria em tempo real.
        * 🧠 **Caderno de Erros Inteligente:** Registre seus erros em 3 níveis (Disciplina, Assunto e Comentário) para identificar padrões e gargalos de estudo.
        """)
        
    with col_config:
        st.subheader("👤 Seu Nome no Aplicativo")
        st.info(f"Atualmente você está cadastrado(a) como: **{nome_aluno}**")
        if st.button("Alterar Apelido / Nome ✏️"):
            st.session_state["nome_preferido"] = None
            st.session_state["abrir_popup_nome"] = True
            st.rerun()

    st.markdown("---")
    st.subheader("⚡ Atalhos Rápidos")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.info("🏋️‍♂️ **Pronto para treinar?**\n\nInicie ou continue o seu circuito de questões.")
    with col_b:
        st.success("📊 **Quer ver sua evolução?**\n\nConfira suas métricas e gráficos de desempenho.")
    with col_c:
        st.warning("🧠 **Registrar uma falha?**\n\nAlimente o seu caderno de erros e acompanhe os assuntos mais frequentes.")


# ==========================================
# TELA 1: EXECUTAR CIRCUITO
# ==========================================
elif menu_principal == "🏋️‍♂️ Executar Circuito":
    st.title(f"⚡ Circuito de Estudos do(a) {nome_aluno}")
    st.caption(f"💬 *{random.choice(FRASES_MOTIVACIONAIS)}*")

    if st.session_state["user"] is None:
        st.warning("⚠️ Você está estudando no modo visitante. Faça login na barra lateral para salvar seu progresso permanentemente na nuvem!")

    if st.session_state.disciplinas:
        idx = st.session_state.indice_atual % len(st.session_state.disciplinas)
        disc_atual = st.session_state.disciplinas[idx]
        serie_atual = st.session_state.series_concluidas.get(disc_atual, 1)

        st.info(f"🎯 **Matéria / Bloco Atual:** `{disc_atual}`  |  🔥 **Série:** `{serie_atual}`")

        with st.form("form_bloco"):
            st.subheader("📝 Registrar Bloco de Questões Resolvidas")
            col1, col2 = st.columns(2)
            with col1:
                feitas = st.number_input("Questões Feitas", min_value=1, value=15, step=1)
            with col2:
                acertos = st.number_input("Questões Acertadas", min_value=0, max_value=feitas, value=12, step=1)

            enviar_bloco = st.form_submit_button("✅ Concluir Série e Avançar! 🚀")

            if enviar_bloco:
                aproveitamento_bloco = (acertos / feitas) * 100
                
                if aproveitamento_bloco >= 80:
                    st.balloons()
                    st.success(f"🎉 SENSACIONAL, {nome_aluno}! Aproveitamento de **{aproveitamento_bloco:.0f}%**! Você está voando!")
                elif aproveitamento_bloco >= 60:
                    st.success(f"👏 Muito bem, {nome_aluno}! **{aproveitamento_bloco:.0f}%** de aproveitamento. Mantenha o ritmo!")
                else:
                    st.warning(f"💪 **{aproveitamento_bloco:.0f}%** de aproveitamento. É hora de registrar os erros nos flashcards e ajustar, {nome_aluno}!")

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
                        st.error(f"Erro ao salvar dados: {e}")

                st.session_state.series_concluidas[disc_atual] = serie_atual + 1
                st.session_state.indice_atual = (idx + 1) % len(st.session_state.disciplinas)
                st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Sequência do Seu Circuito")
        for i, d in enumerate(st.session_state.disciplinas):
            marcador = "🔥 [ESTUDAR AGORA]" if i == (st.session_state.indice_atual % len(st.session_state.disciplinas)) else "✅"
            st.text(f"{marcador} {d} — Série {st.session_state.series_concluidas.get(d, 1)}")

    else:
        st.warning("Adicione disciplinas na aba de configurações para iniciar seu circuito de estudos!")


# ==========================================
# TELA 2: PAINEL DE DESEMPENHO
# ==========================================
elif menu_principal == "📊 Painel de Desempenho":
    st.subheader(f"📈 Painel de Evolução — {nome_aluno}")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login na barra lateral para carregar seu painel com histórico completo.")
    else:
        if supabase:
            try:
                res = supabase.table("historico_estudos").select("*").eq("user_id", st.session_state["user"].id).execute()
                dados = res.data

                if not dados:
                    st.info(f"📭 Nenhum bloco registrado ainda, {nome_aluno}. Complete sua primeira série na tela do circuito!")
                else:
                    df = pd.DataFrame(dados)
                    
                    total_feitas = df["feitas"].sum
