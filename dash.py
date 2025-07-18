import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

from financial_analyzer import FinancialAnalyzer
from financial_tab import show_financial_analysis_tab

import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Dashboard de Finanças Pessoais",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: ##3f3f3f61;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
            
    div.stMetric label[data-testid="stMetricLabel"] p {
        font-size: 1.5rem !important;
    }

    /* (Opcional) aumenta também o valor */
    div.stMetric div[data-testid="stMetricValue"] > div p {
        font-size: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess financial data."""
    try:
        df = pd.read_csv("finances.csv")
        df["Mês"] = df["date"].apply(lambda x: "-".join(x.split("-")[:-1]))
        df["Data"] = pd.to_datetime(df["date"])
        df["Ano"] = df["Data"].dt.year
        df["Mês_Nome"] = df["Data"].dt.strftime("%B")
        df["Dia_Semana"] = df["Data"].dt.day_name()
        df = df[df["category"] != "Saldo do dia"]
        df = df[~df["description"].str.lower().str.contains("lucas m", na=False)]
        df["amount"] = df["amount"].abs()
        df = df.rename(columns={"category": "Categoria", "amount": "Valor"})
        return df
    except FileNotFoundError:
        st.error("Arquivo 'finances.csv' não encontrado. Execute primeiro o classificador de gastos.")
        st.stop()


def calculate_insights(df, df_filtered):
    """Calculate basic financial insights from the filtered DataFrame."""
    insights = {}
    insights['total_gastos'] = df_filtered["Valor"].sum()
    insights['media_diaria'] = df_filtered.groupby("Data")["Valor"].sum().mean()
    insights['maior_gasto'] = df_filtered["Valor"].max()
    insights['categoria_mais_cara'] = df_filtered.groupby("Categoria")["Valor"].sum().idxmax()
    insights['transacoes_total'] = len(df_filtered)
    meses_unicos = sorted(df["Mês"].unique())
    if len(meses_unicos) > 1:
        mes_atual = df_filtered["Mês"].iloc[0] if len(df_filtered) else None
        if mes_atual and mes_atual in meses_unicos:
            idx = meses_unicos.index(mes_atual)
            if idx > 0:
                mes_anterior = meses_unicos[idx - 1]
                df_anterior = df[df["Mês"] == mes_anterior]
                insights['gasto_anterior'] = df_anterior["Valor"].sum()
                insights['variacao_mensal'] = ((insights['total_gastos'] - insights['gasto_anterior']) / insights['gasto_anterior']) * 100
    gastos_por_dia = df_filtered.groupby("Data")["Valor"].sum().reset_index()
    if len(gastos_por_dia) > 1:
        x = np.arange(len(gastos_por_dia))
        y = gastos_por_dia["Valor"].values
        z = np.polyfit(x, y, 1)
        insights['tendencia'] = "crescente" if z[0] > 0 else "decrescente"
    return insights


def create_advanced_charts(df_filtered):
    """Create advanced visualizations for the financial data."""

    category_dist = df_filtered.groupby("Categoria")["Valor"].sum().reset_index()
    category_dist["Percentual"] = (category_dist["Valor"] / category_dist["Valor"].sum()) * 100
    fig_pie = px.pie(
        category_dist, values='Valor', names='Categoria', hole=0.4,
        title='Distribuição de Gastos por Categoria', color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    # Expenses over time
    gastos_tempo = df_filtered.groupby("Data")["Valor"].sum().reset_index()
    fig_line = px.line(
        gastos_tempo, x='Data', y='Valor', title='Evolução dos Gastos no Período', markers=True
    )
    fig_line.update_traces(line_color='#667eea')
    # Heatmap of expenses by day of week and category
    heatmap_data = df_filtered.groupby(['Dia_Semana', 'Categoria'])['Valor'].sum().reset_index()
    fig_heatmap = px.density_heatmap(
        heatmap_data, x='Dia_Semana', y='Categoria', z='Valor', title='Heatmap de Gastos por Dia/Semana e Categoria'
    )
    # Top 10 expenses
    top_gastos = df_filtered.nlargest(10, 'Valor')
    fig_top = px.bar(
        top_gastos, x='Valor', y='description', orientation='h', title='Top 10 Maiores Gastos Individuais', color='Categoria'
    )
    return fig_pie, fig_line, fig_heatmap, fig_top


def create_comparison_chart(df, selected_categories):
    """Create a comparison chart between months"""
    df_comp = df[df['Categoria'].isin(selected_categories)] if selected_categories else df
    monthly = df_comp.groupby(['Mês', 'Categoria'])['Valor'].sum().reset_index()
    fig = px.bar(
        monthly, x='Mês', y='Valor', color='Categoria', barmode='stack',
        title='Comparação de Gastos por Mês e Categoria'
    )
    return fig


def display_insights(insights):
    """Display financial insights in a structured format."""
    st.markdown("### 📊 Insights Financeiros")
    cols = st.columns(3)
    if 'variacao_mensal' in insights:
        variacao = insights['variacao_mensal']
        cols[0].markdown(f"<div class='insight-box'><h4>📈 Variação Mensal</h4><p style='color: {'green' if variacao<0 else 'orange' if variacao<10 else 'red'};'>{variacao:+.1f}% em relação ao mês anterior</p></div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div class='insight-box'><h4>🎯 Categoria Dominante</h4><p><strong>{insights['categoria_mais_cara']}</strong></p></div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div class='insight-box'><h4>💳 Gasto Médio Diário</h4><p><strong>R$ {insights['media_diaria']:,.2f}</strong></p></div>", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Dashboard de Finanças Pessoais</h1>', unsafe_allow_html=True)

    df = load_data()
    # Sidebar: filters
    st.sidebar.header("🔍 Filtros")
    tipos = ["Mês específico", "Múltiplos meses", "Ano completo"]
    sel_tipo = st.sidebar.selectbox("Tipo de período", tipos)
    if sel_tipo == "Mês específico":
        mes = st.sidebar.selectbox("Selecione o mês", sorted(df["Mês"].unique()))
        df_filtered = df[df['Mês']==mes]
    elif sel_tipo == "Múltiplos meses":
        meses = st.sidebar.multiselect("Selecione os meses", sorted(df["Mês"].unique()))
        df_filtered = df[df['Mês'].isin(meses)] if meses else df
    else:
        ano = st.sidebar.selectbox("Selecione o ano", sorted(df["Ano"].unique()))
        df_filtered = df[df['Ano']==ano]
    # Filters by category and value
    categories = df["Categoria"].unique().tolist()
    selected_categories = st.sidebar.multiselect("Filtrar por Categorias", categories, default=categories)
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(selected_categories)]
    # Value range filter
    vmin, vmax = st.sidebar.slider("Faixa de valores (R$)", float(df["Valor"].min()), float(df["Valor"].max()), (float(df["Valor"].min()), float(df["Valor"].max())))
    df_filtered = df_filtered[(df_filtered["Valor"]>=vmin)&(df_filtered["Valor"]<=vmax)]
    if df_filtered.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        return

    analyzer = FinancialAnalyzer(df_filtered)
    insights = calculate_insights(df, df_filtered)

    # windows
    main_tab, financial_tab = st.tabs(["📊 Visão Geral", "🔍 Análise Financeira Avançada"])
    with main_tab:
        st.markdown("### 📊 Resumo Executivo")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Gastos", f"R$ {insights['total_gastos']:,.2f}", delta=f"{insights.get('variacao_mensal', 0):+.1f}%" if 'variacao_mensal' in insights else None)
        c2.metric("Número de Transações", f"{insights['transacoes_total']:,}")
        c3.metric("Maior Gasto Individual", f"R$ {insights['maior_gasto']:,.2f}")
        c4.metric("Gasto Médio Diário", f"R$ {insights['media_diaria']:,.2f}")

        display_insights(insights)

        # Main charts
        fig_pie, fig_line, fig_heatmap, fig_top = create_advanced_charts(df_filtered)
        col_a, col_b = st.columns([1,1])
        with col_a:
            st.plotly_chart(fig_pie, use_container_width=True)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        with col_b:
            st.plotly_chart(fig_line, use_container_width=True)
            st.plotly_chart(fig_top, use_container_width=True)

        # Comparison chart
        if len(df["Mês"].unique())>1:
            st.markdown("### 📈 Análise Comparativa")
            fig_comp = create_comparison_chart(df, selected_categories)
            st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("### 📋 Transações Detalhadas")
        o1, o2, o3 = st.columns(3)
        sort_by = o1.selectbox("Ordenar por", ["Data","Valor","Categoria"])
        order = o2.selectbox("Ordem", ["Crescente","Decrescente"])
        nrows = o3.selectbox("Linhas por página", [10,25,50,100])
        asc = order == "Crescente"
        df_display = df_filtered.sort_values(by=sort_by, ascending=asc)
        st.dataframe(df_display[['Data','description','Categoria','Valor']].head(nrows), use_container_width=True)

        # Statistics by category
        st.markdown("### 📊 Estatísticas por Categoria")
        stats = df_filtered.groupby('Categoria').agg({'Valor':['sum','mean','count','max','min']}).round(2)
        stats.columns = ['Total','Média','Transações','Maior','Menor']
        stats = stats.sort_values('Total', ascending=False)
        st.dataframe(stats, use_container_width=True)

        # Download CSV
        st.markdown("### 💾 Download dos Dados")
        csv = df_filtered.to_csv(index=False)
        st.download_button("📥 Baixar dados filtrados (CSV)", data=csv,
                            file_name=f"financas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv")
        st.markdown("---")
        st.markdown(f"<div style='text-align:center;color:gray;font-size:0.8em;'>Dashboard gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | Total de {len(df)} transações no dataset completo</div>", unsafe_allow_html=True)
    with financial_tab:
        show_financial_analysis_tab(df_filtered, analyzer)

if __name__ == "__main__":
    main()
