"""
Publish X Daily — genera un tweet objetivo con el flujo de capital del día
y lo publica en X vía API v2 (OAuth 1.0a User Context).

NO usa LLM. Solo templating con datos reales de Supabase.

Uso:
  python agents/publish_x_daily.py                     # publica (si hay secrets)
  python agents/publish_x_daily.py --dry-run           # genera el texto, no publica
  python agents/publish_x_daily.py --force-fetch       # fuerza fetch de precios antes
  python agents/publish_x_daily.py --tf d1             # timeframe (d1|w1|m1|m3|m6)
  python agents/publish_x_daily.py --intro "Hello 👋"  # añade una intro al tweet

Requiere (solo si publica):
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

Variables opcionales:
  SUPABASE_URL (default: https://rieyywfkpprgkenljilm.supabase.co)
  SUPABASE_ANON_KEY (si no se pasa, usa la key pública embebida en el script)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
SB_URL = os.environ.get("SUPABASE_URL", "https://rieyywfkpprgkenljilm.supabase.co")
# Anon key: es pública por diseño (RLS protege la BBDD). Se puede sobrescribir.
SB_ANON = os.environ.get(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpZXl5d2ZrcHByZ2tlbmxqaWxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzNzQ5NDgsImV4cCI6MjA5MTk1MDk0OH0.d4H4QW_BeBc6axpgmevLKNdMb0gJ-U6hQ15Rk9Bn-20",
)
SITE_URL = "money-tracker-new-app.vercel.app"

TIMEFRAMES = {
    "d1": {"days": 1,   "label": "1-day",   "human": "Today"},
    "w1": {"days": 5,   "label": "1-week",  "human": "This week"},
    "m1": {"days": 21,  "label": "1-month", "human": "This month"},
    "m3": {"days": 63,  "label": "3-month", "human": "Last 3 months"},
    "m6": {"days": 126, "label": "6-month", "human": "Last 6 months"},
}

# Traducción ES → EN para los nombres de sector (se muestran en inglés en X)
SECTOR_EN = {
    "Tecnología": "Technology",
    "Energía": "Energy",
    "Financieros": "Financials",
    "Salud": "Healthcare",
    "Referencias": "Reference",
}


# -----------------------------------------------------------------------------
# Supabase
# -----------------------------------------------------------------------------
def sb_get(path: str) -> list[dict]:
    headers = {"apikey": SB_ANON, "Authorization": f"Bearer {SB_ANON}"}
    r = httpx.get(f"{SB_URL}/rest/v1/{path}", headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_metadata() -> list[dict]:
    return sb_get(
        "etf_metadata?select=symbol,name,sector,sector_color,display_order"
        "&enabled=eq.true&order=display_order"
    )


def fetch_prices(symbol: str) -> list[dict]:
    # 150 trading days es más que suficiente incluso para tf m6 (≈126d)
    return sb_get(
        f"etf_daily?symbol=eq.{symbol}&select=date,adj_close"
        f"&order=date.desc&limit=150"
    )


def force_edge_fetch(days: int = 2) -> None:
    print(f"→ Forzando Edge Function fetch-etfs?days={days}...")
    headers = {"Authorization": f"Bearer {SB_ANON}"}
    try:
        r = httpx.get(
            f"{SB_URL}/functions/v1/fetch-etfs?days={days}",
            headers=headers,
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        print(f"  ✓ fetch-etfs: {len(data.get('ok', []))} ok, "
              f"{len(data.get('failed', []))} failed")
    except Exception as e:
        print(f"  ⚠ Edge Function falló (seguimos con datos existentes): {e}")


# -----------------------------------------------------------------------------
# Cálculo de flujo agregado por sector
# -----------------------------------------------------------------------------
def pct_change(rows_desc: list[dict], days_back: int) -> float | None:
    """rows_desc viene ordenado por date DESC. Calcula % entre el último close
    y el close de hace `days_back` filas."""
    closes = [float(r["adj_close"]) for r in rows_desc if r.get("adj_close") is not None]
    if len(closes) < 2:
        return None
    latest = closes[0]
    idx = min(days_back, len(closes) - 1)
    past = closes[idx]
    if past <= 0:
        return None
    return (latest - past) / past * 100.0


def aggregate_by_sector(
    metadata: list[dict],
    prices_by_symbol: dict[str, list[dict]],
    tf_key: str,
) -> tuple[list[dict], str | None]:
    days_back = TIMEFRAMES[tf_key]["days"]
    by_sector: dict[str, list[float]] = {}
    colors: dict[str, str] = {}
    latest_date: str | None = None

    for m in metadata:
        sector = m["sector"]
        if sector.lower() in ("referencias", "reference"):
            continue  # benchmarks fuera del flujo agregado
        rows = prices_by_symbol.get(m["symbol"]) or []
        if rows and rows[0].get("date"):
            d = rows[0]["date"]
            if not latest_date or d > latest_date:
                latest_date = d
        pct = pct_change(rows, days_back)
        if pct is None:
            continue
        by_sector.setdefault(sector, []).append(pct)
        colors[sector] = m.get("sector_color") or ""

    agg = []
    for sector, vals in by_sector.items():
        avg = sum(vals) / len(vals)
        agg.append({
            "sector_es": sector,
            "sector_en": SECTOR_EN.get(sector, sector),
            "avg": avg,
            "n": len(vals),
            "color": colors.get(sector, ""),
        })
    agg.sort(key=lambda x: x["avg"], reverse=True)
    return agg, latest_date


# -----------------------------------------------------------------------------
# Templating del tweet (inglés, ≤280 chars)
# -----------------------------------------------------------------------------
def fmt_pct(v: float) -> str:
    return f"{'+' if v >= 0 else ''}{v:.2f}%"


def build_tweet(agg: list[dict], tf_key: str, latest_date: str | None,
                intro: str | None = None) -> str:
    if not agg:
        return "📊 US Capital Flow — no data available today.\n\n" + SITE_URL

    tf = TIMEFRAMES[tf_key]
    date_str = ""
    if latest_date:
        try:
            dt = datetime.fromisoformat(latest_date)
            date_str = f" · {dt.strftime('%b %d, %Y')}"
        except Exception:
            date_str = f" · {latest_date}"

    ins  = [s for s in agg if s["avg"] > 0]
    outs = [s for s in reversed(agg) if s["avg"] < 0]  # más negativos primero

    def lines(items, max_n=2):
        return [f"  {s['sector_en']} {fmt_pct(s['avg'])}" for s in items[:max_n]]

    parts = [f"📊 US Capital Flow{date_str}"]
    if intro:
        parts.append("")
        parts.append(intro.strip())

    body = []
    if ins:
        body.append("🟢 IN")
        body += lines(ins)
    if outs:
        if ins:
            body.append("")
        body.append("🔴 OUT")
        body += lines(outs)
    if not ins and not outs:
        body.append("All sectors flat.")

    parts.append("")
    parts.extend(body)
    parts.append("")
    parts.append(f"{tf['label']} · sector avg (adj close)")
    parts.append(SITE_URL)

    text = "\n".join(parts)

    # Fallback si excede 280: acortamos secciones
    if len(text) > 280:
        body = []
        if ins:
            body.append("🟢 IN: " + ", ".join(
                f"{s['sector_en']} {fmt_pct(s['avg'])}" for s in ins[:2]
            ))
        if outs:
            body.append("🔴 OUT: " + ", ".join(
                f"{s['sector_en']} {fmt_pct(s['avg'])}" for s in outs[:2]
            ))
        parts = [f"📊 US Capital Flow{date_str}", "", *body, "", SITE_URL]
        text = "\n".join(parts)

    return text


# -----------------------------------------------------------------------------
# Publicación en X
# -----------------------------------------------------------------------------
def publish_tweet(text: str) -> dict:
    try:
        import tweepy
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tweepy", "-q"])
        import tweepy

    required = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Faltan secrets: {', '.join(missing)}")

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    resp = client.create_tweet(text=text)
    tweet_id = resp.data.get("id") if hasattr(resp, "data") and resp.data else None
    return {"id": tweet_id, "raw": str(resp)}


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Genera el texto pero NO publica")
    ap.add_argument("--force-fetch", action="store_true",
                    help="Invoca la Edge Function antes de leer precios")
    ap.add_argument("--tf", default="d1", choices=list(TIMEFRAMES.keys()),
                    help="Timeframe del tweet (default d1)")
    ap.add_argument("--intro", default=None,
                    help="Línea de introducción opcional")
    args = ap.parse_args()

    if args.force_fetch:
        force_edge_fetch(days=2)

    print("→ Leyendo metadata de Supabase...")
    metadata = fetch_metadata()
    print(f"  ✓ {len(metadata)} ETFs activos")

    prices_by_symbol = {}
    for m in metadata:
        try:
            prices_by_symbol[m["symbol"]] = fetch_prices(m["symbol"])
        except Exception as e:
            print(f"  ⚠ {m['symbol']}: {e}")
            prices_by_symbol[m["symbol"]] = []

    agg, latest_date = aggregate_by_sector(metadata, prices_by_symbol, args.tf)
    print(f"  ✓ {len(agg)} sectores con flujo calculado, data from {latest_date}")

    text = build_tweet(agg, args.tf, latest_date, intro=args.intro)
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)
    print(f"Length: {len(text)} chars")

    if args.dry_run:
        print("\n(dry-run) no publico.")
        # Guardamos el texto en un artefacto por si el workflow quiere leerlo
        Path("last_tweet_preview.txt").write_text(text, encoding="utf-8")
        return 0

    print("\n→ Publicando en X...")
    result = publish_tweet(text)
    if result["id"]:
        tweet_url = f"https://x.com/i/web/status/{result['id']}"
        print(f"  ✓ Publicado: {tweet_url}")
        Path("last_tweet.txt").write_text(
            f"{text}\n\n---\nurl: {tweet_url}\nposted_at: {datetime.now(timezone.utc).isoformat()}\n",
            encoding="utf-8",
        )
    else:
        print(f"  ⚠ Respuesta inesperada: {result['raw']}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
