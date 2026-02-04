# -*- coding: utf-8 -*-
"""
NBA 球队方案评估 - 主程序 v2
核心输出: 预期胜场 + 净利润
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import Q2_evaluate as ev
import Q2_config as cfg 
import matplotlib.pyplot as plt
import numpy as np

# 配置字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

COLORS = cfg.VISUALIZATION["colors"]

# 为每个候选球员分配不同颜色
PLAYER_COLORS = [
    '#3b82f6',  # 蓝
    '#ef4444',  # 红
    '#22c55e',  # 绿
    '#f59e0b',  # 橙
    '#8b5cf6',  # 紫
    '#06b6d4',  # 青
    '#ec4899',  # 粉
    '#84cc16',  # 黄绿
]


def print_detailed_result(name, result):
    """打印详细评估结果"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    
    # 核心指标
    print(f"\n  📊 核心指标")
    print(f"  ├─ 预期总胜场: {result['Total Wins']:.1f} 场")
    print(f"  └─ 净利润:     ${result['Net Profit']:.1f}M")
    
    # 胜场分解
    print(f"\n  🏀 胜场分解")
    print(f"  ├─ 常规赛胜场: {result['Regular Wins']:.1f} 场")
    print(f"  ├─ 季后赛轮数: {result['Playoff Rounds']:.1f} 轮 (进入概率: {result['Playoff Entry Prob']*100:.0f}%)")
    print(f"  └─ 季后赛胜场: {result['Playoff Wins']:.1f} 场")
    
    # 财务分解
    rev = result['Revenue Breakdown']
    cost = result['Cost Breakdown']
    print(f"\n  💰 财务分解")
    print(f"  ├─ 总收入: ${result['Revenue']:.1f}M")
    print(f"  │   ├─ 联盟分成: ${rev['base']:.1f}M")
    print(f"  │   ├─ 门票收入: ${rev['gate']:.1f}M")
    print(f"  │   ├─ 季后赛收入: ${rev['playoff']:.1f}M")
    print(f"  │   ├─ 场馆收入: ${rev['arena']:.1f}M")
    print(f"  │   └─ 联盟上缴: -${rev['sharing']:.1f}M")
    print(f"  └─ 总成本: ${result['Costs']:.1f}M")
    print(f"      ├─ 固定成本: ${cost['fixed']:.1f}M")
    print(f"      ├─ 球员工资: ${cost['salary']:.1f}M")
    print(f"      └─ 奢侈税:   ${cost['tax']:.1f}M")
    
    # 化学反应
    if result['Chemistry Details']:
        print(f"\n  ⚗️ 化学反应加成")
        for chem in result['Chemistry Details']:
            p1, p2 = chem['pair']
            print(f"  └─ {p1} + {p2}: +{chem['bonus']:.1f} 胜")


def plot_comparison(result_A, result_B, save_path=None):
    """绘制方案对比图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['background'])
    
    plans = ['Plan A\n(All-in)', 'Plan B\n(Rebuild)']
    colors = [COLORS['plan_a'], COLORS['plan_b']]
    
    # 图1: 胜场对比
    ax1 = axes[0]
    ax1.set_facecolor(COLORS['background'])
    
    regular = [result_A['Regular Wins'], result_B['Regular Wins']]
    playoff = [result_A['Playoff Wins'], result_B['Playoff Wins']]
    
    x = np.arange(2)
    width = 0.5
    
    bars1 = ax1.bar(x, regular, width, label='Regular Season', color=colors, alpha=0.8)
    bars2 = ax1.bar(x, playoff, width, bottom=regular, label='Playoff', color=colors, alpha=0.5, hatch='//')
    
    # 标注常规赛胜场 (在常规赛柱子顶部)
    for i, r in enumerate(regular):
        ax1.text(i, r - 3, f'{r:.1f}', ha='center', fontsize=15, 
                fontweight='bold', color='white')
    
    # 标注总胜场 (在总柱子顶部)
    for i, (r, p) in enumerate(zip(regular, playoff)):
        ax1.text(i, r + p + 1, f'Total: {r+p:.1f}', ha='center', fontsize=14, 
                fontweight='bold', color=COLORS['text'])
    
    ax1.set_ylabel('Wins', fontsize=15, color=COLORS['text'])
    ax1.set_title('Total Wins Comparison', fontsize=17, fontweight='bold', color=COLORS['text'])
    ax1.set_xticks(x)
    ax1.set_xticklabels(plans, fontsize=14, color=COLORS['text'])
    ax1.legend(facecolor=COLORS['background'], edgecolor=COLORS['grid'], 
              labelcolor=COLORS['text'])
    ax1.tick_params(colors=COLORS['text'])
    for spine in ax1.spines.values():
        spine.set_color(COLORS['grid'])
    
    # 图2: 利润对比
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['background'])
    
    profits = [result_A['Net Profit'], result_B['Net Profit']]
    bars = ax2.bar(plans, profits, color=colors, edgecolor='white', linewidth=2, width=0.5)
    
    for bar, profit in zip(bars, profits):
        color = COLORS['text'] if profit >= 0 else '#ef4444'
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'${profit:.1f}M', ha='center', fontsize=17, fontweight='bold', color=color)
    
    ax2.axhline(y=0, color=COLORS['grid'], linestyle='--', alpha=0.5)
    ax2.set_ylabel('Net Profit ($M)', fontsize=15, color=COLORS['text'])
    ax2.set_title('Net Profit Comparison', fontsize=17, fontweight='bold', color=COLORS['text'])
    ax2.tick_params(colors=COLORS['text'])
    for spine in ax2.spines.values():
        spine.set_color(COLORS['grid'])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=cfg.VISUALIZATION['figure_dpi'], 
                   bbox_inches='tight', facecolor=COLORS['background'])
        print(f"图表已保存: {save_path}")
    
    return fig


def plot_breakdown(result_A, result_B, save_path=None):
    """绘制财务分解图"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['background'])
    
    results = [result_A, result_B]
    titles = ['Plan A (All-in)', 'Plan B (Rebuild)']
    
    for ax, result, title in zip(axes, results, titles):
        ax.set_facecolor(COLORS['background'])
        
        rev = result['Revenue Breakdown']
        cost = result['Cost Breakdown']
        
        categories = ['League\nRev', 'Gate\nRev', 'Playoff', 'Arena', 'Sharing', 
                     'Fixed\nCost', 'Salary', 'Tax']
        values = [rev['base'], rev['gate'], rev['playoff'], rev['arena'], -rev['sharing'],
                 -cost['fixed'], -cost['salary'], -cost['tax']]
        colors_bar = ['#22c55e']*4 + ['#94a3b8'] + ['#ef4444']*3
        
        bars = ax.bar(categories, values, color=colors_bar, edgecolor='white', linewidth=1)
        
        ax.axhline(y=0, color=COLORS['text'], linewidth=1)
        ax.set_ylabel('$M', fontsize=14, color=COLORS['text'])
        ax.set_title(f'{title}\nNet: ${result["Net Profit"]:.1f}M', 
                    fontsize=15, fontweight='bold', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'], labelsize=12)
        
        for spine in ax.spines.values():
            spine.set_color(COLORS['grid'])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=cfg.VISUALIZATION['figure_dpi'], 
                   bbox_inches='tight', facecolor=COLORS['background'])
        print(f"图表已保存: {save_path}")
    
    return fig


def find_pareto_front(summary):
    """找出Pareto前沿点"""
    pareto = []
    for i, r1 in enumerate(summary):
        dominated = False
        for j, r2 in enumerate(summary):
            if i != j:
                if r2["wins"] >= r1["wins"] and r2["profit"] >= r1["profit"]:
                    if r2["wins"] > r1["wins"] or r2["profit"] > r1["profit"]:
                        dominated = True
                        break
        if not dominated:
            pareto.append(r1)
    return pareto

def plot_replacement_scatter(summary, save_path=None):
    """单轴散点图 - Kuminga 替换分析"""
    
    fig, ax = plt.subplots(figsize=(12, 9), facecolor=COLORS['background'])
    ax.set_facecolor('#f8f9fa')
    
    # 分离基准和候选
    baseline = [s for s in summary if s["is_baseline"]][0]
    candidates = [s for s in summary if not s["is_baseline"]]
    
    # 提取数据
    candidate_wins = [s["wins"] for s in candidates]
    candidate_profits = [s["profit"] for s in candidates]
    candidate_names = [s["player"] for s in candidates]
    candidate_diff_wins = [s["diff_wins"] for s in candidates]
    candidate_diff_profits = [s["diff_profit"] for s in candidates]
    
    all_wins = [baseline["wins"]] + candidate_wins
    all_profits = [baseline["profit"]] + candidate_profits
    
    # 1. 绑制网格和基准线
    ax.grid(True, alpha=0.15, color=COLORS['grid'], linestyle='--', linewidth=0.5)
    
    ax.axhline(y=baseline["profit"], color=COLORS['highlight'], 
              linewidth=2, alpha=0.5, linestyle=':', zorder=1)
    ax.axvline(x=baseline["wins"], color=COLORS['highlight'], 
              linewidth=2, alpha=0.5, linestyle=':', zorder=1)
    
    # 2. 设置坐标轴范围
    x_padding = (max(all_wins) - min(all_wins)) * 0.15
    y_padding = (max(all_profits) - min(all_profits)) * 0.18
    
    ax.set_xlim(min(all_wins) - x_padding, max(all_wins) + x_padding)
    ax.set_ylim(min(all_profits) - y_padding, max(all_profits) + y_padding)
    
    x_range = ax.get_xlim()
    y_range = ax.get_ylim()
    
    # 2.5 绘制四个象限背景色 (高透明度)
    # 第一象限 (右上): 绿色 - 双优
    ax.fill_between([baseline["wins"], x_range[1]], 
                   [baseline["profit"], baseline["profit"]], 
                   y_range[1], alpha=0.12, color='#22c55e', zorder=0)
    # 第二象限 (左上): 紫色 - 利润优
    ax.fill_between([x_range[0], baseline["wins"]], 
                   [baseline["profit"], baseline["profit"]], 
                   y_range[1], alpha=0.12, color='#8b5cf6', zorder=0)
    # 第三象限 (左下): 红色 - 双劣
    ax.fill_between([x_range[0], baseline["wins"]], 
                   y_range[0],
                   [baseline["profit"], baseline["profit"]], 
                   alpha=0.12, color='#ef4444', zorder=0)
    # 第四象限 (右下): 蓝色 - 胜场优
    ax.fill_between([baseline["wins"], x_range[1]], 
                   y_range[0],
                   [baseline["profit"], baseline["profit"]], 
                   alpha=0.12, color='#3b82f6', zorder=0)
    
    # 3. 绘制候选球员点
    # 自定义标签位置 (offset_x, offset_y, ha, va)
    custom_label_positions = {
        "D. Hunter": (20, 25, 'right', 'bottom'),      # 正上
        "T. Harris": (110, 20, 'right', 'center'),     # 正左
        "A. Wiggins": (60, -20, 'center', 'top'),        # 正下
        "M. Porter Jr.": (-70, 40, 'center', 'top'),     # 正下
        "R. Barrett": (-110, 0, 'left', 'center'),        # 正右
        "T. Herro": (-20, 0, 'right', 'center'),        # 正左
        "K. Porzingis": (0, -25, 'center', 'top'),      # 正下
        "M. Bridges": (-105, 5, 'left', 'bottom'),       # 左上
    }
    
    for i, (wins, profit, name, dw, dp) in enumerate(zip(candidate_wins, candidate_profits, 
                                                         candidate_names, candidate_diff_wins, 
                                                         candidate_diff_profits)):
        # 根据象限决定颜色和标记 (使用箭头)
        if dw > 0 and dp > 0:  # 双优 - 右上箭头
            color = COLORS['good']
            marker = r'$\nearrow$'  # ↗
            size = 280
            edge_color = '#0d9488'
        elif dw > 0 and dp <= 0:  # 胜场优 - 右箭头
            color = COLORS['plan_a']
            marker = r'$\rightarrow$'  # →
            size = 250
            edge_color = '#2563eb'
        elif dw <= 0 and dp > 0:  # 利润优 - 上箭头
            color = '#8b5cf6'
            marker = r'$\uparrow$'  # ↑
            size = 250
            edge_color = '#7c3aed'
        else:  # 双劣 - 左下箭头
            color = COLORS['bad']
            marker = r'$\swarrow$'  # ↙
            size = 220
            edge_color = '#dc2626'
        
        # 绘制散点
        ax.scatter(wins, profit, s=size, c=color, marker=marker,
                  alpha=0.9, edgecolors=edge_color, linewidths=1.5, 
                  zorder=10 + i)
        
        # 标签位置 - 检查是否有自定义位置
        if name in custom_label_positions:
            text_offset_x, text_offset_y, ha, va = custom_label_positions[name]
        else:
            # 默认位置
            text_offset_x = 15 if dw >= 0 else -15
            text_offset_y = 10 if dp >= 0 else -10
            ha = 'left' if text_offset_x > 0 else 'right'
            va = 'bottom' if text_offset_y > 0 else 'top'
        
        bbox_props = dict(boxstyle="round,pad=0.35", 
                         facecolor='white', 
                         edgecolor=color, 
                         alpha=0.92, 
                         linewidth=1.5)
        
        ax.annotate(f"{name}\nW:{wins:.1f} ({dw:+.1f})\nP:${profit:.1f}M", 
                   xy=(wins, profit),
                   xytext=(text_offset_x, text_offset_y),
                   textcoords='offset points',
                   fontsize=14,
                   color=color,
                   fontweight='bold',
                   ha=ha,
                   va=va,
                   bbox=bbox_props,
                   zorder=20)
    
    # 4. 绘制基准球员（Kuminga）- 标签在上方
    ax.scatter(baseline["wins"], baseline["profit"],
              s=200, c=COLORS['highlight'], marker='*',
              edgecolors='white', linewidths=1.5, 
              zorder=50)
    
    bbox_props_baseline = dict(boxstyle="round,pad=0.4", 
                              facecolor='white', 
                              edgecolor=COLORS['highlight'], 
                              alpha=0.95, 
                              linewidth=1.5)
    
    ax.annotate(f"★ Current ★\n{baseline['player']}\nW: {baseline['wins']:.1f}\nP: ${baseline['profit']:.1f}M", 
               xy=(baseline["wins"], baseline["profit"]),
               xytext=(0, 40),  # 向上偏移
               textcoords='offset points',
               fontsize=14,
               color=COLORS['highlight'],
               fontweight='bold',
               ha='center',
               va='bottom',
               bbox=bbox_props_baseline,
               arrowprops=dict(arrowstyle='-|>',
                              color=COLORS['highlight'], 
                              lw=1.2,
                              alpha=0.7,
                              mutation_scale=8),
               zorder=50)
    
    # 5. Pareto前沿
    pareto = find_pareto_front(summary)
    if len(pareto) > 1:
        pareto_sorted = sorted(pareto, key=lambda x: x["wins"])
        pareto_x = [p["wins"] for p in pareto_sorted]
        pareto_y = [p["profit"] for p in pareto_sorted]
        
        ax.plot(pareto_x, pareto_y, '--', 
               color=COLORS['good'], 
               linewidth=2, 
               alpha=0.6, 
               zorder=2)
    
    # 6. 添加标题和轴标签
    ax.set_xlabel("Total Wins (Regular + Playoff)", 
                 fontsize=17, 
                 color=COLORS['text'], 
                 fontweight='bold',
                 labelpad=10)
    
    ax.set_ylabel("Net Profit ($M)", 
                 fontsize=17, 
                 color=COLORS['text'], 
                 fontweight='bold',
                 labelpad=10)
    
    ax.set_title("KUMINGA REPLACEMENT ANALYSIS\nWin vs Profit Trade-off", 
                fontsize=19, 
                color=COLORS['text'], 
                fontweight='bold',
                pad=15)
    
    # 7. 样式调整
    ax.tick_params(colors=COLORS['text'], labelsize=14)
    for spine in ax.spines.values():
        spine.set_color('#cbd5e1')
        spine.set_linewidth(1.5)
    
    # 8. 添加图例 (左上角) - 使用箭头
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor=COLORS['highlight'],
              markersize=12, label='Current (Kuminga)', markeredgecolor='white', markeredgewidth=1),
        Line2D([0], [0], marker=r'$\nearrow$', color='w', markerfacecolor=COLORS['good'],
              markersize=12, label='Better in Both'),
        Line2D([0], [0], marker=r'$\rightarrow$', color='w', markerfacecolor=COLORS['plan_a'],
              markersize=12, label='Better Wins'),
        Line2D([0], [0], marker=r'$\uparrow$', color='w', markerfacecolor='#8b5cf6',
              markersize=12, label='Better Profit'),
        Line2D([0], [0], marker=r'$\swarrow$', color='w', markerfacecolor=COLORS['bad'],
              markersize=12, label='Worse in Both'),
    ]
    
    legend = ax.legend(handles=legend_elements, 
                      loc='upper left',  # 左上角
                      facecolor='white',
                      edgecolor=COLORS['grid'],
                      fontsize=13,
                      framealpha=0.95,
                      borderpad=0.6)
    
    for text in legend.get_texts():
        text.set_color(COLORS['text'])
    
    # 9. 数据来源
    ax.text(0.98, 0.02, 
           "Data: NBA 2025-26 Projections", 
           transform=ax.transAxes,
           fontsize=12,
           color=COLORS['text'],
           alpha=0.5,
           ha='right',
           va='bottom')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, 
                   bbox_inches='tight', 
                   facecolor='white')
        print(f"图表已保存: {save_path}")
    
    return fig

    
def print_replacement_table(summary):
    """打印替换分析表格"""
    print("\n" + "="*105)
    print("  Kuminga 替换方案对比")
    print("="*105)
    
    # 按净利润排序
    sorted_summary = sorted(summary, key=lambda x: x["profit"], reverse=True)
    baseline = [s for s in summary if s["is_baseline"]][0]
    
    print(f"\n{'Rank':<5} {'Player':<20} {'Regular':<10} {'Playoff':<10} {'Total':<10} {'Profit($M)':<12} {'Salary($M)':<12} {'Recommend':<10}")
    print("-"*105)
    
    for i, s in enumerate(sorted_summary, 1):
        # 推荐标记
        recommend = ""
        if s["profit"] > baseline["profit"] and s["wins"] > baseline["wins"]:
            recommend = "*** BEST"
        elif s["profit"] > baseline["profit"]:
            recommend = "** Profit"
        elif s["wins"] > baseline["wins"]:
            recommend = "* Wins"
        
        marker = " (baseline)" if s["is_baseline"] else ""
        print(f"{i:<5} {s['player'] + marker:<20} {s['regular_wins']:<10.1f} {s['playoff_wins']:<10.1f} {s['wins']:<10.1f} ${s['profit']:<11.1f} ${s['salary']:<11.1f} {recommend:<10}")
    
    print("\n" + "-"*105)
    print("Legend: *** Both Better | ** Better Profit | * Better Wins")
    print("="*105)


def main():
    print("\n" + "="*70)
    print("  NBA 球队方案评估系统 v2")
    print("  Golden State Warriors 2025-26")
    print("  Kuminga Replacement Analysis")
    print("="*70)
    
    # ==========================================
    # 替换分析
    # ==========================================
    print("\n>>> 运行 Kuminga 替换分析...")
    print(f"基准阵容: {cfg.BASE_ROSTER}")
    print(f"被替换球员: {cfg.PLAYER_TO_REPLACE}")
    print(f"候选球员: {list(cfg.REPLACEMENT_CANDIDATES.keys())}")
    
    # 运行替换分析
    results = ev.run_replacement_analysis()
    summary = ev.get_replacement_summary(results)
    
    # 打印基准结果
    baseline = [r for r in results if r["is_baseline"]][0]
    print(f"\n基准方案评估:")
    print(f"  总胜场: {baseline['Total Wins']:.1f}")
    print(f"  净利润: ${baseline['Net Profit']:.1f}M")
    
    # 打印替换对比表
    print_replacement_table(summary)
    
    # 生成可视化
    print("\n>>> 生成可视化图表")
    print("-"*50)
    
    save_dir = cfg.VISUALIZATION["save_path"]
    fig = plot_replacement_scatter(summary, f'{save_dir}kuminga_replacement_analysis.png')
    
    # 决策建议
    print("\n" + "="*70)
    print("  决策建议")
    print("="*70)
    
    # 找出最佳选择
    best_profit = max(summary, key=lambda x: x["profit"])
    best_wins = max(summary, key=lambda x: x["wins"])
    
    # 找出两者都更好的
    baseline_s = [s for s in summary if s["is_baseline"]][0]
    both_better = [s for s in summary 
                   if s["wins"] > baseline_s["wins"] and s["profit"] > baseline_s["profit"]]
    
    print(f"""
    基准 ({cfg.PLAYER_TO_REPLACE}): {baseline_s['wins']:.1f} 胜, ${baseline_s['profit']:.1f}M

    最优选择:
    • 追求利润最大化 → {best_profit['player']} (${best_profit['profit']:.1f}M, {best_profit['wins']:.1f} 胜)
    • 追求胜场最大化 → {best_wins['player']} ({best_wins['wins']:.1f} 胜, ${best_wins['profit']:.1f}M)
    """)
    
    if both_better:
        print("    两项指标均优于基准的选择:")
        for s in sorted(both_better, key=lambda x: x["profit"], reverse=True):
            print(f"      ★ {s['player']}: +{s['diff_wins']:.1f} 胜, +${s['diff_profit']:.1f}M")
    
    plt.show()
    
    return results, summary


if __name__ == "__main__":
    results, summary = main()
