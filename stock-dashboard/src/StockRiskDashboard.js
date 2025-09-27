import React, { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";
import LiquidEther from "./LiquidEther";
import ClickSpark from "./ClickSpark";
import StarBorder from "./StarBorder";

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
      return "bg-green-900/30 text-green-300 border border-green-700/50";
    case "medium":
      return "bg-yellow-900/30 text-yellow-300 border border-yellow-700/50";
    case "high":
      return "bg-red-900/30 text-red-300 border border-red-700/50";
    default:
      return "bg-gray-900/30 text-gray-300 border border-gray-700/50";
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

  useEffect(() => {
    if (data && data.symbol) {
      generateAISummary();
    }
  }, [data]);

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
    <div className="min-h-screen bg-slate-950 relative overflow-hidden p-6">
      <div className="absolute inset-0 z-0">
        <LiquidEther colors={['#1e293b', '#3b82f6', '#8b5cf6']} />
      </div>
      <div className="max-w-7xl mx-auto relative z-10">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">Stock Risk Dashboard</h1>
          <p className="text-sm text-slate-300">Quick, simple financial stats for everyday investors</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Sidebar */}
          <StarBorder
            as="aside"
            className="md:col-span-1 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-4 flex flex-col gap-4"
            color="#8b5cf6"
            speed="8s"
          >
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Stocks</h2>
              <p className="text-xs text-slate-400">Click a stock to view details</p>
            </div>
            <div className="flex flex-col gap-2 mt-2">
              {STOCKS.map((s) => (
                <StarBorder
                  key={s.symbol}
                  as="div"
                  color="#8b5cf6"
                  speed="3s"
                  className="rounded-xl"
                >
                  <ClickSpark
                    sparkColor="#8b5cf6"
                    sparkCount={12}
                    sparkRadius={25}
                    duration={600}
                  >
                    <button
                      onClick={() => {
                        setSelected(s.symbol);
                        setManualRisk("");
                        setAiSummary("");
                      }}
                      className={`text-left p-3 rounded-xl w-full transition-all flex items-center justify-between ${
                        selected === s.symbol ? "shadow-lg bg-gradient-to-r from-indigo-900/50 to-purple-900/50 border border-indigo-500/50" : "hover:bg-slate-800/50 border border-transparent"
                      }`}
                    >
                      <div>
                        <div className="font-semibold text-white">{s.name}</div>
                        <div className="text-xs text-slate-400">{s.symbol}</div>
                      </div>
                      <div className="text-xs text-slate-500">›</div>
                    </button>
                  </ClickSpark>
                </StarBorder>
              ))}
            </div>

            <div className="mt-auto text-xs text-slate-400">
              Data source: backend scrapes Yahoo Finance. Frontend expects an endpoint at <code className="text-slate-300">/api/stock</code>.
            </div>
          </StarBorder>

          {/* Main content */}
          <main className="md:col-span-3">
            <StarBorder
              as="div"
              className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6"
              color="#3b82f6"
              speed="12s"
            >
              {/* Header row: title, price, sparkline */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-4">
                    <div className="text-lg font-bold text-white">{selected}</div>
                    <div className="text-sm text-slate-400">{data?.shortName}</div>
                  </div>
                  <div className="mt-2 text-3xl font-extrabold">
                    {loading ? (
                      <span className="text-slate-400">Loading…</span>
                    ) : error ? (
                      <span className="text-red-400">Error</span>
                    ) : (
                      <>
                        <span className="text-white">${data?.price?.toFixed(2) ?? "—"}</span>
                        <span className={`ml-3 text-sm ${data && data.changePercent >= 0 ? "text-green-400" : "text-red-400"}`}>
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
                    <div className="flex items-center justify-center h-full text-sm text-slate-500">No chart data</div>
                  )}
                </div>
              </div>

              {/* Risk card and controls */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <StarBorder
                  as="div"
                  className="md:col-span-1 bg-gradient-to-br from-slate-800/50 to-indigo-900/30 backdrop-blur border border-slate-700/50 rounded-xl p-4 flex flex-col gap-4"
                  color="#f59e0b"
                  speed="4s"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-slate-300">Risk Score</div>
                      <div className="text-2xl font-bold mt-1 text-white">{displayRisk() ? displayRisk().score : "—"}</div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${gradeColor(displayRisk()?.grade)}`}>{displayRisk()?.grade ?? "Not graded"}</div>
                  </div>

                  <div className="text-xs text-slate-400">This is the main focal point. You will supply the score from your backend or type it below manually.</div>

                  <div className="flex gap-2">
                    <input
                      value={manualRisk}
                      onChange={(e) => setManualRisk(e.target.value)}
                      placeholder="Enter risk score (0-100)"
                      className="flex-1 rounded-lg border border-slate-600 bg-slate-800/50 text-white px-3 py-2 text-sm placeholder-slate-400"
                      type="number"
                      min={0}
                      max={100}
                    />
                    <ClickSpark
                      sparkColor="#3b82f6"
                      sparkCount={8}
                      sparkRadius={20}
                      duration={400}
                    >
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
                    </ClickSpark>
                  </div>
                </StarBorder>

                {/* Key stats */}
                <div className="md:col-span-2 grid grid-cols-2 gap-4">
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="Market Cap" value={prettyNumber(data?.marketCap)} />
                  </StarBorder>
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="P/E Ratio" value={data?.peRatio ?? "—"} />
                  </StarBorder>
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="Beta" value={data?.beta ?? "—"} />
                  </StarBorder>
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="Dividend Yield" value={data?.dividendYield ? (data.dividendYield * 100).toFixed(2) + "%" : "—"} />
                  </StarBorder>
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="52-week range" value={data ? `${data.week52Low ?? "—"} - ${data.week52High ?? "—"}` : "—"} />
                  </StarBorder>
                  <StarBorder as="div" color="#3b82f6" speed="4s" className="rounded-xl">
                    <Stat title="Volume / Avg" value={data ? `${prettyNumber(data.volume)} / ${prettyNumber(data.avgVolume)}` : "—"} />
                  </StarBorder>
                </div>
              </div>

              {/* AI Summary Section */}
              <div className="mt-6 border-t border-slate-700/50 pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200">AI Investment Summary</h3>
                  {summaryLoading && (
                    <div className="text-sm text-slate-400">Generating summary...</div>
                  )}
                </div>

                <div className="min-h-[120px]">
                  {aiSummary ? (
                    <div className="bg-gradient-to-r from-purple-900/30 to-indigo-900/30 backdrop-blur rounded-xl p-4 border border-purple-500/30">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                          AI
                        </div>
                        <div className="flex-1">
                          <div className="text-sm text-slate-200 leading-relaxed">{aiSummary}</div>
                          <div className="text-xs text-slate-400 mt-2">Generated by Gemini AI</div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-[100px] text-slate-500 text-sm">
                      {summaryLoading ? "Generating AI summary..." : "Select a stock to see AI analysis"}
                    </div>
                  )}
                </div>
              </div>

              {/* More details / explanation */}
              <div className="mt-6 border-t border-slate-700/50 pt-4">
                <h3 className="text-sm font-semibold text-slate-200">What these stats mean</h3>
                <div className="mt-2 text-xs text-slate-400 grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div>
                    <strong className="text-slate-300">Market Cap</strong>
                    <div className="text-xs">Size of the company — gives quick sense of scale.</div>
                  </div>
                  <div>
                    <strong className="text-slate-300">P/E Ratio</strong>
                    <div className="text-xs">Price-to-earnings — how expensive the stock is relative to earnings.</div>
                  </div>
                  <div>
                    <strong className="text-slate-300">Beta</strong>
                    <div className="text-xs">Measures volatility vs market (1 = market-level volatility).</div>
                  </div>
                </div>
              </div>

              {/* Loading / error display */}
              {error && (
                <div className="mt-4 text-sm text-red-400">Error fetching data: {error}</div>
              )}
            </StarBorder>
          </main>
        </div>
      </div>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="bg-slate-800/40 backdrop-blur border border-slate-700/30 rounded-xl p-3 shadow-sm flex flex-col">
      <div className="text-xs text-slate-400">{title}</div>
      <div className="mt-2 font-semibold text-white">{value}</div>
    </div>
  );
}