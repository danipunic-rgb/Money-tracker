"""
Holdings Fetcher — descarga holdings reales de ETFs desde Yahoo Finance.
NO necesita LLM ni API de pago. Solo Python + httpx.

Uso:
  python agents/fetch_holdings.py                    # genera data/holdings.json
  python agents/fetch_holdings.py --write-supabase   # además escribe en Supabase

Requiere (solo si --write-supabase):
  SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en env
"""

import json
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Instalando httpx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx


def fetch_etf_holdings(symbol: str, max_holdings: int = 15) -> list[dict]:
    """Descarga top holdings de un ETF vía Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v6/finance/quoteSummary/{symbol}"
    params = {"modules": "topHoldings,assetProfile"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
    }

    try:
        r = httpx.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ⚠ Yahoo quoteSummary falló para {symbol}: {e}")
        return fetch_holdings_fallback(symbol, max_holdings)

    result = data.get("quoteSummary", {}).get("result", [])
    if not result:
        return fetch_holdings_fallback(symbol, max_holdings)

    top = result[0].get("topHoldings", {})
    raw_holdings = top.get("holdings", [])

    holdings = []
    for h in raw_holdings[:max_holdings]:
        sym = h.get("symbol", "")
        name = h.get("holdingName", sym)
        weight = h.get("holdingPercent", {}).get("raw", 0)
        if sym and weight > 0:
            holdings.append({
                "symbol": sym,
                "name": name,
                "weight": round(weight * 100, 4),
            })

    return holdings


def fetch_holdings_fallback(symbol: str, max_holdings: int = 15) -> list[dict]:
    """Fallback: intenta el endpoint de finance/chart para al menos confirmar que el ETF existe."""
    print(f"  → Intentando fallback para {symbol}...")
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = httpx.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            print(f"  → ETF {symbol} existe pero no se pudieron obtener holdings")
        return []
    except Exception:
        return []


def fetch_stock_info(symbol: str) -> dict:
    """Obtiene info básica de una acción (sector, industria, país)."""
    url = f"https://query1.finance.yahoo.com/v6/finance/quoteSummary/{symbol}"
    params = {"modules": "assetProfile,price"}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = httpx.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = data.get("quoteSummary", {}).get("result", [])
        if not result:
            return {}

        profile = result[0].get("assetProfile", {})
        price = result[0].get("price", {})

        return {
            "sector": profile.get("sector", ""),
            "industry": profile.get("industry", ""),
            "country": profile.get("country", ""),
            "name": price.get("longName", "") or price.get("shortName", symbol),
        }
    except Exception:
        return {}


def main():
    write_supabase = "--write-supabase" in sys.argv

    etfs_path = Path("data/etfs.json")
    if not etfs_path.exists():
        print("✕ data/etfs.json no encontrado. Ejecuta primero la curación de ETFs.")
        sys.exit(1)

    etfs_data = json.loads(etfs_path.read_text())
    all_holdings = {}
    all_stocks = {}
    errors = []

    for etf in etfs_data["etfs"]:
        symbol = etf["symbol"]
        print(f"Procesando {symbol}...")

        holdings = fetch_etf_holdings(symbol)
        if holdings:
            all_holdings[symbol] = holdings
            print(f"  ✓ {len(holdings)} holdings encontrados")

            for h in holdings:
                if h["symbol"] not in all_stocks:
                    time.sleep(0.3)
                    info = fetch_stock_info(h["symbol"])
                    all_stocks[h["symbol"]] = {
                        "symbol": h["symbol"],
                        "name": info.get("name", h["name"]),
                        "sector": info.get("sector", ""),
                        "industry": info.get("industry", ""),
                        "country": info.get("country", ""),
                    }
        else:
            errors.append(symbol)
            print(f"  ✕ Sin holdings para {symbol}")

        time.sleep(0.5)

    # Guardar JSON local
    output = {
        "last_updated": time.strftime("%Y-%m-%d"),
        "etfs_with_holdings": len(all_holdings),
        "etfs_without_holdings": len(errors),
        "errors": errors,
        "unique_stocks": len(all_stocks),
        "holdings": all_holdings,
        "stocks": all_stocks,
    }

    output_path = Path("data/holdings.json")
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n✓ data/holdings.json: {len(all_holdings)} ETFs, {len(all_stocks)} empresas únicas")

    if errors:
        print(f"⚠ Sin holdings: {', '.join(errors)}")

    # Escribir en Supabase si se pide
    if write_supabase:
        import os
        sb_url = os.environ.get("SUPABASE_URL")
        sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        if not sb_url or not sb_key:
            print("⚠ SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no configuradas, saltando escritura")
            return

        print("\nEscribiendo en Supabase...")
        write_to_supabase(sb_url, sb_key, all_holdings, all_stocks)


def write_to_supabase(url: str, key: str, holdings: dict, stocks: dict):
    """Escribe holdings y metadata de stocks en Supabase."""
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    # Upsert stocks
    stock_rows = list(stocks.values())
    if stock_rows:
        r = httpx.post(
            f"{url}/rest/v1/stock_metadata",
            headers=headers,
            json=stock_rows,
            timeout=30,
        )
        if r.status_code < 300:
            print(f"  ✓ {len(stock_rows)} stocks upserted")
        else:
            print(f"  ⚠ stock_metadata: {r.status_code} {r.text[:200]}")

    # Upsert holdings
    today = time.strftime("%Y-%m-%d")
    holding_rows = []
    for etf_symbol, holds in holdings.items():
        for h in holds:
            holding_rows.append({
                "etf_symbol": etf_symbol,
                "stock_symbol": h["symbol"],
                "weight": h["weight"],
                "as_of_date": today,
            })

    if holding_rows:
        r = httpx.post(
            f"{url}/rest/v1/etf_holdings",
            headers=headers,
            json=holding_rows,
            timeout=30,
        )
        if r.status_code < 300:
            print(f"  ✓ {len(holding_rows)} holdings upserted")
        else:
            print(f"  ⚠ etf_holdings: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    main()
