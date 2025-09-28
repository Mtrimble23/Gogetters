import React, { useEffect, useState } from "react";
import LiquidEther from "./LiquidEther";
import ClickSpark from "./ClickSpark";
import StockChart from "./StockChart";

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
  { symbol: "NVDA", name: "NVIDIA" },
  { symbol: "TSLA", name: "Tesla" }
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
      // Fetch both stock data and risk analysis from backend
      const [stockRes, riskRes] = await Promise.all([
        fetch(`http://localhost:8000/stock/${encodeURIComponent(sym)}`),
        fetch(`http://localhost:8000/risk-level/${encodeURIComponent(sym)}`)
      ]);

      if (!stockRes.ok) throw new Error(`Stock API error: ${stockRes.status}`);
      if (!riskRes.ok) throw new Error(`Risk API error: ${riskRes.status}`);

      const stockResponse = await stockRes.json();
      const riskResponse = await riskRes.json();

      const stockData = stockResponse.data;
      const riskData = riskResponse.data;

      // Combine real API data
      const combinedData = {
        symbol: sym,
        shortName: STOCKS.find(s => s.symbol === sym)?.name + " Inc." || sym,
        price: stockData.current_price,
        changePercent: stockData.price_change_percent,
        marketCap: stockData.market_cap,
        peRatio: stockData.pe_ratio,
        beta: stockData.beta,
        week52Low: stockData.fifty_two_week_low,
        week52High: stockData.fifty_two_week_high,
        volume: stockData.volume,
        avgVolume: stockData.avg_volume,
        dividendYield: stockData.dividend_yield,
        debtToEquity: stockData.debt_to_equity,
        cboeVolatility: riskData.financial_data?.cboe_volatility,
        price_history: stockData.price_history, // Add historical data for chart
        risk: {
          score: Math.round((riskData.risk_analysis?.risk_score || 0) * 100),
          grade: riskData.risk_analysis?.risk_level?.charAt(0).toUpperCase() + riskData.risk_analysis?.risk_level?.slice(1) || "Medium"
        }
      };

      setData(combinedData);
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
      // Try the new AI summary endpoint first
      const res = await fetch(`http://localhost:8000/ai-summary/${encodeURIComponent(data.symbol)}`);

      if (res.ok) {
        const result = await res.json();
        if (result.success) {
          setAiSummary(result.data.summary);
          return;
        }
      }

      // Fallback to generating a summary based on available data
      const risk = displayRisk();
      const symbol = data.symbol;
      const price = data.price;
      const changePercent = data.changePercent;
      const peRatio = data.peRatio;
      const beta = data.beta;

      // Generate intelligent summary based on financial metrics
      let summary = `${symbol} is currently trading at $${price?.toFixed(2) || 'N/A'}`;

      if (changePercent !== null) {
        const direction = changePercent >= 0 ? 'up' : 'down';
        summary += `, ${direction} ${Math.abs(changePercent).toFixed(2)}% today. `;
      } else {
        summary += '. ';
      }

      // Risk assessment
      if (risk?.grade) {
        summary += `The stock shows ${risk.grade.toLowerCase()} risk characteristics `;
        if (risk.score > 70) {
          summary += `with elevated volatility concerns. `;
        } else if (risk.score < 30) {
          summary += `indicating stable fundamentals. `;
        } else {
          summary += `suggesting balanced risk-reward potential. `;
        }
      }

      // PE ratio analysis
      if (peRatio && peRatio > 0) {
        if (peRatio > 30) {
          summary += `Trading at a premium P/E of ${peRatio.toFixed(1)}x, suggesting high growth expectations. `;
        } else if (peRatio < 15) {
          summary += `Attractively valued at ${peRatio.toFixed(1)}x P/E ratio. `;
        } else {
          summary += `Reasonably valued at ${peRatio.toFixed(1)}x earnings. `;
        }
      }

      // Beta analysis
      if (beta && beta > 0) {
        if (beta > 1.2) {
          summary += `High beta of ${beta.toFixed(2)} indicates above-average volatility relative to the market.`;
        } else if (beta < 0.8) {
          summary += `Low beta of ${beta.toFixed(2)} suggests lower volatility than the broader market.`;
        } else {
          summary += `Beta of ${beta.toFixed(2)} indicates market-level volatility.`;
        }
      }

      // Add investment recommendation based on metrics
      if (risk?.score && risk.score < 40 && peRatio && peRatio < 25) {
        summary += ` Overall metrics suggest a potentially attractive investment opportunity.`;
      } else if (risk?.score && risk.score > 70) {
        summary += ` Current metrics warrant careful consideration due to elevated risk factors.`;
      } else {
        summary += ` Mixed signals suggest a balanced approach to position sizing.`;
      }

      setAiSummary(summary);

    } catch (e) {
      console.error('AI Summary generation failed:', e);
      setAiSummary('AI analysis temporarily unavailable. Please check that the backend services are running.');
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
          <aside className="md:col-span-1 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-4 flex flex-col gap-4 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-2xl hover:bg-slate-400/5">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Stocks</h2>
              <p className="text-xs text-slate-400">Click a stock to view details</p>
            </div>
            <div className="flex flex-col gap-2 mt-2">
              {STOCKS.map((s) => (
                <div key={s.symbol} className="rounded-xl border border-slate-700/50 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg hover:bg-slate-400/5">
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
                </div>
              ))}
            </div>

            <div className="mt-auto text-xs text-slate-400">
              Data source: backend scrapes Yahoo Finance. Frontend expects an endpoint at <code className="text-slate-300">/api/stock</code>.
            </div>
          </aside>

          {/* Main content */}
          <main className="md:col-span-3">
            <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-2xl hover:bg-slate-400/5">
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

              </div>

              {/* Risk card and graph placeholder */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Risk Score */}
                <div className="md:col-span-1 bg-gradient-to-br from-slate-800/50 to-indigo-900/30 backdrop-blur border border-slate-700/50 rounded-xl p-4 flex flex-col gap-4 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg hover:bg-slate-400/5" title="Overall risk assessment based on multiple financial factors">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-slate-300">Risk Score</div>
                      <div className="text-2xl font-bold mt-1 text-white">{displayRisk() ? displayRisk().score : "—"}</div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${gradeColor(displayRisk()?.grade)}`}>{displayRisk()?.grade ?? "Not graded"}</div>
                  </div>

                  <div className="text-xs text-slate-400">Real-time risk analysis from backend data.</div>

                  <div className="flex gap-2">
                    <input
                      value={manualRisk}
                      onChange={(e) => setManualRisk(e.target.value)}
                      placeholder="Override risk score (0-100)"
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
                          if (manualRisk === "") return;
                        }}
                        className="px-3 py-2 rounded-lg bg-indigo-600 text-white text-sm"
                      >
                        Apply
                      </button>
                    </ClickSpark>
                  </div>
                </div>

                {/* Stock Chart */}
                <div className="md:col-span-2 bg-gradient-to-br from-slate-800/30 to-purple-900/20 backdrop-blur border border-slate-700/50 rounded-xl p-6 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg hover:bg-slate-400/5">
                  {loading ? (
                    <div className="flex items-center justify-center h-full text-slate-400">
                      <div className="text-center">
                        <div className="text-sm">Loading chart...</div>
                      </div>
                    </div>
                  ) : error ? (
                    <div className="flex items-center justify-center h-full text-red-400">
                      <div className="text-center">
                        <div className="text-sm">Chart unavailable</div>
                        <div className="text-xs mt-1">{error}</div>
                      </div>
                    </div>
                  ) : (
                    <StockChart data={data} symbol={selected} />
                  )}
                </div>
              </div>

              {/* Financial Metrics Grid */}
              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatBox
                  title="% Yield"
                  value={data?.dividendYield ? (data.dividendYield).toFixed(2) + "%" : "—"}
                  tooltip="Dividend yield - annual dividends as a percentage of stock price"
                />
                <StatBox
                  title="Beta"
                  value={data?.beta ? data.beta.toFixed(3) : "—"}
                  tooltip="Beta - measures stock volatility relative to the market (1.0 = market volatility)"
                />
                <StatBox
                  title="52 Week Range"
                  value={data ? `$${data.week52Low?.toFixed(2) ?? "—"} - $${data.week52High?.toFixed(2) ?? "—"}` : "—"}
                  tooltip="52-week high and low prices - shows the stock's trading range over the past year"
                />
                <StatBox
                  title="P/E Ratio"
                  value={data?.peRatio ? data.peRatio.toFixed(2) : "—"}
                  tooltip="Price-to-Earnings ratio - how much investors pay per dollar of earnings"
                />
                <StatBox
                  title="CBOE Volatility"
                  value={data?.cboeVolatility ? data.cboeVolatility.toFixed(2) + "%" : "—"}
                  tooltip="CBOE-style volatility index - measures expected stock price fluctuations"
                />
                <StatBox
                  title="D/E Ratio"
                  value={data?.debtToEquity ? data.debtToEquity.toFixed(2) : "—"}
                  tooltip="Debt-to-Equity ratio - measures financial leverage (debt relative to shareholder equity)"
                />
                <StatBox
                  title="Price per Share"
                  value={data?.price ? `$${data.price.toFixed(2)}` : "—"}
                  tooltip="Current stock price per share"
                />
                <StatBox
                  title="Price Change Today"
                  value={data?.changePercent != null ? `${data.changePercent >= 0 ? "+" : ""}${data.changePercent.toFixed(2)}%` : "—"}
                  valueColor={data?.changePercent != null ? (data.changePercent >= 0 ? "text-green-400" : "text-red-400") : "text-white"}
                  tooltip="Percentage change in stock price from previous trading day"
                />
              </div>

              {/* AI Summary Section */}
              <div className="mt-6 border-t border-slate-700/50 pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-200">AI Investment Summary</h3>
                  {summaryLoading && (
                    <div className="text-sm text-slate-400">Analyzing news sentiment...</div>
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
                          <div className="text-xs text-slate-400 mt-2">
                            Powered by Yahoo Finance News + Sentiment Analysis
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-[100px] text-slate-500 text-sm">
                      {summaryLoading ? "Analyzing news and market sentiment..." : "Select a stock to see AI news analysis"}
                    </div>
                  )}
                </div>
              </div>


              {/* Loading / error display */}
              {error && (
                <div className="mt-4 text-sm text-red-400">Error fetching data: {error}</div>
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
    <div className="bg-slate-800/40 backdrop-blur rounded-xl p-3 shadow-sm flex flex-col h-full">
      <div className="text-xs text-slate-400">{title}</div>
      <div className="mt-2 font-semibold text-white">{value}</div>
    </div>
  );
}

function StatBox({ title, value, tooltip, valueColor = "text-white" }) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      className="relative bg-slate-800/40 backdrop-blur rounded-xl p-4 shadow-sm flex flex-col h-full transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg hover:bg-slate-400/5 border border-slate-700/50 cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="text-xs text-slate-400 mb-2">{title}</div>
      <div className={`text-lg font-semibold ${valueColor}`}>{value}</div>

      {showTooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 text-white text-xs rounded-lg shadow-lg border border-slate-700 max-w-64 z-50">
          <div className="text-center">{tooltip}</div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-slate-900"></div>
        </div>
      )}
    </div>
  );
}