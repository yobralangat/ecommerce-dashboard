# app.py (The Lean and Fast Version)

import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# --- Configuration & Setup ---
APP_THEME = dbc.themes.LUX

# --- ** Load FAST Pre-processed Data on App Startup ** ---
try:
    sales_df = pd.read_parquet('assets/sales_data.parquet')
    rfm_df = pd.read_parquet('assets/rfm_data.parquet')
except FileNotFoundError:
    print("FATAL ERROR: Processed data files not found in 'assets/' folder.")
    print("Please run 'preprocess.py' first to generate these files.")
    exit()

# Convert date columns upon loading for proper filtering
sales_df['InvoiceYearMonth'] = pd.to_datetime(sales_df['InvoiceYearMonth'])

# --- Initialize the Dash App ---
app = dash.Dash(__name__, external_stylesheets=[APP_THEME])
server = app.server

# --- App Layout ---
app.layout = dbc.Container(fluid=True, className="p-4 bg-light", children=[
    dbc.Row([
        dbc.Col(html.H1("E-commerce Performance Dashboard", className="text-primary"), md=8),
        dbc.Col([
            dbc.Label("Filter by Country"),
            dcc.Dropdown(
                id='country-dropdown', 
                placeholder="Select a Country", 
                value="United Kingdom",
                options=[{'label': country, 'value': country} for country in sorted(sales_df['Country'].unique())]
            )
        ], md=4)
    ], align="center", className="mb-4"),

    dbc.Tabs(id="dashboard-tabs", active_tab="tab-overview", children=[
        dbc.Tab(label="Global Overview", tab_id="tab-overview"),
        dbc.Tab(label="Product Analysis", tab_id="tab-products"),
        dbc.Tab(label="Customer Segmentation (RFM)", tab_id="tab-rfm"),
    ]),
    
    html.Div(id="tab-content", className="mt-4")
])

# --- Main Callback to Render Tab Content ---
@app.callback(
    Output('tab-content', 'children'),
    Input('dashboard-tabs', 'active_tab'),
    Input('country-dropdown', 'value')
)
def render_tab_content(active_tab, selected_country):
    if not active_tab or not selected_country:
        return "Loading..."

    filtered_sales = sales_df[sales_df['Country'] == selected_country]
    template = "plotly_white"

    if active_tab == "tab-overview":
        total_revenue = filtered_sales['TotalPrice'].sum()
        total_quantity = filtered_sales['Quantity'].sum()
        monthly_trend = filtered_sales.groupby('InvoiceYearMonth')['TotalPrice'].sum().reset_index()
        fig_monthly_trend = px.area(monthly_trend, x='InvoiceYearMonth', y='TotalPrice', title=f"Monthly Sales Trend in {selected_country}", labels={'InvoiceYearMonth': 'Month', 'TotalPrice': 'Total Revenue'}, template=template)
        country_sales = sales_df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).reset_index().head(10)
        fig_country_sales = px.bar(country_sales, x='Country', y='TotalPrice', title="Top 10 Countries by Revenue (Global)", labels={'TotalPrice': 'Total Revenue'}, template=template)
        
        return html.Div([
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Total Revenue", className="text-muted"), html.H3(f"${total_revenue:,.0f}")])), md=6),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Total Items Sold", className="text-muted"), html.H3(f"{total_quantity:,}")])), md=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_monthly_trend)), md=6),
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_country_sales)), md=6),
            ])
        ])

    elif active_tab == "tab-products":
        top_prod_revenue = filtered_sales.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).reset_index().head(10)
        fig_top_rev = px.bar(top_prod_revenue, y='Description', x='TotalPrice', orientation='h', title=f"Top Products by Revenue in {selected_country}", labels={'Description': ''}, template=template)
        fig_top_rev.update_layout(yaxis={'categoryorder':'total ascending'})
        top_prod_quant = filtered_sales.groupby('Description')['Quantity'].sum().sort_values(ascending=False).reset_index().head(10)
        fig_top_quant = px.bar(top_prod_quant, y='Description', x='Quantity', orientation='h', title=f"Top Products by Volume in {selected_country}", labels={'Description': ''}, template=template)
        fig_top_quant.update_layout(yaxis={'categoryorder':'total ascending'})
        
        return dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_top_rev)), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_top_quant)), md=6),
        ])

    elif active_tab == "tab-rfm":
        customers_in_country = sales_df[sales_df['Country'] == selected_country]['Customer ID'].unique()
        country_rfm_df = rfm_df[rfm_df['Customer ID'].isin(customers_in_country)]
        country_champions = country_rfm_df[country_rfm_df['Segment'] == 'Champions'].shape[0]
        country_loyal = country_rfm_df[country_rfm_df['Segment'] == 'Loyal Customers'].shape[0]
        country_at_risk = country_rfm_df[country_rfm_df['Segment'] == 'At Risk'].shape[0]
        
        segment_counts = rfm_df['Segment'].value_counts().reset_index()
        fig_segments = px.bar(segment_counts, y='Segment', x='count', orientation='h', title="Customer Segment Distribution (Global)", labels={'Segment':''}, template=template)
        fig_segments.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_rfm_scatter = px.scatter(
            rfm_df, x='Recency', y='Frequency', color='Segment', size='MonetaryValue',
            hover_name='Customer ID', title="RFM Analysis (Global)",
            labels={'Recency': 'Days Since Last Purchase', 'Frequency': 'Total Orders'},
            template=template, size_max=40
        )
        
        return html.Div([
            dbc.Row([
                dbc.Col(html.H4(f"Key Segments in {selected_country}", className="mb-3 text-primary"), width=12),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Champion Customers", className="text-muted"), html.H3(f"{country_champions}")])), md=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("Loyal Customers", className="text-muted"), html.H3(f"{country_loyal}")])), md=4),
                dbc.Col(dbc.Card(dbc.CardBody([html.P("At Risk Customers", className="text-muted"), html.H3(f"{country_at_risk}")])), md=4),
            ], className="mb-4 text-center"),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_segments)), md=4),
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_rfm_scatter)), md=8),
            ])
        ])

if __name__ == '__main__':
    app.run(debug=True)