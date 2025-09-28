import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const StockChart = ({ data, symbol }) => {
  const [viewMode, setViewMode] = useState('30d'); // '30d' or 'ytd'

  // Check if we have data for both views
  const has30DayData = data && data.price_history && data.price_history.dates && data.price_history.dates.length > 0;
  const hasYTDData = data && data.ytd_history && data.ytd_history.dates && data.ytd_history.dates.length > 0;

  if (!has30DayData && !hasYTDData) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="text-center">
          <div className="text-sm">No chart data available</div>
          <div className="text-xs mt-1">Historical data loading...</div>
        </div>
      </div>
    );
  }

  // Determine which data to use
  const isYTDView = viewMode === 'ytd' && hasYTDData;
  const currentData = isYTDView ? data.ytd_history : data.price_history;
  
  // If selected view doesn't have data, fall back to available data
  if (!currentData || !currentData.dates || currentData.dates.length === 0) {
    const fallbackData = has30DayData ? data.price_history : data.ytd_history;
    if (!fallbackData || !fallbackData.dates || fallbackData.dates.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-slate-400">
          <div className="text-center">
            <div className="text-sm">No chart data available</div>
            <div className="text-xs mt-1">Historical data loading...</div>
          </div>
        </div>
      );
    }
  }

  // Transform data for Recharts
  const chartData = currentData.dates.map((date, index) => ({
    date: new Date(date).toLocaleDateString('en-US', { 
      month: isYTDView ? 'short' : 'short', 
      day: 'numeric',
      ...(isYTDView && currentData.dates.length > 100 ? {} : {})
    }),
    price: currentData.prices[index],
    fullDate: date
  }));

  // Calculate price trend and period info
  const firstPrice = chartData[0]?.price || 0;
  const lastPrice = chartData[chartData.length - 1]?.price || 0;
  const isPositiveTrend = lastPrice >= firstPrice;
  const periodChange = ((lastPrice - firstPrice) / firstPrice * 100);

  // Get YTD performance if available
  const ytdPerformance = data.ytd_performance?.percent_change || 0;

  const lineColor = isPositiveTrend ? '#10b981' : '#ef4444'; // green-500 : red-500
  const gradientId = `gradient-${symbol}`;

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-xl">
          <div className="text-slate-300 text-xs mb-1">{label}</div>
          <div className="text-white font-semibold">
            ${data.value?.toFixed(2)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-full">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">            
            {/* Toggle Buttons */}
            <div className="flex bg-slate-800 rounded-md p-1">
              <button
                onClick={() => setViewMode('30d')}
                disabled={!has30DayData}
                className={`px-2 py-1 text-xs rounded transition-all ${
                  viewMode === '30d'
                    ? 'bg-blue-600 text-white'
                    : has30DayData 
                      ? 'text-slate-400 hover:text-slate-200' 
                      : 'text-slate-600 cursor-not-allowed'
                }`}
              >
                30D
              </button>
              <button
                onClick={() => setViewMode('ytd')}
                disabled={!hasYTDData}
                className={`px-2 py-1 text-xs rounded transition-all ${
                  viewMode === 'ytd'
                    ? 'bg-blue-600 text-white'
                    : hasYTDData 
                      ? 'text-slate-400 hover:text-slate-200' 
                      : 'text-slate-600 cursor-not-allowed'
                }`}
              >
                YTD
              </button>
            </div>
          </div>
          
          <div className="text-xs text-slate-400">
            {symbol} • {chartData.length} trading days
            {isYTDView && data.ytd_performance?.start_date && 
              ` • Since ${new Date(data.ytd_performance.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
            }
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400">
            {isYTDView ? 'YTD change' : '30-day change'}
          </div>
          <div className={`text-sm font-semibold ${isPositiveTrend ? 'text-green-400' : 'text-red-400'}`}>
            {isPositiveTrend ? '+' : ''}{(isYTDView && data.ytd_performance ? ytdPerformance : periodChange).toFixed(2)}%
          </div>
          {isYTDView && (
            <div className="text-xs text-slate-500 mt-1">
              ${data.ytd_performance?.start_price?.toFixed(2)} → ${lastPrice.toFixed(2)}
            </div>
          )}
        </div>
      </div>

      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={lineColor} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={lineColor} stopOpacity={0.05}/>
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#374151"
              opacity={0.3}
            />

            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: '#9ca3af' }}
              interval="preserveStartEnd"
            />

            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: '#9ca3af' }}
              domain={['dataMin - 5', 'dataMax + 5']}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />

            <Tooltip content={<CustomTooltip />} />

            <Line
              type="monotone"
              dataKey="price"
              stroke={lineColor}
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 4,
                fill: lineColor,
                stroke: '#1f2937',
                strokeWidth: 2
              }}
              fill={`url(#${gradientId})`}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default StockChart;