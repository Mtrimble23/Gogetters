#!/usr/bin/env python3
"""
Financial Risk Analysis Tool for Stocks
========================================

This tool analyzes stocks based on key financial metrics and provides risk scores
to help average investors understand investment risk levels.

Author: Your Financial Risk Analysis Tool
Date: September 2025
"""

import pandas as pd
import yfinance as yf
import numpy as np
import sqlite3
from datetime import datetime
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')


class FinancialRiskAnalyzer:
    """
    A comprehensive financial risk analyzer for stocks using Yahoo Finance data.
    
    This class fetches financial data and calculates key risk metrics including:
    - Debt-to-Equity Ratio
    - Beta (market risk)
    - Return on Equity (ROE)
    - Current Ratio
    
    Results are stored in SQLite database for historical tracking.
    """
    
    def __init__(self, db_path: str = "financial_risk_analysis.db"):
        """Initialize the risk analyzer with predefined risk thresholds and database."""
        # Risk thresholds for classification (Low/Medium/High)
        self.risk_thresholds = {
            'debt_to_equity': {'low': 0.3, 'high': 1.0},
            'beta': {'low': 0.8, 'high': 1.3},
            'roe': {'low': 15, 'high': 8},  # Higher ROE is better (reverse logic)
            'current_ratio': {'low': 2.0, 'high': 1.2},  # Higher is better (reverse logic)
        }
        
        # Database setup
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """
        Initialize SQLite database with required tables.
        Creates tables for stock analysis results and historical tracking.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create main analysis results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        company_name TEXT,
                        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        debt_to_equity REAL,
                        debt_to_equity_risk TEXT,
                        beta REAL,
                        beta_risk TEXT,
                        roe REAL,
                        roe_risk TEXT,
                        current_ratio REAL,
                        current_ratio_risk TEXT,
                        overall_risk_score REAL,
                        overall_risk_level TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_ticker_date 
                    ON stock_analysis(ticker, analysis_date)
                ''')
                
                conn.commit()
                print(f"✅ Database initialized: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
    
    def save_to_database(self, ticker: str, company_name: str, metrics: Dict, 
                        overall_risk_score: float, overall_risk_level: str) -> bool:
        """
        Save analysis results to SQLite database.
        
        Args:
            ticker (str): Stock ticker symbol
            company_name (str): Company name
            metrics (Dict): Dictionary containing all calculated metrics
            overall_risk_score (float): Overall risk score
            overall_risk_level (str): Overall risk level
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO stock_analysis (
                        ticker, company_name, debt_to_equity, debt_to_equity_risk,
                        beta, beta_risk, roe, roe_risk, current_ratio, current_ratio_risk,
                        overall_risk_score, overall_risk_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    company_name,
                    metrics.get('debt_to_equity'),
                    metrics.get('debt_to_equity_risk'),
                    metrics.get('beta'),
                    metrics.get('beta_risk'),
                    metrics.get('roe'),
                    metrics.get('roe_risk'),
                    metrics.get('current_ratio'),
                    metrics.get('current_ratio_risk'),
                    overall_risk_score,
                    overall_risk_level
                ))
                
                conn.commit()
                print(f"💾 Analysis saved to database for {ticker}")
                return True
                
        except Exception as e:
            print(f"❌ Error saving to database: {str(e)}")
            return False
    
    def get_historical_data(self, ticker: Optional[str] = None, limit: int = 10) -> pd.DataFrame:
        """
        Retrieve historical analysis data from database.
        
        Args:
            ticker (str, optional): Filter by specific ticker
            limit (int): Maximum number of records to return
            
        Returns:
            pd.DataFrame: Historical analysis data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if ticker:
                    query = '''
                        SELECT * FROM stock_analysis 
                        WHERE ticker = ? 
                        ORDER BY analysis_date DESC 
                        LIMIT ?
                    '''
                    df = pd.read_sql_query(query, conn, params=(ticker.upper(), limit))
                else:
                    query = '''
                        SELECT * FROM stock_analysis 
                        ORDER BY analysis_date DESC 
                        LIMIT ?
                    '''
                    df = pd.read_sql_query(query, conn, params=(limit,))
                
                return df
                
        except Exception as e:
            print(f"❌ Error retrieving historical data: {str(e)}")
            return pd.DataFrame()
    
    def get_risk_summary(self) -> pd.DataFrame:
        """
        Get a summary of risk levels across all analyzed stocks.
        
        Returns:
            pd.DataFrame: Risk summary statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT 
                        overall_risk_level,
                        COUNT(*) as count,
                        AVG(overall_risk_score) as avg_score,
                        MIN(overall_risk_score) as min_score,
                        MAX(overall_risk_score) as max_score
                    FROM stock_analysis 
                    GROUP BY overall_risk_level
                    ORDER BY avg_score
                '''
                df = pd.read_sql_query(query, conn)
                return df
                
        except Exception as e:
            print(f"❌ Error retrieving risk summary: {str(e)}")
            return pd.DataFrame()
    
    def fetch_stock_data(self, ticker: str) -> Optional[yf.Ticker]:
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            yf.Ticker: Yahoo Finance ticker object or None if failed
        """
        try:
            stock = yf.Ticker(ticker)
            # Test if the ticker is valid by trying to get basic info
            info = stock.info
            if not info or 'symbol' not in info:
                raise ValueError(f"Invalid ticker symbol: {ticker}")
            return stock
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def calculate_debt_to_equity(self, stock: yf.Ticker) -> Optional[float]:
        """
        Calculate Debt-to-Equity ratio from balance sheet.
        
        D/E = Total Debt / Total Shareholders' Equity
        Lower values indicate lower financial risk.
        
        Args:
            stock: Yahoo Finance ticker object
            
        Returns:
            float: Debt-to-Equity ratio or None if calculation fails
        """
        try:
            balance_sheet = stock.balance_sheet
            if balance_sheet.empty:
                return None
            
            # Get the most recent data (first column)
            recent = balance_sheet.iloc[:, 0]
            
            # Calculate total debt (short-term + long-term)
            total_debt = 0
            if 'Current Debt' in recent.index:
                total_debt += recent.get('Current Debt', 0)
            if 'Long Term Debt' in recent.index:
                total_debt += recent.get('Long Term Debt', 0)
            if 'Total Debt' in recent.index:
                total_debt = recent.get('Total Debt', total_debt)
            
            # Get shareholders' equity
            shareholders_equity = recent.get('Stockholders Equity', 0)
            
            if shareholders_equity <= 0:
                return None
                
            return total_debt / shareholders_equity
            
        except Exception as e:
            print(f"Error calculating Debt-to-Equity: {str(e)}")
            return None
    
    def get_beta(self, stock: yf.Ticker) -> Optional[float]:
        """
        Get Beta from stock info.
        
        Beta measures stock volatility relative to the market.
        - Beta > 1: More volatile than market
        - Beta < 1: Less volatile than market
        
        Args:
            stock: Yahoo Finance ticker object
            
        Returns:
            float: Beta value or None if not available
        """
        try:
            info = stock.info
            return info.get('beta')
        except Exception as e:
            print(f"Error getting Beta: {str(e)}")
            return None
    
    def calculate_roe(self, stock: yf.Ticker) -> Optional[float]:
        """
        Calculate Return on Equity (ROE).
        
        ROE = (Net Income / Shareholders' Equity) * 100
        Higher values indicate better profitability and efficiency.
        
        Args:
            stock: Yahoo Finance ticker object
            
        Returns:
            float: ROE percentage or None if calculation fails
        """
        try:
            # Get financial data
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            
            if financials.empty or balance_sheet.empty:
                return None
            
            # Get most recent data
            recent_financials = financials.iloc[:, 0]
            recent_balance = balance_sheet.iloc[:, 0]
            
            # Get net income
            net_income = recent_financials.get('Net Income', 0)
            
            # Get shareholders' equity
            shareholders_equity = recent_balance.get('Stockholders Equity', 0)
            
            if shareholders_equity <= 0:
                return None
                
            roe = (net_income / shareholders_equity) * 100
            return roe
            
        except Exception as e:
            print(f"Error calculating ROE: {str(e)}")
            return None
    
    def calculate_current_ratio(self, stock: yf.Ticker) -> Optional[float]:
        """
        Calculate Current Ratio from balance sheet.
        
        Current Ratio = Current Assets / Current Liabilities
        Higher values indicate better short-term liquidity.
        
        Args:
            stock: Yahoo Finance ticker object
            
        Returns:
            float: Current ratio or None if calculation fails
        """
        try:
            balance_sheet = stock.balance_sheet
            if balance_sheet.empty:
                return None
            
            # Get most recent data
            recent = balance_sheet.iloc[:, 0]
            
            current_assets = recent.get('Current Assets', 0)
            current_liabilities = recent.get('Current Liabilities', 0)
            
            if current_liabilities <= 0:
                return None
                
            return current_assets / current_liabilities
            
        except Exception as e:
            print(f"Error calculating Current Ratio: {str(e)}")
            return None
    
    def classify_risk(self, metric_name: str, value: Optional[float]) -> Tuple[str, int]:
        """
        Classify a metric value into risk categories.
        
        Args:
            metric_name (str): Name of the metric
            value (float): Metric value
            
        Returns:
            Tuple[str, int]: Risk category ('Low'/'Medium'/'High') and numeric score (1-3)
        """
        if value is None:
            return 'N/A', 0
        
        thresholds = self.risk_thresholds.get(metric_name, {})
        low_threshold = thresholds.get('low')
        high_threshold = thresholds.get('high')
        
        # Handle reverse logic metrics (higher is better)
        if metric_name in ['roe', 'current_ratio']:
            if value >= low_threshold:
                return 'Low', 1
            elif value >= high_threshold:
                return 'Medium', 2
            else:
                return 'High', 3
        else:
            # Normal logic (lower is better)
            if value <= low_threshold:
                return 'Low', 1
            elif value <= high_threshold:
                return 'Medium', 2
            else:
                return 'High', 3
    
    def calculate_overall_risk_score(self, risk_scores: List[int]) -> Tuple[str, float]:
        """
        Calculate overall risk score from individual metric scores.
        
        Args:
            risk_scores (List[int]): List of individual risk scores (1-3)
            
        Returns:
            Tuple[str, float]: Overall risk category and average score
        """
        # Filter out N/A scores (0s)
        valid_scores = [score for score in risk_scores if score > 0]
        
        if not valid_scores:
            return 'N/A', 0.0
        
        avg_score = sum(valid_scores) / len(valid_scores)
        
        if avg_score <= 1.5:
            return 'Low', avg_score
        elif avg_score <= 2.5:
            return 'Medium', avg_score
        else:
            return 'High', avg_score
    
    def analyze_stock(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Perform complete risk analysis for a given stock.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            pd.DataFrame: Risk analysis results table
        """
        print(f"\n🔍 Analyzing {ticker.upper()}...")
        print("-" * 50)
        
        # Fetch stock data
        stock = self.fetch_stock_data(ticker)
        if not stock:
            print(f"❌ Failed to fetch data for {ticker}")
            return None
        
        # Get company info
        try:
            info = stock.info
            company_name = info.get('longName', ticker.upper())
            print(f"📊 Company: {company_name}")
        except:
            company_name = ticker.upper()
        
        # Calculate all metrics
        print("⚡ Calculating financial metrics...")
        
        debt_to_equity = self.calculate_debt_to_equity(stock)
        beta = self.get_beta(stock)
        roe = self.calculate_roe(stock)
        current_ratio = self.calculate_current_ratio(stock)
        
        # Classify risks
        de_risk, de_score = self.classify_risk('debt_to_equity', debt_to_equity)
        beta_risk, beta_score = self.classify_risk('beta', beta)
        roe_risk, roe_score = self.classify_risk('roe', roe)
        cr_risk, cr_score = self.classify_risk('current_ratio', current_ratio)
        
        # Calculate overall risk
        overall_risk, avg_score = self.calculate_overall_risk_score([
            de_score, beta_score, roe_score, cr_score
        ])
        
        # Prepare metrics dictionary for database storage
        metrics = {
            'debt_to_equity': debt_to_equity,
            'debt_to_equity_risk': de_risk,
            'beta': beta,
            'beta_risk': beta_risk,
            'roe': roe,
            'roe_risk': roe_risk,
            'current_ratio': current_ratio,
            'current_ratio_risk': cr_risk
        }
        
        # Save to database
        self.save_to_database(ticker.upper(), company_name, metrics, avg_score, overall_risk)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'Metric': [
                'Debt-to-Equity Ratio',
                'Beta (Market Risk)',
                'Return on Equity (%)',
                'Current Ratio',
                'OVERALL RISK'
            ],
            'Value': [
                f"{debt_to_equity:.2f}" if debt_to_equity is not None else "N/A",
                f"{beta:.2f}" if beta is not None else "N/A",
                f"{roe:.1f}%" if roe is not None else "N/A",
                f"{current_ratio:.2f}" if current_ratio is not None else "N/A",
                f"{avg_score:.2f}"
            ],
            'Risk Level': [
                de_risk, beta_risk, roe_risk, cr_risk, overall_risk
            ],
            'Interpretation': [
                "Lower is better (less debt burden)",
                "~1.0 is market average volatility",
                "Higher is better (profitability)",
                "Higher is better (liquidity)",
                "Average of all metric scores"
            ]
        })
        
        return results
    
    def analyze_multiple_stocks(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Analyze multiple stocks and return results.
        
        Args:
            tickers (List[str]): List of ticker symbols
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of ticker -> results DataFrame
        """
        results = {}
        for ticker in tickers:
            result = self.analyze_stock(ticker)
            if result is not None:
                results[ticker.upper()] = result
        return results
    
    def export_to_csv(self, results: pd.DataFrame, ticker: str, filename: Optional[str] = None) -> None:
        """
        Export analysis results to CSV file.
        
        Args:
            results (pd.DataFrame): Analysis results
            ticker (str): Stock ticker
            filename (str, optional): Custom filename
        """
        if filename is None:
            filename = f"{ticker.upper()}_risk_analysis.csv"
        
        try:
            results.to_csv(filename, index=False)
            print(f"📄 Results exported to: {filename}")
        except Exception as e:
            print(f"❌ Error exporting to CSV: {str(e)}")


def main():
    """
    Main function to run the financial risk analyzer.
    """
    # Initialize the analyzer
    analyzer = FinancialRiskAnalyzer()
    
    print("🏦 Financial Risk Analysis Tool with Database Storage")
    print("="*50)
    print("Analyze stocks based on key financial metrics")
    print("Data is automatically saved to SQLite database")
    print()
    
    while True:
        print("\n" + "="*50)
        print("OPTIONS:")
        print("1. 📈 Analyze a stock")
        print("2. 📊 View historical data") 
        print("3. 📋 View risk summary")
        print("4. 🚪 Exit")
        print("="*50)
        
        try:
            choice = input("Select option (1-4): ").strip()
            
            if choice == "1" or choice == "":
                # Analyze a stock
                print("\n📈 STOCK ANALYSIS")
                print("-" * 20)
                ticker = input("Enter ticker symbol (default: AAPL): ").strip().upper()
                
                if not ticker:
                    ticker = "AAPL"
                
                print(f"Analyzing {ticker}...")
                results = analyzer.analyze_stock(ticker)
                
                if results is not None:
                    print(f"\n📈 RISK ANALYSIS RESULTS FOR {ticker}")
                    print("="*60)
                    print(results.to_string(index=False))
                    
                    # Ask about CSV export
                    try:
                        export_choice = input(f"\nExport to CSV? (y/N): ").strip().lower()
                        if export_choice == 'y' or export_choice == 'yes':
                            analyzer.export_to_csv(results, ticker)
                    except (EOFError, KeyboardInterrupt):
                        print("\nSkipping CSV export...")
                    
                    print(f"\n✅ Analysis complete for {ticker}!")
                    print("💾 Data saved to database for historical tracking")
                
                else:
                    print(f"❌ Could not complete analysis for {ticker}")
            
            elif choice == "2":
                # View historical data
                print("\n📊 HISTORICAL DATA")
                print("-" * 20)
                ticker = input("Enter ticker for specific history (or press Enter for all): ").strip().upper()
                
                try:
                    limit_input = input("Number of records to show (default: 10): ").strip()
                    limit = int(limit_input) if limit_input.isdigit() else 10
                except ValueError:
                    limit = 10
                
                if ticker:
                    historical_data = analyzer.get_historical_data(ticker, limit)
                    print(f"\n📈 HISTORICAL DATA FOR {ticker}")
                else:
                    historical_data = analyzer.get_historical_data(limit=limit)
                    print(f"\n📈 RECENT ANALYSIS HISTORY (Last {limit})")
                
                print("="*80)
                if not historical_data.empty:
                    # Format the display
                    display_cols = ['ticker', 'company_name', 'analysis_date', 'overall_risk_level', 'overall_risk_score']
                    print(historical_data[display_cols].to_string(index=False))
                else:
                    print("No historical data found.")
            
            elif choice == "3":
                # Show risk summary
                print("\n📋 RISK SUMMARY")
                print("-" * 20)
                summary = analyzer.get_risk_summary()
                print(f"\n📊 RISK LEVEL SUMMARY")
                print("="*40)
                if not summary.empty:
                    print(summary.to_string(index=False))
                else:
                    print("No analysis data available yet.")
            
            elif choice == "4":
                print("\n👋 Thank you for using the Financial Risk Analysis Tool!")
                print("📊 All your analysis data is safely stored in the database.")
                break
            
            else:
                print("❌ Invalid option. Please choose 1-4.")
        
        except (EOFError, KeyboardInterrupt):
            print("\n\n� Goodbye! Your data is safely stored in the database.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    main()