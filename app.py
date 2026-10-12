import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURAÇÃO DO SUPABASE ---
# Substitua pelos seus dados reais do Supabase
SUPABASE_URL = "https://hweawyyqnzavrhejaotv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh3ZWF3eXlxbnphdnJoZWphb3R2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE3NjgwMDQsImV4cCI6MjEwNzM0NDAwNH0.2mgHfTLJCy8fkId_w5yP6EFDP-cYWM0wM6ZpvHrIhpk"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase: Client = init_supabase()

st.set_page_config(page_title="Circuito de Estudos para Concursos", page_icon="🏋️‍♂️", layout="wide")

# --- AUTENTICAÇÃO / LOGIN ---
st.sidebar.title("🔑 Acesso do Usuário")

if "user" not in st.session_state:
    st.session_erros = []
    st.session_state["user"] = None

if supabase is None:
    st.sidebar.error("Erro ao conectar com o Supabase. Verifique as credenciais.")
else:
    if st.session_state["user"] is None:
        aba_auth = st.sidebar.radio("Escolha:", ["Entrar", "Criar Conta"])
        
        email_input = st.sidebar.text_input("E-mail")
        senha_input = st.sidebar.text_input("Senha", type="password")
        
        if aba_auth == "Criar Conta":
            if st.sidebar.button("Cadastrar"):
                try:
                    res = supabase.auth.sign_up({"email": email_input, "password": senha_input})
                    st.sidebar.success("Conta criada! Verifique o e-mail ou faça login.")
                except Exception as e:
                    st.sidebar.error(f"Erro no cadastro: {e}")
        else:
            if st.sidebar.button("Entrar"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": senha_input})
                    st.session_state["user"] = res.user
                    st.sidebar.success("Login efetuado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error("E-mail ou senha incorretos.")
    else:
        st.sidebar.success(f"Logado como: {st.session_state['user'].email}")
        if st.sidebar.button("Terminar Sessão"):
            supabase.auth.sign_out()
            st.session_state["user"] = None
            st.rerun()

# --- TÍTULO PRINCIPAL ---
st.title("🏋️‍♂️ Circuito de Estudos para Concursos")
st.markdown("Gerencie suas rodadas de exercícios em formato de **séries de academia** para manter o ritmo e a alta performance.")

# Se o usuário não estiver logado, avisa
if st.session_state["user"] is None:
    st.warning("⚠️ Faça login na barra lateral para salvar o seu progresso de forma permanente na nuvem.")

# --- GERENCIAMENTO DE DISCIPLINAS ---
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

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configurar Circuito")
nova_disciplina = st.sidebar.text_input("Adicionar nova disciplina:")
if st.sidebar.button("Adicionar ao Circuito") and nova_disciplina:
    if nova_disciplina not in st.session_state.disciplinas:
        st.session_state.disciplinas.append(nova_disciplina)
        st.session_state.series_concluidas[nova_disciplina] = 1
        st.success(f"'{nova_disciplina}' adicionada!")
        st.rerun()

st.sidebar.markdown("### Disciplinas no Circuito:")
for i, disc in enumerate(st.session_state.disciplinas):
    prefixo = "👉 [ATUAL] " if i == st.session_state.indice_atual else "• "
    st.sidebar.markdown(f"{prefixo}{disc} (Série {st.session_state.series_concluidas.get(disc, 1)})")

# --- LÓGICA DO CIRCUITO ATUAL ---
if st.session_state.disciplinas:
    disciplina_atual = st.session_state.disciplinas[st.session_state.indice_atual]
    serie_atual = st.session_state.series_concluidas[disciplina_atual]

    st.markdown(f"### 🎯 Aparelho / Disciplina Atual: {disciplina_atual} (Série {serie_atual} de 13)")

    with st.container():
        st.subheader("Registrar Bloco de Questões")
        col1, col2 = st.columns(2)
        with col1:
            questoes_feitas = st.number_input("Questões Feitas neste Bloco", min_value=1, value=10, step=1)
        with col2:
            questoes_acertadas = st.number_input("Questões Acertadas", min_value=0, max_value=questoes_feitas, value=8, step=1)

        detalhe_erro = st.text_area("Caderno de Erros (O que errou e por quê? Ex: Jurisprudência X, pegadinha de lei seca):", placeholder="Descreva brevemente o motivo do erro para revisar depois...")

        if st.button("Concluir Série e Passar para a Próxima ➡️"):
            # Salvar no Supabase se o usuário estiver logado
            if st.session_state["user"] and supabase:
                try:
                    dados_inserir = {
                        "user_id": st.session_state["user"].id,
                        "disciplina": disciplina_atual,
                        "feitas": questoes_feitas,
                        "acertos": questoes_acertadas,
                        "erros": detalhe_erro if detalhe_erro else None
                    }
                    supabase.table("historico_estudos").insert(dados_inserir).execute()
                    st.success("✅ Progresso salvo na sua conta com sucesso na nuvem!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco de dados: {e}")
            else:
                st.info("ℹ️ Bloco concluído localmente (faça login para persistir permanentemente).")

            # Avança o circuito
            st.session_state.series_concluidas[disciplina_atual] += 1
            st.session_state.indice_atual = (st.session_state.indice_atual + 1) % len(st.session_state.disciplinas)
            st.rerun()
else:
    st.warning("Cadastre disciplinas na barra lateral para iniciar o circuito.")
