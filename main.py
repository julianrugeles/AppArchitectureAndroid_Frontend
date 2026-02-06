from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import json
import pandas as pd

# Inicialización de la app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# --- Estilos ---
sidebar_style = {
    "height": "100vh",
    "padding": "2rem 1rem",
    "background-color": "#343a40",
    "position": "fixed",
    "width": "250px",
    "overflow-y": "auto"
}

link_style = {
    "color": "#fff",
    "margin-bottom": "0.5rem",
    "display": "block",
    "padding": "0.5rem 1rem",
    "border-radius": "5px",
    "text-decoration": "none"
}

link_hover = {
    "background-color": "#495057"
}

card_style = {
    "padding": "2rem",
    "box-shadow": "0 4px 12px rgba(0,0,0,0.1)",
    "border-radius": "10px",
    "margin-bottom": "2rem",
    "background-color": "#fff"
}

button_style = {
    "border-radius": "8px",
    "font-weight": "bold"
}

input_style = {
    "border-radius": "8px"
}

# --- Sidebar ---
sidebar = html.Div([
    html.H2("Dashboard", className="text-center", style={"color": "#fff"}),
    html.Hr(style={"border-color": "#fff"}),
    dcc.Link("Publicar Plan", href="/", style=link_style),
    dcc.Link("Todos los Planes", href="/all-plans", style=link_style),
    dcc.Link("Planes por Categoría", href="/by-category", style=link_style),
    dcc.Link("Categorías", href="/categories", style=link_style)
], style=sidebar_style)

# --- Contenido principal ---
content = html.Div(id="page-content", style={"margin-left": "270px", "padding": "2rem"})

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# --- Layouts ---
publish_layout = dbc.Card([
    dbc.CardHeader(html.H4("Publicar Plan")),
    dbc.CardBody([
        dbc.Row([dbc.Label("Nombre", width=3), dbc.Col(dbc.Input(id="name", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Descripción", width=3), dbc.Col(dbc.Textarea(id="description", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Fecha", width=3), dbc.Col(dbc.Input(id="date", placeholder="2026-03-15T10:00:00", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Imagen URL", width=3), dbc.Col(dbc.Input(id="imageUrl", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Ubicación", width=3), dbc.Col(dbc.Input(id="location", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Mapa URL", width=3), dbc.Col(dbc.Input(id="map", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Prioridad (ID)", width=3), dbc.Col(dbc.Input(id="priority", type="number", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Categoría (ID)", width=3), dbc.Col(dbc.Input(id="category", type="number", style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Activo", width=3),
                 dbc.Col(dcc.Dropdown(id="isActive", options=[{"label":"Sí","value":True},{"label":"No","value":False}], value=True, style=input_style), width=9)], className="mb-2"),
        dbc.Row([dbc.Label("Costo Estimado", width=3), dbc.Col(dbc.Input(id="costEstimate", type="number", style=input_style), width=9)], className="mb-2"),
        dbc.Button("Publicar", id="submit", color="primary", className="mt-2", style=button_style),
        html.Div(id="response", className="mt-2")
    ])
], style=card_style)

all_plans_layout = dbc.Card([
    dbc.CardHeader(html.H4("Todos los Planes")),
    dbc.CardBody([
        dbc.Button("Cargar planes", id="fetch-all", color="secondary", className="mb-2", style=button_style),
        html.Div(id="all-plans", style={"maxHeight": "500px", "overflowY": "auto"})
    ])
], style=card_style)

by_category_layout = dbc.Card([
    dbc.CardHeader(html.H4("Planes por Categoría")),
    dbc.CardBody([
        dbc.Input(id="cat-id", type="number", placeholder="ID categoría", style=input_style),
        dbc.Button("Consultar", id="fetch-cat", color="secondary", className="mt-2", style=button_style),
        html.Div(id="cat-plans", style={"maxHeight": "400px", "overflowY": "auto"})
    ])
], style=card_style)

categories_layout = dbc.Card([
    dbc.CardHeader(html.H4("Categorías Disponibles")),
    dbc.CardBody([
        dbc.Button("Cargar categorías", id="fetch-categories", color="info", className="mb-2", style=button_style),
        html.Div(id="categories-table", style={"maxHeight": "400px", "overflowY": "auto"})
    ])
], style=card_style)

# --- Callbacks ---
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/all-plans":
        return all_plans_layout
    elif pathname == "/by-category":
        return by_category_layout
    elif pathname == "/categories":
        return categories_layout
    else:
        return publish_layout

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
    State("costEstimate", "value")
)
def publish_plan(n_clicks, name, description, date, imageUrl, location, map_url, priority, category, isActive, costEstimate):
    if n_clicks and n_clicks > 0:
        payload = {
            "name": name, "description": description, "date": date, "imageUrl": imageUrl,
            "location": location, "map": map_url, "priority": priority, "category": category,
            "isActive": isActive, "costEstimate": costEstimate
        }
        try:
            response = requests.post("http://localhost:12500/plans/publish", headers={"Content-Type":"application/json"}, data=json.dumps(payload))
            if response.status_code == 200:
                return dbc.Alert(f"Plan publicado: {response.json().get('name')}", color="success")
            else:
                return dbc.Alert(f"Error {response.status_code}: {response.text}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Excepción: {str(e)}", color="warning")
    return ""

@app.callback(
    Output("all-plans", "children"),
    Input("fetch-all", "n_clicks")
)
def fetch_all(n_clicks):
    if n_clicks and n_clicks > 0:
        try:
            response = requests.get("http://localhost:12500/plans")
            if response.status_code == 200:
                plans = response.json()
                items = [dbc.ListGroupItem(f"{p['id']}: {p['name']} (Vistas: {p.get('views',0)})") for p in plans]
                return dbc.ListGroup(items)
            else:
                return dbc.Alert(f"Error {response.status_code}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Excepción: {str(e)}", color="warning")
    return ""

@app.callback(
    Output("cat-plans", "children"),
    Input("fetch-cat", "n_clicks"),
    State("cat-id", "value")
)
def fetch_by_category(n_clicks, cat_id):
    if n_clicks and cat_id:
        try:
            response = requests.get(f"http://localhost:12500/plans/category/{cat_id}")
            if response.status_code == 200:
                plans = response.json()
                items = [dbc.ListGroupItem(f"{p['id']}: {p['name']}") for p in plans]
                return dbc.ListGroup(items)
            else:
                return dbc.Alert(f"Error {response.status_code}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Excepción: {str(e)}", color="warning")
    return ""

@app.callback(
    Output("categories-table", "children"),
    Input("fetch-categories", "n_clicks")
)
def fetch_categories(n_clicks):
    if n_clicks and n_clicks > 0:
        try:
            response = requests.get("http://localhost:12500/categories")
            if response.status_code == 200:
                categories = response.json()
                if not categories:
                    return dbc.Alert("No hay categorías disponibles", color="warning")
                df = pd.DataFrame(categories)
                table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
                return table
            else:
                return dbc.Alert(f"Error {response.status_code}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Excepción: {str(e)}", color="warning")
    return ""

# --- Ejecutar la app ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
