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

# Ajuste preventivo de índice para evitar KeyError
if st.session_state.disciplinas:
    st.session_state.indice_atual = st.session_state.indice_atual % len(st.session_state.disciplinas)

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


# ==========================================
# TELA 1: EXECUTAR CIRCUITO
# ==========================================
if menu_principal == "🏋️‍♂️ Executar Circuito":
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
                    st.success(f"🎉 SENSACIONAL! Aproveitamento de **{aproveitamento_bloco:.0f}%**! Você está indo muito bem!")
                elif aproveitamento_bloco >= 60:
                    st.success(f"👏 Muito bem! **{aproveitamento_bloco:.0f}%** de aproveitamento. Mantenha o ritmo!")
                else:
                    st.warning(f"💪 **{aproveitamento_bloco:.0f}%** de aproveitamento. É hora de registrar os erros nos flashcards e ajustar!")

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
    st.subheader("📈 Painel de Evolução e Estatísticas")

    if st.session_state["user"] is None:
        st.warning("⚠️ Faça login na barra lateral para carregar seu painel com histórico completo.")
    else:
        if supabase:
            try:
                res = supabase.table("historico_estudos").select("*").eq("user_id", st.session_state["user"].id).execute()
                dados = res.data

                if not dados:
                    st.info("📭 Nenhum bloco registrado ainda. Complete sua primeira série na tela do circuito!")
                else:
                    df =
