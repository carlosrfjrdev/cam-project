/** Hooks do Market Data / Provenance — TASK-U018 (BL-UI-3). */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";

export interface Provenance {
  import_id: string;
  source: string;
  source_url: string | null;
  asset: string;
  ts_origin_min: string | null;
  ts_origin_max: string | null;
  ts_ingestion: string | null;
  tick_count: number;
  hash: string;
  quality_flags: Record<string, unknown>;
  license_terms_ack: boolean;
}

export interface Instrument {
  ticker: string;
  asset_class: string;
  exchange: string;
  contract_size: string;
  tick_size: string;
  point_value: string;
  active: boolean;
}

export function useProvenance() {
  return useQuery({
    queryKey: ["market-data-provenance"],
    queryFn: () => api.get<Provenance[]>("/market-data/provenance"),
  });
}

export function useInstruments() {
  return useQuery({
    queryKey: ["market-data-instruments"],
    queryFn: () => api.get<Instrument[]>("/market-data/instruments"),
  });
}
