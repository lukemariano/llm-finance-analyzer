import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

def show_financial_analysis_tab(df, analyzer):
    """
    Display the financial analysis tab with advanced insights and visualizations.
    """
    st.header("🔍 Análise Financeira Avançada")
    
    # Seção 1: Health Score and Insights
    st.subheader("📊 Score de Saúde Financeira")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        score, insights = analyzer.calculate_financial_health_score()
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score de Saúde"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.write("### Insights do Score:")
        for insight in insights:
            if "⚠️" in insight:
                st.warning(insight)
            elif "⚡" in insight:
                st.info(insight)
            else:
                st.success(insight)
    
    # Seção 2: Expenses Patterns Section
    st.subheader("🎯 Padrões de Gasto Identificados")
    patterns = analyzer.detect_spending_patterns()
    
    cols = st.columns(len(patterns))
    for i, pattern in enumerate(patterns):
        with cols[i]:
            st.metric(
                label=pattern['tipo'],
                value="",
                help=pattern['insight']
            )
            st.write(pattern['insight'])
    
    # Seção 3: Predictions and Outliers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔮 Previsão Próximo Mês")
        predicted_spending, method = analyzer.predict_next_month_spending()
        
        if predicted_spending:
            current_month_spending = df[df['Mês'] == df['Mês'].iloc[-1]]['Valor'].sum()
            
            st.metric(
                label="Gasto Previsto",
                value=f"R$ {predicted_spending:.2f}",
                delta=f"R$ {predicted_spending - current_month_spending:.2f}"
            )
            st.caption(f"Método: {method}")
        else:
            st.warning(method)
    
    with col2:
        st.subheader("⚡ Gastos Outliers")
        outliers = analyzer.find_outliers()
        
        if not outliers.empty:
            st.dataframe(
                outliers,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum gasto outlier identificado")
    
    # Seção 4: Efficiency Analysis by Category
    st.subheader("⚖️ Análise de Eficiência por Categoria")
    efficiency_analysis = analyzer.category_efficiency_analysis()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            efficiency_analysis,
            use_container_width=True
        )
    
    with col2:
        classification_counts = efficiency_analysis['Classificação'].value_counts()
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=classification_counts.index,
            values=classification_counts.values,
            hole=0.3
        )])
        
        fig_pie.update_layout(
            title="Classificação de Eficiência",
            height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Seção 5: Personalized Recommendations
    st.subheader("💡 Recomendações Personalizadas")
    recommendations = analyzer.generate_recommendations()
    
    for rec in recommendations:
        if rec['tipo'] == 'Alerta':
            st.error(f"**{rec['titulo']}**")
        elif rec['tipo'] == 'Atenção':
            st.warning(f"**{rec['titulo']}**")
        else:
            st.info(f"**{rec['titulo']}**")
        
        st.write(rec['descricao'])
        st.write(f"**Ação recomendada:** {rec['acao']}")
        st.divider()

    # Seção 6: Advanced Visualizations
    st.subheader("📈 Visualizações Avançadas")
    
    tab1, tab2 = st.tabs(["Waterfall de Gastos", "Análise Temporal"])
    
    with tab1:
        fig_waterfall, fig_correlation = analyzer.create_advanced_visualizations()
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    with tab2:
        st.plotly_chart(fig_correlation, use_container_width=True)

    # Seção 7: Executive Summary
    with st.expander("📋 Resumo Executivo"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_spending = df['Valor'].sum()
            st.metric("Gasto Total", f"R$ {total_spending:.2f}")
        
        with col2:
            avg_daily = df.groupby('Data')['Valor'].sum().mean()
            st.metric("Média Diária", f"R$ {avg_daily:.2f}")
        
        with col3:
            top_category = df.groupby('Categoria')['Valor'].sum().idxmax()
            st.metric("Categoria Principal", top_category)
        
        st.write("### Principais Conclusões:")
        st.write(f"- Seu score de saúde financeira é **{score}/100**")
        st.write(f"- Você tem **{len(patterns)}** padrões de gasto identificados")
        st.write(f"- **{len(outliers)}** gastos outliers foram detectados")
        st.write(f"- **{len(recommendations)}** recomendações personalizadas foram geradas")