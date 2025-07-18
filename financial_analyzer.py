import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

class FinancialAnalyzer:
    def __init__(self, df):
        self.df = df
        self.df['Data'] = pd.to_datetime(self.df['Data'])
        
    def calculate_financial_health_score(self):
        """Calculate financial health score based on spending patterns"""
        score = 100
        insights = []
        
        category_concentration = self.df.groupby('Categoria')['Valor'].sum()
        max_category_pct = (category_concentration.max() / category_concentration.sum()) * 100
        
        if max_category_pct > 50:
            score -= 20
            insights.append(f"⚠️ Concentração alta em {category_concentration.idxmax()} ({max_category_pct:.1f}%)")
        elif max_category_pct > 30:
            score -= 10
            insights.append(f"⚡ Concentração moderada em {category_concentration.idxmax()} ({max_category_pct:.1f}%)")
        else:
            insights.append(f"✅ Gastos bem diversificados")
        
        daily_spending = self.df.groupby('Data')['Valor'].sum()
        cv = daily_spending.std() / daily_spending.mean()
        
        if cv > 1.5:
            score -= 15
            insights.append("⚠️ Gastos muito irregulares")
        elif cv > 1.0:
            score -= 8
            insights.append("⚡ Gastos moderadamente irregulares")
        else:
            insights.append("✅ Gastos consistentes")
        
        x = np.arange(len(daily_spending))
        if len(x) > 1:
            trend = np.polyfit(x, daily_spending.values, 1)[0]
            if trend > daily_spending.mean() * 0.1:
                score -= 25
                insights.append("⚠️ Tendência de aumento significativo nos gastos")
            elif trend > 0:
                score -= 10
                insights.append("⚡ Tendência de aumento moderado nos gastos")
            else:
                insights.append("✅ Gastos estáveis ou em redução")
        
        return max(0, score), insights
    
    def detect_spending_patterns(self):
        """Detect spending patterns and insights based on the data."""
        patterns = []
        pt_days = {
            'Monday':    'Segunda-feira',
            'Tuesday':   'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday':  'Quinta-feira',
            'Friday':    'Sexta-feira',
            'Saturday':  'Sábado',
            'Sunday':    'Domingo'
        }
        
        weekday_spending = (
            self.df
            .groupby(
                self.df['Data']
                .dt.day_name()
                .map(pt_days)
            )
            ['Valor']
            .sum()
        )
        highest_day = weekday_spending.idxmax()
        lowest_day = weekday_spending.idxmin()
        
        patterns.append({
            'tipo': 'Dia da semana',
            'insight': f"Você gasta mais às {highest_day}s (R\$ {weekday_spending[highest_day]:.2f}) e menos às {lowest_day}s (R\$ {weekday_spending[lowest_day]:.2f})"
        })
        
        if 'time' in self.df.columns:
            hourly_spending = self.df.groupby(pd.to_datetime(self.df['time']).dt.hour)['Valor'].sum()
            peak_hour = hourly_spending.idxmax()
            patterns.append({
                'tipo': 'Horário',
                'insight': f"Seu horário de maior gasto é às {peak_hour}h"
            })
        
        monthly_category = self.df.groupby(['Mês', 'Categoria'])['Valor'].sum().reset_index()
        growing_categories = []
        
        for category in self.df['Categoria'].unique():
            cat_data = monthly_category[monthly_category['Categoria'] == category]
            if len(cat_data) > 1:
                trend = np.polyfit(range(len(cat_data)), cat_data['Valor'], 1)[0]
                if trend > 0:
                    growing_categories.append(category)
        
        if growing_categories:
            patterns.append({
                'tipo': 'Tendência de categorias',
                'insight': f"Categorias em crescimento: {', '.join(growing_categories[:3])}"
            })
        
        return patterns
    
    def predict_next_month_spending(self):
        """Predict next month's spending based on historical data."""
        monthly_totals = self.df.groupby('Mês')['Valor'].sum()
        
        if len(monthly_totals) < 2:
            return None, "Dados insuficientes para previsão. Por favor, forneça pelo menos 2 meses de dados."
        
        recent_months = monthly_totals.tail(3)
        predicted_spending = recent_months.mean()
        
        last_month = monthly_totals.iloc[-1]
        trend = (last_month - monthly_totals.iloc[-2]) / monthly_totals.iloc[-2]
        
        if abs(trend) > 0.1:
            predicted_spending *= (1 + trend * 0.5)
        
        return predicted_spending, f"Baseado na média dos últimos {len(recent_months)} meses"
    
    def find_outliers(self, threshold=2):
        """Find outliers in the spending data based on Z-score."""
        z_scores = np.abs((self.df['Valor'] - self.df['Valor'].mean()) / self.df['Valor'].std())
        outliers = self.df[z_scores > threshold].sort_values('Valor', ascending=False)
        
        return outliers[['Data', 'description', 'Categoria', 'Valor']].head(10)
    
    def category_efficiency_analysis(self):
        """Analyze spending efficiency by category."""
        category_stats = self.df.groupby('Categoria').agg({
            'Valor': ['sum', 'mean', 'count', 'std']
        }).round(2)
        
        category_stats.columns = ['Total', 'Média', 'Frequência', 'Desvio']
        category_stats['Eficiência'] = category_stats['Total'] / category_stats['Frequência']
        category_stats['Consistência'] = category_stats['Média'] / category_stats['Desvio']
        
        category_stats['Classificação'] = pd.cut(
            category_stats['Eficiência'],
            bins=3,
            labels=['Eficiente', 'Moderado', 'Ineficiente']
        )
        
        return category_stats.sort_values('Total', ascending=False)
    
    def generate_recommendations(self):
        """Generate personalized recommendations based on spending data."""
        recommendations = []
        
        category_spending = self.df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        total_spending = category_spending.sum()
        
        top_category = category_spending.index[0]
        top_percentage = (category_spending.iloc[0] / total_spending) * 100
        
        if top_percentage > 40:
            recommendations.append({
                'tipo': 'Alerta',
                'titulo': f'Concentração alta em {top_category}',
                'descricao': f'Você está gastando {top_percentage:.1f}% do seu orçamento com {top_category}. Considere revisar esses gastos.',
                'acao': f'Analise detalhadamente os gastos em {top_category} e identifique oportunidades de economia.'
            })
        
        daily_spending = self.df.groupby('Data')['Valor'].sum()
        if len(daily_spending) > 7:
            recent_avg = daily_spending.tail(7).mean()
            overall_avg = daily_spending.mean()
            
            if recent_avg > overall_avg * 1.2:
                recommendations.append({
                    'tipo': 'Atenção',
                    'titulo': 'Gastos recentes acima da média',
                    'descricao': f'Seus gastos dos últimos 7 dias (R$ {recent_avg:.2f}/dia) estão 20% acima da média geral.',
                    'acao': 'Monitore mais de perto os gastos dos próximos dias para voltar ao padrão normal.'
                })
        
        savings_opportunity = category_spending.head(3).sum() * 0.1  # 10% of top 3 categories
        recommendations.append({
            'tipo': 'Oportunidade',
            'titulo': 'Potencial de economia',
            'descricao': f'Reduzindo 10% dos gastos nas suas 3 principais categorias, você poderia economizar R$ {savings_opportunity:.2f} por mês.',
            'acao': 'Foque em otimizar gastos em: ' + ', '.join(category_spending.head(3).index)
        })
        
        return recommendations
    
    def create_advanced_visualizations(self):
        """Create advanced visualizations."""
        
        # 1. Waterfall chart of spending
        category_spending = self.df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Gastos por Categoria",
            orientation="v",
            measure=["relative"] * len(category_spending),
            x=category_spending.index,
            y=category_spending.values,
            text=[f"R$ {v:.2f}" for v in category_spending.values],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig_waterfall.update_layout(
            title="Decomposição dos Gastos por Categoria",
            showlegend=False,
            height=500
        )
        
        # 2. Correlation between daily spending and distribution
        daily_spending = self.df.groupby('Data')['Valor'].sum().reset_index()
        daily_spending['MA7'] = daily_spending['Valor'].rolling(window=7).mean()
        
        fig_correlation = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Gastos Diários', 'Distribuição de Gastos'),
            vertical_spacing=0.1
        )
        
        fig_correlation.add_trace(
            go.Scatter(
                x=daily_spending['Data'],
                y=daily_spending['Valor'],
                mode='lines+markers',
                name='Gastos Diários',
                line=dict(color='lightblue')
            ),
            row=1, col=1
        )
        
        fig_correlation.add_trace(
            go.Scatter(
                x=daily_spending['Data'],
                y=daily_spending['MA7'],
                mode='lines',
                name='Média Móvel 7 dias',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
        
        fig_correlation.add_trace(
            go.Histogram(
                x=daily_spending['Valor'],
                nbinsx=20,
                name='Distribuição',
                marker_color='lightgreen'
            ),
            row=2, col=1
        )
        
        fig_correlation.update_layout(height=600, showlegend=True)
        
        return fig_waterfall, fig_correlation