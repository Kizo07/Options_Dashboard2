import numpy as np
from scipy.stats import norm
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_components as dc
from dash import html

from instruments import Instrument
from visualization import PortfolioPlotter

def register_callbacks(app):
    """Register all callbacks with the Dash app."""
    
    @app.callback(Output('tabs-content', 'children'),
                  [Input('tabs', 'value')])
    def render_content(tab):
        if tab == 'tab-1':
            return dc.create_trading_strategies_tab()
        elif tab == 'tab-2':
            return dc.create_single_option_analysis_tab()
        elif tab == 'tab-3':
            return dc.create_option_greeks_tab()

    @app.callback(
        Output('strategy-graph', 'figure'),
        [Input('update-strategy', 'n_clicks')],
        [
            State('instrument-1-type', 'value'),
            State('instrument-1-strike', 'value'),
            State('instrument-1-position', 'value'),
            State('instrument-2-type', 'value'),
            State('instrument-2-strike', 'value'),
            State('instrument-2-position', 'value'),
            State('instrument-3-type', 'value'),
            State('instrument-3-strike', 'value'),
            State('instrument-3-position', 'value'),
            State('instrument-4-type', 'value'),
            State('instrument-4-strike', 'value'),
            State('instrument-4-position', 'value'),
            State('underlying-price', 'value'),
            State('time-maturity', 'value'),
            State('current-time', 'value'),
            State('volatility', 'value'),
            State('risk-free-rate', 'value')
        ]
    )
    def update_strategy(n_clicks, 
                       instr1_type, instr1_strike, instr1_position,
                       instr2_type, instr2_strike, instr2_position,
                       instr3_type, instr3_strike, instr3_position,
                       instr4_type, instr4_strike, instr4_position,
                       S, T, t, sigma, r):
        if None in [S, T, t, sigma, r]:
            return go.Figure()
        
        instruments = []
        instrument_inputs = [
            (instr1_type, instr1_strike, instr1_position),
            (instr2_type, instr2_strike, instr2_position),
            (instr3_type, instr3_strike, instr3_position),
            (instr4_type, instr4_strike, instr4_position)
        ]
        
        for inst_type, strike, position in instrument_inputs:
            if strike is not None:
                try:
                    instruments.append(Instrument(inst_type, strike, position))
                except ValueError as e:
                    print(f"Error creating instrument: {e}")
                    continue
        
        if not instruments:
            return go.Figure()
        
        # Create plotter and generate figure
        plotter = PortfolioPlotter(instruments)
        S_min = max(0.1, S/2)
        S_max = 2 * S
        
        # Plot both payoff and current value on the same figure
        fig = go.Figure()
        
        # Add payoff at expiration
        S_range = np.linspace(S_min, S_max, 200)
        total_payoff = np.zeros_like(S_range)
        for inst in instruments:
            payoff = np.array([inst.get_payoff(s) for s in S_range])
            total_payoff += payoff
        
        fig.add_trace(go.Scatter(
            x=S_range,
            y=total_payoff,
            mode='lines',
            name='Payoff at T'
        ))
        
        # Add current portfolio value
        total_value = np.zeros_like(S_range)
        for inst in instruments:
            values = np.array([inst.get_current_value(s, T, t, sigma, r) for s in S_range])
            total_value += values
        
        fig.add_trace(go.Scatter(
            x=S_range,
            y=total_value,
            mode='lines',
            name='Current Value'
        ))
        
        fig.update_layout(
            title="Trading Strategy: Payoff at Expiration vs. Current Value",
            xaxis_title="Underlying Price",
            yaxis_title="Profit / Loss",
            hovermode='x unified',
            template="plotly_white"
        )
        
        return fig

    @app.callback(
        [Output('graph-ncdf-diff', 'figure'),
         Output('graph-ncdf-ratio', 'figure')],
        [Input('update-option', 'n_clicks')],
        [
            State('stk-ratio', 'value'),
            State('time-remaining', 'value'),
            State('sigma', 'value'),
            State('r', 'value')
        ]
    )
    def update_option_analysis(n_clicks, stk_ratio, tau, sigma, r):
        if None in [stk_ratio, tau, sigma, r] or tau <= 0 or sigma <= 0:
            return go.Figure(), go.Figure()
        
        try:
            plotter = PortfolioPlotter([])  # Empty list since we don't need instruments for this analysis
            return plotter.plot_ncdf_analysis(stk_ratio, tau, sigma, r)
        except Exception as e:
            print(f"Error in option analysis: {e}")
            return go.Figure(), go.Figure()

    @app.callback(
        Output('greeks-output', 'children'),
        [Input('compute-greeks', 'n_clicks')],
        [
            State('greek-underlying', 'value'),
            State('greek-strike', 'value'),
            State('greek-time-maturity', 'value'),
            State('greek-current-time', 'value'),
            State('greek-volatility', 'value'),
            State('greek-risk-free', 'value'),
            State('greek-option-type', 'value')
        ]
    )
    def update_greeks(n_clicks, S, K, T, t, sigma, r, option_type):
        instrument = Instrument(option_type, K)
        greeks = instrument.compute_greeks(S, T, t, sigma, r)
        return [html.P(f"{key}: {value:.4f}") for key, value in greeks.items()]
