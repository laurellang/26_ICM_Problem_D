import matplotlib.pyplot as plt
import numpy as np

# Set font for display
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

# --- Data Preparation ---
years = np.array(['2026(Construction)', '2027(Construction)', '2028(Mature)', '2029', '2030'])
n_years = len(years)

# Investment expenditure (negative) - $180M total over 3 years
investment = np.array([-60, -60, -60, 0, 0])

# Incremental revenue components (Unit: Million USD)
# Gate premium, Digital upsell, Non-game day complex, Sponsorship uplift
gate_premium = np.array([5, 12, 35, 38, 40])
digital_upsell = np.array([2, 5, 15, 16, 17])
arena_complex = np.array([10, 20, 40, 42, 45])
sponsorship = np.array([3, 8, 21, 22, 23])

# Annual net cash flow = Sum of revenues + Investment
annual_cash_flow = (gate_premium + digital_upsell + arena_complex + sponsorship) + investment
# Cumulative cash flow
cumulative_cash_flow = np.cumsum(annual_cash_flow)

# --- Plotting ---
fig, ax1 = plt.subplots(figsize=(12, 7))

# Revenue components - lower alpha to 0.5
ax1.bar(years, gate_premium, label='Gate Premium (Premium Seats)', color='#F9B288', alpha=0.6)
ax1.bar(years, digital_upsell, bottom=gate_premium, label='Digital/AI Upsell', color='#FDE49C', alpha=0.8)
ax1.bar(years, arena_complex, bottom=gate_premium+digital_upsell, label='Non-Game Day Complex Revenue', color='#B4E197', alpha=0.5)
ax1.bar(years, sponsorship, bottom=gate_premium+digital_upsell+arena_complex, label='Sponsorship/Brand Uplift', color='#83BD75', alpha=0.5)

# Investment - set alpha for visual consistency
ax1.bar(years, investment, label='Renovation Investment (CapEx)', color='#F29191')

#加条线
ax1.axhline(0, color='black', linewidth=1)

# 3. Plot cumulative cash flow line (right Y-axis)
ax2 = ax1.twinx()
ax2.plot(years, cumulative_cash_flow, color='black', marker='o', linewidth=3, label='Cumulative Net Cash Flow')
ax2.axhline(0, color='gray', linestyle='--', linewidth=1) # Break-even line

# Annotate break-even point
ax2.annotate('Break-even Point', xy=(1.6, 0), xytext=(0.5, 50),
             arrowprops=dict(facecolor='black', shrink=0.05),
             fontsize=12, fontweight='bold')

# --- Chart Styling ---
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Annual Incremental Revenue/Investment (Million USD)', fontsize=12)
ax2.set_ylabel('Cumulative Cash Flow (Million USD)', fontsize=12)
plt.title('Chase Center Renovation Project: ROI and Revenue Breakdown Analysis (2026-2030)', fontsize=16)

# Merge legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)

plt.tight_layout()
plt.show()
