import feedparser
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Circuito de Estudos", page_icon="⚖️", layout="wide"
)

# ==========================================
# MENU PRINCIPAL (Sidebar)
# ==========================================
st.sidebar.title("📌 Menu Principal")
opcoes_menu = [
    "🏠 Início",
    "🏋️‍♂️ Executar Circuito",
    "📊 Painel de Desempenho",
    "🧠 Flashcards & Recorrências",
    "📰 Radar Jurídico & Notícias",
    "⚙️ Gerenciar Disciplinas",
]

# O parâmetro index=0 garante que abre sempre na tela de Início sem falhas
menu_principal = st.sidebar.radio(
    "Navegue pelas telas:", opcoes_menu, index=0
)

# ==========================================
# TELA: 🏠 INÍCIO
# ==========================================
if "Início" in menu_principal:
  st.title("🏠 Página Inicial — Circuito de Estudos")
  st.write(
      "Seja bem-vindo ao seu painel central! Utilize o menu à esquerda para"
      " navegar entre as ferramentas."
  )
  st.info(
      "Dica: Selecione **Radar Jurídico & Notícias** no menu lateral para ver"
      " as últimas atualizações do STF e STJ em tempo real."
  )

# ==========================================
# TELA: 🏋️‍♂️ EXECUTAR CIRCUITO
# ==========================================
elif "Executar Circuito" in menu_principal:
  st.title("🏋️‍♂️ Executar Circuito de Estudos")
  st.write("Aqui você gerencia e executa as suas rodadas de estudo.")

# ==========================================
# TELA: 📊 PAINEL DE DESEMPENHO
# ==========================================
elif "Painel de Desempenho" in menu_principal:
  st.title("📊 Painel de Desempenho")
  st.write("Acompanhe as suas estatísticas e evolução.")

# ==========================================
# TELA: 🧠 FLASHCARDS & RECORRÊNCIAS
# ==========================================
elif "Flashcards & Recorrências" in menu_principal:
  st.title("🧠 Flashcards & Recorrências")
  st.write("Reveja os seus cartões de memória e pontos recorrentes.")

# ==========================================
# TELA: 📰 RADAR JURÍDICO & NOTÍCIAS
# ==========================================
elif "Radar Jurídico" in menu_principal:
  nome_aluno = "Mauricio"
  st.title(f"📰 Radar Jurídico & Jurisprudência — {nome_aluno}")
  st.caption(
      "Acompanhe em tempo real as últimas notícias, destaques e julgados do"
      " STF e STJ."
  )

  tab_stf, tab_stj, tab_busca = st.tabs(
      ["🏛️ Notícias STF", "⚖️ Notícias STJ", "🔍 Busca por Tema"]
  )

  # 1. ABA STF
  with tab_stf:
    st.subheader("📌 Últimas do Supremo Tribunal Federal (STF)")
    feed_stf_url = "https://portal.stf.jus.br/rss/noticias.xml"

    try:
      feed_stf = feedparser.parse(feed_stf_url)
      if feed_stf.entries:
        for entry in feed_stf.entries[:8]:
          titulo = entry.get("title", "Sem título")
          link = entry.get("link", "#")
          data_pub = entry.get(
              "published", entry.get("updated", "Data não disponível")
          )
          resumo = entry.get("summary", "Sem resumo disponível.")

          with st.expander(f"📌 {titulo}"):
            st.caption(f"🗓️ Publicado em: {data_pub}")
            st.write(resumo, unsafe_allow_html=True)
            st.markdown(f"[🔗 Ler notícia completa no STF]({link})")
      else:
        st.warning("Nenhuma notícia encontrada no Feed RSS do STF.")
    except Exception as e:
      st.error(f"Erro ao carregar o feed do STF: {e}")

  # 2. ABA STJ
  with tab_stj:
    st.subheader("📌 Últimas do Superior Tribunal de Justiça (STJ)")
    feed_stj_url = "https://www.stj.jus.br/sites/portalp/rss/noticias.xml"

    try:
      feed_stj = feedparser.parse(feed_stj_url)
      if feed_stj.entries:
        for entry in feed_stj.entries[:8]:
          titulo = entry.get("title", "Sem título")
          link = entry.get("link", "#")
          data_pub = entry.get(
              "published", entry.get("updated", "Data não disponível")
          )
          resumo = entry.get("summary", "Sem resumo disponível.")

          with st.expander(f"⚖️ {titulo}"):
            st.caption(f"🗓️ Publicado em: {data_pub}")
            st.write(resumo, unsafe_allow_html=True)
            st.markdown(f"[🔗 Ler notícia completa no STJ]({link})")
      else:
        st.warning("Nenhuma notícia encontrada no Feed RSS do STJ.")
    except Exception as e:
      st.error(f"Erro ao carregar o feed do STJ: {e}")

  # 3. ABA BUSCA POR TEMA
  with tab_busca:
    st.subheader("🔍 Filtrar Notícias por Palavra-Chave")
    termo_busca = st.text_input(
        "Digite um tema (ex: Direito Constitucional, Penal, Tributário):"
    )

    if termo_busca:
      st.markdown(f"**Resultados para:** *'{termo_busca}'*")
      encontrados = 0

      feeds = [
          ("STF", "https://portal.stf.jus.br/rss/noticias.xml"),
          ("STJ", "https://www.stj.jus.br/sites/portalp/rss/noticias.xml"),
      ]

      for tribunal, url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
          titulo = entry.get("title", "")
          summary = entry.get("summary", "")

          if (
              termo_busca.lower() in titulo.lower()
              or termo_busca.lower() in summary.lower()
          ):
            encontrados += 1
            with st.expander(f"[{tribunal}] {titulo}"):
              st.write(summary, unsafe_allow_html=True)
              st.markdown(
                  f"[🔗 Acesse a matéria original]({entry.get('link', '#')})"
              )

      if encontrados == 0:
        st.info("Nenhuma notícia encontrada com este termo.")

# ==========================================
# TELA: ⚙️ GERENCIAR DISCIPLINAS
# ==========================================
elif "Gerenciar Disciplinas" in menu_principal:
  st.title("⚙️ Gerenciar Disciplinas")
  st.write("Adicione ou edite as disciplinas do seu ciclo de estudos.")
