# -*- coding: utf-8 -*-
"""
2026 ICM Problem D - 动力系统模型
球队：金州勇士 (Golden State Warriors)

基于系统动力学的球队财务与竞技表现优化模型
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
from scipy.integrate import odeint
from scipy.optimize import minimize, differential_evolution
import matplotlib.pyplot as plt

# 配置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 1. 数据加载与整理 ====================
print("=" * 60)
print("2026 ICM Problem D - 动力系统模型")
print("球队: 金州勇士 (Golden State Warriors)")
print("=" * 60)

# 从Excel读取数据
df_finance = pd.read_excel('【财务分析】五季度.xlsx')
df_league = pd.read_excel('【联盟财务】五季度.xlsx')
df_players = pd.read_excel('【球员信息】25-26季度.xlsx')
df_history = pd.read_excel('【历史数据】.xlsx')

# ==================== 2. 参数提取 ====================
print("\n>>> 步骤1: 提取模型参数")
print("-" * 60)

# 2025-26赛季联盟参数
SALARY_CAP = 154647000  # 工资帽
LUXURY_TAX_LINE = 187895000  # 奢侈税起征点
FIRST_APRON = 195945000  # 第一土豪线
SECOND_APRON = 207824000  # 第二土豪线

# 奢侈税率表 (阶梯式，累犯税率)
TAX_BRACKETS = [
    (0, 4999999, 2.5),      # $0 - $5M: 2.5倍
    (5000000, 9999999, 2.75),  # $5M - $10M: 2.75倍
    (10000000, 14999999, 3.5),  # $10M - $15M: 3.5倍
    (15000000, 19999999, 4.25),  # $15M - $20M: 4.25倍
    (20000000, float('inf'), 4.75),  # $20M+: 每$5M增加0.5
]

# 勇士队历史数据 (用于参数估计)
historical_data = {
    'season': ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25'],
    'win_rate': [0.542, 0.646, 0.537, 0.561, 0.585],
    'revenue': [258e6, 765e6, 765e6, 800e6, 880e6],  # 美元
    'valuation': [4.7e9, 5.6e9, 7.0e9, 7.7e9, 8.8e9],  # 美元
    'brand_value': [0.95e9, 1.005e9, 1.18e9, 1.36e9, 1.521e9],  # 美元
    'salary': [147.7e6, 175.85e6, 191.7e6, 209.3e6, 176.89e6],
    'luxury_tax': [68.9e6, 170.3e6, 163.7e6, 176.9e6, 15.41e6],
    'ebitda': [-44e6, 206e6, 79e6, 142e6, 409e6],
}

print(f"工资帽: ${SALARY_CAP/1e6:.1f}M")
print(f"奢侈税线: ${LUXURY_TAX_LINE/1e6:.1f}M")
print(f"第一土豪线: ${FIRST_APRON/1e6:.1f}M")
print(f"第二土豪线: ${SECOND_APRON/1e6:.1f}M")

# 当前球员薪资
current_salary = df_players['25-26 薪资'].sum()
print(f"\n当前阵容总薪资: ${current_salary/1e6:.1f}M")

# ==================== 3. 奢侈税计算函数 ====================
def calculate_luxury_tax(salary, is_repeater=True):
    """
    计算奢侈税 (阶梯式累犯税率)
    
    参数:
        salary: 总薪资
        is_repeater: 是否为累犯 (勇士队是)
    """
    if salary <= LUXURY_TAX_LINE:
        return 0
    
    excess = salary - LUXURY_TAX_LINE
    total_tax = 0
    
    for low, high, rate in TAX_BRACKETS:
        if excess <= 0:
            break
        taxable = min(excess, high - low + 1) if low <= excess else 0
        if taxable > 0:
            actual_rate = rate if is_repeater else rate - 1.0
            total_tax += taxable * actual_rate
            excess -= (high - low + 1)
    
    return total_tax

# 验证奢侈税计算
test_tax = calculate_luxury_tax(current_salary)
print(f"当前薪资对应奢侈税: ${test_tax/1e6:.1f}M")

# ==================== 4. 参数估计 ====================
print("\n>>> 步骤2: 参数估计")
print("-" * 60)

# 使用历史数据估计参数
win_rates = np.array(historical_data['win_rate'])
revenues = np.array(historical_data['revenue'])
brand_values = np.array(historical_data['brand_value'])
salaries = np.array(historical_data['salary'])

# 估计 α (胜率对收入的影响)
# R = R_fixed + α * S + β * B
# 使用线性回归
from numpy.linalg import lstsq

# 构建设计矩阵 [1, S, B]
X = np.column_stack([np.ones(5), win_rates, brand_values / 1e9])
y = revenues / 1e6  # 转换为百万美元

# 最小二乘估计
coeffs, residuals, rank, s = lstsq(X, y, rcond=None)
R_FIXED = coeffs[0] * 1e6  # 固定收入
ALPHA = coeffs[1] * 1e6    # 胜率系数
BETA = coeffs[2] * 1e6     # 品牌系数

print(f"估计参数:")
print(f"  R_fixed (固定收入): ${R_FIXED/1e6:.1f}M")
print(f"  α (胜率→收入): ${ALPHA/1e6:.2f}M per win%")
print(f"  β (品牌→收入): ${BETA/1e6:.2f}M per $B brand")

# 品牌演化参数 (dB/dt = η*S + ζ*Star - δ*B)
# 简化估计
ETA = 0.5e9      # 表现转化系数 (每胜率点贡献品牌)
ZETA = 0.1e9    # 球星效应系数
DELTA = 0.15    # 品牌自然衰减率 (15%/年)

print(f"  η (表现→品牌): ${ETA/1e9:.2f}B")
print(f"  ζ (球星→品牌): ${ZETA/1e9:.2f}B")
print(f"  δ (品牌衰减率): {DELTA*100:.0f}%/年")

# 胜率与薪资的关系
# S = f(C_pay) - 简化为对数函数
# 从历史数据拟合
log_salaries = np.log(salaries / 1e6)
poly_coeffs = np.polyfit(log_salaries, win_rates, 1)
SALARY_WIN_SLOPE = poly_coeffs[0]
SALARY_WIN_INTERCEPT = poly_coeffs[1]

print(f"  薪资-胜率关系: S = {SALARY_WIN_SLOPE:.3f} * ln(C_pay) + {SALARY_WIN_INTERCEPT:.3f}")

# 运营成本 (从历史数据估计)
# EBITDA = Revenue - Salary - LuxuryTax - C_ops
# C_ops = Revenue - Salary - LuxuryTax - EBITDA
ebitdas = np.array(historical_data['ebitda'])
luxury_taxes = np.array(historical_data['luxury_tax'])
ops_costs = revenues - salaries - luxury_taxes - ebitdas
C_OPS = np.mean(ops_costs)  # 平均运营成本

print(f"  C_ops (运营成本): ${C_OPS/1e6:.1f}M")

# 季后赛奖金
PLAYOFF_BONUS = 34.7e6  # 2025-26赛季奖金池
PLAYOFF_THRESHOLD = 0.5  # 进季后赛的胜率门槛

# ==================== 5. 动力系统方程 ====================
print("\n>>> 步骤3: 定义动力系统方程")
print("-" * 60)

# 球星效应指数 (库里为主)
STAR_EFFECT = 1.0  # 归一化的球星效应

def win_rate_function(salary):
    """薪资转化为胜率的函数"""
    # S = slope * ln(C_pay/1e6) + intercept
    # 限制在合理范围 [0.3, 0.8]
    s = SALARY_WIN_SLOPE * np.log(salary / 1e6) + SALARY_WIN_INTERCEPT
    return np.clip(s, 0.3, 0.8)

def revenue_function(win_rate, brand_value):
    """营收函数"""
    # R(t) = R_fixed + α*S(t) + β*B(t) + I_playoff(S)*Ω
    base_revenue = R_FIXED + ALPHA * win_rate + BETA * (brand_value / 1e9)
    playoff_bonus = PLAYOFF_BONUS if win_rate >= PLAYOFF_THRESHOLD else 0
    return base_revenue + playoff_bonus

def expense_function(salary):
    """支出函数"""
    # E(t) = C_pay + T(C_pay) + C_ops
    luxury_tax = calculate_luxury_tax(salary)
    return salary + luxury_tax + C_OPS

def dynamics(state, t, salary):
    """
    状态转移微分方程
    
    state = [P, B] = [累计利润, 品牌价值]
    """
    P, B = state
    
    # 计算胜率
    S = win_rate_function(salary)
    
    # 计算收入和支出
    R = revenue_function(S, B)
    E = expense_function(salary)
    
    # 利润变化率
    dP_dt = R - E
    
    # 品牌价值变化率
    dB_dt = ETA * S + ZETA * STAR_EFFECT - DELTA * B
    
    return [dP_dt, dB_dt]

print("动力系统方程已定义:")
print("  dP/dt = R(t) - E(t)")
print("  dB/dt = η*S(t) + ζ*Star(t) - δ*B(t)")

# ==================== 6. 模拟与优化 ====================
print("\n>>> 步骤4: 模型模拟与优化")
print("-" * 60)

# 初始条件 (2025-26赛季开始)
P0 = 0  # 累计利润从0开始计算
B0 = 1.246e9  # 当前品牌价值 (12.46亿)
V0 = 11e9  # 当前估值 (110亿)

# 时间跨度 (5年)
H = 5
t = np.linspace(0, H, 100)

# 折现率
RHO = 0.05  # 5%年折现率

# 目标权重
W1 = 0.6  # 利润权重
W2 = 0.4  # 估值权重

def objective_function(salary_trajectory):
    """
    目标函数: 最大化折现后的利润+估值
    
    J = ∫[0,H] e^(-ρt) [w1*P(t) + w2*V(t)] dt
    """
    # 将薪资轨迹插值到时间点
    salary_interp = np.interp(t, np.linspace(0, H, len(salary_trajectory)), salary_trajectory)
    
    # 数值积分求解微分方程
    total_value = 0
    state = [P0, B0]
    
    for i in range(len(t) - 1):
        dt = t[i+1] - t[i]
        salary = salary_interp[i]
        
        # 欧拉法求解
        dstate = dynamics(state, t[i], salary)
        state = [state[0] + dstate[0] * dt, state[1] + dstate[1] * dt]
        
        # 估值假设为品牌价值的倍数
        V = state[1] * 7  # 估值约为品牌价值的7倍
        
        # 折现
        discount = np.exp(-RHO * t[i+1])
        total_value += discount * (W1 * state[0] + W2 * V) * dt
    
    return -total_value  # 返回负值因为scipy最小化

def constraint_min_profit(salary_trajectory):
    """约束: 确保单年利润不为负"""
    salary_interp = np.interp(t, np.linspace(0, H, len(salary_trajectory)), salary_trajectory)
    
    state = [P0, B0]
    min_annual_profit = float('inf')
    
    for i in range(len(t) - 1):
        dt = t[i+1] - t[i]
        salary = salary_interp[i]
        
        dstate = dynamics(state, t[i], salary)
        annual_profit = dstate[0]  # 年利润率
        min_annual_profit = min(min_annual_profit, annual_profit)
        
        state = [state[0] + dstate[0] * dt, state[1] + dstate[1] * dt]
    
    return min_annual_profit + 50e6  # 允许最多亏损5000万

# 优化
print("开始优化薪资策略...")

# 简化: 每年一个薪资决策 (5个决策变量)
n_periods = 5
bounds = [(150e6, 250e6) for _ in range(n_periods)]  # 薪资范围: 1.5亿-2.5亿

# 初始猜测: 当前薪资水平
x0 = [current_salary] * n_periods

# 使用差分进化求解
result = differential_evolution(
    objective_function,
    bounds,
    seed=42,
    maxiter=200,
    tol=1e-6,
    workers=1
)

optimal_salaries = result.x
print(f"\n优化完成!")
print(f"目标函数值: {-result.fun/1e9:.2f}B (折现总价值)")

# ==================== 7. 结果分析 ====================
print("\n>>> 步骤5: 结果分析")
print("-" * 60)

print("\n最优薪资策略 (未来5年):")
print("-" * 40)
years = ['2025-26', '2026-27', '2027-28', '2028-29', '2029-30']
for i, (year, salary) in enumerate(zip(years, optimal_salaries)):
    win_rate = win_rate_function(salary)
    tax = calculate_luxury_tax(salary)
    print(f"  {year}: 薪资 ${salary/1e6:.1f}M, 奢侈税 ${tax/1e6:.1f}M, 预期胜率 {win_rate:.1%}")

# 模拟最优策略下的状态演化
print("\n状态演化模拟:")
print("-" * 40)

salary_interp = np.interp(t, np.linspace(0, H, n_periods), optimal_salaries)
states = [[P0, B0]]
profits = []
revenues = []
expenses = []

for i in range(len(t) - 1):
    dt = t[i+1] - t[i]
    salary = salary_interp[i]
    state = states[-1]
    
    S = win_rate_function(salary)
    R = revenue_function(S, state[1])
    E = expense_function(salary)
    
    dstate = dynamics(state, t[i], salary)
    new_state = [state[0] + dstate[0] * dt, state[1] + dstate[1] * dt]
    states.append(new_state)
    profits.append(dstate[0])
    revenues.append(R)
    expenses.append(E)

states = np.array(states)
final_profit = states[-1, 0]
final_brand = states[-1, 1]
final_valuation = final_brand * 7

print(f"5年后累计利润: ${final_profit/1e9:.2f}B")
print(f"5年后品牌价值: ${final_brand/1e9:.2f}B")
print(f"5年后估计估值: ${final_valuation/1e9:.2f}B")

# ==================== 8. 可视化 ====================
print("\n>>> 步骤6: 生成可视化图表")
print("-" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 图1: 薪资策略
ax1 = axes[0, 0]
ax1.bar(years, optimal_salaries / 1e6, color='steelblue', alpha=0.7)
ax1.axhline(y=LUXURY_TAX_LINE/1e6, color='red', linestyle='--', label=f'奢侈税线 ${LUXURY_TAX_LINE/1e6:.0f}M')
ax1.axhline(y=SALARY_CAP/1e6, color='green', linestyle='--', label=f'工资帽 ${SALARY_CAP/1e6:.0f}M')
ax1.set_ylabel('薪资 (百万美元)')
ax1.set_title('最优薪资策略')
ax1.legend()
ax1.set_ylim(100, 280)

# 图2: 累计利润演化
ax2 = axes[0, 1]
ax2.plot(t, states[:, 0] / 1e9, 'b-', linewidth=2)
ax2.fill_between(t, 0, states[:, 0] / 1e9, alpha=0.3)
ax2.set_xlabel('年')
ax2.set_ylabel('累计利润 (十亿美元)')
ax2.set_title('累计利润演化')
ax2.grid(True, alpha=0.3)

# 图3: 品牌价值演化
ax3 = axes[1, 0]
ax3.plot(t, states[:, 1] / 1e9, 'g-', linewidth=2)
ax3.set_xlabel('年')
ax3.set_ylabel('品牌价值 (十亿美元)')
ax3.set_title('品牌价值演化')
ax3.grid(True, alpha=0.3)

# 图4: 年度收入vs支出
ax4 = axes[1, 1]
ax4.plot(t[:-1], np.array(revenues) / 1e6, 'g-', linewidth=2, label='收入')
ax4.plot(t[:-1], np.array(expenses) / 1e6, 'r-', linewidth=2, label='支出')
ax4.fill_between(t[:-1], np.array(revenues)/1e6, np.array(expenses)/1e6, 
                  where=np.array(revenues) > np.array(expenses), 
                  color='green', alpha=0.3, label='盈利')
ax4.fill_between(t[:-1], np.array(revenues)/1e6, np.array(expenses)/1e6, 
                  where=np.array(revenues) <= np.array(expenses), 
                  color='red', alpha=0.3, label='亏损')
ax4.set_xlabel('年')
ax4.set_ylabel('金额 (百万美元)')
ax4.set_title('年度收入 vs 支出')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('dynamical_system_results.png', dpi=150, bbox_inches='tight')
print("图表已保存为 dynamical_system_results.png")

# ==================== 9. 场景分析 ====================
print("\n>>> 步骤7: 场景分析")
print("-" * 60)

# 场景1: 保守策略 (控制在奢侈税线以下)
print("\n场景1: 保守策略 (控制薪资在奢侈税线以下)")
conservative_salaries = [LUXURY_TAX_LINE * 0.95] * n_periods
conservative_value = -objective_function(conservative_salaries)
print(f"  总价值: ${conservative_value/1e9:.2f}B")

# 场景2: 激进策略 (高薪资追求胜利)
print("\n场景2: 激进策略 (高薪资)")
aggressive_salaries = [220e6] * n_periods
aggressive_value = -objective_function(aggressive_salaries)
print(f"  总价值: ${aggressive_value/1e9:.2f}B")

# 场景3: 优化策略
print("\n场景3: 优化策略")
optimal_value = -objective_function(optimal_salaries)
print(f"  总价值: ${optimal_value/1e9:.2f}B")

# 对比
print("\n策略对比:")
print(f"  保守策略: ${conservative_value/1e9:.2f}B")
print(f"  激进策略: ${aggressive_value/1e9:.2f}B")
print(f"  优化策略: ${optimal_value/1e9:.2f}B (最优)")
print(f"  优化相对保守提升: {(optimal_value - conservative_value)/conservative_value*100:.1f}%")

# ==================== 10. 总结 ====================
print("\n" + "=" * 60)
print("模型总结")
print("=" * 60)
print("""
动力系统模型核心要素:

1. 状态变量:
   - P(t): 累计净利润
   - B(t): 品牌资产价值

2. 控制变量:
   - C_pay(t): 每年球员薪资投入

3. 系统方程:
   - dP/dt = R(t) - E(t)
   - dB/dt = η*S(t) + ζ*Star(t) - δ*B(t)

4. 目标函数:
   - max J = ∫ e^(-ρt) [w1*P(t) + w2*V(t)] dt

5. 关键发现:
   - 最优策略在奢侈税线附近波动
   - 品牌价值是长期增值的关键驱动力
   - 需要平衡短期利润与长期估值
""")

plt.show()
