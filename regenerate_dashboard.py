from src.utils.dashboard_gen import DashboardGenerator
import json
import os
import pandas as pd

def regenerate():
    print("Regenerating Dashboard...")
    
    # Load Config
    try:
        with open('outputs/model_config.json', 'r') as f:
            config = json.load(f)
            ticker = config.get('ticker', 'UNKNOWN')
            asset_type = config.get('asset_type', 'Futures')
    except:
        ticker = "MNQ=F"
        asset_type = "Futures"
        
    # Load History
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []
        
    # Mock Metrics (since we aren't running the full backtest here)
    # We just want to verify the HTML generation
    metrics = {'RMSE': 0.0, 'MAPE': 0.0}
    backtest_metrics = {'Win Rate': 0.0, 'Total Return %': 0.0}
    
    # Mock Signals DF
    signals_df = pd.DataFrame([{
        'Date': pd.Timestamp.now(),
        'Price': 0.0,
        'Prediction': 0.0,
        'Signal': 'HOLD',
        'Position': 0
    }])
    
    gen = DashboardGenerator()
    path = gen.generate_dashboard(ticker, metrics, backtest_metrics, signals_df, history, asset_type)
    print(f"Dashboard regenerated at: {path}")

if __name__ == "__main__":
    regenerate()
