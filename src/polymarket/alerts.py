"""
Módulo ALERTAS — Formata e envia sinais via Telegram
"""
import json
from datetime import datetime
from config import DATA_DIR


def format_signal(signal: dict) -> str:
    """Formata um sinal pra mensagem Telegram."""
    consensus = signal["consensus_pct"] * 100
    
    # Emoji baseado na confiança
    if consensus >= 90:
        emoji = "🔴"  # Muito forte
    elif consensus >= 80:
        emoji = "🟡"  # Forte
    else:
        emoji = "⚪"
    
    msg = (
        f"{emoji} SINAL POLYMARKET\n"
        f"Basket: {signal['basket'].upper()}\n"
        f"Mercado: {signal['market_title'][:60]}\n"
        f"Outcome: {signal['outcome']}\n"
        f"Consenso: {consensus:.0f}% ({signal['wallets_in']}/{signal['wallets_total']} wallets)\n"
        f"Detectado: {signal['detected_at'][:16]}"
    )
    return msg


def format_daily_report(signals: list) -> str:
    """Formata relatório diário de sinais."""
    if not signals:
        return "📊 Polymarket Monitor — Sem sinais hoje"
    
    today = datetime.now().strftime("%d/%m/%Y")
    
    msg = f"📊 Polymarket Copy Trading — {today}\n"
    msg += f"Sinais detectados: {len(signals)}\n\n"
    
    for i, signal in enumerate(signals, 1):
        consensus = signal["consensus_pct"] * 100
        msg += (
            f"{i}. {signal['market_title'][:50]}\n"
            f"   {signal['outcome']} — {consensus:.0f}% ({signal['basket']})\n\n"
        )
    
    return msg


def load_today_signals() -> list:
    """Carrega sinais de hoje."""
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = DATA_DIR / "signals" / f"signals-{today}.json"
    
    if not filepath.exists():
        return []
    
    with open(filepath) as f:
        return json.load(f)


def main():
    """Gera relatório diário — pra ser chamado pelo cron/Iris."""
    signals = load_today_signals()
    report = format_daily_report(signals)
    print(report)
    return report


if __name__ == "__main__":
    main()
