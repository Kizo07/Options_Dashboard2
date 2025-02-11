import numpy as np
import plotly.graph_objects as go
from instruments import Instrument
from scipy.stats import norm

class PortfolioPlotter:
    def __init__(self, instruments):
        """
        Initialize the PortfolioPlotter with a list of instruments.
        Each instrument should have a get_payoff(S_T) method that returns its payoff
        at expiration given an underlying price S_T.

        Parameters:
        - instruments: List of instrument objects.
        """
        self.instruments = instruments
    
    def plot_portfolio_value(self, S_min, S_max, t, r, sigma, num_points=200):
            """
            Plots the actual value of the portfolio at time t using Black-Scholes for options
            and intrinsic value for stocks over a range of underlying prices.

            Parameters:
            - S_min: Minimum underlying price.
            - S_max: Maximum underlying price.
            - t: Current time (in years, where T = maturity time).
            - r: Risk-free interest rate.
            - sigma: Volatility of the underlying asset.
            - num_points: Number of points in the stock price range.
            """
            S_range = np.linspace(S_min, S_max, num_points)
            fig = go.Figure()

            total_value = np.zeros_like(S_range)

            for idx, instrument in enumerate(self.instruments):
                # Compute Black-Scholes value for options and intrinsic value for stocks
                instrument_values = np.array([instrument.get_value(S, t, r, sigma) for S in S_range])
                total_value += instrument_values

                fig.add_trace(go.Scatter(
                    x=S_range,
                    y=instrument_values,
                    mode='lines',
                    name=f'Instrument {idx + 1}'
                ))

            # Add total portfolio value trace
            fig.add_trace(go.Scatter(
                x=S_range,
                y=total_value,
                mode='lines',
                name='Total Portfolio Value',
                line=dict(color='black', width=3, dash='dash')
            ))

            fig.update_layout(
                title="Portfolio Value at Time t vs. Underlying Price",
                xaxis_title="Underlying Price (S_t)",
                yaxis_title="Portfolio Value",
                template="plotly_white"
            )

            fig.show()



    def plot_payoffs(self, S_min, S_max, num_points=200):
        """
        Plots the payoff for each individual instrument as well as the total
        portfolio payoff over a range of underlying prices at expiration.
        """
        # Create an array of underlying prices from S_min to S_max.
        S_range = np.linspace(float(S_min), float(S_max), num_points)
        
        # Create a new Plotly figure.
        fig = go.Figure()

        # Initialize an array to accumulate the total portfolio payoff.
        total_payoff = np.zeros_like(S_range)

        # Loop over each instrument, compute its payoff, and add it as a trace.
        for idx, instrument in enumerate(self.instruments):
            try:
                # Compute the payoff at each price in S_range
                instrument_payoff = np.array([instrument.get_payoff(S) for S in S_range])
                total_payoff += instrument_payoff

                fig.add_trace(go.Scatter(
                    x=S_range,
                    y=instrument_payoff,
                    mode='lines',
                    name=f'Instrument {idx + 1} ({instrument.instrument_type.capitalize()}, K={instrument.strike})'
                ))
            except Exception as e:
                print(f"Error plotting instrument {idx + 1}: {e}")
                continue

        # Add a trace for the total portfolio payoff.
        fig.add_trace(go.Scatter(
            x=S_range,
            y=total_payoff,
            mode='lines',
            name='Total Portfolio',
            line=dict(color='black', width=3, dash='dash')
        ))

        # Update the layout for a nicer appearance.
        fig.update_layout(
            title="Portfolio Payoff at Expiration vs. Underlying Price",
            xaxis_title="Underlying Price at Expiration",
            yaxis_title="Payoff",
            template="plotly_white",
            hovermode='x unified'
        )

        return fig  # Return the figure instead of showing it

    def plot_ncdf_analysis(self, stk_ratio, tau, sigma, r):
        """
        Plot the N(d1)-N(d2) and N(d1)/N(d2) analysis charts.
        
        Parameters:
        - stk_ratio: The S/K ratio
        - tau: Time to maturity (T-t)
        - sigma: Volatility
        - r: Risk-free rate
        
        Returns:
        - tuple of two Plotly figures (diff_figure, ratio_figure)
        """
        x = np.linspace(max(0.1, 0.5 * stk_ratio), 1.5 * stk_ratio, 200)
        d1 = (np.log(x) + (r + sigma**2 / 2) * tau) / (sigma * np.sqrt(tau))
        d2 = d1 - sigma * np.sqrt(tau)
        y_diff = norm.cdf(d1) - norm.cdf(d2)
        
        # Avoid division by zero in ratio calculation
        y_ratio = np.where(
            norm.cdf(d2) > 1e-10,
            norm.cdf(d1) / norm.cdf(d2),
            np.nan
        )
        
        fig_diff = go.Figure()
        fig_diff.add_trace(go.Scatter(x=x, y=y_diff, mode='lines', name='N(d1) - N(d2)'))
        fig_diff.update_layout(
            title="N(d1) - N(d2)",
            xaxis_title="S/K",
            yaxis_title="Value",
            hovermode='x unified',
            template="plotly_white"
        )
        
        fig_ratio = go.Figure()
        fig_ratio.add_trace(go.Scatter(x=x, y=y_ratio, mode='lines', name='N(d1) / N(d2)'))
        fig_ratio.update_layout(
            title="N(d1) / N(d2)",
            xaxis_title="S/K",
            yaxis_title="Value",
            hovermode='x unified',
            template="plotly_white"
        )
        
        return fig_diff, fig_ratio

    def plot_delta_analysis(self, instrument, S_range, T, t, sigma, r):
        """
        Plot delta sensitivity analysis charts.
        
        Parameters:
        - instrument: Option instrument
        - S_range: Range of underlying prices
        - T, t, sigma, r: Other market parameters
        
        Returns:
        - tuple of three Plotly figures (delta_vs_S, delta_vs_tau, delta_vs_sigma)
        """
        # Delta vs S
        deltas = [instrument.compute_greeks(S, T, t, sigma, r)['Delta'] for S in S_range]
        fig_delta_S = go.Figure()
        fig_delta_S.add_trace(go.Scatter(x=S_range, y=deltas, mode='lines', name='Delta'))
        fig_delta_S.update_layout(
            title="Delta vs Underlying Price",
            xaxis_title="Underlying Price (S)",
            yaxis_title="Delta",
            template="plotly_white",
            height=250
        )

        # Delta vs tau (T-t)
        tau_range = np.linspace(0.1, 2, 100)  # Time to maturity from 0.1 to 2 years
        deltas_tau = [instrument.compute_greeks(S_range[len(S_range)//2], tau + t, t, sigma, r)['Delta'] 
                      for tau in tau_range]
        fig_delta_tau = go.Figure()
        fig_delta_tau.add_trace(go.Scatter(x=tau_range, y=deltas_tau, mode='lines', name='Delta'))
        fig_delta_tau.update_layout(
            title="Delta vs Time to Maturity",
            xaxis_title="Time to Maturity (τ)",
            yaxis_title="Delta",
            template="plotly_white",
            height=250
        )

        # Delta vs sigma
        sigma_range = np.linspace(0.1, 0.8, 100)  # Volatility from 10% to 80%
        deltas_sigma = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sig, r)['Delta'] 
                        for sig in sigma_range]
        fig_delta_sigma = go.Figure()
        fig_delta_sigma.add_trace(go.Scatter(x=sigma_range, y=deltas_sigma, mode='lines', name='Delta'))
        fig_delta_sigma.update_layout(
            title="Delta vs Volatility",
            xaxis_title="Volatility (σ)",
            yaxis_title="Delta",
            template="plotly_white",
            height=250
        )

        return fig_delta_S, fig_delta_tau, fig_delta_sigma



