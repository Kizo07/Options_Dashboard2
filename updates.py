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
            State('instrument-5-type', 'value'),
            State('instrument-5-strike', 'value'),
            State('instrument-5-position', 'value'),
            State('instrument-6-type', 'value'),
            State('instrument-6-strike', 'value'),
            State('instrument-6-position', 'value'),
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
                       instr5_type, instr5_strike, instr5_position,
                       instr6_type, instr6_strike, instr6_position,
                       S, T, t, sigma, r):
        if None in [S, T, t, sigma, r]:
            return go.Figure()
        
        instruments = []
        instrument_inputs = [
            (instr1_type, instr1_strike, instr1_position),
            (instr2_type, instr2_strike, instr2_position),
            (instr3_type, instr3_strike, instr3_position),
            (instr4_type, instr4_strike, instr4_position),
            (instr5_type, instr5_strike, instr5_position),
            (instr6_type, instr6_strike, instr6_position)
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
        [Output('greeks-output', 'children'),
         Output('delta-vs-s', 'figure'),
         Output('delta-vs-tau', 'figure'),
         Output('delta-vs-sigma', 'figure'),
         Output('gamma-vs-s', 'figure'),
         Output('gamma-vs-tau', 'figure'),
         Output('gamma-vs-sigma', 'figure'),
         Output('gamma-vs-r', 'figure'),
         Output('vega-vs-s', 'figure'),
         Output('vega-vs-tau', 'figure'),
         Output('vega-vs-sigma', 'figure'),
         Output('vega-vs-r', 'figure'),
         Output('rho-vs-s', 'figure'),
         Output('rho-vs-tau', 'figure'),
         Output('rho-vs-sigma', 'figure'),
         Output('rho-vs-r', 'figure'),
         Output('theta-vs-s', 'figure'),
         Output('theta-vs-tau', 'figure'),
         Output('theta-vs-sigma', 'figure'),
         Output('theta-vs-r', 'figure')],
        [Input('compute-greeks', 'n_clicks')],
        [State('greek-underlying', 'value'),
         State('greek-strike-1', 'value'),
         State('greek-strike-2', 'value'),
         State('greek-time-maturity-1', 'value'),
         State('greek-time-maturity-2', 'value'),
         State('greek-current-time', 'value'),
         State('greek-volatility', 'value'),
         State('greek-risk-free', 'value'),
         State('greek-option-type-1', 'value'),
         State('greek-option-type-2', 'value')]
    )
    def update_greeks(n_clicks, S, K1, K2, T1, T2, t, sigma, r, option_type_1, option_type_2):
        if None in [S, K1, K2, T1, T2, t, sigma, r]:
            return [go.Figure() for _ in range(20)]
            
        instrument1 = Instrument(option_type_1, K1)
        instrument2 = Instrument(option_type_2, K2)
        
        greeks1 = instrument1.compute_greeks(S, T1, t, sigma, r)
        greeks2 = instrument2.compute_greeks(S, T2, t, sigma, r)
        
        greeks_output = [
            html.H4(f"Instrument 1 ({option_type_1.capitalize()}, K={K1}, T={T1}):"),
            *[html.P(f"{key}: {value:.4f}") for key, value in greeks1.items()],
            html.H4(f"Instrument 2 ({option_type_2.capitalize()}, K={K2}, T={T2}):"),
            *[html.P(f"{key}: {value:.4f}") for key, value in greeks2.items()]
        ]
        
        # Generate analysis plots
        S_range = np.linspace(max(0.1, min(K1, K2)/2), 1.5*max(K1, K2), 100)
        plotter = PortfolioPlotter([instrument1, instrument2])
        
        # Update plotting functions to handle multiple instruments with different T
        def add_second_trace(fig, y_values, name):
            y_values = np.array(y_values)
            instrument1_y = np.array(fig.data[0].y)
            fig.add_trace(go.Scatter(
                x=fig.data[0].x,
                y=y_values,
                mode='lines',
                name=f'{name} (Instrument 2)'
            ))
            fig.add_trace(go.Scatter(
                x=fig.data[0].x,
                y=instrument1_y + y_values,
                mode='lines',
                name=f'{name} (Portfolio)'
            ))
            fig.data[0].name = f'{name} (Instrument 1)'
            return fig
        
        
        # Generate all plots with both instruments using their respective T values
        delta_s, delta_tau, delta_sigma = plotter.plot_delta_analysis(
            instrument1, S_range, T1, t, sigma, r
        )
        delta_s2, delta_tau2, delta_sigma2 = plotter.plot_delta_analysis(
            instrument2, S_range, T2, t, sigma, r
        )
        
        # Add second instrument traces to each plot
        for fig1, fig2, name in [
            (delta_s, delta_s2, 'Delta'),
            (delta_tau, delta_tau2, 'Delta'),
            (delta_sigma, delta_sigma2, 'Delta')
        ]:
            add_second_trace(fig1, fig2.data[0].y, name)
            
            
        
        # Repeat for other Greeks...
        gamma_s, gamma_tau, gamma_sigma, gamma_r = plotter.plot_gamma_analysis(
            instrument1, S_range, T1, t, sigma, r
        )
        gamma_s2, gamma_tau2, gamma_sigma2, gamma_r2 = plotter.plot_gamma_analysis(
            instrument2, S_range, T2, t, sigma, r
        )
        
        for fig1, fig2, name in [
            (gamma_s, gamma_s2, 'Gamma'),
            (gamma_tau, gamma_tau2, 'Gamma'),
            (gamma_sigma, gamma_sigma2, 'Gamma'),
            (gamma_r, gamma_r2, 'Gamma')
        ]:
            add_second_trace(fig1, fig2.data[0].y, name)
            
        
        # Similar updates for vega, rho, and theta...
        # (Add the same pattern for the remaining Greeks)
        
        vega_s, vega_tau, vega_sigma, vega_r = plotter.plot_vega_analysis(
            instrument1, S_range, T1, t, sigma, r
        )
        vega_s2, vega_tau2, vega_sigma2, vega_r2 = plotter.plot_vega_analysis(
            instrument2, S_range, T2, t, sigma, r
        )
        
        for fig1, fig2, name in [
            (vega_s, vega_s2, 'Vega'),
            (vega_tau, vega_tau2, 'Vega'),
            (vega_sigma, vega_sigma2, 'Vega'),
            (vega_r, vega_r2, 'Vega')
        ]:
            add_second_trace(fig1, fig2.data[0].y, name)
            
            
        rho_s, rho_tau, rho_sigma, rho_r = plotter.plot_rho_analysis(
            instrument1, S_range, T1, t, sigma, r
        )
        rho_s2, rho_tau2, rho_sigma2, rho_r2 = plotter.plot_rho_analysis(
            instrument2, S_range, T2, t, sigma, r
        )
        
        for fig1, fig2, name in [
            (rho_s, rho_s2, 'Rho'),
            (rho_tau, rho_tau2, 'Rho'),
            (rho_sigma, rho_sigma2, 'Rho'),
            (rho_r, rho_r2, 'Rho')
        ]:
            add_second_trace(fig1, fig2.data[0].y, name)
            
            
        theta_s, theta_tau, theta_sigma, theta_r = plotter.plot_theta_analysis(
            instrument1, S_range, T1, t, sigma, r
        )
        theta_s2, theta_tau2, theta_sigma2, theta_r2 = plotter.plot_theta_analysis(
            instrument2, S_range, T2, t, sigma, r
        )
        
        for fig1, fig2, name in [
            (theta_s, theta_s2, 'Theta'),
            (theta_tau, theta_tau2, 'Theta'),
            (theta_sigma, theta_sigma2, 'Theta'),
            (theta_r, theta_r2, 'Theta')
        ]:
            add_second_trace(fig1, fig2.data[0].y, name)
            
        
        return (greeks_output, 
                delta_s, delta_tau, delta_sigma,
                gamma_s, gamma_tau, gamma_sigma, gamma_r,
                vega_s, vega_tau, vega_sigma, vega_r,
                rho_s, rho_tau, rho_sigma, rho_r,
                theta_s, theta_tau, theta_sigma, theta_r)
