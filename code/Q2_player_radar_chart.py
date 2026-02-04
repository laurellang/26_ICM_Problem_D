# -*- coding: utf-8 -*-
"""
NBA 2K风格 - 球员七维属性雷达图
支持单球员、多球员对比、矩阵布局展示
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 浅色系颜色主题 ====================
COLORS = {
    'background': '#ffffff',       # 白色背景
    'background_card': '#f8fafc',  # 浅灰卡片背景
    'grid': '#e2e8f0',             # 网格线颜色
    'grid_light': '#cbd5e1',       # 浅网格线
    'text': '#1e293b',             # 深色文字
    'text_dim': '#64748b',         # 暗淡文字
    'gold': '#d97706',             # 金色 (高数值) - 深一点更清晰
    'accent': '#2563eb',           # 蓝色强调
    'green': '#16a34a',            # 绿色
    'red': '#dc2626',              # 红色
    'orange': '#ea580c',           # 橙色
    'purple': '#7c3aed',           # 紫色
}

# 多球员配色调色板 (浅色系适配 - 更鲜艳)
PLAYER_COLORS = [
    '#2563eb',  # 蓝色
    '#dc2626',  # 红色
    '#16a34a',  # 绿色
    '#ea580c',  # 橙色
    '#7c3aed',  # 紫色
    '#0891b2',  # 青色
    '#e11d48',  # 玫红色
    '#059669',  # 深绿
    '#d97706',  # 琥珀色
    '#9333ea',  # 深紫
]

# 七维属性标签 (英文标签)
ATTRIBUTE_LABELS = [
    'Outside Scoring',    # 外线投射
    'Inside Scoring',     # 内线终结
    'Playmaking',         # 组织/控球
    'Athleticism',        # 运动天赋
    'Defense',            # 防守
    'Rebounding',         # 篮板
    'Stamina'             # 体能
]
ATTRIBUTE_LABELS_SHORT = ['Outside', 'Inside', 'Playmk', 'Athletic', 'Defense', 'Rebound', 'Stamina']

# 热力图英文标签
HEATMAP_LABELS = ['Outside', 'Inside', 'Playmaking', 'Athletic', 'Defense', 'Rebound', 'Stamina', 'OVR']


def draw_single_radar(ax, data, label=None, color='#58a6ff', fill_alpha=0.25, 
                      line_width=2, show_values=True, value_fontsize=9):
    """在给定的极坐标轴上绘制单个雷达图"""
    
    num_vars = len(data)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    values = list(data) + [data[0]]
    angles += angles[:1]
    
    # 填充区域
    ax.fill(angles, values, color=color, alpha=fill_alpha)
    # 边线
    ax.plot(angles, values, color=color, linewidth=line_width, alpha=0.9)
    ax.plot(angles, values, color='white', linewidth=1, alpha=0.5)
    
    # 数据点
    for i, (angle, val) in enumerate(zip(angles[:-1], values[:-1])):
        ax.scatter(angle, val, s=40, c=color, edgecolors='white', 
                   linewidths=1, zorder=5)
        if show_values:
            # 数值颜色：高分金色，低分红色
            val_color = COLORS['gold'] if val >= 80 else (COLORS['red'] if val < 60 else COLORS['text'])
            ax.annotate(str(int(val)), xy=(angle, val + 7), ha='center', va='center',
                       fontsize=value_fontsize, fontweight='bold', color=val_color)
    
    return ax


def setup_radar_axes(ax, labels=None, max_val=100):
    """设置雷达图的网格和标签"""
    
    if labels is None:
        labels = ATTRIBUTE_LABELS_SHORT
    
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_facecolor(COLORS['background_card'])
    
    # 绘制网格圈
    for val in [25, 50, 75, 99]:
        circle_angles = np.linspace(0, 2 * np.pi, 100)
        ax.plot(circle_angles, [val]*100, color=COLORS['grid_light'], 
                linewidth=0.8, alpha=0.5, linestyle='-')
    
    # 射线
    for angle in angles:
        ax.plot([angle, angle], [0, max_val], color=COLORS['grid_light'], 
                linewidth=0.8, alpha=0.6)
    
    ax.set_xticks(angles)
    ax.set_xticklabels([])  # 清空默认标签，手动放置
    ax.set_yticklabels([])
    ax.set_ylim(0, max_val + 10)
    ax.spines['polar'].set_visible(False)
    
    # 手动放置标签，避免重叠
    label_distance = max_val + 18  # 标签到中心的距离
    for i, (angle, label) in enumerate(zip(angles, labels)):
        # 计算标签位置，某些标签需要额外偏移
        extra_offset = 0
        if 'Playmaking' in label or 'Playmk' in label:
            extra_offset = -5  # 向外偏移（向下移动了5个单位）
        elif 'Rebounding' in label or 'Rebound' in label:
            extra_offset = 15  # 向外偏移
        
        ax.text(angle, label_distance + extra_offset, label, 
                ha='center', va='center', fontsize=17, fontweight='bold',
                color=COLORS['text'])
    
    return ax


def create_matrix_radar(players_df, title=None, cols=4, figsize=None,
                        save_path=None, show_overall=True):
    """
    创建矩阵布局的多球员雷达图
    
    参数:
    - players_df: DataFrame, 包含球员数据
    - title: str, 图表标题 (可选，默认无标题)
    - cols: int, 每行显示的球员数
    - figsize: tuple, 图表大小
    - save_path: str, 保存路径
    - show_overall: bool, 是否显示总评
    """
    
    n_players = len(players_df)
    rows = (n_players + cols - 1) // cols
    
    if figsize is None:
        figsize = (cols * 4, rows * 4.2)
    
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(COLORS['background'])
    
    for idx, (_, row) in enumerate(players_df.iterrows()):
        # 提取数据
        player_name = row['球员名']
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        overall = row.get('总评', None)
        
        # 创建子图
        ax = fig.add_subplot(rows, cols, idx + 1, polar=True)
        setup_radar_axes(ax)
        
        # 根据总评选择颜色
        if overall and overall >= 82:
            color = COLORS['gold']
        elif overall and overall >= 80:
            color = COLORS['accent']
        else:
            color = COLORS['green']
        
        draw_single_radar(ax, data, color=color, show_values=True, value_fontsize=8)
        
        # 球员名字 - 使用英文名
        en_name = player_name.split('(')[1].rstrip(')') if '(' in player_name else player_name
        ax.set_title(en_name, fontsize=11, fontweight='bold', 
                    color=COLORS['text'], pad=20)
        
        # 总评标签
        if show_overall and overall:
            rating_color = COLORS['gold'] if overall >= 82 else COLORS['accent']
            ax.text(0.5, 0.5, str(int(overall)), transform=ax.transAxes,
                   ha='center', va='center', fontsize=18, fontweight='bold',
                   color=rating_color,
                   bbox=dict(boxstyle='circle,pad=0.3', facecolor=COLORS['background'],
                            edgecolor=rating_color, linewidth=2))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight',
                   facecolor=COLORS['background'], edgecolor='none')
        print(f"矩阵雷达图已保存: {save_path}")
    
    return fig


def create_overlay_comparison(players_df, title=None, figsize=(12, 10),
                              save_path=None, max_players=8):
    """
    创建叠加式多球员对比雷达图
    
    参数:
    - players_df: DataFrame, 包含球员数据
    - title: str, 图表标题 (可选)
    - figsize: tuple, 图表大小
    - save_path: str, 保存路径
    - max_players: int, 最多显示的球员数
    """
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(COLORS['background'])
    
    setup_radar_axes(ax, labels=ATTRIBUTE_LABELS)
    
    num_vars = 7
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    legend_handles = []
    
    for idx, (_, row) in enumerate(players_df.head(max_players).iterrows()):
        player_name = row['球员名']
        short_name = player_name.split('(')[0].strip() if '(' in player_name else player_name
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        values = data + [data[0]]
        
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        
        # 填充
        ax.fill(angles, values, color=color, alpha=0.1)
        # 线条
        line, = ax.plot(angles, values, color=color, linewidth=2.5, alpha=0.9)
        # 数据点
        ax.scatter(angles[:-1], values[:-1], s=50, c=color, 
                   edgecolors='white', linewidths=1, zorder=5)
        
        overall = row.get('总评', '')
        label = f"{short_name} ({overall})" if overall else short_name
        legend_handles.append(Line2D([0], [0], color=color, linewidth=3, label=label))
    
    # 图例
    legend = ax.legend(handles=legend_handles, loc='upper left', 
                      bbox_to_anchor=(1.05, 1.0),
                      fontsize=14, frameon=True, 
                      facecolor=COLORS['background_card'],
                      edgecolor=COLORS['grid_light'], 
                      labelcolor=COLORS['text'])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight',
                   facecolor=COLORS['background'], edgecolor='none')
        print(f"叠加对比图已保存: {save_path}")
    
    return fig, ax


def create_heatmap_comparison(players_df, title=None, figsize=(14, 10),
                              save_path=None):
    """
    创建热力图样式的球员属性对比
    
    参数:
    - players_df: DataFrame, 包含球员数据
    - title: str, 图表标题 (可选)
    - figsize: tuple, 图表大小
    - save_path: str, 保存路径
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    # 准备数据
    attributes_cn = ['外线得分', '内线得分', '组织能力', '运动能力', '防守', '篮板', '体能', '总评']
    player_names = [name.split('(')[1].rstrip(')') if '(' in name else name 
                    for name in players_df['球员名']]
    
    data = players_df[attributes_cn].values
    
    # 创建热力图
    from matplotlib.colors import LinearSegmentedColormap
    
    # 蓝红色系：低分蓝色 → 高分红色
    colors_cmap = ['#1e3a5f', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',  # 蓝色系 (低)
                   '#d1d5db',                                              # 灰色 (中)
                   '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c']  # 红色系 (高)
    cmap = LinearSegmentedColormap.from_list('blue_red', colors_cmap, N=256)
    
    im = ax.imshow(data, cmap=cmap, aspect='auto', vmin=45, vmax=95)
    
    # 设置刻度 - 使用英文标签
    ax.set_xticks(np.arange(len(HEATMAP_LABELS)))
    ax.set_yticks(np.arange(len(player_names)))
    ax.set_xticklabels(HEATMAP_LABELS, fontsize=11, fontweight='bold', color=COLORS['text'])
    ax.set_yticklabels(player_names, fontsize=10, color=COLORS['text'])
    
    # 在每个格子中显示数值
    for i in range(len(player_names)):
        for j in range(len(attributes_cn)):
            val = data[i, j]
            # 根据数值选择文字颜色：深色背景用白字
            text_color = 'white' #if val < 68 or val > 78 else 'black'
            ax.text(j, i, str(int(val)), ha='center', va='center',
                   fontsize=12, fontweight='bold', color=text_color)
    
    # 网格线
    ax.set_xticks(np.arange(len(HEATMAP_LABELS) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(player_names) + 1) - 0.5, minor=True)
    ax.grid(which='minor', color=COLORS['grid'], linewidth=1)
    ax.tick_params(which='minor', size=0)
    
    # 颜色条
    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.ax.tick_params(colors=COLORS['text'])
    cbar.set_label('Rating', color=COLORS['text'], fontsize=11)
    
    # 移除边框
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight',
                   facecolor=COLORS['background'], edgecolor='none')
        print(f"热力图已保存: {save_path}")
    
    return fig, ax


def create_comprehensive_dashboard(df1, df2, title1=None, title2=None,
                                   figsize=(20, 16), save_path=None):
    """
    创建综合仪表板：包含两组球员的对比
    
    参数:
    - df1, df2: DataFrame, 两组球员数据
    - title1, title2: str, 两组标题 (可选)
    - figsize: tuple, 图表大小
    - save_path: str, 保存路径
    """
    
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(COLORS['background'])
    
    # 使用GridSpec创建复杂布局
    gs = GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.3)
    
    # ===== 左半部分: 第一组球员 =====
    ax_radar1 = fig.add_subplot(gs[0:3, 0:2], polar=True)
    setup_radar_axes(ax_radar1, labels=ATTRIBUTE_LABELS_SHORT)
    
    num_vars = 7
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    for idx, (_, row) in enumerate(df1.iterrows()):
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        values = data + [data[0]]
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        ax_radar1.fill(angles, values, color=color, alpha=0.1)
        ax_radar1.plot(angles, values, color=color, linewidth=2, alpha=0.8)
    
    # ===== 右半部分: 第二组球员 =====
    ax_radar2 = fig.add_subplot(gs[0:3, 2:4], polar=True)
    setup_radar_axes(ax_radar2, labels=ATTRIBUTE_LABELS_SHORT)
    
    for idx, (_, row) in enumerate(df2.iterrows()):
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        values = data + [data[0]]
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        ax_radar2.fill(angles, values, color=color, alpha=0.1)
        ax_radar2.plot(angles, values, color=color, linewidth=2, alpha=0.8)
    
    # ===== 底部: 热力图对比 =====
    ax_heat = fig.add_subplot(gs[3, :])
    ax_heat.set_facecolor(COLORS['background'])
    
    # 合并两组数据
    all_players = pd.concat([df1, df2], ignore_index=True)
    attributes_cn = ['外线得分', '内线得分', '组织能力', '运动能力', '防守', '篮板', '体能', '总评']
    player_names = [name.split('(')[1].rstrip(')')[:12] if '(' in name else name[:12] 
                    for name in all_players['球员名']]
    data = all_players[attributes_cn].values
    
    from matplotlib.colors import LinearSegmentedColormap
    colors_cmap = ['#1e3a5f', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                   '#d1d5db',
                   '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c']
    cmap = LinearSegmentedColormap.from_list('blue_red', colors_cmap, N=256)
    
    im = ax_heat.imshow(data, cmap=cmap, aspect='auto', vmin=45, vmax=95)
    ax_heat.set_xticks(np.arange(len(HEATMAP_LABELS)))
    ax_heat.set_yticks(np.arange(len(player_names)))
    ax_heat.set_xticklabels(HEATMAP_LABELS, fontsize=10, fontweight='bold', color=COLORS['text'])
    ax_heat.set_yticklabels(player_names, fontsize=9, color=COLORS['text'])
    
    for i in range(len(player_names)):
        for j in range(len(attributes_cn)):
            val = data[i, j]
            text_color = 'white' #if val < 68 or val > 78 else 'black'
            ax_heat.text(j, i, str(int(val)), ha='center', va='center',
                        fontsize=11, fontweight='bold', color=text_color)
    
    ax_heat.set_xticks(np.arange(len(HEATMAP_LABELS) + 1) - 0.5, minor=True)
    ax_heat.set_yticks(np.arange(len(player_names) + 1) - 0.5, minor=True)
    ax_heat.grid(which='minor', color=COLORS['grid'], linewidth=1)
    ax_heat.tick_params(which='minor', size=0)
    
    # 分隔线（区分两组）
    ax_heat.axhline(y=len(df1) - 0.5, color=COLORS['accent'], linewidth=3, linestyle='-')
    
    for spine in ax_heat.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight',
                   facecolor=COLORS['background'], edgecolor='none')
        print(f"综合仪表板已保存: {save_path}")
    
    return fig


def create_side_by_side_radar(df1, df2, title1=None, title2=None,
                              figsize=(20, 11), save_path=None):
    """
    创建并排双组对比雷达图 (推荐方案)
    
    左右各一组球员，每组叠加显示
    """
    
    fig, axes = plt.subplots(1, 2, figsize=figsize, subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(COLORS['background'])
    
    num_vars = 7
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    # ===== 左图: 第一组 =====
    ax1 = axes[0]
    setup_radar_axes(ax1, labels=ATTRIBUTE_LABELS)
    
    legend_handles1 = []
    for idx, (_, row) in enumerate(df1.iterrows()):
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        values = data + [data[0]]
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        
        ax1.fill(angles, values, color=color, alpha=0.12)
        ax1.plot(angles, values, color=color, linewidth=2.5, alpha=0.9)
        ax1.scatter(angles[:-1], values[:-1], s=40, c=color, 
                   edgecolors='white', linewidths=1, zorder=5)
        
        # 使用英文名
        en_name = row['球员名'].split('(')[1].rstrip(')') if '(' in row['球员名'] else row['球员名']
        overall = row.get('总评', '')
        label = f"{en_name} ({overall})"
        legend_handles1.append(Line2D([0], [0], color=color, linewidth=3, 
                                      marker='o', markersize=6, label=label))
    
    # ===== 右图: 第二组 =====
    ax2 = axes[1]
    setup_radar_axes(ax2, labels=ATTRIBUTE_LABELS)
    
    legend_handles2 = []
    for idx, (_, row) in enumerate(df2.iterrows()):
        data = [row['外线得分'], row['内线得分'], row['组织能力'], 
                row['运动能力'], row['防守'], row['篮板'], row['体能']]
        values = data + [data[0]]
        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        
        ax2.fill(angles, values, color=color, alpha=0.12)
        ax2.plot(angles, values, color=color, linewidth=2.5, alpha=0.9)
        ax2.scatter(angles[:-1], values[:-1], s=40, c=color, 
                   edgecolors='white', linewidths=1, zorder=5)
        
        # 使用英文名
        en_name = row['球员名'].split('(')[1].rstrip(')') if '(' in row['球员名'] else row['球员名']
        overall = row.get('总评', '')
        label = f"{en_name} ({overall})"
        legend_handles2.append(Line2D([0], [0], color=color, linewidth=3, 
                                      marker='o', markersize=6, label=label))
    
    # ===== 合并图例，放在正中间（两个雷达图之间） =====
    all_handles = legend_handles1 + legend_handles2
    fig.legend(handles=all_handles, loc='center', bbox_to_anchor=(0.5, 0.9),
              fontsize=9, frameon=True, facecolor=COLORS['background_card'],
              edgecolor=COLORS['grid_light'], labelcolor=COLORS['text'], 
              ncol=2, columnspacing=1.0, handlelength=1.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight',
                   facecolor=COLORS['background'], edgecolor='none')
        print(f"并排对比图已保存: {save_path}")
    
    return fig, axes


# ==================== 主程序 ====================
if __name__ == "__main__":
    
    print("=" * 70)
    print("NBA 2K风格 - 球员七维属性雷达图")
    print("=" * 70)
    
    # 读取数据
    df_salary = pd.read_excel('【引进】薪资适合.xlsx')
    df_wing = pd.read_excel('【引进】锋线.xlsx')
    
    print(f"\n加载数据:")
    print(f"  - 薪资适合球员: {len(df_salary)} 人")
    print(f"  - 锋线候选球员: {len(df_wing)} 人")
    
    # ===== 方案1: 矩阵布局 - 每人一个小雷达图 =====
    print("\n>>> 生成方案1: 矩阵布局雷达图")
    
    fig1 = create_matrix_radar(
        df_salary, 
        cols=4,
        save_path='radar_matrix_salary.png'
    )
    
    fig2 = create_matrix_radar(
        df_wing, 
        cols=4,
        save_path='radar_matrix_wing.png'
    )
    
    # ===== 方案2: 并排叠加对比 =====
    print("\n>>> 生成方案2: 并排叠加对比图")
    
    fig3, _ = create_side_by_side_radar(
        df_salary, df_wing,
        save_path='radar_side_by_side.png'
    )
    
    # ===== 方案3: 热力图 =====
    print("\n>>> 生成方案3: 属性热力图")
    
    all_players = pd.concat([df_salary, df_wing], ignore_index=True)
    fig4, _ = create_heatmap_comparison(
        all_players,
        save_path='radar_heatmap_all.png'
    )
    
    print("\n" + "=" * 70)
    print("所有图表生成完成!")
    print("=" * 70)
    print("\n生成的文件:")
    print("  1. radar_matrix_salary.png - 薪资适合球员矩阵图")
    print("  2. radar_matrix_wing.png   - 锋线候选球员矩阵图")
    print("  3. radar_side_by_side.png  - 两组并排对比图")
    print("  4. radar_heatmap_all.png   - 全员属性热力图")
    
    plt.show()
