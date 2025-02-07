# Options Dashboard

An interactive dashboard for analyzing options trading strategies and Black-Scholes option pricing, built with Dash and Python.

## Features

### 1. Trading Strategies Tab
- Create and analyze portfolios with up to 4 instruments
- Supported instruments: Calls, Puts, and Stocks
- Long (Buy) and Short (Sell) positions
- Real-time visualization of:
  - Payoff at expiration
  - Current portfolio value using Black-Scholes pricing

### 2. Single Option Analysis Tab
- Analyze N(d1)-N(d2) and N(d1)/N(d2) relationships
- Adjustable parameters:
  - S/K ratio
  - Time to maturity
  - Volatility
  - Risk-free rate

### 3. Option Greeks Tab
- Calculate and display key option Greeks:
  - Delta: Price sensitivity to underlying
  - Gamma: Delta sensitivity to underlying
  - Theta: Price sensitivity to time
  - Vega: Price sensitivity to volatility
  - Rho: Price sensitivity to interest rate

## Technical Details

### Core Components
- **Instrument Class**: Handles option pricing and calculations
- **PortfolioPlotter**: Manages visualization of strategies
- **Black-Scholes Implementation**: For European option pricing

### Dependencies
- Dash
- Plotly
- NumPy
- SciPy

### Running the Application