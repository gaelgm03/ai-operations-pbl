1. Why Monte Carlo Simulation is the OM Standard
In inventory management, "the average is a lie." If we only stock for average demand, we fail to satisfy customers 50% of the time.
Capturing Stochasticity: Real-world retail demand is a "stochastic process," not a deterministic one. Monte Carlo simulation allows us to move beyond point forecasts to a probability distribution of outcomes.
Stress Testing "Tail Risks": Traditional models often break during extreme events (e.g., a sudden promotion or weather-driven surge). Simulation generates thousands of "synthetic futures" to see how our inventory levels hold up under pressure.
Quantifying the "Service Level": It allows us to calculate the Fill Rate—the percentage of demand met from on-hand inventory—across different scenarios, providing a far more robust metric than simple accuracy scores.
2. The Canonical Nature of (r, Q) Policies
We have chosen the Continuous Review (r, Q) Policy (ordering a fixed quantity Q whenever the inventory level drops to the reorder point r) as our baseline for several reasons:
The EOQ Foundation: The (r, Q) policy is the stochastic extension of the Economic Order Quantity (EOQ) model. It is mathematically designed to balance three conflicting costs: Ordering Costs (shipping/admin), Holding Costs (warehouse rent/capital), and Stockout Penalties.
Handling Lead-Time Uncertainty: The reorder point r specifically accounts for demand during the "Lead Time" (the gap between ordering and receiving goods). By setting r = \text{Expected Demand during Lead Time} + \text{Safety Stock}, we create a buffer against uncertainty.
Defensibility & Interpretability: Unlike "black-box" AI models, an (r, Q) policy is transparent. If an advanced algorithm cannot outperform a well-tuned (r, Q) baseline, it indicates the algorithm is over-engineered.
3. Theoretical Justification for Learning \sigma (Demand Volatility)
A core critique from our supervisor was the quantification of uncertainty. We justify "learning" \sigma (the standard deviation of demand) as follows:
Volatility as a Proxy for Risk: In finance and OM, \sigma is the universal measure of risk. By calculating the Rolling Standard Deviation or Forecast Error \sigma, we are essentially measuring the "environment's noise level."
Adaptive Safety Stock: Safety stock is a function of \sigma. If the environment becomes noisier (e.g., during a holiday or crisis), \sigma increases. Learning this parameter dynamically allows the model to "tighten" its protection automatically.
The "Equity" Mechanism: This is our response to the "baby formula" case. Different product categories have different volatilities. By accurately learning the \sigma for essentials (Groceries), we can mathematically justify higher safety stock levels for those items to ensure social equity, even if they are less profitable than non-essentials.
