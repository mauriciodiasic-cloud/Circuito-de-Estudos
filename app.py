import random
import pandas as pd
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
        padding: 10px 24px !important;
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

# --- INICIALIZAÇÃO SEGURA DO SESSION STATE ---
if "disciplinas" not in st.session_state:
  st.session_state.disciplinas = [
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

if "indice_atual" not in st.session_state:
  st.session_state.indice_atual = 0

if "series_concluidas" not in st.session_state:
  st.session_state.series_concluidas = {
      d: 1 for d in st.session_state.disciplinas
  }

if "user" not in st.session_state:
  st.session_state["user"] = None

if "nome_preferido" not in st.session_state:
  st.session_state["nome_preferido"] = "Concursando"

# --- RECUPERAÇÃO AUTOMÁTICA DE SESSÃO DO SUPABASE ---
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
  st.title(f"Circuito de Estudos - {nome_aluno}")

  if st.session_state["user"] is None:
    st.warning(
        "Você está no modo visitante. Faça login para salvar seu progresso na"
        " nuvem!"
    )

  if st.session_state.disciplinas:
    idx = st.session_state.indice_atual % len(st.session_state.disciplinas)
    disc_atual = st.session_state.disciplinas[idx]
    serie_atual = st.session_state.series_concluidas.get(disc_atual, 1)

    st.info(f"Matéria Atual: `{disc_atual}` | Série: `{serie_atual}`")

    with st.form("form_bloco"):
      st.subheader("Registrar Bloco de Questões Resolvidas")
      col1, col2 = st.columns(2)
      with col1:
        feitas = st.number_input(
            "Questões Feitas", min_value=1, value=15, step=1
        )
      with col2:
        acertos = st.number_input(
            "Questões Acertadas", min_value=0, max_value=feitas, value=12, step=1
        )

      enviar_bloco = st.form_submit_button("Concluir Série e Avançar")

    if enviar_bloco:
      aproveitamento_bloco = (acertos / feitas) * 100
      st.success(f"Parabéns! Aproveitamento de **{aproveitamento_bloco:.0f}%**!")

      if st.session_state["user"] and supabase:
        try:
          dados = {
              "user_id": st.session_state["user"].id,
              "disciplina": disc_atual,
              "feitas": feitas,
              "acertos": acertos,
          }
          supabase.table("historico_estudos").insert(dados).execute()
        except Exception as e:
          st.error(f"Erro ao salvar dados: {e}")

      st.session_state.series_concluidas[disc_atual] = serie_atual + 1
      st.session_state.indice_atual = (idx + 1) % len(
          st.session_state.disciplinas
      )
      st.rerun()

    st.markdown("---")
    st.markdown("### Sequência do Circuito")
    for i, d in enumerate(st.session_state.disciplinas):
      marcador = (
          "[ESTUDAR AGORA]"
          if i
          == (st.session_state.indice_atual % len(st.session_state.disciplinas))
          else "[OK]"
      )
      st.text(
          f"{marcador} {d} — Série"
          f" {st.session_state.series_concluidas.get(d, 1)}"
      )


# ==========================================
# TELA: PAINEL DE DESEMPENHO
# ==========================================
elif menu_principal == "Painel de Desempenho":
  st.subheader(f"Painel de Evolução — {nome_aluno}")

  if st.session_state["user"] is None:
    st.warning("Faça login na barra lateral para carregar seu histórico.")
  else:
    if supabase:
      try:
        res = (
            supabase.table("historico_estudos")
            .select("*")
            .eq("user_id", st.session_state["user"].id)
            .execute()
        )
        dados = res.data

        if not dados:
          st.info("Nenhum bloco registrado ainda.")
        else:
          df = pd.DataFrame(dados)
          total_feitas = df["feitas"].sum()
          total_acertos = df["acertos"].sum()
          aproveitamento_geral = (
              (total_acertos / total_feitas) * 100 if total_feitas > 0 else 0
          )

          c1, c2, c3 = st.columns(3)
          c1.metric("Questões Resolvidas", f"{total_feitas:,}")
          c2.metric("Total de Acertos", f"{total_acertos:,}")
          c3.metric("Rendimento Geral", f"{aproveitamento_geral:.1f}%")

          st.markdown("---")
          st.subheader("Aproveitamento Por Disciplina")
          resumo_disc = (
              df.groupby("disciplina")[["feitas", "acertos"]]
              .sum()
              .reset_index()
          )
          resumo_disc["Aproveitamento (%)"] = (
              resumo_disc["acertos"] / resumo_disc["feitas"] * 100
          ).round(1)
          st.dataframe(resumo_disc, use_container_width=True)

      except Exception as e:
        st.error(f"Erro ao carregar painel: {e}")


# ==========================================
# TELA: FLASHCARDS E RECORRÊNCIAS
# ==========================================
elif menu_principal == "Flashcards e Recorrências":
  st.subheader(f"Caderno de Erros — {nome_aluno}")

  if st.session_state["user"] is None:
    st.warning("Faça login na barra lateral para salvar flashcards na nuvem.")
  else:
    with st.expander("Adicionar Novo Flashcard", expanded=False):
      with st.form("form_fc"):
        disc_escolhida = st.selectbox(
            "Disciplina:", st.session_state.disciplinas
        )
        assunto_livre = st.text_input("Assunto:")
        comentario_erro = st.text_area("Fundamento / Comentário do Erro:")

        enviar_fc = st.form_submit_button("Salvar Flashcard")

      if enviar_fc:
        if assunto_livre.strip() and comentario_erro.strip() and supabase:
          try:
            dados_fc = {
                "user_id": st.session_state["user"].id,
                "disciplina": disc_escolhida,
                "assunto": assunto_livre.strip(),
                "pergunta_erro": assunto_livre.strip(),
                "resposta_fundamento": comentario_erro,
            }
            supabase.table("flashcards_erros").insert(dados_fc).execute()
            st.success("Flashcard registrado com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao salvar flashcard: {e}")


# ==========================================
# TELA: GERENCIAR DISCIPLINAS
# ==========================================
else:
  st.subheader("Gerenciar Disciplinas e Ordem do Circuito")
  st.markdown(
      "Adicione novas matérias ou altere a ordem em que aparecem no circuito"
      " usando os botões **Subir** e **Descer**."
  )

  with st.expander("Adicionar Nova Disciplina", expanded=False):
    nova_disc = st.text_input("Nome da disciplina:")
    if st.button("Adicionar") and nova_disc.strip():
      nova_limpa = nova_disc.strip()
      if nova_limpa not in st.session_state.disciplinas:
        st.session_state.disciplinas.append(nova_limpa)
        st.session_state.series_concluidas[nova_limpa] = 1
        st.success("Disciplina adicionada com sucesso!")
        st.rerun()
      else:
        st.warning("Esta disciplina já consta no circuito.")

  st.markdown("---")
  st.subheader("Ordem Atual das Disciplinas")

  if not st.session_state.disciplinas:
    st.warning("Nenhuma disciplina cadastrada.")
  else:
    for idx, d in enumerate(st.session_state.disciplinas):
      c_pos, c_nome, c_subir, c_descer, c_remover = st.columns(
          [1, 4, 1.5, 1.5, 1.5]
      )

      c_pos.markdown(f"**#{idx + 1}**")
      c_nome.write(f"**{d}**")

      if c_subir.button("Subir ⬆️", key=f"up_{idx}"):
        if idx > 0:
          st.session_state.disciplinas[idx], st.session_state.disciplinas[
              idx - 1
          ] = (
              st.session_state.disciplinas[idx - 1],
              st.session_state.disciplinas[idx],
          )
          st.rerun()

      if c_descer.button("Descer ⬇️", key=f"down_{idx}"):
        if idx < len(st.session_state.disciplinas) - 1:
          st.session_state.disciplinas[idx], st.session_state.disciplinas[
              idx + 1
          ] = (
              st.session_state.disciplinas[idx + 1],
              st.session_state.disciplinas[idx],
          )
          st.rerun()

      if c_remover.button("Remover 🗑️", key=f"rem_{idx}"):
        st.session_state.disciplinas.pop(idx)
        if st.session_state.disciplinas:
          st.session_state.indice_atual = st.session_state.indice_atual % len(
              st.session_state.disciplinas
          )
        else:
          st.session_state.indice_atual = 0
        st.rerun()
