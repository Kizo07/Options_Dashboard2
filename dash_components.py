from dash import dcc, html
import plotly.graph_objs as go

# Common styles
CONTAINER_STYLE = {
    'width': '100%',
    'margin': '0',
    'padding': '10px',
    'font-family': 'Arial, sans-serif'
}

INPUT_CONTAINER_STYLE = {
    'background': '#f8f9fa',
    'border-radius': '8px',
    'padding': '20px',
    'margin': '10px 0',
    'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
}

BUTTON_STYLE = {
    'background-color': '#007bff',
    'color': 'white',
    'padding': '10px 20px',
    'border': 'none',
    'border-radius': '4px',
    'cursor': 'pointer',
    'margin': '10px 0'
}

INPUT_STYLE = {
    'margin': '5px 0',
    'padding': '8px',
    'border': '1px solid #ddd',
    'border-radius': '4px',
    'width': '100%'
}

def create_layout():
    """Create the main layout of the Dash application."""
    return html.Div([
        html.H1("Kanav's Options Dashboard", style={'text-align': 'center', 'color': '#2c3e50'}),
        dcc.Tabs(
            id='tabs',
            value='tab-1',
            children=[
                dcc.Tab(label='Trading Strategies', value='tab-1'),
                dcc.Tab(label='Single Option Analysis', value='tab-2'),
                dcc.Tab(label='Option Greeks', value='tab-3')
            ],
            style={'margin': '20px 0'}
        ),
        html.Div(id='tabs-content')
    ], style=CONTAINER_STYLE)

def create_instrument_input(instrument_number):
    """Create input components for a single instrument."""
    # Set default strike value for first instrument
    default_strike = 100 if instrument_number == 1 else None
    
    return html.Div([
        html.H4(f'Instrument {instrument_number}', style={'color': '#34495e'}),
        html.Div([
            dcc.Dropdown(
                id=f'instrument-{instrument_number}-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'},
                    {'label': 'Stock', 'value': 'stock'}
                ],
                value='call',
                style={'margin': '5px 0', 'flex': 2}
            ),
            dcc.Dropdown(
                id=f'instrument-{instrument_number}-position',
                options=[
                    {'label': 'Buy', 'value': 1},
                    {'label': 'Sell', 'value': -1}
                ],
                value=1,
                style={'margin': '5px 0', 'flex': 1}
            ),
        ], style={'display': 'flex', 'gap': '10px'}),
        dcc.Input(
            id=f'instrument-{instrument_number}-strike',
            type='number',
            placeholder='Strike',
            value=default_strike,
            style=INPUT_STYLE
        )
    ], style={'padding': '15px', 'flex': 1, 'margin': '0 10px', 'background': 'white', 'border-radius': '4px'})

def create_parameter_input(label, id_name, default_value):
    """Create a labeled input component."""
    return html.Div([
        html.Label(label, style={'font-weight': 'bold', 'margin': '5px 0'}),
        dcc.Input(
            id=id_name,
            type='number',
            value=default_value,
            style=INPUT_STYLE
        )
    ], style={'margin': '10px 0'})

def create_trading_strategies_tab():
    """Create the layout for the Trading Strategies tab."""
    return html.Div([
        # Main content area with instruments and graph
        html.Div([
            html.H3('Trading Strategies', style={'color': '#2c3e50'}),
            html.Div([
                create_instrument_input(1),
                create_instrument_input(2),
                create_instrument_input(3),
                create_instrument_input(4)
            ], style={'display': 'flex', 'flex-direction': 'row', 'gap': '10px', 'margin': '20px 0'}),
            html.Button(
                'Update Strategy',
                id='update-strategy',
                n_clicks=0,
                style=BUTTON_STYLE
            ),
            dcc.Graph(id='strategy-graph', style={'height': '75vh'})  # Make graph taller
        ], style={'flex': '4', 'margin-right': '20px'}),
        
        # Sidebar with market parameters
        html.Div([
            html.Div(
                create_market_parameters_inputs(),
                style={
                    **INPUT_CONTAINER_STYLE,
                    'position': 'sticky',
                    'top': '20px'
                }
            )
        ], style={
            'flex': '1',
            'min-width': '200px',
            'max-width': '300px',
            'margin-top': '60px'  # Align with content below main heading
        })
    ], style={
        'display': 'flex',
        'flex-direction': 'row',
        'gap': '10px',
        'align-items': 'flex-start',
        'width': '100%',
        'height': '100%'
    })

def create_market_parameters_inputs():
    """Create input components for market parameters."""
    return html.Div([
        html.H4('Market Parameters', style={'color': '#34495e', 'margin-bottom': '15px'}),
        create_parameter_input("Underlying Price (S):", 'underlying-price', 100),
        create_parameter_input("Time to Maturity (T):", 'time-maturity', 1),
        create_parameter_input("Current Time (t):", 'current-time', 0),
        create_parameter_input("Volatility (σ):", 'volatility', 0.2),
        create_parameter_input("Risk Free Rate (r):", 'risk-free-rate', 0.05)
    ])

def create_single_option_analysis_tab():
    """Create the layout for the Single Option Analysis tab."""
    return html.Div([
        html.H3('Single Option Analysis', style={'color': '#2c3e50'}),
        html.Div([
            create_parameter_input("St/K Ratio:", 'stk-ratio', 1),
            create_parameter_input("Time to Maturity (T-t):", 'time-remaining', 1),
            create_parameter_input("Volatility (σ):", 'sigma', 0.2),
            create_parameter_input("Risk Free Rate (r):", 'r', 0.05)
        ], style=INPUT_CONTAINER_STYLE),
        html.Button(
            'Update Option Analysis',
            id='update-option',
            n_clicks=0,
            style=BUTTON_STYLE
        ),
        html.Div([
            dcc.Graph(id='graph-ncdf-diff'),
            dcc.Graph(id='graph-ncdf-ratio')
        ])
    ])

def create_option_greeks_tab():
    """Create the layout for the Option Greeks tab."""
    return html.Div([
        html.H3('Option Greeks', style={'color': '#2c3e50'}),
        html.Div([
            create_parameter_input("Underlying Price (S):", 'greek-underlying', 100),
            create_parameter_input("Strike Price (K):", 'greek-strike', 100),
            create_parameter_input("Time to Maturity (T):", 'greek-time-maturity', 1),
            create_parameter_input("Current Time (t):", 'greek-current-time', 0),
            create_parameter_input("Volatility (σ):", 'greek-volatility', 0.2),
            create_parameter_input("Risk Free Rate (r):", 'greek-risk-free', 0.05),
            html.Label("Option Type:", style={'font-weight': 'bold', 'margin': '5px 0'}),
            dcc.Dropdown(
                id='greek-option-type',
                options=[
                    {'label': 'Call', 'value': 'call'},
                    {'label': 'Put', 'value': 'put'}
                ],
                value='call',
                style={'margin': '5px 0'}
            )
        ], style=INPUT_CONTAINER_STYLE),
        html.Button(
            'Compute Greeks',
            id='compute-greeks',
            n_clicks=0,
            style=BUTTON_STYLE
        ),
        html.Div(id='greeks-output', style={'margin': '20px 0'})
    ])
