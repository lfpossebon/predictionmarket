#!/usr/bin/env python3
"""
Versão lite do consolidado — agrega dados para o dashboard carregar rápido.
Em vez de 1.5M trades individuais, pré-agrega por dia/trader/mercado.
"""
import json
import os
from datetime import datetime
from collections import defaultdict

TRADERS_DIR = 'historical/traders/'
OUTPUT = 'historical/consolidated_lite.json'

def main():
    traders = []
    # Agregações
    daily_volume = defaultdict(lambda: {'vol':0, 'trades':0, 'traders':set()})
    hourly_volume = defaultdict(float)
    dow_volume = defaultdict(float)
    trader_daily = defaultdict(lambda: defaultdict(lambda: {'vol':0, 'trades':0, 'markets':set()}))
    trader_markets = defaultdict(lambda: defaultdict(float))  # trader -> market -> volume
    cum_cashflow = defaultdict(lambda: defaultdict(float))  # trader -> date -> cashflow
    positions = []
    
    files = [f for f in os.listdir(TRADERS_DIR) if f.endswith('.json')]
    print(f'📦 Processando {len(files)} traders...')
    
    for i, filename in enumerate(sorted(files)):
        filepath = os.path.join(TRADERS_DIR, filename)
        with open(filepath) as f:
            data = json.load(f)
        
        info = data.get('info', {})
        username = info.get('username', 'unknown')
        wallet = data.get('wallet', '')
        unique_markets = set()
        
        for t in data.get('trades', []):
            if t.get('type') != 'TRADE':
                continue
            ts = t.get('timestamp', 0)
            usdc = t.get('usdcSize', 0)
            dt = datetime.utcfromtimestamp(ts)
            date_str = dt.strftime('%Y-%m-%d')
            slug = t.get('slug', '')
            title = t.get('title', '')
            side = t.get('side', '')
            
            unique_markets.add(slug)
            
            # Daily aggregates
            daily_volume[date_str]['vol'] += usdc
            daily_volume[date_str]['trades'] += 1
            daily_volume[date_str]['traders'].add(username)
            
            # Hourly / DOW
            hourly_volume[dt.hour] += usdc
            dow_volume[dt.weekday()] += usdc
            
            # Per-trader daily
            trader_daily[username][date_str]['vol'] += usdc
            trader_daily[username][date_str]['trades'] += 1
            trader_daily[username][date_str]['markets'].add(slug)
            
            # Per-trader markets
            trader_markets[username][title] += usdc
            
            # Cashflow for cumulative PnL
            cf = -usdc if side == 'BUY' else usdc
            cum_cashflow[username][date_str] += cf
        
        # Positions
        for p in data.get('positions', []):
            positions.append({
                'u': username,
                't': p.get('title', ''),
                'cv': round(p.get('currentValue', 0), 2),
                'pnl': round(p.get('cashPnl', 0), 2),
                'pct': round(p.get('percentPnl', 0), 2),
                'o': p.get('outcome', ''),
            })
        
        traders.append({
            'u': username,
            'w': wallet,
            'pnl': round(info.get('pnl', 0), 2),
            'cat': info.get('categories', []),
            'tc': data.get('trades_count', 0),
            'pc': data.get('positions_count', 0),
            'um': len(unique_markets),
        })
        
        if (i + 1) % 100 == 0:
            print(f'  ... {i+1}/{len(files)}')
    
    # Prepare daily data (convert sets)
    daily_out = {}
    for d, v in sorted(daily_volume.items()):
        daily_out[d] = {'v': round(v['vol'], 2), 'n': v['trades'], 't': len(v['traders'])}
    
    # Hourly & DOW
    hourly_out = {str(h): round(v, 2) for h, v in sorted(hourly_volume.items())}
    dow_out = {str(d): round(v, 2) for d, v in sorted(dow_volume.items())}
    
    # Top 30 traders: daily + markets + cumulative
    top30 = sorted(traders, key=lambda t: t['pnl'], reverse=True)[:30]
    top30_names = {t['u'] for t in top30}
    
    trader_details = {}
    for name in top30_names:
        # Daily
        td = trader_daily.get(name, {})
        daily = {d: {'v': round(v['vol'],2), 'n': v['trades']} for d, v in sorted(td.items())}
        
        # Top 10 markets
        tm = trader_markets.get(name, {})
        top_mkts = sorted(tm.items(), key=lambda x: x[1], reverse=True)[:10]
        mkts = [{'t': t[:50], 'v': round(v,2)} for t, v in top_mkts]
        
        # Cumulative cashflow
        cf = cum_cashflow.get(name, {})
        cum = 0
        cum_data = {}
        for d in sorted(cf.keys()):
            cum += cf[d]
            cum_data[d] = round(cum, 2)
        
        trader_details[name] = {'daily': daily, 'markets': mkts, 'cum': cum_data}
    
    result = {
        'ts': datetime.now().isoformat(),
        'traders': traders,
        'daily': daily_out,
        'hourly': hourly_out,
        'dow': dow_out,
        'details': trader_details,
        'positions': positions,
    }
    
    with open(OUTPUT, 'w') as f:
        json.dump(result, f, separators=(',',':'))
    
    size_mb = os.path.getsize(OUTPUT) / 1e6
    print(f'\n📊 Resultado:')
    print(f'  Traders: {len(traders)}')
    print(f'  Dias com dados: {len(daily_out)}')
    print(f'  Posições: {len(positions)}')
    print(f'  Detalhes top 30: {len(trader_details)}')
    print(f'\n✅ Salvo em {OUTPUT} ({size_mb:.1f} MB)')

if __name__ == '__main__':
    main()
