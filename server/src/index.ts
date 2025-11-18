import cors from "cors";
import express from "express";
import { mockTrades } from "./mockData";
import { DonchianTag, TradeWithSignals } from "./types";

const app = express();
app.use(cors());
app.use(express.json());

const computeDonchianTag = (trade: TradeWithSignals): DonchianTag | null => {
  const signals = trade.signals;
  if (!signals) {
    return null;
  }

  const { donchianHigh20, donchianLow20, donchianMid20, sma20 } = signals;
  const price = sma20;

  if (
    price == null ||
    donchianHigh20 == null ||
    donchianLow20 == null ||
    donchianMid20 == null
  ) {
    return null;
  }

  let zone: DonchianTag["zone"] = null;
  if (price >= donchianMid20 && price <= donchianHigh20) {
    zone = "upper";
  } else if (price < donchianMid20 && price > donchianLow20) {
    zone = "mid";
  } else if (price <= donchianLow20) {
    zone = "lower";
  }

  const tag: DonchianTag = {
    breakoutLong: false,
    breakdownShort: false,
    zone,
  };

  if (trade.transaction === "Purchase" && price > donchianHigh20) {
    tag.breakoutLong = true;
    tag.zone = "upper";
  } else if (trade.transaction === "Sale" && price < donchianLow20) {
    tag.breakdownShort = true;
    tag.zone = "lower";
  }

  return tag;
};

const attachDonchian = (trade: TradeWithSignals): TradeWithSignals => ({
  ...trade,
  donchian: computeDonchianTag(trade),
});

const filterTrades = (params: {
  ticker?: string;
  party?: string;
  transaction?: string;
}): TradeWithSignals[] => {
  const { ticker, party, transaction } = params;
  return mockTrades.filter((trade) => {
    if (ticker && trade.ticker?.toLowerCase() !== ticker.toLowerCase()) {
      return false;
    }
    if (party && trade.party.toLowerCase() !== party.toLowerCase()) {
      return false;
    }
    if (transaction && trade.transaction.toLowerCase() !== transaction.toLowerCase()) {
      return false;
    }
    return true;
  });
};

app.get("/api/trades/congress", (req, res) => {
  const trades = filterTrades({
    ticker: typeof req.query.ticker === "string" ? req.query.ticker : undefined,
    party: typeof req.query.party === "string" ? req.query.party : undefined,
    transaction:
      typeof req.query.transaction === "string" ? req.query.transaction : undefined,
  }).map(attachDonchian);

  res.json(trades);
});

app.get("/api/trades/congress/:id", (req, res) => {
  const trade = mockTrades.find((t) => t.id === Number(req.params.id));
  if (!trade) {
    res.status(404).json({ message: "Trade not found" });
    return;
  }

  res.json(attachDonchian(trade));
});

app.get("/api/trades/congress/signals", (req, res) => {
  const bullishOnly = req.query.bullishOnly === "true";
  const donchianBreakoutsOnly = req.query.donchianBreakoutsOnly === "true";

  let trades = mockTrades.filter((trade) => trade.signals !== null);

  if (bullishOnly) {
    trades = trades.filter((trade) => {
      const signals = trade.signals;
      if (!signals) {
        return false;
      }
      return (signals.rsi14 ?? 0) > 55 && (signals.macdHist ?? 0) > 0;
    });
  }

  if (donchianBreakoutsOnly) {
    trades = trades.filter((trade) => {
      const tag = computeDonchianTag(trade);
      return Boolean(tag?.breakoutLong || tag?.breakdownShort);
    });
  }

  res.json(trades.map(attachDonchian));
});

const port = Number(process.env.PORT ?? 4000);
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
