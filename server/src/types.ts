export type TransactionType = "Purchase" | "Sale";

export interface CongressTrade {
  id: number;
  ticker: string | null;
  securityName: string;
  assetType: string;
  transaction: TransactionType;
  amountMin: number | null;
  amountMax: number | null;
  politicianName: string;
  office: string;
  party: "R" | "D" | "I" | string;
  stateDistrict: string | null;
  filedDate: string;
  tradedDate: string;
  ownerType: string | null;
  description: string | null;
  perfSince: number | null;
}

export interface TechSignals {
  ticker: string;
  date: string;
  rsi14: number | null;
  macd: number | null;
  macdSignal: number | null;
  macdHist: number | null;
  sma20: number | null;
  sma50: number | null;
  sma200: number | null;
  bandUpper: number | null;
  bandLower: number | null;
  donchianHigh20: number | null;
  donchianLow20: number | null;
  donchianMid20: number | null;
}

export interface DonchianTag {
  breakoutLong: boolean;
  breakdownShort: boolean;
  zone: "upper" | "mid" | "lower" | null;
}

export interface TradeWithSignals extends CongressTrade {
  signals: TechSignals | null;
  donchian?: DonchianTag | null;
}
