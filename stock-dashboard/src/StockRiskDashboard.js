import React, { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

// Single-file React component (Tailwind CSS required in the app)
// Usage: place this component inside your React app. The frontend expects a backend API endpoint:
// GET /api/stock?symbol=SYMBOL
// which should return JSON like:
// {
//   symbol: "AAPL",
//   shortName: "Apple Inc.",
//   price: 192.34,
//   changePercent: -0.84,
//   marketCap: 3.0e12,
//   peRatio: 28.4,
//   beta: 1.12,
//   week52Low: 120.23,
//   week52High: 203.45,
//   volume: 52_000_000,
//   avgVolume: 60_000_000,
//   dividendYield: 0.005,
//   historical: [{t: "2025-09-01", p: 180}, ...], // for sparkline
//   risk: { score: 72, grade: "Medium" } // optional — your backend or manual input can supply this
// }

const STOCKS = [
  { symbol: "AAPL", name: "Apple" },
  { symbol: "AMZN", name: "Amazon" },
  { symbol: "GOOGL", name: "Google" },
  { symbol: "META", name: "Meta" },
  { symbol: "NVDA", name: "NVIDIA" }
];

function prettyNumber(n) {
  if (n == null) return "—";
  if (n >= 1e12) return (n / 1e12).toFixed(2) + "T";
  if (n >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (n >= 1e6) return (n / 1e6).toFixed(2) + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(1) + "k";
  return n.toString();
}

function gradeColor(grade) {
  switch ((grade || "").toLowerCase()) {
    case "low":
      return "bg-green-100 text-green-800";
    case "medium":
      return "bg-yellow-100 text-yellow-800";
    case "high":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
}

export default function StockRiskDashboard() {
  const [selected, setSelected] = useState(STOCKS[0].symbol);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [manualRisk, setManualRisk] = useState("");
  const [aiSummary, setAiSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    fetchStock(selected);
  }, [selected]);

  async function fetchStock(sym) {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      // Frontend assumes backend scrapes Yahoo Finance for you.
      const res = await fetch(`/api/stock?symbol=${encodeURIComponent(sym)}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const json = await res.json();
      // normalize historical prices for sparkline
      if (json.historical && Array.isArray(json.historical)) {
        json.spark = json.historical.map((p) => ({ value: p.p || p.price }));
      } else {
        json.spark = [];
      }
      setData(json);
    } catch (e) {
      console.error(e);
      setError(e.message || "Failed to fetch");
    } finally {
      setLoading(false);
    }
  }

  const displayRisk = () => {
    if (manualRisk) return { score: parseFloat(manualRisk), grade: inferGrade(manualRisk) };
    if (data && data.risk) return data.risk;
    return null;
  };

  function inferGrade(score) {
    const s = parseFloat(score);
    if (Number.isNaN(s)) return "";
    if (s <= 33) return "Low";
    if (s <= 66) return "Medium";
    return "High";
  }

  async function generateAISummary() {
    if (!data) return;

    setSummaryLoading(true);
    try {
      const risk = displayRisk();
      const summaryData = {
        symbol: data.symbol,
        price: data.price,
        changePercent: data.changePercent,
        marketCap: data.marketCap,
        peRatio: data.peRatio,
        beta: data.beta,
        riskScore: risk?.score,
        riskGrade: risk?.grade
      };

      const res = await fetch('/api/stock/summary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(summaryData)
      });

      if (!res.ok) throw new Error(`Summary API error: ${res.status}`);
      const result = await res.json();

      if (result.success) {
        setAiSummary(result.summary);
      } else {
        throw new Error(result.error || 'Failed to generate summary');
      }
    } catch (e) {
      console.error('Summary generation failed:', e);
      setAiSummary('Failed to generate AI summary. Please try again.');
    } finally {
      setSummaryLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white p-6">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl md:text-3xl font-extrabold">Stock Risk Dashboard</h1>
          <p className="text-sm text-slate-600">Quick, simple financial stats for everyday investors</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Sidebar */}
          <aside className="md:col-span-1 bg-white rounded-2xl shadow p-4 flex flex-col gap-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-700">Stocks</h2>
              <p className="text-xs text-slate-500">Click a stock to view details</p>
            </div>
            <div className="flex flex-col gap-2 mt-2">
              {STOCKS.map((s) => (
                <button
                  key={s.symbol}
                  onClick={() => {
                    setSelected(s.symbol);
                    setManualRisk("");
                    setAiSummary("");
                  }}
                  className={`text-left p-3 rounded-xl w-full transition-shadow flex items-center justify-between ${
                    selected === s.symbol ? "shadow-lg bg-gradient-to-r from-indigo-50 to-white" : "hover:bg-slate-50"
                  }`}
                >
                  <div>
                    <div className="font-semibold">{s.name}</div>
                    <div className="text-xs text-slate-500">{s.symbol}</div>
                  </div>
                  <div className="text-xs text-slate-400">›</div>
                </button>
              ))}
            </div>

            <div className="mt-auto text-xs text-slate-500">
              Data source: backend scrapes Yahoo Finance. Frontend expects an endpoint at <code>/api/stock</code>.
            </div>
          </aside>

          {/* Main content */}
          <main className="md:col-span-3">
            <div className="bg-white rounded-2xl shadow p-6">
              {/* Header row: title, price, sparkline */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-4">
                    <div className="text-lg font-bold">{selected}</div>
                    <div className="text-sm text-slate-500">{data?.shortName}</div>
                  </div>
                  <div className="mt-2 text-3xl font-extrabold">
                    {loading ? (
                      <span className="text-slate-400">Loading…</span>
                    ) : error ? (
                      <span className="text-red-500">Error</span>
                    ) : (
                      <>
                        <span>${data?.price?.toFixed(2) ?? "—"}</span>
                        <span className={`ml-3 text-sm ${data && data.changePercent >= 0 ? "text-green-600" : "text-red-600"}`}>
                          {data && data.changePercent != null ? `${data.changePercent >= 0 ? "+" : ""}${data.changePercent.toFixed(2)}%` : ""}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="w-full md:w-1/3 h-28">
                  {data && data.spark && data.spark.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.spark.map((d) => ({ value: d.value }))}>
                        <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-sm text-slate-400">No chart data</div>
                  )}
                </div>
              </div>

              {/* Risk card and controls */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-1 bg-gradient-to-br from-white to-indigo-50 rounded-xl p-4 flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-slate-600">Risk Score</div>
                      <div className="text-2xl font-bold mt-1">{displayRisk() ? displayRisk().score : "—"}</div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${gradeColor(displayRisk()?.grade)}`}>{displayRisk()?.grade ?? "Not graded"}</div>
                  </div>

                  <div className="text-xs text-slate-500">This is the main focal point. You will supply the score from your backend or type it below manually.</div>

                  <div className="flex gap-2">
                    <input
                      value={manualRisk}
                      onChange={(e) => setManualRisk(e.target.value)}
                      placeholder="Enter risk score (0-100)"
                      className="flex-1 rounded-lg border px-3 py-2 text-sm"
                      type="number"
                      min={0}
                      max={100}
                    />
                    <button
                      onClick={() => {
                        // If user clears manual risk, we keep backend value
                        if (manualRisk === "") return;
                        // no-op — the UI will reflect manualRisk; you can optionally POST this to your backend
                      }}
                      className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm"
                    >
                      Apply
                    </button>
                  </div>
                </div>

                {/* Key stats */}
                <div className="md:col-span-2 grid grid-cols-2 gap-4">
                  <Stat title="Market Cap" value={prettyNumber(data?.marketCap)} />
                  <Stat title="P/E Ratio" value={data?.peRatio ?? "—"} />
                  <Stat title="Beta" value={data?.beta ?? "—"} />
                  <Stat title="Dividend Yield" value={data?.dividendYield ? (data.dividendYield * 100).toFixed(2) + "%" : "—"} />
                  <Stat title="52-week range" value={data ? `${data.week52Low ?? "—"} - ${data.week52High ?? "—"}` : "—"} />
                  <Stat title="Volume / Avg" value={data ? `${prettyNumber(data.volume)} / ${prettyNumber(data.avgVolume)}` : "—"} />
                </div>
              </div>

              {/* AI Summary Section */}
              <div className="mt-6 border-t pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold">AI Investment Summary</h3>
                  <button
                    onClick={generateAISummary}
                    disabled={summaryLoading || !data}
                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {summaryLoading ? "Generating..." : "Generate AI Summary"}
                  </button>
                </div>

                {aiSummary && (
                  <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-4 border border-purple-100">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                        AI
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-slate-700 leading-relaxed">{aiSummary}</div>
                        <div className="text-xs text-slate-500 mt-2">Generated by Gemini AI</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* More details / explanation */}
              <div className="mt-6 border-t pt-4">
                <h3 className="text-sm font-semibold">What these stats mean</h3>
                <div className="mt-2 text-xs text-slate-600 grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div>
                    <strong>Market Cap</strong>
                    <div className="text-xs">Size of the company — gives quick sense of scale.</div>
                  </div>
                  <div>
                    <strong>P/E Ratio</strong>
                    <div className="text-xs">Price-to-earnings — how expensive the stock is relative to earnings.</div>
                  </div>
                  <div>
                    <strong>Beta</strong>
                    <div className="text-xs">Measures volatility vs market (1 = market-level volatility).</div>
                  </div>
                </div>
              </div>

              {/* Loading / error display */}
              {error && (
                <div className="mt-4 text-sm text-red-600">Error fetching data: {error}</div>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm flex flex-col">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-2 font-semibold">{value}</div>
    </div>
  );
}