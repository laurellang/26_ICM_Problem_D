# -*- coding: utf-8 -*-
"""
配置文件 - NBA球队方案评估系统
所有可调参数集中管理
"""

# ==========================================
# 1. 勇士队当前球员数据库 (来自【球星conf】勇士.xlsx)
# ==========================================
WARRIORS_ROSTER = {
    "S. Curry": {
        "Salary": 59.61,      # 薪资 (百万美元)
        "WS": 7.2,            # 赛季至今累积贡献 (依然全队最高)
        "OVR": 95,            # 总评
        "Star_Index": 1.0,    # 商业号召力
    },
    "J. Butler": {
        "Salary": 54.13,
        "WS": 6.0,            # 攻守平衡，WS 产出极高
        "OVR": 88,
        "Star_Index": 0.1754,
    },
    "D. Green": {
        "Salary": 25.89,
        "WS": 3.4,            # 虽数据不显，但 DWS (防守贡献) 稳健
        "OVR": 79,
        "Star_Index": 0.0719,
    },
    "J. Kuminga": {
        "Salary": 22.50,
        "WS": 2.8,            # 状态波动，但进攻效率提升了 OWS
        "OVR": 78,
        "Star_Index": 0.0105,
    },
    "M. Moody": {
        "Salary": 11.57,
        "WS": 3.1,            # 职业生涯年，WS 产出显著增加
        "OVR": 78,
        "Star_Index": 0.0044,
    },
    "B. Hield": {
        "Salary": 9.22,
        "WS": 2.6,            # 空间拉开者，主要贡献在进攻端
        "OVR": 76,
        "Star_Index": 0.0158,
    },
    "G. Payton II": {
        "Salary": 9.13,
        "WS": 1.5,            # 受限于出场时间，但单位时间 DWS 很高
        "OVR": 75,
        "Star_Index": 0.0123,
    },
    "A. Horford": {
        "Salary": 5.69,
        "WS": 2.2,            # 空间型内线，WS/48 表现出色
        "OVR": 78,
        "Star_Index": 0.0193,
    },
    "B. Podziemski": {
        "Salary": 3.69,
        "WS": 2.4,            # 全能表现，篮板和助攻带来加成
        "OVR": 79,
        "Star_Index": 0.0053,
    },
    "S. Curry (Seth)": {
        "Salary": 3.30,
        "WS": 1.1,            # 作为替补火力的补充
        "OVR": 74,
        "Star_Index": 0.0351,
    },
    "D. Melton": {
        "Salary": 3.08,
        "WS": 1.4,            # 外线防守锁匠
        "OVR": 78,
        "Star_Index": 0.0026,
    },
    "T. Jackson-Davis": {
        "Salary": 2.22,
        "WS": 1.9,            # 护筐和吃饼带来的高效率 WS
        "OVR": 73,
        "Star_Index": 0.0018,
    },
    "G. Santos": {
        "Salary": 2.22,
        "WS": 0.6,
        "OVR": 72,
        "Star_Index": 0.0026,
    },
    "Q. Post": {
        "Salary": 1.16,
        "WS": 0.5,
        "OVR": 76,
        "Star_Index": 0.0005,
    },
    "W. Richard": {
        "Salary": 1.16,
        "WS": 0.4,
        "OVR": 76,
        "Star_Index": 0.0004,
    },
}

# ==========================================
# 2. 替换候选球员 (来自【球星conf】替换.xlsx)
# 用于替换 J. Kuminga 的 8 个候选人
# ==========================================
REPLACEMENT_CANDIDATES = {
    "T. Herro": {
        "Salary": 31.00,
        "WS": 4.8,
        "OVR": 84,
        "Star_Index": 0.0421,
    },
    "A. Wiggins": {
        "Salary": 28.22,
        "WS": 3.1,
        "OVR": 79,
        "Star_Index": 0.0333,
    },
    "K. Porzingis": {
        "Salary": 30.73,
        "WS": 5.2,
        "OVR": 87,
        "Star_Index": 0.0298,
    },
    "R. Barrett": {
        "Salary": 27.70,
        "WS": 3.6,
        "OVR": 83,
        "Star_Index": 0.0263,
    },
    "M. Porter Jr.": {
        "Salary": 38.33,
        "WS": 5.5,
        "OVR": 85,
        "Star_Index": 0.0193,
    },
    "M. Bridges": {
        "Salary": 23.50,
        "WS": 5.8,
        "OVR": 81,
        "Star_Index": 0.0193,
    },
    "T. Harris": {
        "Salary": 26.00,
        "WS": 3.2,
        "OVR": 79,
        "Star_Index": 0.0105,
    },
    "D. Hunter": {
        "Salary": 23.30,
        "WS": 2.1,
        "OVR": 79,
        "Star_Index": 0.0035,
    },
}

# ==========================================
# 3. 球员化学反应 (Chemistry Bonus)
# 格式: (球员1, 球员2): Bonus WS
# 当两名球员同时在队时，额外增加 Bonus WS
# ==========================================
CHEMISTRY_PAIRS = {
    ("S. Curry", "D. Green"): 1.5,            # 库里+格林: 多年默契搭档 (Curry removed)
    ("J. Kuminga", "M. Moody"): 0.8,          # 库明加+穆迪: 新秀组合
    ("B. Podziemski", "T. Jackson-Davis"): 0.6,  # 波杰+TJD: 新人搭档
}

# ==========================================
# 4. 基础阵容定义 (用于替换比较)
# ==========================================
BASE_ROSTER = [
    "S. Curry",  # Removed - analyzing team without Curry
    "J. Butler", 
    "D. Green",
    "B. Podziemski",
    "M. Moody",
    "T. Jackson-Davis",
    "B. Hield",
]

# 被替换的球员
PLAYER_TO_REPLACE = "J. Kuminga"

# ==========================================
# 5. 财务参数
# ==========================================
FINANCIAL_PARAMS = {
    # 成本
    "fixed_cost": 210.0,              # 固定成本 (百万美元)
    "luxury_tax_threshold": 187.9,    # 奢侈税线 (百万美元)
    
    # 收入参数
    "base_league_revenue": 180.0,       # 仅限全国转播分成 (新合同生效后跳升)
    "base_gate_revenue": 210.0,         # 基础门票收入 
    "win_gate_multiplier": 1.2,         # 边际胜场增益 
    "star_gate_multiplier": 120.0,      # 球星指数 
    "playoff_round_revenue": 35.0,      # 每轮季后赛收入 
    "arena_revenue": 320.0,             # 场馆非篮球收入 
    "revenue_sharing_rate": 0.25,       # 联盟收入分成比例 (固定比例)
    
    # 奢侈税阶梯 (重复受罚者)
    "tax_brackets": [
        (5, 2.50),   # 0-5M
        (5, 2.75),   # 5-10M
        (5, 3.50),   # 10-15M
        (5, 4.25),   # 15-20M
        (999, 4.75)  # 20M+
    ]
}

# ==========================================
# 6. 常规赛参数
# ==========================================
REGULAR_SEASON = {
    "total_games": 82,                # 常规赛总场次
    "base_wins": 9,                   # 基础胜场 (调整: 使 Kuminga 总胜场约 48)
}

# ==========================================
# 7. 季后赛参数
# ==========================================
PLAYOFF_PARAMS = {
    # 进入条件 (所有阈值 -20 以保持相对关系)
    "direct_entry_wins": 28,          # 直通季后赛胜场 (原48-20)
    "playin_min_wins": 20,            # 附加赛最低胜场 (原40-20)
    "playin_prob_per_win": 0.125,     # 附加赛每胜增加的进入概率
    
    # 轮数判定 (胜场阈值 -20, OVR下限不变, 轮数不变)
    "round_thresholds": [
        (38, 92, 4),    # >38胜, OVR>92: 总决赛 (原58-20)
        (33, 88, 3),    # 33-38胜, OVR 88-92: 分区决赛 (原53-20)
        (28, 85, 2),    # 28-32胜, OVR 85-88: 1-2轮 (原48-20)
        (20, 0, 0.5),   # 20-27胜: 附加赛 (原40-20)
    ],
    
    # 场次计算
    "avg_games_per_round": 5.8,       # 每轮平均场次
    "home_bonus_high_seed": 0.5,      # 高种子主场加成
    
    # 胜率计算
    "base_win_prob": 0.5,             # 基础胜率
    "ovr_diff_factor": 0.05,          # OVR差异对胜率的影响
    "avg_opponent_ovr": 85,           # 假设对手平均OVR
}

# ==========================================
# 8. 可视化参数
# ==========================================
VISUALIZATION = {
    "colors": {
        # 亮色系配色
        "plan_a": "#3b82f6",      # 蓝色
        "plan_b": "#22c55e",      # 绿色
        "accent": "#f59e0b",      # 橙色
        "background": "#ffffff",  # 白色背景
        "text": "#1e293b",        # 深灰色文字
        "grid": "#e2e8f0",        # 浅灰色网格线
        "good": "#10b981",        # 绿色 
        "bad": "#ef4444",         # 红色 
        "highlight": "#f59e0b"    # 橙色 
    },
    "figure_dpi": 300,            # 提高DPI
    "save_path": "figures/Q2/"
}
