import { useEffect, useMemo, useState } from "react";
import { fetchTrades } from "./api";
import { DonchianTag, TradeWithSignals } from "./types";

const formatCurrencyRange = (min: number | null, max: number | null) => {
  if (min == null && max == null) {
    return "—";
  }
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  if (min != null && max != null) {
    return `${formatter.format(min)} - ${formatter.format(max)}`;
  }
  if (min != null) {
    return `>${formatter.format(min)}`;
  }
  return `<${formatter.format(max as number)}`;
};

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

const getDonchianChip = (tag: DonchianTag | null | undefined) => {
  if (!tag) {
    return { label: "—", className: "bg-slate-800 text-slate-400" };
  }
  if (tag.breakoutLong) {
    return { label: "Breakout↑", className: "bg-emerald-500/20 text-emerald-300" };
  }
  if (tag.breakdownShort) {
    return { label: "Breakdown↓", className: "bg-rose-500/20 text-rose-300" };
  }
  if (tag.zone === "upper") {
    return { label: "Upper", className: "bg-cyan-500/20 text-cyan-200" };
  }
  if (tag.zone === "mid") {
    return { label: "Mid", className: "bg-amber-500/20 text-amber-200" };
  }
  if (tag.zone === "lower") {
    return { label: "Lower", className: "bg-indigo-500/20 text-indigo-200" };
  }
  return { label: "—", className: "bg-slate-800 text-slate-400" };
};

const getDonchianSummary = (trade: TradeWithSignals | null) => {
  if (!trade || !trade.signals) {
    return "No Donchian data";
  }
  const tag = trade.donchian;
  if (!tag) {
    return "Insufficient Donchian context";
  }
  if (tag.breakoutLong) {
    return "Breakout long above 20-day channel";
  }
  if (tag.breakdownShort) {
    return "Breakdown below 20-day channel";
  }
  switch (tag.zone) {
    case "upper":
      return "Upper-band zone at time of trade";
    case "mid":
      return "Mid-channel congestion zone";
    case "lower":
      return "Lower-band zone pressure";
    default:
      return "Neutral relative to Donchian levels";
  }
};

function App() {
  const [trades, setTrades] = useState<TradeWithSignals[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [filters, setFilters] = useState({ ticker: "", party: "", transaction: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTrades = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchTrades({
          ticker: filters.ticker || undefined,
          party: filters.party || undefined,
          transaction: filters.transaction || undefined,
        });
        setTrades(data);
        setSelectedId((prev) => {
          if (prev && data.some((trade) => trade.id === prev)) {
            return prev;
          }
          return data[0]?.id ?? null;
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load trades");
      } finally {
        setLoading(false);
      }
    };

    loadTrades();
  }, [filters]);

  const selectedTrade = useMemo(
    () => trades.find((trade) => trade.id === selectedId) ?? trades[0] ?? null,
    [selectedId, trades]
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-white">Monarch Congressional Trades</h1>
        <p className="text-sm text-slate-400">Mock dashboard overlaying technical and Donchian signals.</p>
      </header>

      <section className="mb-6 grid gap-4 sm:grid-cols-3">
        <label className="flex flex-col text-sm">
          <span className="mb-1 text-slate-400">Ticker</span>
          <input
            className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
            placeholder="e.g. MSFT"
            value={filters.ticker}
            onChange={(e) => setFilters((prev) => ({ ...prev, ticker: e.target.value }))}
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="mb-1 text-slate-400">Party</span>
          <input
            className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
            placeholder="R / D"
            value={filters.party}
            onChange={(e) => setFilters((prev) => ({ ...prev, party: e.target.value }))}
          />
        </label>
        <label className="flex flex-col text-sm">
          <span className="mb-1 text-slate-400">Transaction</span>
          <select
            className="rounded-md border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
            value={filters.transaction}
            onChange={(e) => setFilters((prev) => ({ ...prev, transaction: e.target.value }))}
          >
            <option value="">Any</option>
            <option value="Purchase">Purchase</option>
            <option value="Sale">Sale</option>
          </select>
        </label>
      </section>

      {error && <p className="mb-4 text-sm text-rose-400">{error}</p>}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-4 py-3">Ticker</th>
                  <th className="px-4 py-3">Politician</th>
                  <th className="px-4 py-3">Party</th>
                  <th className="px-4 py-3">Transaction</th>
                  <th className="px-4 py-3">Amounts</th>
                  <th className="px-4 py-3">Traded</th>
                  <th className="px-4 py-3">Filed</th>
                  <th className="px-4 py-3">Perf</th>
                  <th className="px-4 py-3">Donchian</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-6 text-center text-slate-500">
                      Loading trades…
                    </td>
                  </tr>
                ) : trades.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-6 text-center text-slate-500">
                      No trades match the current filters.
                    </td>
                  </tr>
                ) : (
                  trades.map((trade) => {
                    const isSelected = trade.id === selectedTrade?.id;
                    const chip = getDonchianChip(trade.donchian);
                    return (
                      <tr
                        key={trade.id}
                        className={`border-t border-slate-800/70 ${
                          isSelected ? "bg-slate-800/60" : "hover:bg-slate-800/30"
                        } cursor-pointer`}
                        onClick={() => setSelectedId(trade.id)}
                      >
                        <td className="px-4 py-3 font-semibold text-white">{trade.ticker ?? "—"}</td>
                        <td className="px-4 py-3 text-slate-200">{trade.politicianName}</td>
                        <td className="px-4 py-3 text-slate-400">{trade.party}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`rounded-full px-2 py-1 text-xs font-medium ${
                              trade.transaction === "Purchase"
                                ? "bg-emerald-500/10 text-emerald-300"
                                : "bg-rose-500/10 text-rose-300"
                            }`}
                          >
                            {trade.transaction}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-200">
                          {formatCurrencyRange(trade.amountMin, trade.amountMax)}
                        </td>
                        <td className="px-4 py-3 text-slate-300">{formatDate(trade.tradedDate)}</td>
                        <td className="px-4 py-3 text-slate-300">{formatDate(trade.filedDate)}</td>
                        <td className="px-4 py-3 text-slate-200">
                          {trade.perfSince != null ? `${trade.perfSince.toFixed(1)}%` : "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${chip.className}`}>
                            {chip.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg">
          <h2 className="text-lg font-semibold text-white">Trade Detail</h2>
          {selectedTrade ? (
            <div className="mt-4 space-y-4 text-sm">
              <div>
                <p className="text-slate-200">{selectedTrade.politicianName}</p>
                <p className="text-slate-400 text-xs">
                  {selectedTrade.office} · {selectedTrade.party} · {selectedTrade.stateDistrict ?? "N/A"}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="rounded-lg bg-slate-800/60 p-3">
                  <p className="text-slate-400">Transaction</p>
                  <p className="text-base font-semibold text-white">{selectedTrade.transaction}</p>
                </div>
                <div className="rounded-lg bg-slate-800/60 p-3">
                  <p className="text-slate-400">Amount Range</p>
                  <p className="text-base font-semibold text-white">
                    {formatCurrencyRange(selectedTrade.amountMin, selectedTrade.amountMax)}
                  </p>
                </div>
                <div className="rounded-lg bg-slate-800/60 p-3">
                  <p className="text-slate-400">Traded</p>
                  <p className="text-base font-semibold text-white">{formatDate(selectedTrade.tradedDate)}</p>
                </div>
                <div className="rounded-lg bg-slate-800/60 p-3">
                  <p className="text-slate-400">Filed</p>
                  <p className="text-base font-semibold text-white">{formatDate(selectedTrade.filedDate)}</p>
                </div>
              </div>

              <div className="rounded-lg bg-slate-800/40 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <p className="text-xs uppercase tracking-widest text-slate-400">Technical Snapshot</p>
                  <span className="text-xs text-slate-500">{selectedTrade.ticker}</span>
                </div>
                {selectedTrade.signals ? (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between text-slate-300">
                      <span>RSI 14</span>
                      <span className="text-white">{selectedTrade.signals.rsi14 ?? "—"}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>MACD / Signal / Hist</span>
                      <span className="text-white">
                        {selectedTrade.signals.macd ?? "—"} / {selectedTrade.signals.macdSignal ?? "—"} / {selectedTrade.signals.macdHist ?? "—"}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>SMA 20 / 50 / 200</span>
                      <span className="text-white">
                        {selectedTrade.signals.sma20 ?? "—"} / {selectedTrade.signals.sma50 ?? "—"} / {selectedTrade.signals.sma200 ?? "—"}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Bands Low / High</span>
                      <span className="text-white">
                        {selectedTrade.signals.bandLower ?? "—"} / {selectedTrade.signals.bandUpper ?? "—"}
                      </span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span>Donchian 20 H / M / L</span>
                      <span className="text-white">
                        {selectedTrade.signals.donchianHigh20 ?? "—"} / {selectedTrade.signals.donchianMid20 ?? "—"} / {selectedTrade.signals.donchianLow20 ?? "—"}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{getDonchianSummary(selectedTrade)}</p>
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No technical data available.</p>
                )}
              </div>

              {selectedTrade.description && (
                <div>
                  <p className="text-xs uppercase tracking-widest text-slate-500">Notes</p>
                  <p className="text-sm text-slate-200">{selectedTrade.description}</p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-400">Select a trade to view details.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
