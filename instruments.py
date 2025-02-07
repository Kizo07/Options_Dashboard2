import math
from scipy.stats import norm

class Instrument:
    def __init__(self, instrument_type, strike=None, position=1):
        """
        Initialize an instrument.

        Parameters:
        - instrument_type: A string, 'call', 'put', or 'stock' (not case-sensitive).
        - strike: The strike price (required for calls and puts; can be None for stocks).
        - position: 1 for long (buy), -1 for short (sell)
        """
        self.instrument_type = instrument_type.lower()
        if self.instrument_type in ['call', 'put'] and strike is None:
            raise ValueError("Strike price is required for options")
        self.strike = float(strike) if strike is not None else None
        self.position = position  # 1 for long, -1 for short

    def get_current_value(self, S, T, t, sigma, r):
        """
        Compute the current value of the instrument.

        For calls and puts, this method uses the Black–Scholes equation.
        For stocks, the current value is assumed to be the current underlying price.

        Parameters:
        - S: Current price of the underlying asset.
        - T: Time to maturity (expiration time).
        - t: Current time.
        - sigma: Volatility of the underlying asset.
        - r: Risk-free interest rate.

        Returns:
        - The current value (price) of the instrument.
        """
        value = self._compute_raw_value(S, T, t, sigma, r)
        return value * self.position

    def compute_greeks(self, S, T, t, sigma, r):
        """
        Compute basic greeks for a European call or put option.
        
        Parameters:
        - S: Current price of the underlying asset
        - T: Time to maturity (expiration time)
        - t: Current time
        - sigma: Volatility of the underlying asset
        - r: Risk-free interest rate
        
        Returns:
        - Dictionary containing Delta, Gamma, Theta, Vega, and Rho values
        """
        if self.instrument_type == 'stock':
            return {'Delta': 1, 'Gamma': 0, 'Theta': 0, 'Vega': 0, 'Rho': 0}
        
        tau = T - t
        d1 = (math.log(S / self.strike) + (r + sigma**2 / 2) * tau) / (sigma * math.sqrt(tau))
        d2 = d1 - sigma * math.sqrt(tau)
        
        # Common calculations
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(tau))
        vega = S * math.sqrt(tau) * norm.pdf(d1)
        
        if self.instrument_type == 'call':
            delta = norm.cdf(d1)
            theta = (- (S * sigma * norm.pdf(d1)) / (2 * math.sqrt(tau))
                    - r * self.strike * math.exp(-r * tau) * norm.cdf(d2))
            rho = self.strike * tau * math.exp(-r * tau) * norm.cdf(d2)
        elif self.instrument_type == 'put':
            delta = norm.cdf(d1) - 1
            theta = (- (S * sigma * norm.pdf(d1)) / (2 * math.sqrt(tau))
                    + r * self.strike * math.exp(-r * tau) * norm.cdf(-d2))
            rho = -self.strike * tau * math.exp(-r * tau) * norm.cdf(-d2)
        else:
            raise ValueError("Invalid instrument type")
            
        return {
            'Delta': delta,
            'Gamma': gamma,
            'Theta': theta,
            'Vega': vega,
            'Rho': rho
        }

    def get_payoff(self, S_T):
        """
        Compute the payoff of the instrument at expiration (time T).

        For options, the payoff is the intrinsic value at expiration.
        For stocks, the payoff is simply the underlying's price at expiration.

        Parameters:
        - S_T: The price of the underlying asset at expiration (time T).

        Returns:
        - The payoff of the instrument.
        """
        payoff = self._compute_raw_payoff(S_T)
        return payoff * self.position

    def _compute_raw_value(self, S, T, t, sigma, r):
        """Internal method to compute raw value before applying position direction."""
        S = float(S)
        
        if self.instrument_type == 'stock':
            return S

        tau = T - t
        if tau <= 0:
            if self.instrument_type == 'call':
                value = max(S - self.strike, 0)
            elif self.instrument_type == 'put':
                value = max(self.strike - S, 0)
            else:
                raise ValueError("Invalid instrument type")
        else:
            try:
                d1 = (math.log(S / self.strike) + (r + sigma**2 / 2) * tau) / (sigma * math.sqrt(tau))
                d2 = d1 - sigma * math.sqrt(tau)
                
                if self.instrument_type == 'call':
                    value = S * norm.cdf(d1) - self.strike * math.exp(-r * tau) * norm.cdf(d2)
                elif self.instrument_type == 'put':
                    value = self.strike * math.exp(-r * tau) * norm.cdf(-d2) - S * norm.cdf(-d1)
                else:
                    raise ValueError("Invalid instrument type")
            except (ValueError, ZeroDivisionError) as e:
                print(f"Error in Black-Scholes calculation: {e}")
                value = 0
        return value

    def _compute_raw_payoff(self, S_T):
        """Internal method to compute raw payoff before applying position direction."""
        S_T = float(S_T)
        
        if self.instrument_type == 'stock':
            return S_T
        elif self.instrument_type == 'call':
            return max(S_T - self.strike, 0.0)
        elif self.instrument_type == 'put':
            return max(self.strike - S_T, 0.0)
        else:
            raise ValueError("Invalid instrument type")


