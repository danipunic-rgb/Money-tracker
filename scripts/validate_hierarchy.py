#!/usr/bin/env python3
"""
validate_hierarchy.py — Comprueba la consistencia de data/hierarchy.json
contra data/sectors.json y data/etfs.json.

Uso:
    python scripts/validate_hierarchy.py

Salida:
    Exit 0 si todo es correcto.
    Exit 1 con mensajes de error si algo falla.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
errors = []

def err(msg):
    errors.append(f"ERROR: {msg}")
    print(f"ERROR: {msg}", file=sys.stderr)

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        err(f"No se puede leer {path}: {e}")
        sys.exit(1)

hierarchy = load(ROOT / "data" / "hierarchy.json")
sectors_data = load(ROOT / "data" / "sectors.json")
etfs_data = load(ROOT / "data" / "etfs.json")

sector_ids = {s["id"] for s in sectors_data["sectors"]}
etf_symbols = {e["symbol"] for e in etfs_data["etfs"]}
indices = hierarchy.get("indices", [])
subsectors = hierarchy.get("subsectors", [])
etf_to_sub = hierarchy.get("etf_to_subsector", {})

# 1. IDs de índices únicos
idx_ids = [i["id"] for i in indices]
if len(idx_ids) != len(set(idx_ids)):
    dupes = [x for x in set(idx_ids) if idx_ids.count(x) > 1]
    err(f"IDs de índices duplicados: {dupes}")

idx_id_set = set(idx_ids)

# 2. parent apunta a un id existente
for idx in indices:
    if "parent" in idx and idx["parent"] not in idx_id_set:
        err(f"Índice '{idx['id']}' tiene parent='{idx['parent']}' que no existe")

# 3. children apuntan a ids existentes
for idx in indices:
    for cid in idx.get("children", []):
        if cid not in idx_id_set:
            err(f"Índice '{idx['id']}' tiene hijo '{cid}' que no existe")

# 4. key_indices apuntan a ids existentes
for idx in indices:
    for kid in idx.get("key_indices", []):
        if kid not in idx_id_set:
            err(f"Índice '{idx['id']}' tiene key_index '{kid}' que no existe")

# 5. proxy_etf existe en etfs.json
for idx in indices:
    proxy = idx.get("proxy_etf")
    if proxy and proxy not in etf_symbols:
        err(f"Índice '{idx['id']}': proxy_etf='{proxy}' no existe en data/etfs.json")

# 6. sectors_applicable referencia IDs de sectors.json
for idx in indices:
    for sid in idx.get("sectors_applicable", []):
        if sid not in sector_ids:
            err(f"Índice '{idx['id']}': sectors_applicable contiene '{sid}' que no existe en sectors.json")

# 7. subsectors: parent_sector existe en sectors.json, IDs únicos
sub_ids = [s["id"] for s in subsectors]
if len(sub_ids) != len(set(sub_ids)):
    dupes = [x for x in set(sub_ids) if sub_ids.count(x) > 1]
    err(f"IDs de subsectores duplicados: {dupes}")
sub_id_set = set(sub_ids)

for sub in subsectors:
    if sub.get("parent_sector") not in sector_ids:
        err(f"Subsector '{sub['id']}': parent_sector='{sub.get('parent_sector')}' no existe en sectors.json")

# 8. etf_to_subsector: ETF existe en etfs.json, subsector_id existe en subsectors
for etf_sym, sub_id in etf_to_sub.items():
    if etf_sym not in etf_symbols:
        err(f"etf_to_subsector: '{etf_sym}' no existe en data/etfs.json")
    if sub_id not in sub_id_set:
        err(f"etf_to_subsector: '{etf_sym}' → '{sub_id}' subsector no existe")

# 9. Sin ciclos en parent (DFS)
def has_cycle():
    visited = set()
    def dfs(nid, path):
        if nid in path:
            err(f"Ciclo detectado en jerarquía de índices: {' → '.join(path + [nid])}")
            return True
        if nid in visited:
            return False
        visited.add(nid)
        node = next((i for i in indices if i["id"] == nid), None)
        if not node:
            return False
        for cid in node.get("children", []):
            if dfs(cid, path + [nid]):
                return True
        return False
    for idx in indices:
        if "parent" not in idx:
            dfs(idx["id"], [])

has_cycle()

# ——— Resultado ———
if errors:
    print(f"\n{len(errors)} error(es) encontrado(s). Corrige antes de commitear.", file=sys.stderr)
    sys.exit(1)
else:
    total_idx = len(indices)
    total_sub = len(subsectors)
    total_etf_map = len(etf_to_sub)
    print(f"OK - hierarchy.json valido ({total_idx} indices, {total_sub} subsectores, {total_etf_map} mappings ETF->subsector)")
    sys.exit(0)
