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
# TELA: ⚙️ GERENCIAR DISCIPLINAS
# ==========================================
elif "Gerenciar Disciplinas" in menu_principal:
  st.title("⚙️ Gerenciar Disciplinas")
  st.write("Adicione ou edite as disciplinas do seu ciclo de estudos.")
