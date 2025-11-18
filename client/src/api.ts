import { TradeWithSignals } from "./types";

const BASE_URL = "/api";

export interface FetchTradesParams {
  ticker?: string;
  party?: string;
  transaction?: string;
}

const buildQuery = (params: Record<string, string | undefined>) => {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      usp.append(key, value);
    }
  });
  const query = usp.toString();
  return query ? `?${query}` : "";
};

export const fetchTrades = async (params: FetchTradesParams = {}) => {
  const res = await fetch(`${BASE_URL}/trades/congress${buildQuery({
    ticker: params.ticker,
    party: params.party,
    transaction: params.transaction,
  })}`);
  if (!res.ok) {
    throw new Error("Failed to fetch trades");
  }
  const data: TradeWithSignals[] = await res.json();
  return data;
};

export const fetchTradeById = async (id: number) => {
  const res = await fetch(`${BASE_URL}/trades/congress/${id}`);
  if (!res.ok) {
    throw new Error("Trade not found");
  }
  const data: TradeWithSignals = await res.json();
  return data;
};
