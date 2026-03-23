#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Token 使用統計 - 追蹤 Ollama vs Anthropic 的使用量和節省"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

STATS_FILE = Path(__file__).parent.parent / "token_tracker.json"

def load_stats():
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {
        "created": datetime.now().strftime('%Y-%m-%d'),
        "daily_stats": {},
        "ollama_total": {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0},
        "anthropic_saved": {"estimated_tokens": 0, "estimated_cost_usd": 0},
    }

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

def record_ollama_usage(prompt_tokens, completion_tokens, task_name="unknown"):
    """記錄一次 Ollama 使用"""
    stats = load_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 更新總量
    stats['ollama_total']['requests'] += 1
    stats['ollama_total']['prompt_tokens'] += prompt_tokens
    stats['ollama_total']['completion_tokens'] += completion_tokens
    
    # 更新每日統計
    if today not in stats.get('daily_stats', {}):
        stats['daily_stats'] = stats.get('daily_stats', {})
        stats['daily_stats'][today] = {
            'ollama_requests': 0,
            'ollama_tokens': 0,
            'anthropic_requests': 0,
            'anthropic_tokens': 0,
        }
    
    stats['daily_stats'][today]['ollama_requests'] += 1
    stats['daily_stats'][today]['ollama_tokens'] += prompt_tokens + completion_tokens
    
    # 計算省了多少 Anthropic token 費用
    total_tokens = prompt_tokens + completion_tokens
    cost_if_opus = total_tokens / 1_000_000 * 30  # Opus ~$30/1M tokens
    
    stats['anthropic_saved']['estimated_tokens'] += total_tokens
    stats['anthropic_saved']['estimated_cost_usd'] = round(
        stats['anthropic_saved']['estimated_cost_usd'] + cost_if_opus, 4
    )
    
    save_stats(stats)
    return total_tokens, cost_if_opus

def query_ollama(prompt, model="llama3.2"):
    """用 Ollama 執行查詢並記錄 token"""
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        data = resp.json()
        
        prompt_tokens = data.get('prompt_eval_count', 0)
        completion_tokens = data.get('eval_count', 0)
        response_text = data.get('response', '')
        
        # 記錄使用量
        record_ollama_usage(prompt_tokens, completion_tokens)
        
        return {
            'response': response_text,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'duration_s': data.get('total_duration', 0) / 1e9,
        }
    except Exception as e:
        return {'error': str(e)}

def get_summary():
    """取得使用統計摘要"""
    stats = load_stats()
    
    total_ollama_tokens = stats['ollama_total']['prompt_tokens'] + stats['ollama_total']['completion_tokens']
    saved_usd = stats['anthropic_saved']['estimated_cost_usd']
    
    # 計算每日平均
    daily = stats.get('daily_stats', {})
    days = len(daily) or 1
    avg_daily_tokens = total_ollama_tokens / days
    
    # 預估月省
    monthly_tokens = avg_daily_tokens * 30
    monthly_savings = monthly_tokens / 1_000_000 * 30
    
    return {
        'total_requests': stats['ollama_total']['requests'],
        'total_tokens': total_ollama_tokens,
        'total_saved_usd': round(saved_usd, 2),
        'days_tracked': days,
        'avg_daily_tokens': round(avg_daily_tokens),
        'estimated_monthly_savings_usd': round(monthly_savings, 2),
    }

def print_summary():
    """印出統計摘要"""
    s = get_summary()
    print("=== Token 使用統計 ===")
    print(f"追蹤天數: {s['days_tracked']} 天")
    print(f"Ollama 請求數: {s['total_requests']}")
    print(f"Ollama 使用 tokens: {s['total_tokens']:,}")
    print(f"已節省 Anthropic 費用: ${s['total_saved_usd']}")
    print(f"日均 tokens: {s['avg_daily_tokens']:,}")
    print(f"預估月省: ${s['estimated_monthly_savings_usd']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'summary':
        print_summary()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        result = query_ollama("用一句話描述今天的天氣可能如何")
        print(f"回應: {result.get('response', '')[:100]}")
        print(f"Tokens: {result.get('total_tokens', 0)}")
        print(f"耗時: {result.get('duration_s', 0):.1f}s")
        print()
        print_summary()
    else:
        print_summary()
