import streamlit as st
import pandas as pd
import feedparser

# ==========================================
# MENU PRINCIPAL
# ==========================================
menu_principal = st.sidebar.radio(
    "Navegue pelas telas:", 
    [
        "🏠 Início",
        "🏋️‍♂️ Executar Circuito", 
        "📊 Painel de Desempenho", 
        "🧠 Flashcards & Recorrências",
        "📰 Radar Jurídico & Notícias",  # <-- Nova Tela!
        "⚙️ Gerenciar Disciplinas"
    ]
)

# ==========================================
# TELA: 📰 RADAR JURÍDICO & NOTÍCIAS
# ==========================================
if menu_principal == "📰 Radar Jurídico & Notícias":
    nome_aluno = "Mauricio"  # ajuste conforme sua lógica de login
    st.title(f"📰 Radar Jurídico & Jurisprudência — {nome_aluno}")
    st.caption("Acompanhe em tempo real as últimas notícias, destaques e julgados do STF e STJ.")

    tab_stf, tab_stj, tab_busca = st.tabs(["🏛️ Notícias STF", "⚖️ Notícias STJ", "🔍 Busca por Tema"])

    # 1. ABA STF
    with tab_stf:
        st.subheader("📌 Últimas do Supremo Tribunal Federal (STF)")
        feed_stf_url = "https://portal.stf.jus.br/rss/noticias.xml"
        
        try:
            feed_stf = feedparser.parse(feed_stf_url)
            if feed_stf.entries:
                for entry in feed_stf.entries[:8]:  # Exibe os 8 artigos mais recentes
                    with st.expander(f"⚖️ {entry.title}"):
                        st.write(f"**Publicado em:** {entry.get('published', 'Data não informada')}")
                        st.write(entry.get('summary', 'Sem resumo disponível.'))
                        st.markdown(f"[🔗 Ler matéria completa no Portal do STF]({entry.link})")
            else:
                st.info("Não foi possível carregar as notícias do STF no momento.")
        except Exception:
            st.warning("O serviço de RSS do STF está temporariamente indisponível.")

    # 2. ABA STJ
    with tab_stj:
        st.subheader("📌 Últimas do Superior Tribunal de Justiça (STJ)")
        feed_stj_url = "https://www.stj.jus.br/sites/portalp/RSS/Noticias"
        
        try:
