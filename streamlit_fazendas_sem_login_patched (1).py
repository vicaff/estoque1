import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os
from io import BytesIO

# --- Safe Plotly import for Streamlit Cloud ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ModuleNotFoundError:
    import sys, subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly==5.15.0"])
    import plotly.express as px
    import plotly.graph_objects as go


# ===================================================================
# CONFIGURAÇÃO DA PÁGINA
# ===================================================================

st.set_page_config(
    page_title="G&V Florestal - Controle de Fazendas",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================================
# DADOS INICIAIS E CONFIGURAÇÃO
# ===================================================================

# Arquivo para persistir dados
DADOS_FILE = "dados_fazendas_streamlit.json"

# Dados iniciais das fazendas
DADOS_INICIAIS = {
    "fazendas": [
        {
            "id": 1,
            "nome": "Fazenda São João",
            "estado": "Goiás",
            "cidade": "Mineiros",
            "hectares": 1200.5,
            "status": "ativa",
            "proprietario": "João Silva",
            "telefone": "(64) 99999-1234",
            "email": "joao@fazenda.com",
            "data_cadastro": "2024-01-15"
        },
        {
            "id": 2,
            "nome": "Fazenda Santa Maria",
            "estado": "Mato Grosso",
            "cidade": "Sorriso",
            "hectares": 2500.0,
            "status": "ativa",
            "proprietario": "Maria Santos",
            "telefone": "(65) 98888-5678",
            "email": "maria@fazenda.com",
            "data_cadastro": "2024-02-20"
        },
        {
            "id": 3,
            "nome": "Fazenda Boa Vista",
            "estado": "Goiás",
            "cidade": "Rio Verde",
            "hectares": 800.0,
            "status": "inativa",
            "proprietario": "Carlos Oliveira",
            "telefone": "(64) 97777-9012",
            "email": "carlos@fazenda.com",
            "data_cadastro": "2024-03-10"
        }
    ],
    "producao": [
        {
            "fazenda_id": 1,
            "data": "2024-09-01",
            "toneladas_projetadas": 1500.0,
            "toneladas_entregues": 1200.0,
            "observacoes": "Produção dentro do esperado"
        },
        {
            "fazenda_id": 2,
            "data": "2024-09-01",
            "toneladas_projetadas": 3000.0,
            "toneladas_entregues": 2800.0,
            "observacoes": "Excelente produtividade"
        },
        {
            "fazenda_id": 1,
            "data": "2024-09-15",
            "toneladas_projetadas": 1600.0,
            "toneladas_entregues": 1400.0,
            "observacoes": "Pequena redução devido ao clima"
        }
    ]
}

# ===================================================================
# FUNÇÕES DE PERSISTÊNCIA DE DADOS
# ===================================================================

@st.cache_data
def carregar_dados():
    """Carrega dados do arquivo JSON ou retorna dados iniciais"""
    if os.path.exists(DADOS_FILE):
        try:
            with open(DADOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DADOS_INICIAIS
    return DADOS_INICIAIS

def salvar_dados(dados):
    """Salva dados no arquivo JSON"""
    try:
        with open(DADOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def limpar_cache():
    """Limpa o cache do Streamlit"""
    st.cache_data.clear()

# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def gerar_proximo_id(lista):
    """Gera próximo ID disponível"""
    if not lista:
        return 1
    return max([item.get('id', 0) for item in lista]) + 1

def formatar_numero(numero):
    """Formata número com separadores de milhares"""
    return f"{numero:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calcular_estatisticas(dados):
    """Calcula estatísticas gerais"""
    fazendas = dados.get('fazendas', [])
    producao = dados.get('producao', [])
    
    total_fazendas = len(fazendas)
    fazendas_ativas = len([f for f in fazendas if f.get('status') == 'ativa'])
    total_hectares = sum([f.get('hectares', 0) for f in fazendas])
    
    total_projetado = sum([p.get('toneladas_projetadas', 0) for p in producao])
    total_entregue = sum([p.get('toneladas_entregues', 0) for p in producao])
    
    percentual_conclusao = (total_entregue / total_projetado * 100) if total_projetado > 0 else 0
    
    return {
        'total_fazendas': total_fazendas,
        'fazendas_ativas': fazendas_ativas,
        'total_hectares': total_hectares,
        'total_projetado': total_projetado,
        'total_entregue': total_entregue,
        'percentual_conclusao': percentual_conclusao
    }

# ===================================================================
# INTERFACE PRINCIPAL
# ===================================================================

def main():
    # Carregar dados
    dados = carregar_dados()
    
    # Título principal
    st.title("🌲 G&V Florestal - Controle de Fazendas")
    st.markdown("---")
    
    # Sidebar para navegação
    st.sidebar.title("📋 Menu Principal")
    
    opcoes = [
        "📊 Dashboard",
        "🏡 Gerenciar Fazendas", 
        "📈 Controle de Produção",
        "📋 Relatórios",
        "📤 Importar/Exportar",
        "⚙️ Configurações"
    ]
    
    opcao_selecionada = st.sidebar.selectbox("Selecione uma opção:", opcoes)
    
    # Executar função baseada na seleção
    if opcao_selecionada == "📊 Dashboard":
        mostrar_dashboard(dados)
    elif opcao_selecionada == "🏡 Gerenciar Fazendas":
        gerenciar_fazendas(dados)
    elif opcao_selecionada == "📈 Controle de Produção":
        controle_producao(dados)
    elif opcao_selecionada == "📋 Relatórios":
        mostrar_relatorios(dados)
    elif opcao_selecionada == "📤 Importar/Exportar":
        importar_exportar(dados)
    elif opcao_selecionada == "⚙️ Configurações":
        configuracoes(dados)

# ===================================================================
# DASHBOARD
# ===================================================================

def mostrar_dashboard(dados):
    st.header("📊 Dashboard Geral")
    
    # Calcular estatísticas
    stats = calcular_estatisticas(dados)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏡 Total de Fazendas",
            value=stats['total_fazendas'],
            delta=f"{stats['fazendas_ativas']} ativas"
        )
    
    with col2:
        st.metric(
            label="🌾 Total de Hectares",
            value=formatar_numero(stats['total_hectares']),
            delta="hectares"
        )
    
    with col3:
        st.metric(
            label="📦 Toneladas Projetadas",
            value=formatar_numero(stats['total_projetado']),
            delta="toneladas"
        )
    
    with col4:
        st.metric(
            label="✅ % Concluído",
            value=f"{stats['percentual_conclusao']:.1f}%",
            delta=f"{formatar_numero(stats['total_entregue'])} entregues"
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de fazendas por estado
        fazendas_df = pd.DataFrame(dados['fazendas'])
        if not fazendas_df.empty:
            fig_estados = px.pie(
                fazendas_df.groupby('estado').size().reset_index(name='count'),
                values='count',
                names='estado',
                title="📍 Distribuição por Estado"
            )
            st.plotly_chart(fig_estados, use_container_width=True)
    
    with col2:
        # Gráfico de status das fazendas
        if not fazendas_df.empty:
            status_counts = fazendas_df['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="📊 Status das Fazendas",
                labels={'x': 'Status', 'y': 'Quantidade'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
    
    # Tabela resumo por estado
    st.subheader("📋 Resumo por Estado")
    if not fazendas_df.empty:
        resumo_estado = fazendas_df.groupby('estado').agg({
            'nome': 'count',
            'hectares': 'sum'
        }).rename(columns={'nome': 'Fazendas', 'hectares': 'Total Hectares'})
        
        resumo_estado['Total Hectares'] = resumo_estado['Total Hectares'].apply(formatar_numero)
        st.dataframe(resumo_estado, use_container_width=True)

# ===================================================================
# GERENCIAR FAZENDAS
# ===================================================================

def gerenciar_fazendas(dados):
    st.header("🏡 Gerenciar Fazendas")
    
    # Tabs para organizar funcionalidades
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Fazendas", "➕ Nova Fazenda", "✏️ Editar Fazenda"])
    
    with tab1:
        mostrar_lista_fazendas(dados)
    
    with tab2:
        cadastrar_nova_fazenda(dados)
    
    with tab3:
        editar_fazenda(dados)

def mostrar_lista_fazendas(dados):
    st.subheader("📋 Lista de Fazendas Cadastradas")
    
    fazendas = dados.get('fazendas', [])
    
    if not fazendas:
        st.warning("Nenhuma fazenda cadastrada.")
        return
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estados = list(set([f['estado'] for f in fazendas]))
        estado_filtro = st.selectbox("Filtrar por Estado:", ["Todos"] + estados)
    
    with col2:
        status_filtro = st.selectbox("Filtrar por Status:", ["Todos", "ativa", "inativa"])
    
    with col3:
        busca = st.text_input("Buscar por nome:")
    
    # Aplicar filtros
    fazendas_filtradas = fazendas.copy()
    
    if estado_filtro != "Todos":
        fazendas_filtradas = [f for f in fazendas_filtradas if f['estado'] == estado_filtro]
    
    if status_filtro != "Todos":
        fazendas_filtradas = [f for f in fazendas_filtradas if f['status'] == status_filtro]
    
    if busca:
        fazendas_filtradas = [f for f in fazendas_filtradas if busca.lower() in f['nome'].lower()]
    
    # Mostrar fazendas
    if fazendas_filtradas:
        df = pd.DataFrame(fazendas_filtradas)
        df['hectares'] = df['hectares'].apply(formatar_numero)
        
        st.dataframe(
            df[['nome', 'estado', 'cidade', 'hectares', 'status', 'proprietario']],
            use_container_width=True
        )
        
        st.info(f"Mostrando {len(fazendas_filtradas)} de {len(fazendas)} fazendas")
    else:
        st.warning("Nenhuma fazenda encontrada com os filtros aplicados.")

def cadastrar_nova_fazenda(dados):
    st.subheader("➕ Cadastrar Nova Fazenda")
    
    with st.form("nova_fazenda"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome da Fazenda*", placeholder="Ex: Fazenda São João")
            estado = st.selectbox("Estado*", [
                "Goiás", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais",
                "São Paulo", "Bahia", "Tocantins", "Maranhão", "Piauí"
            ])
            cidade = st.text_input("Cidade*", placeholder="Ex: Mineiros")
            hectares = st.number_input("Hectares*", min_value=0.0, step=0.1, format="%.2f")
        
        with col2:
            proprietario = st.text_input("Proprietário*", placeholder="Ex: João Silva")
            telefone = st.text_input("Telefone", placeholder="(64) 99999-1234")
            email = st.text_input("Email", placeholder="contato@fazenda.com")
            status = st.selectbox("Status*", ["ativa", "inativa"])
        
        observacoes = st.text_area("Observações", placeholder="Informações adicionais...")
        
        submitted = st.form_submit_button("✅ Cadastrar Fazenda")
        
        if submitted:
            if not all([nome, estado, cidade, hectares > 0, proprietario]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            else:
                nova_fazenda = {
                    "id": gerar_proximo_id(dados['fazendas']),
                    "nome": nome,
                    "estado": estado,
                    "cidade": cidade,
                    "hectares": hectares,
                    "status": status,
                    "proprietario": proprietario,
                    "telefone": telefone,
                    "email": email,
                    "observacoes": observacoes,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d")
                }
                
                dados['fazendas'].append(nova_fazenda)
                
                if salvar_dados(dados):
                    st.success(f"✅ Fazenda '{nome}' cadastrada com sucesso!")
                    limpar_cache()
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar dados. Tente novamente.")

def editar_fazenda(dados):
    st.subheader("✏️ Editar Fazenda")
    
    fazendas = dados.get('fazendas', [])
    
    if not fazendas:
        st.warning("Nenhuma fazenda cadastrada para editar.")
        return
    
    # Seleção da fazenda
    opcoes_fazendas = {f"{f['nome']} ({f['estado']})": f['id'] for f in fazendas}
    fazenda_selecionada = st.selectbox("Selecione a fazenda para editar:", list(opcoes_fazendas.keys()))
    
    if fazenda_selecionada:
        fazenda_id = opcoes_fazendas[fazenda_selecionada]
        fazenda = next((f for f in fazendas if f['id'] == fazenda_id), None)
        
        if fazenda:
            with st.form("editar_fazenda"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome da Fazenda*", value=fazenda['nome'])
                    estado = st.selectbox("Estado*", [
                        "Goiás", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais",
                        "São Paulo", "Bahia", "Tocantins", "Maranhão", "Piauí"
                    ], index=["Goiás", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais",
                             "São Paulo", "Bahia", "Tocantins", "Maranhão", "Piauí"].index(fazenda['estado']))
                    cidade = st.text_input("Cidade*", value=fazenda['cidade'])
                    hectares = st.number_input("Hectares*", min_value=0.0, step=0.1, format="%.2f", value=fazenda['hectares'])
                
                with col2:
                    proprietario = st.text_input("Proprietário*", value=fazenda['proprietario'])
                    telefone = st.text_input("Telefone", value=fazenda.get('telefone', ''))
                    email = st.text_input("Email", value=fazenda.get('email', ''))
                    status = st.selectbox("Status*", ["ativa", "inativa"], index=0 if fazenda['status'] == 'ativa' else 1)
                
                observacoes = st.text_area("Observações", value=fazenda.get('observacoes', ''))
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    submitted = st.form_submit_button("✅ Salvar Alterações")
                
                with col_btn2:
                    excluir = st.form_submit_button("🗑️ Excluir Fazenda", type="secondary")
                
                if submitted:
                    if not all([nome, estado, cidade, hectares > 0, proprietario]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*)")
                    else:
                        # Atualizar fazenda
                        fazenda.update({
                            "nome": nome,
                            "estado": estado,
                            "cidade": cidade,
                            "hectares": hectares,
                            "status": status,
                            "proprietario": proprietario,
                            "telefone": telefone,
                            "email": email,
                            "observacoes": observacoes
                        })
                        
                        if salvar_dados(dados):
                            st.success(f"✅ Fazenda '{nome}' atualizada com sucesso!")
                            limpar_cache()
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar dados. Tente novamente.")
                
                if excluir:
                    if st.session_state.get('confirmar_exclusao') != fazenda_id:
                        st.session_state.confirmar_exclusao = fazenda_id
                        st.warning("⚠️ Clique novamente para confirmar a exclusão!")
                    else:
                        # Remover fazenda
                        dados['fazendas'] = [f for f in dados['fazendas'] if f['id'] != fazenda_id]
                        
                        if salvar_dados(dados):
                            st.success(f"✅ Fazenda '{fazenda['nome']}' excluída com sucesso!")
                            del st.session_state.confirmar_exclusao
                            limpar_cache()
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar dados. Tente novamente.")

# ===================================================================
# CONTROLE DE PRODUÇÃO
# ===================================================================

def controle_producao(dados):
    st.header("📈 Controle de Produção")
    
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "➕ Novo Registro", "📋 Histórico"])
    
    with tab1:
        visao_geral_producao(dados)
    
    with tab2:
        novo_registro_producao(dados)
    
    with tab3:
        historico_producao(dados)

def visao_geral_producao(dados):
    st.subheader("📊 Visão Geral da Produção")
    
    producao = dados.get('producao', [])
    fazendas = dados.get('fazendas', [])
    
    if not producao:
        st.warning("Nenhum registro de produção encontrado.")
        return
    
    # Criar DataFrame com dados combinados
    df_producao = pd.DataFrame(producao)
    df_fazendas = pd.DataFrame(fazendas)
    
    # Merge dos dados
    df_combined = df_producao.merge(
        df_fazendas[['id', 'nome', 'estado']], 
        left_on='fazenda_id', 
        right_on='id', 
        how='left'
    )
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    total_projetado = df_producao['toneladas_projetadas'].sum()
    total_entregue = df_producao['toneladas_entregues'].sum()
    percentual = (total_entregue / total_projetado * 100) if total_projetado > 0 else 0
    restante = total_projetado - total_entregue
    
    with col1:
        st.metric("📦 Projetado", formatar_numero(total_projetado))
    
    with col2:
        st.metric("✅ Entregue", formatar_numero(total_entregue))
    
    with col3:
        st.metric("📊 % Concluído", f"{percentual:.1f}%")
    
    with col4:
        st.metric("⏳ Restante", formatar_numero(restante))
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Produção por fazenda
        producao_fazenda = df_combined.groupby('nome').agg({
            'toneladas_projetadas': 'sum',
            'toneladas_entregues': 'sum'
        }).reset_index()
        
        fig_fazenda = px.bar(
            producao_fazenda,
            x='nome',
            y=['toneladas_projetadas', 'toneladas_entregues'],
            title="📊 Produção por Fazenda",
            barmode='group'
        )
        st.plotly_chart(fig_fazenda, use_container_width=True)
    
    with col2:
        # Evolução temporal
        df_combined['data'] = pd.to_datetime(df_combined['data'])
        evolucao = df_combined.groupby('data').agg({
            'toneladas_entregues': 'sum'
        }).reset_index()
        
        fig_evolucao = px.line(
            evolucao,
            x='data',
            y='toneladas_entregues',
            title="📈 Evolução das Entregas",
            markers=True
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

def novo_registro_producao(dados):
    st.subheader("➕ Novo Registro de Produção")
    
    fazendas = dados.get('fazendas', [])
    
    if not fazendas:
        st.warning("Nenhuma fazenda cadastrada. Cadastre uma fazenda primeiro.")
        return
    
    with st.form("novo_registro"):
        col1, col2 = st.columns(2)
        
        with col1:
            opcoes_fazendas = {f"{f['nome']} ({f['estado']})": f['id'] for f in fazendas}
            fazenda_selecionada = st.selectbox("Fazenda*", list(opcoes_fazendas.keys()))
            data_registro = st.date_input("Data*", value=date.today())
        
        with col2:
            toneladas_projetadas = st.number_input("Toneladas Projetadas*", min_value=0.0, step=0.1, format="%.2f")
            toneladas_entregues = st.number_input("Toneladas Entregues*", min_value=0.0, step=0.1, format="%.2f")
        
        observacoes = st.text_area("Observações", placeholder="Informações sobre a produção...")
        
        submitted = st.form_submit_button("✅ Registrar Produção")
        
        if submitted:
            if not all([fazenda_selecionada, toneladas_projetadas >= 0, toneladas_entregues >= 0]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            else:
                fazenda_id = opcoes_fazendas[fazenda_selecionada]
                
                novo_registro = {
                    "fazenda_id": fazenda_id,
                    "data": data_registro.strftime("%Y-%m-%d"),
                    "toneladas_projetadas": toneladas_projetadas,
                    "toneladas_entregues": toneladas_entregues,
                    "observacoes": observacoes
                }
                
                if 'producao' not in dados:
                    dados['producao'] = []
                
                dados['producao'].append(novo_registro)
                
                if salvar_dados(dados):
                    st.success("✅ Registro de produção salvo com sucesso!")
                    limpar_cache()
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar dados. Tente novamente.")

def historico_producao(dados):
    st.subheader("📋 Histórico de Produção")
    
    producao = dados.get('producao', [])
    fazendas = dados.get('fazendas', [])
    
    if not producao:
        st.warning("Nenhum registro de produção encontrado.")
        return
    
    # Criar DataFrame com dados combinados
    df_producao = pd.DataFrame(producao)
    df_fazendas = pd.DataFrame(fazendas)
    
    df_combined = df_producao.merge(
        df_fazendas[['id', 'nome', 'estado']], 
        left_on='fazenda_id', 
        right_on='id', 
        how='left'
    )
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fazendas_unicas = df_combined['nome'].unique()
        fazenda_filtro = st.selectbox("Filtrar por Fazenda:", ["Todas"] + list(fazendas_unicas))
    
    with col2:
        data_inicio = st.date_input("Data Início:", value=pd.to_datetime(df_combined['data']).min())
    
    with col3:
        data_fim = st.date_input("Data Fim:", value=pd.to_datetime(df_combined['data']).max())
    
    # Aplicar filtros
    df_filtrado = df_combined.copy()
    
    if fazenda_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['nome'] == fazenda_filtro]
    
    df_filtrado['data'] = pd.to_datetime(df_filtrado['data'])
    df_filtrado = df_filtrado[
        (df_filtrado['data'] >= pd.to_datetime(data_inicio)) &
        (df_filtrado['data'] <= pd.to_datetime(data_fim))
    ]
    
    # Mostrar dados
    if not df_filtrado.empty:
        df_display = df_filtrado[['nome', 'data', 'toneladas_projetadas', 'toneladas_entregues', 'observacoes']].copy()
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        df_display['toneladas_projetadas'] = df_display['toneladas_projetadas'].apply(formatar_numero)
        df_display['toneladas_entregues'] = df_display['toneladas_entregues'].apply(formatar_numero)
        
        df_display.columns = ['Fazenda', 'Data', 'Projetado', 'Entregue', 'Observações']
        
        st.dataframe(df_display, use_container_width=True)
        
        st.info(f"Mostrando {len(df_filtrado)} registros")
    else:
        st.warning("Nenhum registro encontrado com os filtros aplicados.")

# ===================================================================
# RELATÓRIOS
# ===================================================================

def mostrar_relatorios(dados):
    st.header("📋 Relatórios")
    
    tab1, tab2, tab3 = st.tabs(["📊 Relatório Geral", "🏡 Relatório de Fazendas", "📈 Relatório de Produção"])
    
    with tab1:
        relatorio_geral(dados)
    
    with tab2:
        relatorio_fazendas(dados)
    
    with tab3:
        relatorio_producao(dados)

def relatorio_geral(dados):
    st.subheader("📊 Relatório Geral")
    
    stats = calcular_estatisticas(dados)
    
    # Resumo executivo
    st.markdown("### 📋 Resumo Executivo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **🏡 Fazendas:**
        - Total: {stats['total_fazendas']}
        - Ativas: {stats['fazendas_ativas']}
        - Inativas: {stats['total_fazendas'] - stats['fazendas_ativas']}
        
        **🌾 Área Total:**
        - {formatar_numero(stats['total_hectares'])} hectares
        """)
    
    with col2:
        st.markdown(f"""
        **📦 Produção:**
        - Projetado: {formatar_numero(stats['total_projetado'])} ton
        - Entregue: {formatar_numero(stats['total_entregue'])} ton
        - Conclusão: {stats['percentual_conclusao']:.1f}%
        """)
    
    # Gráfico de performance
    if stats['total_projetado'] > 0:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = stats['percentual_conclusao'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Performance Geral (%)"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)

def relatorio_fazendas(dados):
    st.subheader("🏡 Relatório de Fazendas")
    
    fazendas = dados.get('fazendas', [])
    
    if not fazendas:
        st.warning("Nenhuma fazenda cadastrada.")
        return
    
    df = pd.DataFrame(fazendas)
    
    # Estatísticas por estado
    st.markdown("### 📍 Distribuição por Estado")
    
    estado_stats = df.groupby('estado').agg({
        'nome': 'count',
        'hectares': 'sum'
    }).rename(columns={'nome': 'Quantidade', 'hectares': 'Total Hectares'})
    
    estado_stats['Total Hectares'] = estado_stats['Total Hectares'].apply(formatar_numero)
    st.dataframe(estado_stats, use_container_width=True)
    
    # Gráfico de hectares por estado
    fig = px.bar(
        x=estado_stats.index,
        y=[float(x.replace('.', '').replace(',', '.')) for x in estado_stats['Total Hectares']],
        title="🌾 Hectares por Estado",
        labels={'x': 'Estado', 'y': 'Hectares'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Lista detalhada
    st.markdown("### 📋 Lista Detalhada")
    df_display = df[['nome', 'estado', 'cidade', 'hectares', 'status', 'proprietario']].copy()
    df_display['hectares'] = df_display['hectares'].apply(formatar_numero)
    st.dataframe(df_display, use_container_width=True)

def relatorio_producao(dados):
    st.subheader("📈 Relatório de Produção")
    
    producao = dados.get('producao', [])
    fazendas = dados.get('fazendas', [])
    
    if not producao:
        st.warning("Nenhum registro de produção encontrado.")
        return
    
    # Criar DataFrame combinado
    df_producao = pd.DataFrame(producao)
    df_fazendas = pd.DataFrame(fazendas)
    
    df_combined = df_producao.merge(
        df_fazendas[['id', 'nome', 'estado']], 
        left_on='fazenda_id', 
        right_on='id', 
        how='left'
    )
    
    # Resumo por fazenda
    st.markdown("### 🏡 Produção por Fazenda")
    
    resumo_fazenda = df_combined.groupby('nome').agg({
        'toneladas_projetadas': 'sum',
        'toneladas_entregues': 'sum'
    }).reset_index()
    
    resumo_fazenda['percentual'] = (
        resumo_fazenda['toneladas_entregues'] / resumo_fazenda['toneladas_projetadas'] * 100
    ).round(1)
    
    resumo_fazenda['toneladas_projetadas'] = resumo_fazenda['toneladas_projetadas'].apply(formatar_numero)
    resumo_fazenda['toneladas_entregues'] = resumo_fazenda['toneladas_entregues'].apply(formatar_numero)
    
    resumo_fazenda.columns = ['Fazenda', 'Projetado', 'Entregue', '% Conclusão']
    
    st.dataframe(resumo_fazenda, use_container_width=True)
    
    # Gráfico de evolução
    st.markdown("### 📈 Evolução Temporal")
    
    df_combined['data'] = pd.to_datetime(df_combined['data'])
    evolucao = df_combined.groupby('data').agg({
        'toneladas_projetadas': 'sum',
        'toneladas_entregues': 'sum'
    }).reset_index()
    
    fig = px.line(
        evolucao,
        x='data',
        y=['toneladas_projetadas', 'toneladas_entregues'],
        title="📊 Evolução da Produção",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ===================================================================
# IMPORTAR/EXPORTAR
# ===================================================================

def importar_exportar(dados):
    st.header("📤 Importar/Exportar Dados")
    
    tab1, tab2 = st.tabs(["📥 Importar", "📤 Exportar"])
    
    with tab1:
        importar_dados(dados)
    
    with tab2:
        exportar_dados(dados)

def importar_dados(dados):
    st.subheader("📥 Importar Dados")
    
    st.markdown("""
    ### 📋 Formatos Suportados
    - **Excel (.xlsx, .xls)**: Para fazendas e produção
    - **CSV**: Para fazendas e produção
    - **JSON**: Backup completo do sistema
    """)
    
    tipo_import = st.selectbox("Tipo de Importação:", [
        "Fazendas (Excel/CSV)",
        "Produção (Excel/CSV)", 
        "Backup Completo (JSON)"
    ])
    
    arquivo = st.file_uploader(
        "Selecione o arquivo:",
        type=['xlsx', 'xls', 'csv', 'json']
    )
    
    if arquivo:
        try:
            if tipo_import == "Fazendas (Excel/CSV)":
                if arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                    df = pd.read_excel(arquivo)
                
                st.markdown("### 👀 Preview dos Dados")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("✅ Importar Fazendas"):
                    # Processar importação de fazendas
                    importadas = 0
                    for _, row in df.iterrows():
                        nova_fazenda = {
                            "id": gerar_proximo_id(dados['fazendas']),
                            "nome": str(row.get('nome', row.get('FAZENDA', ''))),
                            "estado": str(row.get('estado', 'Goiás')),
                            "cidade": str(row.get('cidade', row.get('CIDADE', ''))),
                            "hectares": float(row.get('hectares', row.get('HA', 0))),
                            "status": "ativa",
                            "proprietario": str(row.get('proprietario', 'Não informado')),
                            "telefone": str(row.get('telefone', '')),
                            "email": str(row.get('email', '')),
                            "data_cadastro": datetime.now().strftime("%Y-%m-%d")
                        }
                        dados['fazendas'].append(nova_fazenda)
                        importadas += 1
                    
                    if salvar_dados(dados):
                        st.success(f"✅ {importadas} fazendas importadas com sucesso!")
                        limpar_cache()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar dados.")
            
            elif tipo_import == "Backup Completo (JSON)":
                dados_json = json.load(arquivo)
                
                st.markdown("### 👀 Preview do Backup")
                st.json(dados_json)
                
                if st.button("✅ Restaurar Backup"):
                    if salvar_dados(dados_json):
                        st.success("✅ Backup restaurado com sucesso!")
                        limpar_cache()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao restaurar backup.")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")

def exportar_dados(dados):
    st.subheader("📤 Exportar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏡 Exportar Fazendas")
        
        fazendas = dados.get('fazendas', [])
        if fazendas:
            df_fazendas = pd.DataFrame(fazendas)
            
            # Excel
            buffer = BytesIO()
            df_fazendas.to_excel(buffer, index=False)
            
            st.download_button(
                label="📊 Download Excel",
                data=buffer.getvalue(),
                file_name=f"fazendas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # CSV
            csv = df_fazendas.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"fazendas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhuma fazenda para exportar.")
    
    with col2:
        st.markdown("### 📈 Exportar Produção")
        
        producao = dados.get('producao', [])
        if producao:
            df_producao = pd.DataFrame(producao)
            
            # Excel
            buffer = BytesIO()
            df_producao.to_excel(buffer, index=False)
            
            st.download_button(
                label="📊 Download Excel",
                data=buffer.getvalue(),
                file_name=f"producao_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # CSV
            csv = df_producao.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name=f"producao_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhum registro de produção para exportar.")
    
    st.markdown("---")
    st.markdown("### 💾 Backup Completo")
    
    # JSON completo
    json_data = json.dumps(dados, ensure_ascii=False, indent=2)
    st.download_button(
        label="💾 Download Backup JSON",
        data=json_data,
        file_name=f"backup_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

def configuracoes(dados):
    st.header("⚙️ Configurações")
    
    tab1, tab2, tab3 = st.tabs(["🔧 Sistema", "📊 Dados", "ℹ️ Sobre"])
    
    with tab1:
        configuracoes_sistema(dados)
    
    with tab2:
        gerenciar_dados(dados)
    
    with tab3:
        sobre_sistema()

def configuracoes_sistema(dados):
    st.subheader("🔧 Configurações do Sistema")
    
    st.markdown("### 🎨 Aparência")
    
    # Tema (simulado - Streamlit não permite mudança dinâmica)
    tema = st.selectbox("Tema:", ["Claro", "Escuro", "Auto"])
    
    st.markdown("### 📊 Dashboard")
    
    auto_refresh = st.checkbox("Atualização automática", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Intervalo (segundos):", 10, 300, 60)
    
    st.markdown("### 🔔 Notificações")
    
    notif_producao = st.checkbox("Alertas de produção", value=True)
    notif_fazendas = st.checkbox("Alertas de fazendas", value=True)
    
    if st.button("💾 Salvar Configurações"):
        # Salvar configurações (simulado)
        st.success("✅ Configurações salvas com sucesso!")

def gerenciar_dados(dados):
    st.subheader("📊 Gerenciar Dados")
    
    # Estatísticas
    stats = calcular_estatisticas(dados)
    
    st.markdown("### 📈 Estatísticas do Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏡 Fazendas", stats['total_fazendas'])
        st.metric("🌾 Hectares", formatar_numero(stats['total_hectares']))
    
    with col2:
        producao_count = len(dados.get('producao', []))
        st.metric("📈 Registros Produção", producao_count)
        st.metric("📦 Total Projetado", formatar_numero(stats['total_projetado']))
    
    with col3:
        # Tamanho dos dados
        dados_size = len(json.dumps(dados))
        st.metric("💾 Tamanho Dados", f"{dados_size:,} bytes")
        st.metric("✅ % Conclusão", f"{stats['percentual_conclusao']:.1f}%")
    
    st.markdown("---")
    st.markdown("### 🗑️ Limpeza de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Limpar Cache", help="Limpa o cache do Streamlit"):
            limpar_cache()
            st.success("✅ Cache limpo!")
    
    with col2:
        if st.button("🔄 Resetar Dados", help="Volta aos dados iniciais"):
            if st.session_state.get('confirmar_reset'):
                # Resetar para dados iniciais
                if salvar_dados(DADOS_INICIAIS):
                    st.success("✅ Dados resetados!")
                    limpar_cache()
                    st.rerun()
                else:
                    st.error("❌ Erro ao resetar dados.")
            else:
                st.session_state.confirmar_reset = True
                st.warning("⚠️ Clique novamente para confirmar!")

def sobre_sistema():
    st.subheader("ℹ️ Sobre o Sistema")
    
    st.markdown("""
    ### 🌲 G&V Florestal - Controle de Fazendas
    
    **Versão:** 2.0 (Streamlit)
    **Desenvolvido para:** Gestão eficiente de fazendas florestais
    
    ### 🎯 Funcionalidades Principais
    
    - **📊 Dashboard Interativo**: Visão geral com métricas e gráficos
    - **🏡 Gestão de Fazendas**: Cadastro, edição e controle completo
    - **📈 Controle de Produção**: Acompanhamento de metas e entregas
    - **📋 Relatórios Detalhados**: Análises e estatísticas avançadas
    - **📤 Import/Export**: Integração com Excel, CSV e JSON
    - **⚙️ Configurações**: Personalização e gerenciamento
    
    ### 🛠️ Tecnologias Utilizadas
    
    - **Streamlit**: Interface web interativa
    - **Pandas**: Manipulação de dados
    - **Plotly**: Gráficos interativos
    - **JSON**: Persistência de dados
    
    ### 📞 Suporte
    
    Para suporte técnico ou sugestões, entre em contato através do sistema.
    
    ---
    
    **© 2024 G&V Florestal - Todos os direitos reservados**
    """)
    
    # Informações técnicas
    with st.expander("🔧 Informações Técnicas"):
        st.markdown(f"""
        - **Arquivo de dados:** `{DADOS_FILE}`
        - **Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        - **Streamlit versão:** {st.__version__}
        - **Python versão:** Disponível no ambiente
        """)

# ===================================================================
# EXECUÇÃO PRINCIPAL
# ===================================================================

if __name__ == "__main__":
    main()
