import React, { useEffect, useState } from "react";
import LiquidEther from "./LiquidEther";
import ClickSpark from "./ClickSpark";
import StockChart from "./StockChart";
import TextType from "./TextType";
import Papa from "papaparse";

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

function getRiskLabel(percentage) {
  if (percentage >= 0 && percentage <= 25) return "Low";
  if (percentage > 25 && percentage <= 45) return "Low-Medium";
  if (percentage > 45 && percentage <= 65) return "Medium";
  if (percentage > 65 && percentage <= 80) return "Medium-High";
  if (percentage > 80) return "High";
  return "Unknown";
}

function getRiskGradient(percentage) {
  if (percentage >= 0 && percentage <= 25) {
    // Green gradient (low risk)
    const intensity = percentage / 25;
    return `linear-gradient(135deg, rgba(34, 197, 94, ${0.2 + intensity * 0.3}) 0%, rgba(21, 128, 61, ${0.3 + intensity * 0.4}) 100%)`;
  }
  if (percentage > 25 && percentage <= 45) {
    // Yellow-green gradient (low-medium risk)
    const intensity = (percentage - 25) / 20;
    return `linear-gradient(135deg, rgba(132, 204, 22, ${0.2 + intensity * 0.3}) 0%, rgba(101, 163, 13, ${0.3 + intensity * 0.4}) 100%)`;
  }
  if (percentage > 45 && percentage <= 65) {
    // Yellow gradient (medium risk)
    const intensity = (percentage - 45) / 20;
    return `linear-gradient(135deg, rgba(234, 179, 8, ${0.2 + intensity * 0.3}) 0%, rgba(161, 98, 7, ${0.3 + intensity * 0.4}) 100%)`;
  }
  if (percentage > 65 && percentage <= 80) {
    // Orange gradient (medium-high risk)
    const intensity = (percentage - 65) / 15;
    return `linear-gradient(135deg, rgba(249, 115, 22, ${0.2 + intensity * 0.3}) 0%, rgba(194, 65, 12, ${0.3 + intensity * 0.4}) 100%)`;
  }
  if (percentage > 80) {
    // Red gradient (high risk)
    const intensity = Math.min((percentage - 80) / 20, 1);
    return `linear-gradient(135deg, rgba(239, 68, 68, ${0.3 + intensity * 0.4}) 0%, rgba(153, 27, 27, ${0.4 + intensity * 0.5}) 100%)`;
  }
  return "linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(75, 85, 99, 0.3) 100%)";
}

function getRiskTextColor(percentage) {
  if (percentage >= 0 && percentage <= 25) return "text-green-300";
  if (percentage > 25 && percentage <= 45) return "text-lime-300";
  if (percentage > 45 && percentage <= 65) return "text-yellow-300";
  if (percentage > 65 && percentage <= 80) return "text-orange-300";
  if (percentage > 80) return "text-red-300";
  return "text-gray-300";
}

// Trading Algorithm Page Component
function TradingPage({ currentPage, switchPage }) {
  const [selectedStock, setSelectedStock] = useState("AAPL");
  const [stockData, setStockData] = useState(null);
  const [tradingData, setTradingData] = useState([]);
  const [animationProgress, setAnimationProgress] = useState(0);
  const [currentPortfolioValue, setCurrentPortfolioValue] = useState(10000);
  const [isAnimating, setIsAnimating] = useState(false);
  const [animationSpeed] = useState(100); // milliseconds between trades

  // Load stock data for selected symbol
  useEffect(() => {
    fetchStockData(selectedStock);
    loadTradingData();
  }, [selectedStock]);

  const fetchStockData = async (symbol) => {
    try {
      // Use the same endpoints as the dashboard for consistency
      const response = await fetch(`http://localhost:8000/stock/${symbol}`);
      const result = await response.json();
      if (result.success) {
        setStockData(result.data);
      }
    } catch (error) {
      console.error("Error fetching stock data:", error);
    }
  };

  const loadTradingData = async () => {
    try {
      const response = await fetch('/data/trading_decisions_20250928_024735.csv');
      const csvText = await response.text();

      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          const filteredData = results.data
            .filter(row => row.date && row.signal)
            .map(row => ({
              date: new Date(row.date),
              signal: row.signal.toUpperCase(),
              confidence: parseFloat(row.confidence),
              price: parseFloat(row.price),
              portfolioValue: parseFloat(row.portfolio_value)
            }))
            .sort((a, b) => a.date - b.date);

          setTradingData(filteredData);
          setAnimationProgress(0);
          setCurrentPortfolioValue(10000);
        }
      });
    } catch (error) {
      console.error("Error loading trading data:", error);
    }
  };

  // Start animation when both stock data and trading data are ready
  useEffect(() => {
    if (tradingData.length > 0 && stockData) {
      // Wait 2 seconds for chart to load, then start animation
      setTimeout(() => {
        startAnimation();
      }, 2000);
    }
  }, [tradingData, stockData]);

  const startAnimation = () => {
    setIsAnimating(true);
    setAnimationProgress(0);
    setCurrentPortfolioValue(10000);

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex >= tradingData.length) {
        setIsAnimating(false);
        clearInterval(interval);
        return;
      }

      setAnimationProgress(currentIndex + 1);
      setCurrentPortfolioValue(tradingData[currentIndex].portfolioValue);
      currentIndex++;
    }, animationSpeed);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative">
      <div className="max-w-7xl mx-auto relative z-10 p-6">
        <header className="flex items-center justify-between mb-8">
          <div>
            <TextType
              text={["Trading Algorithm", "AI Strategy Builder", "Market Automation"]}
              as="h1"
              className="text-2xl md:text-3xl font-extrabold text-white"
              typingSpeed={75}
              pauseDuration={1500}
              showCursor={true}
              cursorCharacter="|"
              textColors={["#ffffff", "#f59e0b", "#ef4444"]}
            />
            <p className="text-sm text-slate-300 mt-2">Advanced algorithmic trading strategies and automation</p>
          </div>
          <div className="flex items-center gap-4">
            {/* Page Toggle */}
            <div className="flex items-center bg-slate-800/60 backdrop-blur rounded-lg p-1 border border-slate-700/50">
              <button
                onClick={() => switchPage("dashboard")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  currentPage === "dashboard"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-300 hover:text-white hover:bg-slate-700/50"
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => switchPage("trading")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  currentPage === "trading"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-300 hover:text-white hover:bg-slate-700/50"
                }`}
              >
                Trading
              </button>
            </div>
            <p className="text-sm text-slate-300">Automated strategies and intelligent market execution</p>
          </div>
        </header>

        {/* Main Trading Visualization Container */}
        <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl p-6 h-[calc(100vh-160px)]">
          {/* Top Controls */}
          <div className="flex items-center justify-between mb-6">
            {/* Stock Selector */}
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-slate-300">Stock:</label>
              <select
                value={selectedStock}
                onChange={(e) => setSelectedStock(e.target.value)}
                className="bg-slate-800/60 border border-slate-700/50 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {STOCKS.map(stock => (
                  <option key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} - {stock.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Portfolio Value */}
            <div className="text-right">
              <div className="text-sm text-slate-400">Portfolio Value</div>
              <div className="text-2xl font-bold text-green-400">
                ${currentPortfolioValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              {isAnimating && (
                <div className="text-xs text-blue-400">
                  Progress: {animationProgress}/{tradingData.length} trades
                </div>
              )}
            </div>
          </div>

          {/* Chart Container */}
          <div className="h-[550px] bg-slate-800/20 rounded-lg p-4 relative">
            {stockData ? (
              <TradingChart
                stockData={stockData}
                tradingData={tradingData.slice(0, animationProgress)}
                selectedStock={selectedStock}
                animationProgress={animationProgress}
                totalTrades={tradingData.length}
                isAnimating={isAnimating}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-slate-400">Loading chart data...</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Trading Chart Component
function TradingChart({ stockData, tradingData, selectedStock, animationProgress, totalTrades, isAnimating }) {
  const canvasRef = React.useRef(null);
  const [hoverData, setHoverData] = React.useState(null);
  const [mousePos, setMousePos] = React.useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!stockData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Set canvas size with better padding for axis labels
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const width = rect.width;
    const height = rect.height;
    const padding = { top: 40, right: 40, bottom: 60, left: 80 };

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Use the YTD historical data from the API response
    const ytdHistory = stockData.ytd_history;

    if (!ytdHistory || !ytdHistory.dates || !ytdHistory.prices) {
      // Draw "No data" message
      ctx.fillStyle = '#94a3b8';
      ctx.font = '16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Loading historical data...', width / 2, height / 2);
      return;
    }

    // Convert to the format we need: {date, price}
    const historical = ytdHistory.dates.map((date, index) => ({
      date: date,
      price: ytdHistory.prices[index]
    }));

    // Data is already sorted chronologically
    const sortedHistorical = historical;

    // Get price range from sorted data (format: {date, price})
    const prices = sortedHistorical.map(h => h.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;

    // Draw chart area and axes
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Draw main axes
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 2;
    ctx.beginPath();
    // Y-axis
    ctx.moveTo(padding.left, padding.top);
    ctx.lineTo(padding.left, height - padding.bottom);
    // X-axis
    ctx.lineTo(width - padding.right, height - padding.bottom);
    ctx.stroke();

    // Draw gridlines
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 0.5;

    // Horizontal gridlines (price levels)
    const numHorizontalLines = 6;
    for (let i = 1; i < numHorizontalLines; i++) {
      const y = padding.top + (i / numHorizontalLines) * chartHeight;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();
    }

    // Vertical gridlines (time intervals)
    const numVerticalLines = 8;
    for (let i = 1; i < numVerticalLines; i++) {
      const x = padding.left + (i / numVerticalLines) * chartWidth;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, height - padding.bottom);
      ctx.stroke();
    }

    // Draw price line
    ctx.strokeStyle = '#60a5fa';
    ctx.lineWidth = 2;
    ctx.beginPath();

    sortedHistorical.forEach((point, index) => {
      const price = point.price;
      const x = padding.left + (index / (sortedHistorical.length - 1)) * chartWidth;
      const y = height - padding.bottom - ((price - minPrice) / priceRange) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw trading signals
    tradingData.forEach(trade => {
      // Find closest historical point
      const tradeDate = trade.date;
      let closestIndex = 0;
      let closestDiff = Math.abs(new Date(sortedHistorical[0].date) - tradeDate);

      sortedHistorical.forEach((point, index) => {
        const pointDate = new Date(point.date);
        const diff = Math.abs(pointDate - tradeDate);
        if (diff < closestDiff) {
          closestDiff = diff;
          closestIndex = index;
        }
      });

      if (closestIndex >= 0) {
        const x = padding.left + (closestIndex / (sortedHistorical.length - 1)) * chartWidth;
        const price = sortedHistorical[closestIndex].price;
        const baseY = height - padding.bottom - ((price - minPrice) / priceRange) * chartHeight;

        // Draw candlestick-style trading signal
        const candleHeight = 30;
        const candleWidth = 5;
        const wickWidth = 1;

        if (trade.signal === 'BUY') {
          // Green candlestick (bullish)
          ctx.fillStyle = '#22c55e';
          ctx.strokeStyle = '#16a34a';
          ctx.lineWidth = 1;

          // Draw wick (thin line extending up)
          ctx.beginPath();
          ctx.moveTo(x, baseY - candleHeight - 15);
          ctx.lineTo(x, baseY - candleHeight);
          ctx.lineWidth = wickWidth;
          ctx.stroke();

          // Draw candle body (rectangle)
          ctx.fillRect(x - candleWidth/2, baseY - candleHeight, candleWidth, candleHeight);
          ctx.strokeRect(x - candleWidth/2, baseY - candleHeight, candleWidth, candleHeight);

        } else if (trade.signal === 'SELL') {
          // Red candlestick (bearish)
          ctx.fillStyle = '#ef4444';
          ctx.strokeStyle = '#dc2626';
          ctx.lineWidth = 1;

          // Draw wick (thin line extending down)
          ctx.beginPath();
          ctx.moveTo(x, baseY + candleHeight);
          ctx.lineTo(x, baseY + candleHeight + 15);
          ctx.lineWidth = wickWidth;
          ctx.stroke();

          // Draw candle body (rectangle)
          ctx.fillRect(x - candleWidth/2, baseY, candleWidth, candleHeight);
          ctx.strokeRect(x - candleWidth/2, baseY, candleWidth, candleHeight);
        }
      }
    });

    // Draw price labels (Y-axis)
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    // Price labels at regular intervals
    const numPriceLabels = 6;
    for (let i = 0; i <= numPriceLabels; i++) {
      const priceValue = minPrice + (priceRange * i / numPriceLabels);
      const y = height - padding.bottom - ((priceValue - minPrice) / priceRange) * chartHeight;
      ctx.fillText(`$${priceValue.toFixed(2)}`, padding.left - 8, y);
    }

    // Draw time labels (X-axis)
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    const numTimeLabels = 6;
    for (let i = 0; i <= numTimeLabels; i++) {
      const dataIndex = Math.floor((sortedHistorical.length - 1) * i / numTimeLabels);
      if (dataIndex < sortedHistorical.length) {
        const date = new Date(sortedHistorical[dataIndex].date);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const x = padding.left + (dataIndex / (sortedHistorical.length - 1)) * chartWidth;
        ctx.fillText(dateStr, x, height - padding.bottom + 8);
      }
    }

    // Draw axis labels
    ctx.fillStyle = '#e2e8f0';
    ctx.font = '12px sans-serif';

    // Y-axis label
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillText('Price (USD)', 0, 0);
    ctx.restore();

    // X-axis label
    ctx.textAlign = 'center';
    ctx.fillText('Time', width / 2, height - 15);

    // Draw title
    ctx.fillStyle = '#e2e8f0';
    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`${selectedStock} Trading Strategy - 1 Year Historical Data`, padding.left, 25);

    // Draw animated timeline progress line
    if (isAnimating && animationProgress > 0 && totalTrades > 0) {
      const currentTrade = tradingData[animationProgress - 1];
      if (currentTrade) {
        // Find the closest historical point for the current trade
        const tradeDate = currentTrade.date;
        let closestIndex = 0;
        let closestDiff = Math.abs(new Date(sortedHistorical[0].date) - tradeDate);

        sortedHistorical.forEach((point, index) => {
          const pointDate = new Date(point.date);
          const diff = Math.abs(pointDate - tradeDate);
          if (diff < closestDiff) {
            closestDiff = diff;
            closestIndex = index;
          }
        });

        if (closestIndex >= 0) {
          const timelineX = padding.left + (closestIndex / (sortedHistorical.length - 1)) * chartWidth;

          // Draw transparent vertical line
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
          ctx.lineWidth = 2;
          ctx.setLineDash([5, 5]); // Dashed line
          ctx.beginPath();
          ctx.moveTo(timelineX, padding.top);
          ctx.lineTo(timelineX, height - padding.bottom);
          ctx.stroke();
          ctx.setLineDash([]); // Reset line dash

          // Draw small indicator at the bottom
          ctx.fillStyle = 'rgba(96, 165, 250, 0.8)';
          ctx.beginPath();
          ctx.arc(timelineX, height - padding.bottom + 5, 4, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
    }

  }, [stockData, tradingData, selectedStock, animationProgress, totalTrades, isAnimating]);

  // Handle mouse movement for hover detection
  const handleMouseMove = (event) => {
    if (!canvasRef.current || !stockData) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    setMousePos({ x, y });

    // Use exact same padding and dimensions as the drawing code
    const width = rect.width;
    const height = rect.height;
    const padding = { top: 40, right: 40, bottom: 60, left: 80 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    let hoveredTrade = null;

    tradingData.forEach(trade => {
      if (!stockData.ytd_history) return;

      const ytdHistory = stockData.ytd_history;
      const historical = ytdHistory.dates.map((date, index) => ({
        date: date,
        price: ytdHistory.prices[index]
      }));

      // Find closest historical point (same logic as drawing)
      const tradeDate = trade.date;
      let closestIndex = 0;
      let closestDiff = Math.abs(new Date(historical[0].date) - tradeDate);

      historical.forEach((point, index) => {
        const pointDate = new Date(point.date);
        const diff = Math.abs(pointDate - tradeDate);
        if (diff < closestDiff) {
          closestDiff = diff;
          closestIndex = index;
        }
      });

      // Use exact same calculation as drawing code
      const candleX = padding.left + (closestIndex / (historical.length - 1)) * chartWidth;
      const candleWidth = 5;
      const candleHalfWidth = candleWidth / 2;

      // Expand hit area slightly for easier hovering
      const hitArea = 8;

      // Check if mouse is within candle bounds
      if (x >= candleX - hitArea && x <= candleX + hitArea) {
        hoveredTrade = trade;
      }
    });

    setHoverData(hoveredTrade);
  };

  const handleMouseLeave = () => {
    setHoverData(null);
  };

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ width: '100%', height: '100%' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />

      {/* Hover tooltip */}
      {hoverData && (
        <div
          className="absolute bg-slate-800/40 backdrop-blur-sm border border-slate-600/30 rounded-lg p-3 text-sm text-white shadow-lg pointer-events-none z-10"
          style={{
            left: mousePos.x + 10,
            top: mousePos.y - 80,
            transform: mousePos.x > 300 ? 'translateX(-100%)' : 'none'
          }}
        >
          <div className="font-semibold mb-1">
            <span className={hoverData.signal === 'BUY' ? 'text-green-400' : 'text-red-400'}>
              {hoverData.signal}
            </span> Signal
          </div>
          <div>Date: {hoverData.date.toLocaleDateString()}</div>
          <div>Price: ${hoverData.price?.toFixed(2)}</div>
          <div>Confidence: {(hoverData.confidence * 100).toFixed(1)}%</div>
          <div>Portfolio: ${hoverData.portfolioValue?.toLocaleString()}</div>
        </div>
      )}
    </div>
  );
}

export default function StockRiskDashboard() {
  const [selected, setSelected] = useState(STOCKS[0].symbol);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState({});
  const [advancedMetrics, setAdvancedMetrics] = useState({});
  const [aiSummary, setAiSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState("dashboard"); // "dashboard" or "trading"
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Page transition function
  const switchPage = (newPage) => {
    if (newPage === currentPage || isTransitioning) return;

    setIsTransitioning(true);

    // Wait for slide out, then change page and slide in
    setTimeout(() => {
      setCurrentPage(newPage);
      setTimeout(() => {
        setIsTransitioning(false);
      }, 50);
    }, 250);
  };

  useEffect(() => {
    fetchStock(selected);
    fetchPredictions();
    fetchAdvancedMetrics();
  }, [selected]);

  useEffect(() => {
    if (data && data.symbol) {
      generateAISummary();
    }
  }, [data]);

  async function fetchPredictions() {
    try {
      const predRes = await fetch('http://localhost:8000/predictions');
      if (predRes.ok) {
        const predResponse = await predRes.json();
        if (predResponse.success) {
          setPredictions(predResponse.data);
        }
      }
    } catch (e) {
      console.warn('Could not fetch predictions:', e);
    }
  }

  async function fetchAdvancedMetrics() {
    try {
      // We'll need to create an endpoint for this, but for now try individual calls
      const promises = STOCKS.map(async (stock) => {
        try {
          const response = await fetch(`http://localhost:8000/advanced-metrics/${stock.symbol}`);
          if (response.ok) {
            const data = await response.json();
            return { symbol: stock.symbol, data: data.success ? data.metrics : null };
          }
        } catch (e) {
          console.warn(`Could not fetch advanced metrics for ${stock.symbol}:`, e);
        }
        return { symbol: stock.symbol, data: null };
      });

      const results = await Promise.all(promises);
      const metricsMap = {};
      results.forEach(result => {
        if (result.data) {
          metricsMap[result.symbol] = result.data;
        }
      });
      setAdvancedMetrics(metricsMap);
    } catch (e) {
      console.warn('Could not fetch advanced metrics:', e);
    }
  }

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
        price_history: stockData.price_history, // 30-day data for existing charts
        ytd_history: riskData.financial_data?.ytd_history, // YTD data for new chart toggle
        ytd_performance: riskData.financial_data?.ytd_performance, // YTD performance metrics
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

  const getRiskScore = () => {
    if (predictions && predictions[selected]) {
      return {
        score: predictions[selected],
        percentage: predictions[selected],
        label: getRiskLabel(predictions[selected])
      };
    }
    return null;
  };

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
      const risk = getRiskScore();
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
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Shared background - stays consistent */}
      <div className="absolute inset-0 z-0">
        <LiquidEther colors={['#1e293b', '#3b82f6', '#8b5cf6']} />
      </div>

      {/* Page content with slide transition */}
      <div className="relative z-10 h-full">
        {currentPage === "trading" ? (
          <div
            className={`transition-transform duration-300 ease-out ${
              isTransitioning ? 'transform translate-x-full' : 'transform translate-x-0'
            }`}
          >
            <TradingPage currentPage={currentPage} switchPage={switchPage} />
          </div>
        ) : (
          <div
            className={`p-6 transition-transform duration-300 ease-out ${
              isTransitioning ? 'transform -translate-x-full' : 'transform translate-x-0'
            }`}
          >
            <div className="max-w-7xl mx-auto relative z-10">
        <header className="flex items-center justify-between mb-6">
          <TextType
            text={["Stock Risk Dashboard", "Real-time Analysis", "AI-Powered Insights"]}
            as="h1"
            className="text-2xl md:text-3xl font-extrabold text-white"
            typingSpeed={75}
            pauseDuration={1500}
            showCursor={true}
            cursorCharacter="|"
            textColors={["#ffffff", "#60a5fa", "#34d399"]}
          />
          <div className="flex items-center gap-4">
            {/* Page Toggle */}
            <div className="flex items-center bg-slate-800/60 backdrop-blur rounded-lg p-1 border border-slate-700/50">
              <button
                onClick={() => switchPage("dashboard")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  currentPage === "dashboard"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-300 hover:text-white hover:bg-slate-700/50"
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => switchPage("trading")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  currentPage === "trading"
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-slate-300 hover:text-white hover:bg-slate-700/50"
                }`}
              >
                Trading
              </button>
            </div>
            <p className="text-sm text-slate-300">Quick, simple financial stats for everyday investors</p>
          </div>
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
                          {data && data.changePercent != null ? `${data.changePercent >= 0 ? "+" : ""}${data.changePercent.toFixed(2)}% today` : ""}
                        </span>
                      </>
                    )}
                  </div>
                </div>

              </div>

              {/* Risk card and graph placeholder */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Risk Score */}
                <div
                  className="md:col-span-1 backdrop-blur border border-slate-700/50 rounded-xl p-6 flex flex-col gap-4 transition-all duration-300 hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg"
                  style={{
                    background: getRiskScore() ? getRiskGradient(getRiskScore().percentage) : 'linear-gradient(135deg, rgba(107, 114, 128, 0.2) 0%, rgba(75, 85, 99, 0.3) 100%)'
                  }}
                  title="AI-powered risk prediction based on market analysis"
                >
                  <div className="flex flex-col items-center justify-center text-center flex-1">
                    <div className="text-sm text-slate-300 mb-3">Risk Score</div>
                    <div className={`text-6xl font-bold mb-3 ${getRiskScore() ? getRiskTextColor(getRiskScore().percentage) : 'text-white'}`}>
                      {getRiskScore() ? `${getRiskScore().score.toFixed(1)}%` : "—"}
                    </div>
                    <div className={`text-xl font-semibold ${getRiskScore() ? getRiskTextColor(getRiskScore().percentage) : 'text-gray-300'}`}>
                      {getRiskScore() ? getRiskScore().label : "No Data"}
                    </div>
                  </div>

                  <div className="border-t border-white/10 pt-4">
                    <div className="text-xs text-slate-300 text-center">
                      AI Prediction from Market Analysis
                    </div>
                    
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
                  title="Omega Ratio"
                  value={advancedMetrics[selected]?.omega_ratio ? advancedMetrics[selected].omega_ratio.toFixed(3) : "—"}
                  tooltip="Measures risk-adjusted returns by comparing gains to losses above/below a threshold"
                />
                <StatBox
                  title="Beta"
                  value={data?.beta ? data.beta.toFixed(3) : "—"}
                  tooltip="Beta - measures stock volatility relative to the market (1.0 = market volatility)"
                />
                <StatBox
                  title="52 Week Range"
                  value={data ? `$${data.week52Low?.toFixed(2) ?? "—"} - $${data.week52High?.toFixed(2) ?? "—"}` : "—"}
                  tooltip="Shows the stock's lowest and highest trading range over the past year"
                />
                <StatBox
                  title="Price/Earnings Ratio"
                  value={data?.peRatio ? data.peRatio.toFixed(2)  : "—"}
                  tooltip="Tells how expensive a stock is by comparing its price to the company's yearly profit per share"
                />
                <StatBox
                  title="CBOE Volatility"
                  value={data?.cboeVolatility ? data.cboeVolatility.toFixed(2) + "%" : "—"}
                  tooltip="Measures expected volatility and expected stock price fluctuations"
                />
                <StatBox
                  title="Total Debt/Equity"
                  value={data?.debtToEquity ? data.debtToEquity.toFixed(2) + "%" : "—"}
                  tooltip="Compares what a company owes to what it owns, showing how much it relies on borrowing"
                />
                <StatBox
                  title="Tail Ratio"
                  value={advancedMetrics[selected]?.tail_ratio ? advancedMetrics[selected].tail_ratio.toFixed(3) : "—"}
                  tooltip="Measures the ratio of average gains to average losses in extreme price movements"
                />
                <StatBox
                  title="Sortino Ratio"
                  value={advancedMetrics[selected]?.sortino_ratio ? advancedMetrics[selected].sortino_ratio.toFixed(3) : "—"}

                  tooltip="Measures return compared to only the downside risk, focusing on bad volatility instead of all ups and downs"
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
        )}
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
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className="relative bg-slate-800/40 backdrop-blur rounded-xl p-4 shadow-sm flex flex-col hover:border-slate-400/60 hover:shadow-slate-400/20 hover:shadow-lg hover:bg-slate-400/5 border border-slate-700/50 cursor-pointer will-change-transform"
      style={{
        height: isExpanded ? 'auto' : '80px',
        minHeight: isExpanded ? '128px' : '80px',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Main content */}
      <div className="flex flex-col">
        <div className="text-xs text-slate-400 mb-2 flex items-center justify-between">
          {title}
          <span
            className="text-slate-500 transition-transform duration-400 ease-out"
            style={{
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
            }}
          >
            ▼
          </span>
        </div>
        <div className={`text-lg font-semibold ${valueColor}`}>{value}</div>
      </div>

      {/* Expandable description */}
      <div
        className="overflow-hidden"
        style={{
          maxHeight: isExpanded ? '160px' : '0px',
          marginTop: isExpanded ? '12px' : '0px',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
      >
        <div className="border-t border-slate-600/50 pt-3">
          <div
            className="text-xs text-slate-300 leading-relaxed will-change-transform"
            style={{
              opacity: isExpanded ? 1 : 0,
              transform: isExpanded ? 'translateY(0px)' : 'translateY(-8px)',
              transition: 'opacity 0.5s ease-out 0.1s, transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s'
            }}
          >
            {tooltip}
          </div>
        </div>
      </div>
    </div>
  );
}