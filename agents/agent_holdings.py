"""
Agent 3: Holdings Tracker
--------------------------
Lee data/etfs.json, descarga holdings reales de cada ETF,
y los sube a Supabase (etf_holdings + stock_metadata).

Corre semanalmente vía GitHub Actions, después de Agent 2.

NOTA: Este agente requiere que las tablas etf_holdings y stock_metadata
existan en Supabase. Se crearán en la Fase 1 del roadmap.
Por ahora, genera data/holdings.json como output local.
"""

import json
import os
from pathlib import Path

# Placeholder: en Fase 1 se añadirá:
# - httpx para llamar a Yahoo Finance / FMP y descargar holdings reales
# - supabase-py para escribir directamente en la BBDD
# Por ahora genera un archivo de ejemplo para validar el pipeline


def main():
    etfs_path = Path("data/etfs.json")
    if not etfs_path.exists():
        print("⚠ data/etfs.json no encontrado, ejecuta agent_etfs.py primero")
        return

    etfs_data = json.loads(etfs_path.read_text())

    # Placeholder: datos de ejemplo para validar la estructura
    # En Fase 1, esto se reemplazará por datos reales de Yahoo/FMP
    holdings_output = []

    for etf in etfs_data["etfs"]:
        holdings_output.append(
            {
                "etf_symbol": etf["symbol"],
                "holdings_status": "pending",
                "note": "Holdings reales se cargarán en Fase 1 cuando las tablas estén creadas",
            }
        )

    output_path = Path("data/holdings.json")
    output = {
        "version": "0.1-placeholder",
        "last_updated": "2026-04-18",
        "agent": "agent_holdings",
        "status": "placeholder - Fase 1 pendiente",
        "etfs_processed": len(holdings_output),
        "holdings": holdings_output,
    }

    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✓ Generado {output_path} (placeholder, {len(holdings_output)} ETFs)")

    # --- Fase 1: descomentar cuando las tablas existan ---
    # supabase_url = os.environ.get('SUPABASE_URL')
    # supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    # if not supabase_url or not supabase_key:
    #     print("⚠ SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no configuradas")
    #     return
    #
    # from supabase import create_client
    # sb = create_client(supabase_url, supabase_key)
    #
    # for etf in etfs_data['etfs']:
    #     holdings = fetch_holdings_from_yahoo(etf['symbol'])
    #     for h in holdings:
    #         sb.table('stock_metadata').upsert({
    #             'symbol': h['symbol'],
    #             'name': h['name'],
    #             'sector': h.get('sector'),
    #             'country': h.get('country'),
    #         }).execute()
    #         sb.table('etf_holdings').upsert({
    #             'etf_symbol': etf['symbol'],
    #             'stock_symbol': h['symbol'],
    #             'weight': h['weight'],
    #             'as_of_date': today,
    #         }).execute()


if __name__ == "__main__":
    main()
