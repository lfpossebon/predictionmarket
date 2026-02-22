#!/usr/bin/env python3
"""
Consolida dados históricos dos traders em um único JSON para o dashboard.
Roda uma vez após a extração — o dashboard carrega instantaneamente depois.

Uso: python3 consolidate_historical.py
"""
import json
import os
from datetime import datetime

TRADERS_DIR = 'historical/traders/'
OUTPUT = 'historical/consolidated.json'
FILELIST = 'historical/filelist.json'

def main():
    traders = []
    trades = []
    positions = []
    filenames = []
    
    files = [f for f in os.listdir(TRADERS_DIR) if f.endswith('.json')]
    print(f'📦 Consolidando {len(files)} traders...')
    
    for i, filename in enumerate(sorted(files)):
        filenames.append(filename)
        filepath = os.path.join(TRADERS_DIR, filename)
        with open(filepath) as f:
            data = json.load(f)
        
        info = data.get('info', {})
        profile = data.get('profile', {})
        username = info.get('username', 'unknown')
        wallet = data.get('wallet', '')
        
        unique_markets = set()
        trader_trades = []
        
        for t in data.get('trades', []):
            if t.get('type') == 'TRADE':
                trade = {
                    'username': username,
                    'ts': t.get('timestamp', 0),
                    'side': t.get('side', ''),
                    'size': t.get('size', 0),
                    'usdc': t.get('usdcSize', 0),
                    'price': t.get('price', 0),
                    'title': t.get('title', ''),
                    'slug': t.get('slug', ''),
                    'outcome': t.get('outcome', ''),
                }
                trades.append(trade)
                trader_trades.append(trade)
                if t.get('slug'):
                    unique_markets.add(t['slug'])
        
        for p in data.get('positions', []):
            positions.append({
                'username': username,
                'title': p.get('title', ''),
                'slug': p.get('slug', ''),
                'size': p.get('size', 0),
                'avg_price': p.get('avgPrice', 0),
                'current_value': p.get('currentValue', 0),
                'cash_pnl': p.get('cashPnl', 0),
                'percent_pnl': p.get('percentPnl', 0),
                'outcome': p.get('outcome', ''),
                'cur_price': p.get('curPrice', 0),
            })
        
        traders.append({
            'wallet': wallet,
            'username': username,
            'pnl': info.get('pnl', 0),
            'categories': info.get('categories', []),
            'ranks': info.get('ranks', {}),
            'trades_count': data.get('trades_count', 0),
            'positions_count': data.get('positions_count', 0),
            'unique_markets': len(unique_markets),
        })
        
        if (i + 1) % 100 == 0:
            print(f'  ... {i+1}/{len(files)}')
    
    # Save consolidated
    consolidated = {
        'generated_at': datetime.now().isoformat(),
        'traders': traders,
        'trades': trades,
        'positions': positions,
    }
    
    print(f'\n📊 Resultado:')
    print(f'  Traders: {len(traders)}')
    print(f'  Trades: {len(trades):,}')
    print(f'  Posições: {len(positions):,}')
    
    with open(OUTPUT, 'w') as f:
        json.dump(consolidated, f)
    
    size_mb = os.path.getsize(OUTPUT) / 1e6
    print(f'\n✅ Salvo em {OUTPUT} ({size_mb:.1f} MB)')
    
    # Save filelist for fallback
    with open(FILELIST, 'w') as f:
        json.dump(filenames, f)
    print(f'✅ Filelist salvo em {FILELIST}')

if __name__ == '__main__':
    main()
