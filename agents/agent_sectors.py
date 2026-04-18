"""
Agent 1: Sector Analyst
-----------------------
Investiga los sectores clave de la economía global, define el alcance de cada uno,
y detecta sectores emergentes. Genera data/sectors.json.

Corre semanalmente vía GitHub Actions.
"""

import json
import os
from pathlib import Path

# En futuras versiones, este agente usará la API de Anthropic con web search
# para investigar el consenso actual sobre sectores.
# Por ahora, usa la configuración base definida manualmente.

SECTORS = [
    {
        "id": "technology",
        "name": "Tecnología",
        "name_en": "Technology",
        "color": "#7c3aed",
        "description": "Software, hardware, semiconductores, cloud, IA",
        "scope": [
            "Software empresarial y consumo",
            "Semiconductores y equipos de fabricación",
            "Cloud computing e infraestructura",
            "Inteligencia artificial y machine learning",
            "Ciberseguridad",
        ],
        "excludes": [
            "Fintech (va en Financieros)",
            "Healthtech (va en Salud)",
            "Cleantech (va en Energía)",
        ],
        "display_order": 1,
    },
    {
        "id": "energy",
        "name": "Energía",
        "name_en": "Energy",
        "color": "#c2410c",
        "description": "Fósiles, renovables, nuclear, infraestructura energética",
        "scope": [
            "Petróleo y gas (upstream, midstream, downstream)",
            "Energías renovables (solar, eólica, hidro)",
            "Nuclear y uranio",
            "Infraestructura energética (redes, almacenamiento)",
            "Utilities eléctricas",
        ],
        "excludes": [
            "Vehículos eléctricos (va en Tecnología o Consumo según contexto)",
        ],
        "display_order": 2,
    },
    {
        "id": "financials",
        "name": "Financieros",
        "name_en": "Financials",
        "color": "#0369a1",
        "description": "Banca, seguros, gestión de activos, fintech",
        "scope": [
            "Grandes bancos comerciales y de inversión",
            "Banca regional",
            "Seguros (vida, propiedad, reaseguros)",
            "Gestión de activos y wealth management",
            "Fintech y pagos digitales",
            "Bolsas y market makers",
        ],
        "excludes": [
            "Crypto exchanges (va en sector Crypto si se añade)",
        ],
        "display_order": 3,
    },
    {
        "id": "healthcare",
        "name": "Salud",
        "name_en": "Healthcare",
        "color": "#15803d",
        "description": "Farmacéuticas, biotecnología, dispositivos médicos",
        "scope": [
            "Grandes farmacéuticas",
            "Biotecnología (large cap y speculative)",
            "Dispositivos médicos y equipamiento",
            "Servicios de salud y hospitales",
            "Genómica y terapias avanzadas",
        ],
        "excludes": [
            "Cannabis medicinal (demasiado nicho por ahora)",
        ],
        "display_order": 4,
    },
    {
        "id": "reference",
        "name": "Referencias",
        "name_en": "Benchmarks",
        "color": "#78716c",
        "description": "Índices amplios y activos refugio para contextualizar",
        "scope": [
            "Mercado amplio US (S&P 500)",
            "Small caps US (Russell 2000)",
            "Oro y metales preciosos como refugio",
        ],
        "excludes": [],
        "display_order": 5,
    },
]

# Sectores candidatos para investigar en futuras ejecuciones
CANDIDATE_SECTORS = [
    "defense_aerospace",
    "real_estate_reits",
    "consumer_discretionary",
    "consumer_staples",
    "emerging_markets",
    "china",
    "commodities",
    "bonds_fixed_income",
    "crypto",
]


def main():
    output_path = Path("data/sectors.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "version": "1.0",
        "last_updated": "2026-04-18",
        "agent": "agent_sectors",
        "sectors": SECTORS,
        "candidates_for_review": CANDIDATE_SECTORS,
    }

    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✓ Generado {output_path} con {len(SECTORS)} sectores")


if __name__ == "__main__":
    main()
