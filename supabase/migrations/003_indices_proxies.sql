-- =============================================================================
-- Migration 003 — ETFs proxy para índices MSCI (Market Vision)
--
-- Añade ACWI, URTH, IEMG a etf_metadata como proxies de precios para los
-- nodos raíz del navegador jerárquico Market Vision.
-- =============================================================================

insert into public.etf_metadata (symbol, name, sector, sector_color, sector_desc, display_order, enabled) values
  ('ACWI', 'iShares MSCI ACWI ETF',                 'Referencias', '#78716c', 'Proxy MSCI ACWI – índice global',              93, true),
  ('URTH', 'iShares MSCI World ETF',                 'Referencias', '#78716c', 'Proxy MSCI World – países desarrollados',      94, true),
  ('IEMG', 'iShares Core MSCI Emerging Markets ETF', 'Referencias', '#78716c', 'Proxy MSCI Emerging Markets',                  95, true)
on conflict (symbol) do update set
  name         = excluded.name,
  sector       = excluded.sector,
  sector_color = excluded.sector_color,
  sector_desc  = excluded.sector_desc,
  display_order= excluded.display_order,
  enabled      = excluded.enabled;
