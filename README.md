# HCP Intelligence — Equilibrium Dashboard

Dashboard interativo de análise de HCPs (médicos e nutricionistas).

## Como publicar no Streamlit Cloud

### 1. Subir no GitHub
1. Acesse github.com e crie um repositório novo (ex: `equilibrium-dash`)
2. Faça upload dos 3 arquivos deste projeto:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### 2. Publicar no Streamlit Cloud
1. Acesse **share.streamlit.io**
2. Faça login com sua conta GitHub
3. Clique em **"New app"**
4. Selecione o repositório `equilibrium-dash`
5. Main file: `app.py`
6. Clique em **Deploy**

Em poucos minutos você terá um link tipo:
`https://seu-usuario-equilibrium-dash.streamlit.app`

### 3. Configurar a Google Sheets
1. Cole seus dados na planilha com duas abas:
   - **Medicos** — base de médicos
   - **Nutricionistas** — base de nutricionistas
2. Compartilhe a planilha: **Compartilhar → Qualquer pessoa com o link → Visualizador**
3. Copie a URL da planilha
4. No dashboard, cole a URL na barra lateral

### 4. Compartilhar com clientes
- Mande o link do Streamlit
- O cliente cola a URL da planilha e vê os dados na hora
- Quando você atualizar a planilha, o dashboard atualiza automaticamente

## Colunas esperadas

| Campo | Nomes aceitos |
|-------|--------------|
| UF | UfMatricula, UF |
| CRM/Matrícula | Matricula, CRM |
| Nome | Medico, Nutricionista, Nome |
| Segmentação (médico) | Segmentacao, Seg |
| Seg. Influência (nutri) | SegmentacaoInfluencia, SegInfluencia |
| Seg. Prescrição (nutri) | SegmentacaoPrescricao, SegPrescricao |
| Seguidores | NSeguidores, Seguidores |
| Valor Consulta | ValorConsulta, Consulta |
| Local Atendimento | LocalAtendimento, Local |
| Pacientes/dia | NPacientes, Pacientes |
| Especialidade 1 | Especialidade1, Especialidade |
| Especialidade 2 | Especialidade2 |
| Telefone | Telefone1, Telefone |
| Celular | Celular1, Celular |
| E-mail | Email1, Email |
| Endereço | Endereco |
| Instagram | EnderecoRedeSocial, Instagram |
| Cidade | Cidade, Municipio |
