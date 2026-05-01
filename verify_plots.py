import pandas as pd
import numpy as np
from src.utils.visualizer import Visualizer
import os

def verify_plots():
    print("Generating verification plots...")
    vis = Visualizer(output_dir='outputs/verification_plots')
    
    # 1. Training Losses
    d_losses = np.random.uniform(0.4, 0.6, 100)
    g_losses = np.random.uniform(0.8, 1.2, 100)
    vis.plot_training_losses(d_losses, g_losses)
    print("- Training Losses generated.")
    
    # 2. Predictions
    real = np.cumsum(np.random.randn(100)) + 100
    pred = real + np.random.normal(0, 1, 100)
    vis.plot_predictions(real, pred)
    print("- Predictions generated.")
    
    # 3. Features
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Close': real,
        'RSI': np.random.uniform(30, 70, 100),
        'MACD': np.random.randn(100),
        'Signal': np.random.randn(100),
        'Volume': np.random.randint(1000, 5000, 100),
        'MA7': real + 1,
        'MA21': real - 1,
        'BB_Upper': real + 2,
        'BB_Lower': real - 2,
        'VIX': np.random.uniform(15, 25, 100)
    }, index=dates)
    
    vis.plot_features(df)
    print("- Features generated.")
    
    # 4. Technical Dashboard
    vis.plot_technical_dashboard(df, ticker_name="TEST-ASSET")
    print("- Technical Dashboard generated.")
    
    # 5. Feature Importance
    features = ['RSI', 'MACD', 'Volume', 'VIX', 'SMA']
    importance = np.random.rand(5)
    vis.plot_feature_importance(features, importance)
    print("- Feature Importance generated.")
    
    # 6. Correlation
    vis.plot_correlation_matrix(df[['Close', 'RSI', 'Volume', 'VIX']])
    print("- Correlation Matrix generated.")
    
    # 7. ARIMA
    vis.plot_arima(df['Close'].iloc[:80], df['Close'].iloc[80:], df['Close'].iloc[80:] + 0.5)
    print("- ARIMA generated.")
    
    # 8. Sentiment
    vis.plot_sentiment(df)
    print("- Sentiment generated.")
    
    # 9. Gaussian Process
    vis.plot_gaussian_process(df['Close'].iloc[:80], df['Close'].iloc[80:], df['Close'].iloc[80:], np.ones(20)*0.5)
    print("- Gaussian Process generated.")
    
    print("All plots generated successfully in outputs/verification_plots/")

if __name__ == "__main__":
    verify_plots()
