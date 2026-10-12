from datetime import datetime, timedelta
import random
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import Client, create_client

# --- CONFIGURAÇÃO DA PÁGINA E PWA ---
st.set_page_config(
    page_title="Circuito de Estudos - Rumo à Aprovação",
    page_icon="🔥",
    layout="wide",
)

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    h1 {
        background: linear-gradient(90deg, #FF7E5F, #FEB47B, #8A2387);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONFIGURAÇÃO DO SUPABASE ---
SUPABASE_URL = "https://hweawyyqnzavrhejaotv.supabase.co"
SUPABASE_KEY = (
    st.secrets.get("SUPABASE_KEY")
    if hasattr(st, "secrets") and "SUPABASE_KEY" in st.secrets
    else "sb_publishable_DN77kvZt5m7HgRDK8SMgUQ_PAlIRHjZ"
)


@st.cache_resource
def init_supabase():
  try:
    if not SUPABASE_KEY:
      return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)
  except Exception:
    return None


supabase: Client = init_supabase()

# --- DISCIPLINAS PADRÃO ---
DISCIPLINAS_PADRAO = [
    "Direito Constitucional",
    "Direito Administrativo",
    "Processo Civil",
    "Direito Civil",
    "Direito Penal",
    "Processo Penal",
    "E.C.A.",
    "Execução Penal",
    "Direitos Humanos",
    "Empresarial",
    "Direito do Consumidor",
]


# --- FUNÇÕES DE PERSISTÊNCIA DE PREFERÊNCIAS ---
def carregar_preferencias_usuario(user_id):
  if not supabase:
    return None
  try:
    res = (
        supabase.table("preferencias_usuario")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    if res.data and len(res.data) > 0:
      return res.data[0]
  except Exception:
    pass
  return None


def salvar_preferencias_usuario():
  if not supabase or st.session_state.get("user") is None:
    return
  user_id = st.session_state["user"].id
  dados_prefs = {
      "user_id": user_id,
      "disciplinas": st.session_state.disciplinas,
      "series_concluidas": st.session_state.series_concluidas,
      "indice_atual": st.session_state.indice_atual,
  }
  try:
    supabase.table("preferencias_usuario").upsert(dados_prefs).execute()
  except Exception:
    pass


# --- INICIALIZAÇÃO SEGURA DO SESSION STATE ---
if "user" not in st.session_state:
  st.session_state["user"] = None

if "nome_preferido" not in st.session_state:
  st.session_state["nome_preferido"] = "Concursando"

if "disciplinas" not in st.session_state:
  st.session_state.disciplinas = DISCIPLINAS_PADRAO.copy()

if "indice_atual" not in st.session_state:
  st.session_state.indice_atual = 0

if "series_concluidas" not in st.session_state:
  st.session_state.series_concluidas = {
      d: 1 for d in st.session_state.disciplinas
  }

# --- RECUPERAÇÃO AUTOMÁTICA DE SESSÃO E PREFERÊNCIAS ---
if supabase and st.session_state["user"] is None:
  try:
    current_session = supabase.auth.get_session()
    if current_session and getattr(current_session, "user", None):
      st.session_state["user"] = current_session.user
      user_metadata = (
          getattr(current_session.user, "user_metadata", {}) or {}
      )
      st.session_state["nome_preferido"] = user_metadata.get(
          "full_name",
          getattr(current_session.user, "email", "Concursando").split("@")[0],
      )

      prefs = carregar_preferencias_usuario(current_session.user.id)
      if prefs:
        st.session_state.disciplinas = prefs.get(
            "disciplinas", DISCIPLINAS_PADRAO.copy()
        )
        st.session_state.series_concluidas = prefs.get(
            "series_concluidas", {d: 1 for d in st.session_state.disciplinas}
        )
        st.session_state.indice_atual = prefs.get("indice_atual", 0)
  except Exception:
    pass

if st.session_state.disciplinas:
  st.session_state.indice_atual = st.session_state.indice_atual % len(
      st.session_state.disciplinas
  )

nome_aluno = st.session_state.get("nome_preferido") or "Concursando"

# --- NAVEGAÇÃO E AUTENTICAÇÃO NA BARRA LATERAL ---
st.sidebar.title("Menu Principal")

menu_principal = st.sidebar.radio(
    "Navegue pelas telas:",
    [
        "Início",
        "Executar Circuito",
        "Painel de Desempenho",
        "Flashcards e Recorrências",
        "Gerenciar Disciplinas",
    ],
)

st.sidebar.markdown("---")
st.sidebar.title("Área do Usuário")

if supabase is None:
  st.sidebar.warning("Modo Offline / Supabase não configurado.")
else:
  if st.session_state["user"] is None:
    aba_auth = st.sidebar.radio(
        "Sua Conta:", ["Entrar", "Criar Conta", "Esqueci a Senha"]
    )

    if aba_auth == "Criar Conta":
      nome_input = st.sidebar.text_input("Seu Nome ou Apelido")
      email_input = st.sidebar.text_input("E-mail")
      senha_input = st.sidebar.text_input("Senha", type="password")

      if st.sidebar.button("Cadastrar"):
        if not nome_input.strip():
          st.sidebar.error("Por favor, informe o seu nome.")
        elif len(senha_input) < 6:
          st.sidebar.error("A senha deve ter pelo menos 6 caracteres.")
        else:
          try:
            res = supabase.auth.sign_up({
                "email": email_input,
                "password": senha_input,
                "options": {"data": {"full_name": nome_input.strip()}},
            })
            st.session_state["nome_preferido"] = nome_input.strip()
            st.sidebar.success(
                "Conta criada com sucesso! Faça login para continuar."
            )
          except Exception as e:
            st.sidebar.error(f"Erro no cadastro: {e}")

    elif aba_auth == "Entrar":
      email_input = st.sidebar.text_input("E-mail")
      senha_input = st.sidebar.text_input("Senha", type="password")

      if st.sidebar.button("Entrar"):
        try:
          res = supabase.auth.sign_in_with_password(
              {"email": email_input, "password": senha_input}
          )
          st.session_state["user"] = res.user

          user_metadata = getattr(res.user, "user_metadata", {}) or {}
          nome_usuario = user_metadata.get(
              "full_name", email_input.split("@")[0]
          )
          st.session_state["nome_preferido"] = nome_usuario

          prefs = carregar_preferencias_usuario(res.user.id)
          if prefs:
            st.session_state.disciplinas = prefs.get(
                "disciplinas", DISCIPLINAS_PADRAO.copy()
            )
            st.session_state.series_concluidas = prefs.get(
                "series_concluidas",
                {d: 1 for d in st.session_state.disciplinas},
            )
            st.session_state.indice_atual = prefs.get("indice_atual", 0)

          st.sidebar.success(f"Bem-vindo(a) de volta, {nome_usuario}!")
          st.rerun()
        except Exception:
          st.sidebar.error("E-mail ou senha incorretos. Tente novamente.")

    elif aba_auth == "Esqueci a Senha":
      st.sidebar.markdown("Redefinição de Senha")
      email_recuperacao = st.sidebar.text_input("E-mail cadastrado")

      if st.sidebar.button("Enviar E-mail de Recuperação"):
        if email_recuperacao.strip():
          try:
            supabase.auth.reset_password_for_email(email_recuperacao.strip())
            st.sidebar.success("Enviamos um link de redefinição para o e-mail!")
          except Exception as e:
            st.sidebar.error(f"Erro ao enviar e-mail: {e}")
        else:
          st.sidebar.error("Digite o seu e-mail cadastrado.")
  else:
    st.sidebar.success(f"Conectado como: **{nome_aluno}**")
    if st.sidebar.button("Sair da Conta"):
      supabase.auth.sign_out()
      st.session_state["user"] = None
      st.session_state["nome_preferido"] = "Concursando"
      st.session_state.disciplinas = DISCIPLINAS_PADRAO.copy()
      st.rerun()

# --- FRASES MOTIVACIONAIS ---
FRASES_MOTIVACIONAIS = [
    f"Olá, {nome_aluno}! Cada questão resolvida é um passo rumo ao cargo!",
    f"Bora estudar, {nome_aluno}! A constância vence qualquer desafio.",
    f"A Defensoria Pública espera por você, {nome_aluno}! Mantenha o foco!",
]


# ==========================================
# TELA: INÍCIO
# ==========================================
if menu_principal == "Início":
  st.title(f"Olá, {nome_aluno}!")
  st.caption(f"*{random.choice(FRASES_MOTIVACIONAIS)}*")

  st.markdown("---")
  col_bem_vindo, col_config = st.columns([2, 1])

  with col_bem_vindo:
    st.subheader("Bem-vindo(a) ao seu Circuito de Estudos!")
    st.write(
        "Plataforma desenvolvida para potencializar a sua preparação para"
        " concursos públicos:\n- Circuito Rotativo: Mantenha um ritmo dinâmico"
        " passando por todas as disciplinas.\n- Painel Analítico: Acompanhe a"
        " sua porcentagem de acertos em tempo real.\n- Caderno de Erros:"
        " Registre seus erros para identificar gargalos de estudo."
    )

  with col_config:
    st.subheader("Como quer ser chamado(a)?")
    novo_nome = st.text_input("Digite seu nome ou apelido:", value=nome_aluno)

    if st.button("Salvar Meu Nome"):
      if novo_nome.strip():
        st.session_state["nome_preferido"] = novo_nome.strip()
        if st.session_state["user"] and supabase:
          try:
            supabase.auth.update_user(
                {"data": {"full_name": novo_nome.strip()}}
            )
          except Exception:
            pass
        st.success("Nome atualizado com sucesso!")
        st.rerun()
      else:
        st.error("Digite um nome válido.")


# ==========================================
# TELA: EXECUTAR CIRCUITO
# ==========================================
elif menu_principal == "Executar Circuito":
  st.
