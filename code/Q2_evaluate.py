# -*- coding: utf-8 -*-
"""
NBA 球队方案评估模块 v2
核心输出: 预期胜场 + 净利润
"""

import pandas as pd
import numpy as np

# 导入配置
from Q2_config import (
    WARRIORS_ROSTER,
    REPLACEMENT_CANDIDATES,
    BASE_ROSTER,
    PLAYER_TO_REPLACE,
    CHEMISTRY_PAIRS,
    FINANCIAL_PARAMS,
    REGULAR_SEASON,
    PLAYOFF_PARAMS
)

# ==========================================
# 1. 数据加载
# ==========================================
def get_player_database():
    """从配置文件加载球员数据库 (勇士 + 替换候选)"""
    players = []
    
    # 加载勇士阵容
    for name, stats in WARRIORS_ROSTER.items():
        players.append({
            "Player": name,
            "Salary": stats["Salary"],
            "WS": stats["WS"],
            "OVR": stats["OVR"],
            "Star_Index": stats["Star_Index"],
        })
    
    # 加载替换候选
    for name, stats in REPLACEMENT_CANDIDATES.items():
        players.append({
            "Player": name,
            "Salary": stats["Salary"],
            "WS": stats["WS"],
            "OVR": stats["OVR"],
            "Star_Index": stats["Star_Index"],
        })
    
    return pd.DataFrame(players)

df_players = get_player_database()

# 基准阵容 (包含库明加)
baseline_roster = BASE_ROSTER + [PLAYER_TO_REPLACE]

# ==========================================
# 2. 化学反应计算 (加法Bonus)
# ==========================================
def calculate_chemistry_ws(selected_players):
    """
    计算考虑化学反应后的总WS
    
    对于有化学反应的配对，额外增加固定的Bonus WS
    
    返回: (总WS, 化学反应加成详情)
    """
    player_set = set(selected_players)
    total_ws = 0
    chemistry_details = []
    
    # 1. 计算基础WS
    for player in selected_players:
        ws = df_players[df_players['Player'] == player]['WS'].values[0]
        total_ws += ws
        
    # 2. 计算化学反应Bonus
    for (p1, p2), bonus in CHEMISTRY_PAIRS.items():
        if p1 in player_set and p2 in player_set:
            total_ws += bonus
            
            chemistry_details.append({
                "pair": (p1, p2),
                "bonus": bonus
            })
    
    return total_ws, chemistry_details


# ==========================================
# 3. 常规赛胜场计算
# ==========================================
def calculate_regular_season_wins(selected_players):
    """
    计算常规赛预期胜场
    
    公式: W_reg = Base_Wins + Σ(WS with Chemistry)
    """
    total_ws, chem_details = calculate_chemistry_ws(selected_players)
    wins = REGULAR_SEASON["base_wins"] + total_ws
    
    # 限制在合理范围 (0-82)
    wins = max(0, min(82, wins))
    
    return wins, total_ws, chem_details


# ==========================================
# 4. 季后赛判定与计算
# ==========================================
def get_team_core_ovr(selected_players, top_n=3):
    """获取核心球员平均OVR (前N高)"""
    ovrs = []
    for player in selected_players:
        player_data = df_players[df_players['Player'] == player]
        if len(player_data) > 0:
            ovrs.append(player_data['OVR'].values[0])
    
    ovrs.sort(reverse=True)
    return np.mean(ovrs[:top_n]) if len(ovrs) >= top_n else np.mean(ovrs)


def calculate_playoff_entry_prob(regular_wins):
    """计算进入季后赛的概率"""
    params = PLAYOFF_PARAMS
    
    if regular_wins >= params["direct_entry_wins"]:
        return 1.0  # 直通
    elif regular_wins >= params["playin_min_wins"]:
        # 附加赛概率
        return (regular_wins - params["playin_min_wins"]) * params["playin_prob_per_win"]
    else:
        return 0.0  # 无缘


def calculate_playoff_rounds(regular_wins, core_ovr):
    """计算预期季后赛轮数"""
    params = PLAYOFF_PARAMS
    
    for (win_threshold, ovr_threshold, rounds) in params["round_thresholds"]:
        if regular_wins >= win_threshold and core_ovr >= ovr_threshold:
            return rounds
    
    return 0


def calculate_playoff_wins(playoff_rounds, team_ovr):
    """
    计算季后赛预期胜场
    
    每轮胜率: P_win = 0.5 + (OVR_team - OVR_opp) × 0.05
    每轮期望场次: ~5.8
    胜场 = 期望场次 × 胜率 × 轮数
    """
    if playoff_rounds <= 0:
        return 0, 0
    
    params = PLAYOFF_PARAMS
    
    # 计算胜率
    ovr_diff = team_ovr - params["avg_opponent_ovr"]
    win_prob = params["base_win_prob"] + ovr_diff * params["ovr_diff_factor"]
    win_prob = max(0.3, min(0.8, win_prob))  # 限制在合理范围
    
    # 计算场次和胜场
    total_games = playoff_rounds * params["avg_games_per_round"]
    playoff_wins = total_games * win_prob
    
    return playoff_wins, total_games


# ==========================================
# 5. 收入计算
# ==========================================
def calculate_revenue(total_wins, star_index, playoff_rounds):
    """
    计算总收入
    
    收入 = 基础收入 + 门票收入 + 季后赛收入 + 场馆收入 - 联盟分成
    """
    params = FINANCIAL_PARAMS
    
    # 1. 基础保障收入 (联盟转播分成)
    base_rev = params["base_league_revenue"]
    
    # 2. 门票收入 (受胜场和球星影响)
    gate_rev = (params["base_gate_revenue"] + 
                total_wins * params["win_gate_multiplier"] + 
                star_index * params["star_gate_multiplier"])
    
    # 3. 季后赛收入
    playoff_rev = playoff_rounds * params["playoff_round_revenue"]
    
    # 4. 场馆非篮球收入
    arena_rev = params["arena_revenue"]
    
    # 5. 总收入
    total_rev = base_rev + gate_rev + playoff_rev + arena_rev
    
    # 6. 扣除联盟收入分成
    sharing_out = (gate_rev + arena_rev) * params["revenue_sharing_rate"]
    
    return total_rev - sharing_out, {
        "base": base_rev,
        "gate": gate_rev,
        "playoff": playoff_rev,
        "arena": arena_rev,
        "sharing": sharing_out
    }


# ==========================================
# 6. 成本计算
# ==========================================
def calculate_luxury_tax(total_salary):
    """计算奢侈税"""
    params = FINANCIAL_PARAMS
    threshold = params["luxury_tax_threshold"]
    
    if total_salary <= threshold:
        return 0
    
    over = total_salary - threshold
    tax = 0
    
    for size, rate in params["tax_brackets"]:
        if over <= 0:
            break
        chunk = min(over, size)
        tax += chunk * rate
        over -= size
    
    return tax


def calculate_costs(selected_players):
    """
    计算总成本
    
    成本 = 固定成本 + 球员工资 + 奢侈税
    """
    params = FINANCIAL_PARAMS
    
    # 固定成本
    fixed_cost = params["fixed_cost"]
    
    # 球员工资
    total_salary = 0
    for player in selected_players:
        player_data = df_players[df_players['Player'] == player]
        if len(player_data) > 0:
            total_salary += player_data['Salary'].values[0]
    
    # 奢侈税
    luxury_tax = calculate_luxury_tax(total_salary)
    
    return fixed_cost + total_salary + luxury_tax, {
        "fixed": fixed_cost,
        "salary": total_salary,
        "tax": luxury_tax
    }


# ==========================================
# 7. 核心评估函数
# ==========================================
def evaluate_scenario(selected_players):
    """
    完整评估阵容方案
    
    输出:
    - 预期总胜场 (常规赛 + 季后赛)
    - 净利润 (总收入 - 总成本)
    - 详细分解
    """
    # 1. 常规赛胜场
    regular_wins, total_ws, chem_details = calculate_regular_season_wins(selected_players)
    
    # 2. 球队核心数据
    core_ovr = get_team_core_ovr(selected_players)
    star_index = sum(
        df_players[df_players['Player'] == p]['Star_Index'].values[0] 
        for p in selected_players 
        if len(df_players[df_players['Player'] == p]) > 0
    )
    
    # 3. 季后赛判定
    playoff_entry_prob = calculate_playoff_entry_prob(regular_wins)
    playoff_rounds = calculate_playoff_rounds(regular_wins, core_ovr) * playoff_entry_prob
    playoff_wins, playoff_games = calculate_playoff_wins(playoff_rounds, core_ovr)
    
    # 4. 总胜场
    total_wins = regular_wins + playoff_wins
    
    # 5. 收入
    revenue, rev_breakdown = calculate_revenue(total_wins, star_index, playoff_rounds)
    
    # 6. 成本
    costs, cost_breakdown = calculate_costs(selected_players)
    
    # 7. 净利润
    net_profit = revenue - costs
    
    return {
        # 核心输出
        "Total Wins": round(total_wins, 1),
        "Net Profit": round(net_profit, 2),
        
        # 胜场分解
        "Regular Wins": round(regular_wins, 1),
        "Playoff Wins": round(playoff_wins, 1),
        "Playoff Rounds": round(playoff_rounds, 2),
        "Playoff Entry Prob": round(playoff_entry_prob, 2),
        
        # 财务分解
        "Revenue": round(revenue, 2),
        "Costs": round(costs, 2),
        "Revenue Breakdown": rev_breakdown,
        "Cost Breakdown": cost_breakdown,
        
        # 球队数据
        "Core OVR": round(core_ovr, 1),
        "Star Index": round(star_index, 2),
        "Total WS": round(total_ws, 2),
        "Chemistry Details": chem_details
    }


# ==========================================
# 8. 简化输出函数
# ==========================================
def quick_evaluate(selected_players):
    """简化评估 - 只返回两个核心指标"""
    result = evaluate_scenario(selected_players)
    return {
        "Wins": result["Total Wins"],
        "Profit": result["Net Profit"]
    }


# ==========================================
# 9. 替换分析
# ==========================================
def run_replacement_analysis():
    """
    运行替换分析 - 比较用不同球员替换 Kuminga 的效果
    
    返回:
    - results: 包含所有替换方案评估结果的列表
    """
    results = []
    
    # 1. 评估基准 (保留 Kuminga)
    baseline = evaluate_scenario(baseline_roster)
    baseline["player"] = PLAYER_TO_REPLACE
    baseline["is_baseline"] = True
    baseline["salary"] = WARRIORS_ROSTER[PLAYER_TO_REPLACE]["Salary"]
    results.append(baseline)
    
    # 2. 评估每个替换候选
    for candidate, stats in REPLACEMENT_CANDIDATES.items():
        new_roster = BASE_ROSTER + [candidate]
        result = evaluate_scenario(new_roster)
        result["player"] = candidate
        result["is_baseline"] = False
        result["salary"] = stats["Salary"]
        results.append(result)
    
    return results


def get_replacement_summary(results):
    """生成替换分析摘要"""
    baseline = [r for r in results if r["is_baseline"]][0]
    
    summary = []
    for r in results:
        diff_wins = r["Total Wins"] - baseline["Total Wins"]
        diff_profit = r["Net Profit"] - baseline["Net Profit"]
        
        summary.append({
            "player": r["player"],
            "wins": r["Total Wins"],
            "regular_wins": r["Regular Wins"],
            "playoff_wins": r["Playoff Wins"],
            "profit": r["Net Profit"],
            "salary": r["salary"],
            "diff_wins": diff_wins,
            "diff_profit": diff_profit,
            "is_baseline": r["is_baseline"],
            "core_ovr": r["Core OVR"],
            "playoff_rounds": r["Playoff Rounds"],
        })
    
    return summary
