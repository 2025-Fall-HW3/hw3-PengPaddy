"""
Package Import
"""
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import quantstats as qs
import gurobipy as gp
import warnings
import argparse
import sys

"""
Project Setup
"""
warnings.simplefilter(action="ignore", category=FutureWarning)

assets = [
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
]

# Initialize Bdf and df
Bdf = pd.DataFrame()
for asset in assets:
    raw = yf.download(asset, start="2012-01-01", end="2024-04-01", auto_adjust = False)
    Bdf[asset] = raw['Adj Close']

df = Bdf.loc["2019-01-01":"2024-04-01"]

"""
Strategy Creation

Create your own strategy, you can add parameter but please remain "price" and "exclude" unchanged
"""


class MyPortfolio:
    """
    NOTE: You can modify the initialization function
    """

    def __init__(self, price, exclude, lookback=120, gamma=0):
        self.price = price
        self.returns = price.pct_change().fillna(0)
        self.exclude = exclude
        self.lookback = lookback
        self.gamma = gamma

    def calculate_weights(self):
        # Get the assets by excluding the specified column
        assets = self.price.columns[self.price.columns != self.exclude]

        # Calculate the portfolio weights
        self.portfolio_weights = pd.DataFrame(
            index=self.price.index, columns=self.price.columns
        )

        """
        TODO: Complete Task 4 Below
        """
        for i in range(0, self.lookback + 1):
            n_assets = len(assets)
            equal_weight = 1.0 / n_assets
            date = self.price.index[i]

            for asset in assets:
                self.portfolio_weights.loc[date, asset] = equal_weight
        for i in range(self.lookback + 1, len(self.price)):
            # 1. 計算 lookback 期間報酬（Momentum）
            past_ret = (
                self.price[assets].iloc[i-1] /
                self.price[assets].iloc[i - self.lookback - 1]
                - 1
            )

            # 2. 計算 volatility（標準差）
            vol = self.returns[assets].iloc[i - self.lookback : i].std()

            # 3. 把負 momentum 的剔除（long-only strong momentum）
            mom = past_ret.clip(lower=0)

            # 4. 避免 division by zero
            vol = vol.replace(0, np.nan)

            # 5. 計算 risk-adjusted momentum 權重
            score = mom / vol
            score = score.replace([np.inf, -np.inf], np.nan)

            # 若全為 0，則保持上次權重
            if score.sum() == 0 or score.isna().all():
                self.portfolio_weights.loc[self.price.index[i], assets] = \
                    self.portfolio_weights.loc[self.price.index[i-1], assets]
                continue

            w = score / score.sum()

            # 6. 存入權重
            self.portfolio_weights.loc[self.price.index[i], assets] = w.values
        
        """
        TODO: Complete Task 4 Above
        """

        self.portfolio_weights.ffill(inplace=True)
        self.portfolio_weights.fillna(0, inplace=True)

    def calculate_portfolio_returns(self):
        # Ensure weights are calculated
        if not hasattr(self, "portfolio_weights"):
            self.calculate_weights()

        # Calculate the portfolio returns
        self.portfolio_returns = self.returns.copy()
        assets = self.price.columns[self.price.columns != self.exclude]
        self.portfolio_returns["Portfolio"] = (
            self.portfolio_returns[assets]
            .mul(self.portfolio_weights[assets])
            .sum(axis=1)
        )

    def get_results(self):
        # Ensure portfolio returns are calculated
        if not hasattr(self, "portfolio_returns"):
            self.calculate_portfolio_returns()

        return self.portfolio_weights, self.portfolio_returns


if __name__ == "__main__":
    # Import grading system (protected file in GitHub Classroom)
    from grader_2 import AssignmentJudge
    
    parser = argparse.ArgumentParser(
        description="Introduction to Fintech Assignment 3 Part 12"
    )

    parser.add_argument(
        "--score",
        action="append",
        help="Score for assignment",
    )

    parser.add_argument(
        "--allocation",
        action="append",
        help="Allocation for asset",
    )

    parser.add_argument(
        "--performance",
        action="append",
        help="Performance for portfolio",
    )

    parser.add_argument(
        "--report", action="append", help="Report for evaluation metric"
    )

    parser.add_argument(
        "--cumulative", action="append", help="Cumulative product result"
    )

    args = parser.parse_args()

    judge = AssignmentJudge()
    
    # All grading logic is protected in grader_2.py
    judge.run_grading(args)
