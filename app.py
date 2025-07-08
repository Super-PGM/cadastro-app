import os
import json
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import uuid

# Escopos de acesso
escopo = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# ✅ Lê as credenciais do secret (formato string)
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)

# Autoriza usando dicionário
credenciais = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopo)
cliente = gspread.authorize(credenciais)

# Abre a planilha e aba
planilha = cliente.open("CadastroInfo")
aba = planilha.worksheet("Dados")

# Funções
def cadastrar(nome, email, obs):
    id_ = str(uuid.uuid4())
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    aba.append_row([id_, nome, email, data, obs])

def listar():
    dados = aba.get_all_records()
    return pd.DataFrame(dados)

def editar(id_alvo, novo_nome=None, novo_email=None, nova_obs=None):
    dados = aba.get_all_records()
    for i, registro in enumerate(dados):
        if registro["ID"] == id_alvo:
            linha = i + 2
            if novo_nome:
                aba.update_cell(linha, 2, novo_nome)
            if novo_email:
                aba.update_cell(linha, 3, novo_email)
            if nova_obs:
                aba.update_cell(linha, 5, nova_obs)
            return True
    return False

def excluir(id_alvo):
    dados = aba.get_all_records()
    for i, registro in enumerate(dados):
        if registro["ID"] == id_alvo:
            linha = i + 2
            aba.delete_rows(linha)
            return True
    return False

# Interface Streamlit
st.title("📋 Sistema de Cadastro de Informações")

aba_opcao = st.radio("Ação:", ["Cadastrar", "Editar", "Excluir", "Visualizar"])

if aba_opcao == "Cadastrar":
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    obs = st.text_area("Observações")
    if st.button("Salvar"):
        cadastrar(nome, email, obs)
        st.success("✅ Cadastro realizado!")

elif aba_opcao == "Editar":
    id_editar = st.text_input("ID do cadastro")
    novo_nome = st.text_input("Novo nome")
    novo_email = st.text_input("Novo email")
    nova_obs = st.text_area("Nova observação")
    if st.button("Atualizar"):
        if editar(id_editar, novo_nome, novo_email, nova_obs):
            st.success("✅ Cadastro atualizado!")
        else:
            st.error("ID não encontrado.")

elif aba_opcao == "Excluir":
    id_excluir = st.text_input("ID do cadastro a excluir")
    if st.button("Excluir"):
        if excluir(id_excluir):
            st.success("🗑️ Cadastro excluído com sucesso.")
        else:
            st.error("ID não encontrado.")

else:
    st.subheader("📄 Lista de cadastros")
    df = listar()
    st.dataframe(df)
