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

    def plot_theta_analysis(self, instrument, S_range, T, t, sigma, r):
        """
        Plot theta sensitivity analysis charts.
        
        Parameters:
        - instrument: Option instrument
        - S_range: Range of underlying prices
        - T, t, sigma, r: Other market parameters
        
        Returns:
        - tuple of four Plotly figures (theta_vs_S, theta_vs_tau, theta_vs_sigma, theta_vs_r)
        """
        # Theta vs S
        thetas = [instrument.compute_greeks(S, T, t, sigma, r)['Theta'] for S in S_range]
        fig_theta_S = go.Figure()
        fig_theta_S.add_trace(go.Scatter(x=S_range, y=thetas, mode='lines', name='Theta'))
        fig_theta_S.update_layout(
            title="Theta vs Underlying Price",
            xaxis_title="Underlying Price (S)",
            yaxis_title="Theta",
            template="plotly_white",
            height=250
        )

        # Theta vs tau (T-t)
        tau_range = np.linspace(0.1, 2, 100)  # Time to maturity from 0.1 to 2 years
        thetas_tau = [instrument.compute_greeks(S_range[len(S_range)//2], tau + t, t, sigma, r)['Theta'] 
                      for tau in tau_range]
        fig_theta_tau = go.Figure()
        fig_theta_tau.add_trace(go.Scatter(x=tau_range, y=thetas_tau, mode='lines', name='Theta'))
        fig_theta_tau.update_layout(
            title="Theta vs Time to Maturity",
            xaxis_title="Time to Maturity (τ)",
            yaxis_title="Theta",
            template="plotly_white",
            height=250
        )

        # Theta vs sigma
        sigma_range = np.linspace(0.1, 0.8, 100)  # Volatility from 10% to 80%
        thetas_sigma = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sig, r)['Theta'] 
                        for sig in sigma_range]
        fig_theta_sigma = go.Figure()
        fig_theta_sigma.add_trace(go.Scatter(x=sigma_range, y=thetas_sigma, mode='lines', name='Theta'))
        fig_theta_sigma.update_layout(
            title="Theta vs Volatility",
            xaxis_title="Volatility (σ)",
            yaxis_title="Theta",
            template="plotly_white",
            height=250
        )

        # Theta vs r
        r_range = np.linspace(0.01, 0.1, 100)  # Risk-free rate from 1% to 10%
        thetas_r = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sigma, r_val)['Theta'] 
                    for r_val in r_range]
        fig_theta_r = go.Figure()
        fig_theta_r.add_trace(go.Scatter(x=r_range, y=thetas_r, mode='lines', name='Theta'))
        fig_theta_r.update_layout(
            title="Theta vs Risk-Free Rate",
            xaxis_title="Risk-Free Rate (r)",
            yaxis_title="Theta",
            template="plotly_white",
            height=250
        )

        return fig_theta_S, fig_theta_tau, fig_theta_sigma, fig_theta_r

    def plot_gamma_analysis(self, instrument, S_range, T, t, sigma, r):
        """
        Plot gamma sensitivity analysis charts.
        
        Parameters:
        - instrument: Option instrument
        - S_range: Range of underlying prices
        - T, t, sigma, r: Other market parameters
        
        Returns:
        - tuple of four Plotly figures (gamma_vs_S, gamma_vs_tau, gamma_vs_sigma, gamma_vs_r)
        """
        # Gamma vs S
        gammas = [instrument.compute_greeks(S, T, t, sigma, r)['Gamma'] for S in S_range]
        fig_gamma_S = go.Figure()
        fig_gamma_S.add_trace(go.Scatter(x=S_range, y=gammas, mode='lines', name='Gamma'))
        fig_gamma_S.update_layout(
            title="Gamma vs Underlying Price",
            xaxis_title="Underlying Price (S)",
            yaxis_title="Gamma",
            template="plotly_white",
            height=250
        )

        # Gamma vs tau (T-t)
        tau_range = np.linspace(0.1, 2, 100)  # Time to maturity from 0.1 to 2 years
        gammas_tau = [instrument.compute_greeks(S_range[len(S_range)//2], tau + t, t, sigma, r)['Gamma'] 
                      for tau in tau_range]
        fig_gamma_tau = go.Figure()
        fig_gamma_tau.add_trace(go.Scatter(x=tau_range, y=gammas_tau, mode='lines', name='Gamma'))
        fig_gamma_tau.update_layout(
            title="Gamma vs Time to Maturity",
            xaxis_title="Time to Maturity (τ)",
            yaxis_title="Gamma",
            template="plotly_white",
            height=250
        )

        # Gamma vs sigma
        sigma_range = np.linspace(0.1, 0.8, 100)  # Volatility from 10% to 80%
        gammas_sigma = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sig, r)['Gamma'] 
                        for sig in sigma_range]
        fig_gamma_sigma = go.Figure()
        fig_gamma_sigma.add_trace(go.Scatter(x=sigma_range, y=gammas_sigma, mode='lines', name='Gamma'))
        fig_gamma_sigma.update_layout(
            title="Gamma vs Volatility",
            xaxis_title="Volatility (σ)",
            yaxis_title="Gamma",
            template="plotly_white",
            height=250
        )

        # Gamma vs r
        r_range = np.linspace(0.01, 0.1, 100)  # Risk-free rate from 1% to 10%
        gammas_r = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sigma, r_val)['Gamma'] 
                    for r_val in r_range]
        fig_gamma_r = go.Figure()
        fig_gamma_r.add_trace(go.Scatter(x=r_range, y=gammas_r, mode='lines', name='Gamma'))
        fig_gamma_r.update_layout(
            title="Gamma vs Risk-Free Rate",
            xaxis_title="Risk-Free Rate (r)",
            yaxis_title="Gamma",
            template="plotly_white",
            height=250
        )

        return fig_gamma_S, fig_gamma_tau, fig_gamma_sigma, fig_gamma_r

    def plot_vega_analysis(self, instrument, S_range, T, t, sigma, r):
        """
        Plot vega sensitivity analysis charts.
        
        Parameters:
        - instrument: Option instrument
        - S_range: Range of underlying prices
        - T, t, sigma, r: Other market parameters
        
        Returns:
        - tuple of four Plotly figures (vega_vs_S, vega_vs_tau, vega_vs_sigma, vega_vs_r)
        """
        # Vega vs S
        vegas = [instrument.compute_greeks(S, T, t, sigma, r)['Vega'] for S in S_range]
        fig_vega_S = go.Figure()
        fig_vega_S.add_trace(go.Scatter(x=S_range, y=vegas, mode='lines', name='Vega'))
        fig_vega_S.update_layout(
            title="Vega vs Underlying Price",
            xaxis_title="Underlying Price (S)",
            yaxis_title="Vega",
            template="plotly_white",
            height=250
        )

        # Vega vs tau (T-t)
        tau_range = np.linspace(0.1, 2, 100)  # Time to maturity from 0.1 to 2 years
        vegas_tau = [instrument.compute_greeks(S_range[len(S_range)//2], tau + t, t, sigma, r)['Vega'] 
                      for tau in tau_range]
        fig_vega_tau = go.Figure()
        fig_vega_tau.add_trace(go.Scatter(x=tau_range, y=vegas_tau, mode='lines', name='Vega'))
        fig_vega_tau.update_layout(
            title="Vega vs Time to Maturity",
            xaxis_title="Time to Maturity (τ)",
            yaxis_title="Vega",
            template="plotly_white",
            height=250
        )

        # Vega vs sigma
        sigma_range = np.linspace(0.1, 0.8, 100)  # Volatility from 10% to 80%
        vegas_sigma = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sig, r)['Vega'] 
                        for sig in sigma_range]
        fig_vega_sigma = go.Figure()
        fig_vega_sigma.add_trace(go.Scatter(x=sigma_range, y=vegas_sigma, mode='lines', name='Vega'))
        fig_vega_sigma.update_layout(
            title="Vega vs Volatility",
            xaxis_title="Volatility (σ)",
            yaxis_title="Vega",
            template="plotly_white",
            height=250
        )

        # Vega vs r
        r_range = np.linspace(0.01, 0.1, 100)  # Risk-free rate from 1% to 10%
        vegas_r = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sigma, r_val)['Vega'] 
                    for r_val in r_range]
        fig_vega_r = go.Figure()
        fig_vega_r.add_trace(go.Scatter(x=r_range, y=vegas_r, mode='lines', name='Vega'))
        fig_vega_r.update_layout(
            title="Vega vs Risk-Free Rate",
            xaxis_title="Risk-Free Rate (r)",
            yaxis_title="Vega",
            template="plotly_white",
            height=250
        )

        return fig_vega_S, fig_vega_tau, fig_vega_sigma, fig_vega_r

    def plot_rho_analysis(self, instrument, S_range, T, t, sigma, r):
        """
        Plot rho sensitivity analysis charts.
        
        Parameters:
        - instrument: Option instrument
        - S_range: Range of underlying prices
        - T, t, sigma, r: Other market parameters
        
        Returns:
        - tuple of four Plotly figures (rho_vs_S, rho_vs_tau, rho_vs_sigma, rho_vs_r)
        """
        # Rho vs S
        rhos = [instrument.compute_greeks(S, T, t, sigma, r)['Rho'] for S in S_range]
        fig_rho_S = go.Figure()
        fig_rho_S.add_trace(go.Scatter(x=S_range, y=rhos, mode='lines', name='Rho'))
        fig_rho_S.update_layout(
            title="Rho vs Underlying Price",
            xaxis_title="Underlying Price (S)",
            yaxis_title="Rho",
            template="plotly_white",
            height=250
        )

        # Rho vs tau (T-t)
        tau_range = np.linspace(0.1, 2, 100)  # Time to maturity from 0.1 to 2 years
        rhos_tau = [instrument.compute_greeks(S_range[len(S_range)//2], tau + t, t, sigma, r)['Rho'] 
                    for tau in tau_range]
        fig_rho_tau = go.Figure()
        fig_rho_tau.add_trace(go.Scatter(x=tau_range, y=rhos_tau, mode='lines', name='Rho'))
        fig_rho_tau.update_layout(
            title="Rho vs Time to Maturity",
            xaxis_title="Time to Maturity (τ)",
            yaxis_title="Rho",
            template="plotly_white",
            height=250
        )

        # Rho vs sigma
        sigma_range = np.linspace(0.1, 0.8, 100)  # Volatility from 10% to 80%
        rhos_sigma = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sig, r)['Rho'] 
                      for sig in sigma_range]
        fig_rho_sigma = go.Figure()
        fig_rho_sigma.add_trace(go.Scatter(x=sigma_range, y=rhos_sigma, mode='lines', name='Rho'))
        fig_rho_sigma.update_layout(
            title="Rho vs Volatility",
            xaxis_title="Volatility (σ)",
            yaxis_title="Rho",
            template="plotly_white",
            height=250
        )

        # Rho vs r
        r_range = np.linspace(0.01, 0.1, 100)  # Risk-free rate from 1% to 10%
        rhos_r = [instrument.compute_greeks(S_range[len(S_range)//2], T, t, sigma, r_val)['Rho'] 
                  for r_val in r_range]
        fig_rho_r = go.Figure()
        fig_rho_r.add_trace(go.Scatter(x=r_range, y=rhos_r, mode='lines', name='Rho'))
        fig_rho_r.update_layout(
            title="Rho vs Risk-Free Rate",
            xaxis_title="Risk-Free Rate (r)",
            yaxis_title="Rho",
            template="plotly_white",
            height=250
        )

        return fig_rho_S, fig_rho_tau, fig_rho_sigma, fig_rho_r



