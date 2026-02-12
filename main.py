from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import traceback

API_BASE_URL = "http://localhost:12500"

# ==================== CONFIGURACIÓN ====================
app = Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap",
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="Dashboard Analytics | Plan Manager"
)
server = app.server

# Inyectar estilos personalizados de clase empresarial
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary: #2563eb;
                --secondary: #7c3aed;
                --success: #059669;
                --warning: #d97706;
                --danger: #dc2626;
                --dark: #0f172a;
                --light: #f1f5f9;
                --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --gradient-dark: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            }
            
            * {
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
                box-sizing: border-box;
            }
            
            body {
                background: #f8fafc;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            
            /* Sidebar Profesional */
            .pro-sidebar {
                background: var(--gradient-dark);
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                width: 280px;
                z-index: 1000;
                box-shadow: var(--shadow-xl);
                overflow-y: auto;
                transition: transform 0.3s ease;
            }
            
            .pro-sidebar::-webkit-scrollbar {
                width: 6px;
            }
            
            .pro-sidebar::-webkit-scrollbar-track {
                background: rgba(255,255,255,0.05);
            }
            
            .pro-sidebar::-webkit-scrollbar-thumb {
                background: rgba(255,255,255,0.2);
                border-radius: 3px;
            }
            
            .sidebar-header {
                padding: 30px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                background: rgba(255,255,255,0.05);
            }
            
            .sidebar-logo {
                display: flex;
                align-items: center;
                gap: 12px;
                color: white;
            }
            
            .sidebar-logo i {
                font-size: 28px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .sidebar-nav {
                padding: 20px 0;
            }
            
            .nav-item {
                margin: 4px 12px;
            }
            
            .nav-link-pro {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                color: rgba(255,255,255,0.7);
                text-decoration: none;
                border-radius: 12px;
                transition: all 0.3s ease;
                font-weight: 500;
                border-left: 3px solid transparent;
            }
            
            .nav-link-pro:hover {
                background: rgba(255,255,255,0.1);
                color: white;
                border-left-color: #667eea;
                transform: translateX(4px);
            }
            
            .nav-link-pro.active {
                background: rgba(102, 126, 234, 0.2);
                color: white;
                border-left-color: #667eea;
            }
            
            .nav-link-pro i {
                width: 20px;
                text-align: center;
                font-size: 16px;
            }
            
            /* Main Content */
            .main-content {
                margin-left: 280px;
                padding: 24px;
                min-height: 100vh;
            }
            
            /* Top Bar */
            .top-bar {
                background: white;
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 24px;
                box-shadow: var(--shadow-sm);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .breadcrumb-pro {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #64748b;
                font-size: 14px;
            }
            
            .breadcrumb-pro i {
                font-size: 12px;
            }
            
            .breadcrumb-current {
                color: var(--dark);
                font-weight: 600;
            }
            
            /* KPI Cards */
            .kpi-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 24px;
            }
            
            .kpi-card {
                background: white;
                border-radius: 16px;
                padding: 24px;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e2e8f0;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .kpi-card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-4px);
                border-color: var(--primary);
            }
            
            .kpi-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
            }
            
            .kpi-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            }
            
            .kpi-label {
                font-size: 14px;
                color: #64748b;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .kpi-icon {
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }
            
            .kpi-value {
                font-size: 32px;
                font-weight: 700;
                color: var(--dark);
                margin-bottom: 8px;
                font-family: 'JetBrains Mono', monospace;
            }
            
            .kpi-trend {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            
            .trend-up {
                color: var(--success);
            }
            
            .trend-down {
                color: var(--danger);
            }
            
            /* Chart Cards */
            .chart-card {
                background: white;
                border-radius: 16px;
                padding: 24px;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e2e8f0;
                margin-bottom: 24px;
            }
            
            .chart-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 16px;
                border-bottom: 2px solid #f1f5f9;
            }
            
            .chart-title {
                font-size: 18px;
                font-weight: 700;
                color: var(--dark);
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .chart-title i {
                color: var(--primary);
            }
            
            /* Filter Bar */
            .filter-bar {
                background: white;
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 24px;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e2e8f0;
            }
            
            .filter-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            /* Buttons */
            .btn-pro {
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
                transition: all 0.3s ease;
                border: none;
                font-size: 14px;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
            }
            
            .btn-pro:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                color: white;
            }
            
            .btn-secondary {
                background: #64748b;
                color: white;
            }
            
            .btn-outline {
                background: white;
                border: 2px solid var(--primary);
                color: var(--primary);
            }
            
            /* Forms */
            .form-pro {
                background: white;
                border-radius: 16px;
                padding: 32px;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e2e8f0;
            }
            
            .form-section {
                margin-bottom: 32px;
            }
            
            .form-section-title {
                font-size: 16px;
                font-weight: 700;
                color: var(--dark);
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 2px solid #f1f5f9;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .form-section-title i {
                color: var(--primary);
            }
            
            .input-group-pro {
                margin-bottom: 20px;
            }
            
            .input-label {
                font-size: 14px;
                font-weight: 600;
                color: #475569;
                margin-bottom: 8px;
                display: block;
            }
            
            .input-pro {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.3s ease;
                background: #f8fafc;
            }
            
            .input-pro:focus {
                outline: none;
                border-color: var(--primary);
                background: white;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }
            
            /* Data Tables */
            .dash-table-container {
                border-radius: 12px;
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                border: 1px solid #e2e8f0;
            }
            
            .dash-spreadsheet-container .dash-spreadsheet-inner th {
                background: var(--dark) !important;
                color: white !important;
                font-weight: 600 !important;
                padding: 16px !important;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            
            .dash-spreadsheet-container .dash-spreadsheet-inner td {
                padding: 16px !important;
                border-bottom: 1px solid #f1f5f9 !important;
            }
            
            .dash-spreadsheet-container .dash-spreadsheet-inner tr:hover {
                background: #f8fafc !important;
            }
            
            /* Alerts */
            .alert-pro {
                border-radius: 12px;
                padding: 16px 20px;
                border-left: 4px solid;
                margin-bottom: 20px;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Loading Spinner */
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Status Badge */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            
            .status-active {
                background: #d1fae5;
                color: #065f46;
            }
            
            .status-inactive {
                background: #fee2e2;
                color: #991b1b;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .pro-sidebar {
                    transform: translateX(-100%);
                }
                
                .main-content {
                    margin-left: 0;
                }
                
                .kpi-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''



# ==================== COMPONENTES REUTILIZABLES ====================

def create_kpi_card(title, value, color="primary", detail=None):
    """
    Crea una tarjeta KPI simple y profesional sin iconos.
    
    title  : str - nombre del KPI
    value  : str/int/float - valor principal del KPI
    color  : str - color de la tarjeta ('primary', 'success', 'warning', 'danger', 'secondary')
    detail : str - texto adicional o comparación (opcional)
    """
    
    bg_colors = {
        'primary': '#e0f2fe',    # azul claro
        'success': '#d1fae5',    # verde claro
        'warning': '#fef9c3',    # amarillo claro
        'danger': '#fee2e2',     # rojo claro
        'secondary': '#f3f4f6'   # gris claro
    }
    
    text_colors = {
        'primary': '#0369a1',
        'success': '#059669',
        'warning': '#ca8a04',
        'danger': '#b91c1c',
        'secondary': '#374151'
    }
    
    return html.Div(
        [
            html.Div(title, className="kpi-label", style={'fontWeight': '600', 'fontSize': '14px', 'marginBottom': '5px'}),
            html.Div(str(value), className="kpi-value", style={'fontWeight': '700', 'fontSize': '24px'}),
            html.Div(detail or "", className="kpi-detail", style={'fontSize': '12px', 'color': '#4b5563', 'marginTop': '3px'})
        ],
        className="kpi-card",
        style={
            'background': bg_colors.get(color, bg_colors['primary']),
            'color': text_colors.get(color, text_colors['primary']),
            'padding': '15px 20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
            'flex': '1',  # para que se distribuyan horizontalmente
            'minWidth': '120px',
            'textAlign': 'center'
        }
    )


def create_chart_card(title, icon, children, actions=None):
    """Crea una tarjeta con gráfico"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className=icon),
                title
            ], className="chart-title"),
            html.Div(actions) if actions else html.Div()
        ], className="chart-header"),
        children
    ], className="chart-card")

# ==================== SIDEBAR ====================
sidebar = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-chart-line"),
            html.Div([
                html.H4("CENTRO DE CONTROL", style={'margin': 0, 'fontSize': '20px', 'fontWeight': '700'}),
                html.P("App Manager", style={'margin': 0, 'fontSize': '12px', 'opacity': '0.7'})
            ])
        ], className="sidebar-logo")
    ], className="sidebar-header"),
    
    html.Div([
        html.Div([
            dcc.Link([
                html.I(className="fas fa-home"),
                html.Span("Dashboard")
            ], href="/", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-plus-circle"),
                html.Span("Crear Plan")
            ], href="/create", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-list"),
                html.Span("Todos los Planes")
            ], href="/all-plans", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-filter"),
                html.Span("Por Categoría")
            ], href="/by-category", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-tags"),
                html.Span("Categorías")
            ], href="/categories", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)', 'margin': '20px 12px'}),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-chart-bar"),
                html.Span("Analytics")
            ], href="/analytics", className="nav-link-pro"),
        ], className="nav-item"),
        
        html.Div([
            dcc.Link([
                html.I(className="fas fa-file-export"),
                html.Span("Exportar Datos")
            ], href="/export", className="nav-link-pro"),
        ], className="nav-item"),
    ], className="sidebar-nav"),
    
    html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-circle fa-xs", style={'color': '#10b981'}),
                html.Span("API Conectada", style={'fontSize': '13px', 'color': 'rgba(255,255,255,0.7)'})
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '8px'})
        ], id="api-status-sidebar", style={'padding': '16px'})
    ], style={'position': 'absolute', 'bottom': '0', 'left': '0', 'right': '0', 'borderTop': '1px solid rgba(255,255,255,0.1)'})
    
], className="pro-sidebar")

# ==================== LAYOUTS ====================

# Dashboard Principal
dashboard_layout = html.Div([
    # Top Bar
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Dashboard", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
        html.Div([
            html.Span(datetime.now().strftime("%d %B, %Y"), style={'fontSize': '14px', 'color': '#64748b', 'fontWeight': '500'})
        ])
    ], className="top-bar"),
    
    # KPIs
    html.Div(id="dashboard-kpis", className="kpi-grid"),
    
    # Gráficos
    dbc.Row([
        dbc.Col([
            create_chart_card(
                "Agenda Mensual de Planes",
                "fas fa-chart-pie",
                dcc.Graph(id="category-pie-chart", config={'displayModeBar': False})
            )
        ], md=6),
        dbc.Col([
            create_chart_card(
                "Tabla de agostamiento",
                "fas fa-chart-bar",
                dcc.Graph(id="status-bar-chart", config={'displayModeBar': False})
            )
        ], md=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            create_chart_card(
                "Top 10 Planes por Vistas",
                "fas fa-trophy",
                dcc.Graph(id="top-plans-chart", config={'displayModeBar': False})
            )
        ], md=12)
    ]),
    
    # Interval para actualización automática
    dcc.Interval(id='interval-dashboard', interval=30*1000, n_intervals=0)
    
], className="main-content")

# Crear Plan (mejorado)
create_layout = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Crear Plan", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
    ], className="top-bar"),
    
    html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-info-circle"),
                "Información Básica"
            ], className="form-section-title"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Nombre del Plan", className="input-label"),
                        dbc.Input(id="name", placeholder="Ej: Concierto Rock en Vivo", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.Label("Ubicación", className="input-label"),
                        dbc.Input(id="location", placeholder="Ej: Parque Simón Bolívar", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
            ]),
            
            html.Div([
                html.Label("Descripción", className="input-label"),
                dbc.Textarea(id="description", placeholder="Describe el plan en detalle...", className="input-pro", style={'minHeight': '120px'})
            ], className="input-group-pro"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Fecha y Hora", className="input-label"),
                        dbc.Input(id="date", type="datetime-local", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.Label("Costo Estimado ($)", className="input-label"),
                        dbc.Input(id="costEstimate", type="number", placeholder="0", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
            ]),
        ], className="form-section"),
        
        html.Div([
            html.Div([
                html.I(className="fas fa-cog"),
                "Configuración"
            ], className="form-section-title"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("URL de Imagen", className="input-label"),
                        dbc.Input(id="imageUrl", placeholder="https://ejemplo.com/imagen.jpg", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.Label("URL del Mapa", className="input-label"),
                        dbc.Input(id="map", placeholder="https://maps.google.com/...", className="input-pro")
                    ], className="input-group-pro"),
                ], md=6),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Prioridad (1-10)", className="input-label"),
                        dbc.Input(id="priority", type="number", min=1, max=10, value=5, className="input-pro")
                    ], className="input-group-pro"),
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Label("Categoría (ID)", className="input-label"),
                        dbc.Input(id="category", type="number", placeholder="1", className="input-pro")
                    ], className="input-group-pro"),
                ], md=4),
                dbc.Col([
                    html.Div([
                        html.Label("Estado", className="input-label"),
                        dcc.Dropdown(
                            id="isActive",
                            options=[
                                {"label": "✓ Activo", "value": True},
                                {"label": "✗ Inactivo", "value": False}
                            ],
                            value=True,
                            className="input-pro",
                            style={'background': '#f8fafc', 'border': '2px solid #e2e8f0', 'borderRadius': '10px'}
                        )
                    ], className="input-group-pro"),
                ], md=4),
            ]),
        ], className="form-section"),
        
        html.Div([
            dbc.Button([
                html.I(className="fas fa-paper-plane"),
                "Publicar Plan"
            ], id="submit", className="btn-pro btn-primary", style={'width': '100%', 'fontSize': '16px', 'padding': '14px'})
        ]),
        
        html.Div(id="response", style={'marginTop': '20px'})
        
    ], className="form-pro")
], className="main-content")

# Todos los Planes (con filtros)
all_plans_layout = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Todos los Planes", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
    ], className="top-bar"),
    
    # Barra de filtros
    html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="search-plans", placeholder="🔍 Buscar por nombre...", className="input-pro")
                ], md=4),
                dbc.Col([
                    dcc.Dropdown(
                        id="filter-status",
                        options=[
                            {"label": "Todos los estados", "value": "all"},
                            {"label": "Solo activos", "value": "active"},
                            {"label": "Solo inactivos", "value": "inactive"}
                        ],
                        value="all",
                        className="input-pro",
                        style={'background': '#f8fafc'}
                    )
                ], md=3),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt"),
                        "Actualizar"
                    ], id="fetch-all", className="btn-pro btn-primary", style={'width': '100%'})
                ], md=2),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-download"),
                        "Exportar"
                    ], id="export-plans", className="btn-pro btn-outline", style={'width': '100%'})
                ], md=3),
            ])
        ], className="filter-grid")
    ], className="filter-bar"),
    
    # Tabla de datos
    html.Div([
        html.Div(id="all-plans")
    ], className="chart-card")
    
], className="main-content")





# Por Categoría
by_category_layout = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Filtrar por Categoría", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
    ], className="top-bar"),
    
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Seleccione ID de Categoría", className="input-label"),
                dbc.Input(id="cat-id", type="number", placeholder="Ingrese ID", className="input-pro")
            ], md=8),
            dbc.Col([
                html.Label(html.Br()),
                dbc.Button([
                    html.I(className="fas fa-search"),
                    "Buscar"
                ], id="fetch-cat", className="btn-pro btn-primary", style={'width': '100%'})
            ], md=4)
        ])
    ], className="filter-bar"),
    
    html.Div(id="cat-plans")
    
], className="main-content")


# Categorías
categories_layout = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Categorías", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
        dbc.Button([
            html.I(className="fas fa-sync-alt"),
            "Actualizar"
        ], id="fetch-categories", className="btn-pro btn-secondary")
    ], className="top-bar"),
    
    html.Div([
        html.Div(id="categories-table")
    ], className="chart-card")
    
], className="main-content")

# Analytics (NUEVO)
analytics_layout = html.Div([
    # --- Breadcrumb / Top Bar ---
    html.Div([
        html.Div([
            html.I(className="fas fa-home fa-sm"),
            html.I(className="fas fa-chevron-right fa-xs"),
            html.Span("Analytics Avanzado", className="breadcrumb-current")
        ], className="breadcrumb-pro"),
    ], className="top-bar"),

    # --- KPIs en una sola fila ---
    html.Div(id="analytics-kpis", style={
        "display": "flex",
        "flexDirection": "row",
        "justifyContent": "space-between",
        "gap": "1rem",
        "flexWrap": "wrap",
        "marginBottom": "1.5rem"
    }),

    # --- Tendencia de planes ---
    dbc.Row([
        dbc.Col([
            create_chart_card(
                "Tendencia de Planes Creados",
                "fas fa-chart-line",
                dcc.Graph(id="trend-chart", config={'displayModeBar': False})
            )
        ], md=12)
    ]),

    # --- Distribución de costos y prioridad vs vistas ---
    dbc.Row([
        dbc.Col([
            create_chart_card(
                "Distribución de Costos",
                "fas fa-dollar-sign",
                dcc.Graph(id="cost-distribution", config={'displayModeBar': False})
            )
        ], md=6),
        dbc.Col([
            create_chart_card(
                "Prioridad vs Vistas",
                "fas fa-crosshairs",
                dcc.Graph(id="priority-views", config={'displayModeBar': False})
            )
        ], md=6)
    ])
], className="main-content")


# ==================== LAYOUT PRINCIPAL ====================
app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Interval(id="interval-component", interval=30*1000, n_intervals=0),
    sidebar,
    html.Div(id="page-content"),
    dcc.Store(id="plans-data"),
    dcc.Store(id="categories-data")
])

# ==================== CALLBACKS ====================

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/create":
        return create_layout
    elif pathname == "/all-plans":
        return all_plans_layout
    elif pathname == "/by-category":
        return by_category_layout
    elif pathname == "/categories":
        return categories_layout
    elif pathname == "/analytics":
        return analytics_layout
    else:
        return dashboard_layout




# Dashboard KPIs
@app.callback(
    [Output("dashboard-kpis", "children"),
     Output("category-pie-chart", "figure"),
     Output("status-bar-chart", "figure"),
     Output("top-plans-chart", "figure")],
    [Input("interval-dashboard", "n_intervals"),
     Input("url", "pathname")]
)
def update_dashboard(n, pathname):
    if pathname != "/":
        return [], {}, {}, {}
    
    try:
        response = requests.get(f"{API_BASE_URL}/plans", timeout=10)
        
        if response.status_code == 200:
            plans = response.json()
            df = pd.DataFrame(plans)
            
            # Calcular KPIs
            total_plans = len(plans)
            active_plans = len([p for p in plans if p.get('isActive', False)])
            total_views = sum(p.get('views', 0) for p in plans)
            avg_cost = df['costEstimate'].mean() if 'costEstimate' in df.columns and not df.empty else 0
            


            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['isActive'] = df['isActive'].astype(bool)

            today = pd.Timestamp.today().normalize()

            upcoming_this_week = df[
                (df['date'] >= today) & (df['date'] <= today + pd.Timedelta(days=7))
            ].shape[0]

            upcoming_all = df[df['date'] >= today].shape[0]

            expired_plans = df[df['date'] < today].shape[0]

            active_plans = df['isActive'].sum() 

            most_viewed = df['views'].max() if not df.empty else 0

            no_assistance = df[df['assistance'] == 0].shape[0]

            total_plans = df.shape[0]

            # Crear KPIs horizontales
            kpis = html.Div(
                [
                    create_kpi_card("Total Planes", str(total_plans), "", ""),
                    create_kpi_card("Planes Activos", str(active_plans), "", ""),
                    create_kpi_card("Próximos Esta Semana", str(upcoming_this_week), "", ""),
                    create_kpi_card("Próximos (Todos)", str(upcoming_all), "", ""),
                    create_kpi_card("Planes Vencidos", str(expired_plans), "", ""),
                    create_kpi_card("Más Vistos", str(most_viewed), "", ""),
                    create_kpi_card("Sin Asistencia", str(no_assistance), "", ""),
                ],
                style={
                    'display': 'flex',        # activa flexbox
                    'flexDirection': 'row',   # horizontal
                    'gap': '15px',            # espacio entre cards
                    'flexWrap': 'wrap'        # si no caben, pasan a la siguiente fila
                }
            )



            
            # Gráfico de Barras - Planes publicados últimos 15 días
            bar_fig_published = go.Figure()
            if not df.empty and 'date' in df.columns:
                # Convertir date a datetime y filtrar nulos
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df_valid = df.dropna(subset=['date'])

                # Rango de fechas: últimos 15 días hasta mañana
                today = pd.Timestamp.today().normalize()
                end_date = today + pd.Timedelta(days=30)
                start_date = today - pd.Timedelta(days=10)
                date_range = pd.date_range(start=start_date, end=end_date)

                # Contar planes por fecha
                daily_counts = df_valid['date'].dt.floor('D').value_counts()
                daily_counts = daily_counts.reindex(date_range, fill_value=0)

                bar_fig_published = go.Figure(data=[go.Bar(
                    x=[d.strftime('%Y-%m-%d') for d in daily_counts.index],
                    y=daily_counts.values,
                    marker_color=px.colors.sequential.Purples_r
                )])

                bar_fig_published.update_layout(
                    title="Planes Publicados",
                    height=350,
                    margin=dict(t=40, b=40, l=40, r=20),
                    font=dict(family='Outfit'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, tickangle=-45),
                    yaxis=dict(title="Cantidad de Planes", showgrid=True, gridcolor='#f1f5f9')
                )
            else:
                bar_fig_published = go.Figure()


            # Gráfico de Barras - Activos vs Inactivos
            active_count = len([p for p in plans if p.get('isActive', False)])

            today = pd.Timestamp.today().normalize()
            active_df = df[(df['isActive']) & (pd.to_datetime(df['date']) >= today)]
            category_counts = active_df['category'].value_counts()
            category_fig = go.Figure(data=[
                go.Bar(
                    x=category_counts.index,
                    y=category_counts.values,
                    marker_color='#636efa',  # color azul agradable
                    text=category_counts.values,
                    textposition='outside'
                )
            ])

            category_fig.update_layout(
                title="Planes Activos por Categoría",
                height=400,
                margin=dict(t=40, b=40, l=40, r=20),
                font=dict(family='Outfit'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title='Categoría', showgrid=False),
                yaxis=dict(title='Cantidad de Planes', showgrid=True, gridcolor='#f1f5f9')
            )

            
            # Gráfico Top 10 Planes
            if not df.empty and 'views' in df.columns and 'name' in df.columns:
                top_10 = df.nlargest(10, 'views')[['name', 'views']]
                top_fig = go.Figure(data=[go.Bar(
                    x=top_10['views'],
                    y=top_10['name'],
                    orientation='h',
                    marker=dict(
                        color=top_10['views'],
                        colorscale='Purples',
                        showscale=False
                    ),
                    text=top_10['views'],
                    textposition='outside'
                )])
                top_fig.update_layout(
                    height=400,
                    margin=dict(t=20, b=40, l=200, r=40),
                    font=dict(family='Outfit'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title='Vistas'),
                    yaxis=dict(showgrid=False)
                )
            else:
                top_fig = go.Figure()
            
            return kpis, bar_fig_published, category_fig, top_fig
        else:
            return html.Div("Error al cargar datos"), {}, {}, {}
    except Exception as e:
        return html.Div(f"Error: {str(e)}"), {}, {}, {}

@app.callback(
    Output("response", "children"),
    Input("submit", "n_clicks"),
    State("name", "value"),
    State("description", "value"),
    State("date", "value"),
    State("imageUrl", "value"),
    State("location", "value"),
    State("map", "value"),
    State("priority", "value"),
    State("category", "value"),
    State("isActive", "value"),
    State("costEstimate", "value"),
    prevent_initial_call=True
)
def publish_plan(n_clicks, name, description, date, imageUrl, location, map_url, priority, category, isActive, costEstimate):
    # Validaciones
    errors = []
    if not name or len(name.strip()) < 3:
        errors.append("El nombre debe tener al menos 3 caracteres")
    if not description or len(description.strip()) < 10:
        errors.append("La descripción debe tener al menos 10 caracteres")
    if not date:
        errors.append("La fecha es obligatoria")
    if priority and (priority < 1 or priority > 10):
        errors.append("La prioridad debe estar entre 1 y 10")
    if not category:
        errors.append("Debe seleccionar una categoría")
    
    if errors:
        return dbc.Alert([
            html.H5([html.I(className="fas fa-exclamation-triangle me-2"), "Errores de validación"], className="mb-3"),
            html.Ul([html.Li(error) for error in errors])
        ], color="warning", className="alert-pro")
    
    # Convertir datetime a formato completo con segundos
    if date and len(date) == 16:  # "yyyy-MM-ddTHH:mm"
        date += ":00"
    
    payload = {
        "name": name.strip(),
        "description": description.strip(),
        "date": date,
        "imageUrl": imageUrl or "",
        "location": location or "",
        "map": map_url or "",
        "priority": priority or 5,
        "category": category,
        "isActive": isActive if isActive is not None else True,
        "costEstimate": costEstimate or 0
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/plans/publish",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return dbc.Alert([
                html.H4([html.I(className="fas fa-check-circle me-2"), "¡Plan publicado exitosamente!"], className="alert-heading"),
                html.Hr(),
                html.P([
                    html.Strong("Nombre: "), data.get('name', 'N/A'), html.Br(),
                    html.Strong("ID: "), str(data.get('id', 'N/A')), html.Br(),
                    html.Strong("Categoría: "), str(data.get('category', 'N/A'))
                ])
            ], color="success", className="alert-pro")
        else:
            return dbc.Alert([
                html.H5([html.I(className="fas fa-times-circle me-2"), f"Error {response.status_code}"]),
                html.P(response.text)
            ], color="danger", className="alert-pro")
    except Exception as e:
        return dbc.Alert([
            html.H5([html.I(className="fas fa-bug me-2"), "Error"]),
            html.P(str(e))
        ], color="danger", className="alert-pro")


@app.callback(
    Output("all-plans", "children"),
    [Input("fetch-all", "n_clicks"),
     Input("search-plans", "value"),
     Input("filter-status", "value")],
    prevent_initial_call=True
)
def fetch_all_plans(n_clicks, search_value, status_filter):
    try:
        response = requests.get(f"{API_BASE_URL}/plans", timeout=10)
        
        if response.status_code == 200:
            plans = response.json()
            
            if not plans:
                return dbc.Alert([html.I(className="fas fa-inbox me-2"), "No hay planes disponibles"], color="info")
            
            df = pd.DataFrame(plans)
            
            # Filtrar por búsqueda
            if search_value:
                df = df[df['name'].str.contains(search_value, case=False, na=False)]
            
            # Filtrar por estado
            if status_filter == "active":
                df = df[df['isActive'] == True]
            elif status_filter == "inactive":
                df = df[df['isActive'] == False]
            
            # Seleccionar columnas
            columns_to_show = ['id', 'name', 'location', 'category', 'priority', 'views', 'costEstimate', 'isActive']
            df_display = df[[col for col in columns_to_show if col in df.columns]]
            
            # Renombrar
            column_names = {
                'id': 'ID',
                'name': 'Nombre',
                'location': 'Ubicación',
                'category': 'Categoría',
                'priority': 'Prioridad',
                'views': 'Vistas',
                'costEstimate': 'Costo',
                'isActive': 'Estado'
            }
            df_display = df_display.rename(columns=column_names)
            
            # Formatear estado
            if 'Estado' in df_display.columns:
                df_display['Estado'] = df_display['Estado'].apply(lambda x: '✓ Activo' if x else '✗ Inactivo')
            
            return dash_table.DataTable(
                data=df_display.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df_display.columns],
                page_size=15,
                sort_action="native",
                filter_action="native",
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '16px',
                    'fontFamily': 'Outfit'
                },
                style_header={
                    'backgroundColor': '#0f172a',
                    'color': 'white',
                    'fontWeight': '600',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8fafc'
                    },
                    {
                        'if': {'column_id': 'Estado', 'filter_query': '{Estado} = "✓ Activo"'},
                        'backgroundColor': '#d1fae5',
                        'color': '#065f46',
                        'fontWeight': '600'
                    },
                    {
                        'if': {'column_id': 'Estado', 'filter_query': '{Estado} = "✗ Inactivo"'},
                        'backgroundColor': '#fee2e2',
                        'color': '#991b1b',
                        'fontWeight': '600'
                    }
                ],
            )
        else:
            return dbc.Alert(f"Error {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Por Categoría
@app.callback(
    Output("cat-plans", "children"),
    Input("fetch-cat", "n_clicks"),
    State("cat-id", "value"),
    prevent_initial_call=True
)
def fetch_by_category(n_clicks, cat_id):
    if not cat_id:
        return dbc.Alert([html.I(className="fas fa-info-circle me-2"), "Ingrese un ID"], color="info")
    
    try:
        response = requests.get(f"{API_BASE_URL}/plans/category/{cat_id}", timeout=10)
        
        if response.status_code == 200:
            plans = response.json()
            
            if not plans:
                return dbc.Alert([html.I(className="fas fa-inbox me-2"), f"No hay planes en categoría {cat_id}"], color="info")
            
            cards = []
            for plan in plans:
                card = dbc.Card([
                    dbc.CardBody([
                        html.H5([html.I(className="fas fa-bookmark me-2"), plan.get('name', 'Sin nombre')]),
                        html.P(plan.get('description', '')[:150] + "..."),
                        dbc.Row([
                            dbc.Col([html.Small([html.I(className="fas fa-map-marker-alt me-1"), plan.get('location', 'N/A')], className="text-muted")]),
                            dbc.Col([html.Small([html.I(className="fas fa-eye me-1"), f"{plan.get('views', 0)} vistas"], className="text-muted")])
                        ])
                    ])
                ], className="mb-3", style={'boxShadow': 'var(--shadow-sm)', 'border': '1px solid #e2e8f0', 'borderRadius': '12px'})
                cards.append(card)
            
            return html.Div(cards)
        else:
            return dbc.Alert(f"Error {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Categorías
@app.callback(
    Output("categories-table", "children"),
    Input("fetch-categories", "n_clicks"),
    prevent_initial_call=True
)
def fetch_categories(n_clicks):
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=10)
        
        if response.status_code == 200:
            categories = response.json()
            
            if not categories:
                return dbc.Alert([html.I(className="fas fa-inbox me-2"), "No hay categorías"], color="info")
            
            df = pd.DataFrame(categories)
            
            return dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i.upper(), "id": i} for i in df.columns],
                page_size=15,
                sort_action="native",
                filter_action="native",
                style_cell={'textAlign': 'left', 'padding': '16px', 'fontFamily': 'Outfit'},
                style_header={'backgroundColor': '#0f172a', 'color': 'white', 'fontWeight': '600'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}],
            )
        else:
            return dbc.Alert(f"Error {response.status_code}", color="danger")
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Analytics
@app.callback(
    [Output("analytics-kpis", "children"),
     Output("trend-chart", "figure"),
     Output("cost-distribution", "figure"),
     Output("priority-views", "figure")],
    Input("url", "pathname")
)
def update_analytics(pathname):
    if pathname != "/analytics":
        return [], {}, {}, {}

    try:
        response = requests.get(f"{API_BASE_URL}/plans", timeout=10)
        response.raise_for_status()
        plans = response.json()
        df = pd.DataFrame(plans)

        # --- KPIs simplificados ---
        max_views = int(df['views'].max()) if 'views' in df and not df.empty else 0
        min_cost = float(df['costEstimate'].min()) if 'costEstimate' in df and not df.empty else 0
        avg_priority = float(df['priority'].mean()) if 'priority' in df and not df.empty else 0

        kpis = html.Div(
            [
                create_kpi_card("Plan Más Visto", f"{max_views:,}", "fas fa-fire", "danger"),
                create_kpi_card("Costo Mínimo", f"${min_cost:,.2f}", "fas fa-tag", "success"),
                create_kpi_card("Prioridad Promedio", f"{avg_priority:.1f}", "fas fa-star", "warning"),
                create_kpi_card("Engagement Rate", "78.5%", "fas fa-heart", "primary"),
            ],
            style={
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "space-between",
                "gap": "1rem",
                "flexWrap": "wrap"
            }
        )

        # --- Gráficos (mismo código que antes) ---
        trend_fig = go.Figure()
        if not df.empty:
            trend_fig.add_trace(go.Scatter(
                x=pd.date_range(start='2026-01-01', periods=30, freq='D'),
                y=[i*2 + 10 + (i%7)*5 for i in range(30)],
                mode='lines+markers',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=8)
            ))
        trend_fig.update_layout(
            height=300, margin=dict(t=20, b=40, l=40, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Outfit'),
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title='Cantidad')
        )

        cost_fig = go.Figure()
        if not df.empty and 'costEstimate' in df:
            cost_fig.add_trace(go.Histogram(
                x=df['costEstimate'], nbinsx=20, marker_color='#7c3aed'
            ))
            cost_fig.update_layout(
                height=300, margin=dict(t=20, b=40, l=40, r=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Outfit'),
                xaxis=dict(title='Costo Estimado', showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(title='Frecuencia', showgrid=True, gridcolor='#f1f5f9')
            )

        scatter_fig = go.Figure()
        if not df.empty and all(col in df for col in ['priority', 'views']):
            scatter_fig.add_trace(go.Scatter(
                x=df['priority'], y=df['views'],
                mode='markers',
                marker=dict(
                    size=df['costEstimate'] / 10 if 'costEstimate' in df else 10,
                    color=df['category'] if 'category' in df else '#2563eb',
                    colorscale='Purples', showscale=True,
                    colorbar=dict(title="Categoría")
                ),
                text=df['name'] if 'name' in df else None,
                hovertemplate='<b>%{text}</b><br>Prioridad: %{x}<br>Vistas: %{y}<extra></extra>'
            ))
            scatter_fig.update_layout(
                height=300, margin=dict(t=20, b=40, l=40, r=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Outfit'),
                xaxis=dict(title='Prioridad', showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(title='Vistas', showgrid=True, gridcolor='#f1f5f9')
            )

        return kpis, trend_fig, cost_fig, scatter_fig

    except Exception as e:
        return html.Div(f"Error al cargar analytics: {e}"), {}, {}, {}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)