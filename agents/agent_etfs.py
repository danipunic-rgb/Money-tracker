"""
Agent 2: ETF Curator
--------------------
Lee data/sectors.json, investiga los mejores ETFs dentro de cada sector,
y genera data/etfs.json con el detalle completo.

Corre semanalmente vía GitHub Actions, después de Agent 1.
"""

import json
from pathlib import Path

# En futuras versiones, este agente usará la API de Anthropic para
# investigar nuevos ETFs, verificar que siguen activos, y actualizar AUM.
# Por ahora, usa la configuración base.

ETFS_BY_SECTOR = {
    "technology": [
        {
            "symbol": "XLK",
            "name": "Technology Select Sector SPDR",
            "isin": "US81369Y8030",
            "rationale": "El ETF sectorial más grande y líquido de tecnología US",
        },
        {
            "symbol": "SMH",
            "name": "VanEck Semiconductors",
            "isin": "US92189F6875",
            "rationale": "Foco puro en semiconductores, el subsector más caliente de la era IA",
        },
        {
            "symbol": "QQQ",
            "name": "Invesco Nasdaq 100",
            "isin": "US46090E1038",
            "rationale": "Nasdaq 100 amplio, tech-heavy pero incluye consumer y health",
        },
    ],
    "energy": [
        {
            "symbol": "XLE",
            "name": "Energy Select Sector SPDR",
            "isin": "US81369Y5069",
            "rationale": "Sector energético tradicional (oil & gas majors)",
        },
        {
            "symbol": "ICLN",
            "name": "iShares Global Clean Energy",
            "isin": "US46434V7385",
            "rationale": "Energía limpia global, contrapunto a XLE",
        },
        {
            "symbol": "URA",
            "name": "Global X Uranium",
            "isin": "US37954Y8553",
            "rationale": "Nuclear/uranio, la energía de transición que más crece",
        },
    ],
    "financials": [
        {
            "symbol": "XLF",
            "name": "Financial Select Sector SPDR",
            "isin": "US81369Y8188",
            "rationale": "Sector financiero amplio (grandes bancos + seguros + asset mgmt)",
        },
        {
            "symbol": "KRE",
            "name": "SPDR S&P Regional Banking",
            "isin": "US78464A6982",
            "rationale": "Banca regional US, termómetro de la economía real",
        },
        {
            "symbol": "KBE",
            "name": "SPDR S&P Bank ETF",
            "isin": "US78464A5505",
            "rationale": "Bancario puro (equal weight), sin seguros ni asset managers",
        },
    ],
    "healthcare": [
        {
            "symbol": "XLV",
            "name": "Health Care Select Sector SPDR",
            "isin": "US81369Y2090",
            "rationale": "Salud amplio: farma grandes + dispositivos + servicios",
        },
        {
            "symbol": "IBB",
            "name": "iShares Biotechnology",
            "isin": "US4642875235",
            "rationale": "Biotech large/mid cap, más estable que XBI",
        },
        {
            "symbol": "XBI",
            "name": "SPDR S&P Biotech",
            "isin": "US78464A8707",
            "rationale": "Biotech equal weight, más especulativo, captura small caps",
        },
    ],
    "reference": [
        {
            "symbol": "SPY",
            "name": "SPDR S&P 500",
            "isin": "US78462F1030",
            "rationale": "Benchmark del mercado US amplio",
        },
        {
            "symbol": "IWM",
            "name": "iShares Russell 2000",
            "isin": "US4642876555",
            "rationale": "Small caps US, indicador de apetito por riesgo",
        },
        {
            "symbol": "GLD",
            "name": "SPDR Gold Shares",
            "isin": "US78463V1070",
            "rationale": "Oro como refugio, contrapeso a equity",
        },
    ],
}


def main():
    sectors_path = Path("data/sectors.json")
    if not sectors_path.exists():
        print("⚠ data/sectors.json no encontrado, ejecuta agent_sectors.py primero")
        return

    sectors_data = json.loads(sectors_path.read_text())
    sectors = {s["id"]: s for s in sectors_data["sectors"]}

    etfs_output = []
    for sector_id, etfs in ETFS_BY_SECTOR.items():
        sector = sectors.get(sector_id, {})
        for etf in etfs:
            etfs_output.append(
                {
                    "symbol": etf["symbol"],
                    "name": etf["name"],
                    "isin": etf["isin"],
                    "sector_id": sector_id,
                    "sector_name": sector.get("name", sector_id),
                    "sector_color": sector.get("color", "#78716c"),
                    "rationale": etf["rationale"],
                }
            )

    output_path = Path("data/etfs.json")
    output = {
        "version": "1.0",
        "last_updated": "2026-04-18",
        "agent": "agent_etfs",
        "etfs": etfs_output,
        "total": len(etfs_output),
    }

    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✓ Generado {output_path} con {len(etfs_output)} ETFs")


if __name__ == "__main__":
    main()
