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

# --- ESTILIZAÇÃO CSS CUSTOMIZADA (VISUAL ALEGRE, MODERNO E ANIMADO) ---
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
    st.session_state["nome_preferido"] = "Concursando"

# Ajuste preventivo de índice para evitar erros de limites
if st.session_state.disciplinas:
    st.session_state.indice_atual = st.session_state.indice_atual % len(st.session_state.disciplinas)

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
        user_metadata = getattr(st.session_state["user"], "user_metadata", {}) or {}
        nome_exibicao = user_metadata.get("full_name", st.session_state.get("nome_preferido", "Concursando"))
        
        st.sidebar.success(f"⚡ Conectado como: **{nome_exibicao}**")
        if st.sidebar.button("Sair da Conta 👋"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.session_state["nome_preferido"] = "Concursando"
            st.rerun()

# --- OBTER NOME DO USUÁRIO ---
if st.session_state["user"]:
    user_meta = getattr(st.session_state["user"], "user_metadata", {}) or {}
    nome_aluno = user_meta.get("full_name", st.session_state.get("nome_preferido", "Futuro(a) Defensor(a)"))
else:
    nome_aluno = st.session_state.get("nome_preferido", "Concursando")

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
        st.subheader("👤 Como prefere ser chamado(a)?")
        novo_nome = st.text
