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

# --- FRASES MOTIVACIONAIS ALEATÓRIAS ---
FRASES_MOTIVACIONAIS = [
    "🔥 Cada questão resolvida é um passo a mais rumo ao seu cargo público!",
    "🚀 A constância vence o talento. Mantenha o ritmo!",
    "🛡️ A Defensoria Pública espera por você. Mantenha o foco!",
    "💡 O erro de hoje é a sua questão certa na prova de amanhã!",
    "🏆 A sua aprovação é construída bloco a bloco. Força nos estudos!"
]

# --- NAVEGAÇÃO E AUTENTICAÇÃO NA BARRA LATERAL ---
st.sidebar.title("📌 Menu Principal")

menu_principal = st.sidebar.radio(
    "Navegue pelas telas:", 
    [
        "🏋️‍♂️ Executar Circuito", 
        "📊 Painel de Desempenho", 
        "🧠 Flashcards & Recorrências", 
        "⚙️ Gerenciar Disciplinas"
    ]
)

st.sidebar.markdown("---")
st.sidebar.title("🔑 Área do Usuário")

if "user" not in st.session_state:
    st.session_state["user"] = None

if supabase is None:
    st.sidebar.error("Erro ao conectar com o Supabase. Verifique as credenciais.")
else:
    if st.session_state["user"] is None:
        aba_auth = st.sidebar.radio("Sua Conta:", ["Entrar", "Criar Conta"])
        
        email_input = st.sidebar.text_input("E-mail")
        senha_input = st.sidebar.text_input("Senha", type="password")
        
        if aba_auth == "Criar Conta":
            if st.sidebar.button("Cadastrar 🚀"):
                try:
                    res = supabase.auth.sign_up({"email": email_input, "password": senha_input})
                    st.sidebar.success("Conta criada! Faça login para continuar.")
                except Exception as e:
                    st.sidebar.error(f"Erro no cadastro: {e}")
        else:
            if st.sidebar.button("Entrar ✨"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
                    st.session_state["user"] = res.user
                    st.sidebar.success("Bem-vindo de volta! 🎯")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error("E-mail ou senha incorretos.")
    else:
        st.sidebar.success(f"⚡ Conectado como: {st.session_state['user'].email}")
        if st.sidebar.button("Sair da Conta 👋"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()

# --- CABEÇALHO PRINCIPAL ANIMADO ---
st.title("⚡ Circuito de Estudos de Alta Performance")
st.caption(f"💬 *{random.choice(FRASES_MOTIVACIONAIS)}*")

# --- DISCIPLINAS PADRÃO ---
if "disciplinas" not in st.session_state:
    st.session_state.discipl
