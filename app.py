import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Circuito de Estudos - Concursos", page_icon="🏋️‍♂️", layout="wide"
)

# Inicialização dos dados na memória da sessão
if "disciplinas" not in st.session_state:
  st.session_state.disciplinas = [
      "Direito Constitucional",
      "Direito Administrativo",
      "Processo Civil",
  ]

if "historico" not in st.session_state:
  st.session_state.historico = []

if "caderno_erros" not in st.session_state:
  st.session_state.caderno_erros = []

if "indice_atual" not in st.session_state:
  st.session_state.indice_atual = 0

# Cabeçalho
st.title("🏋️‍♂️ Circuito de Estudos para Concursos")
st.markdown(
    "Gerencie suas rodadas de exercícios em formato de **séries de academia**"
    " para manter o ritmo e a alta performance."
)
st.divider()

# Barra lateral para gerenciar o Circuito (Séries)
with st.sidebar:
  st.header("⚙️ Configurar Circuito")

  nova_disc = st.text_input("Adicionar nova disciplina:")
  if st.button("Adicionar ao Circuito") and nova_disc:
    if nova_disc not in st.session_state.disciplinas:
      st.session_state.disciplinas.append(nova_disc)
      st.success(f"'{nova_disc}' adicionada!")
      st.rerun()

  st.markdown("### Disciplinas no Circuito:")
  if st.session_state.disciplinas:
    for i, d in enumerate(st.session_state.disciplinas):
      prefixo = "👉 [ATUAL] " if i == st.session_state.indice_atual else "• "
      st.text(f"{prefixo}{d}")

    if st.button("Resetar Circuito"):
      st.session_state.indice_atual = 0
      st.rerun()
  else:
    st.warning("Adicione pelo menos uma disciplina para começar.")

# Corpo Principal - A "Série" do Momento
if st.session_state.disciplinas:
  disc_ativa = st.session_state.disciplinas[st.session_state.indice_atual]

  st.info(
      f"🎯 **Aparelho / Disciplina Atual:** {disc_ativa} (Série"
      f" {st.session_state.indice_atual + 1} de"
      f" {len(st.session_state.disciplinas)})"
  )

  with st.form("form_serie"):
    st.subheader("Registrar Bloco de Questões")
    col1, col2 = st.columns(2)

    with col1:
      questoes_feitas = st.number_input(
          "Questões Feitas neste Bloco", min_value=1, value=10, step=1
      )
    with col2:
      questoes_acertadas = st.number_input(
          "Questões Acertadas", min_value=0, value=8, step=1
      )

    anotacao_erro = st.text_area(
        "Caderno de Erros (O que errou e por quê? Ex: Jurisprudência X, pegadinha"
        " de lei seca):",
        placeholder=(
            "Descreva brevemente o motivo do erro para revisar depois..."
        ),
    )

    enviado = st.form_submit_button(
        "Concluir Série e Passar para a Próxima ➡️"
    )

    if enviado:
      if questoes_acertadas > questoes_feitas:
        st.error("O número de acertos não pode ser maior que o de questões!")
      else:
        # Salva histórico
        st.session_state.historico.append({
            "Disciplina": disc_ativa,
            "Feitas": questoes_feitas,
            "Acertos": questoes_acertadas,
            "Aproveitamento": f"{(questoes_acertadas / questoes_feitas) * 100:.1f}%",
        })

        # Salva no caderno de erros se houver texto
        if anotacao_erro.strip():
          st.session_state.caderno_erros.append({
              "Disciplina": disc_ativa,
              "Detalhe": anotacao_erro,
          })

        # Gira o circuito para a próxima disciplina
        st.session_state.indice_atual = (
            st.session_state.indice_atual + 1
        ) % len(st.session_state.disciplinas)
        st.success("Série computada com sucesso! Trocando de disciplina...")
        st.rerun()

  # Painel de Desempenho e Histórico
  st.divider()
  col_hist, col_err = st.columns(2)

  with col_hist:
    st.subheader("📊 Histórico de Séries do Dia")
    if st.session_state.historico:
      df_hist = pd.DataFrame(st.session_state.historico)
      st.dataframe(df_hist, use_container_width=True)
    else:
      st.text("Nenhuma série concluída ainda hoje.")

  with col_err:
    st.subheader("⚠️ Caderno de Erros Acumulado")
    if st.session_state.caderno_erros:
      for err in st.session_state.caderno_erros:
        st.warning(f"**{err['Disciplina']}**: {err['Detalhe']}")
    else:
      st.text("Nenhum erro registrado ainda. Ótimo trabalho!")

else:
  st.warning("Cadastre disciplinas na barra lateral para iniciar o circuito.")
