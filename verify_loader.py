from src.data.loader import load_data, preprocess_data
import pandas as pd

def verify_loader():
    print("Testing Data Loader with Indicators...")
    
    # Mock Data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
    df = pd.DataFrame({
        'Open': [100 + i for i in range(100)],
        'High': [105 + i for i in range(100)],
        'Low': [95 + i for i in range(100)],
        'Close': [102 + i for i in range(100)],
        'Volume': [1000 for _ in range(100)]
    }, index=dates)
    
    print("Original Columns:", df.columns.tolist())
    
    # Preprocess
    dataset, scaler = preprocess_data(df, seq_length=10)
    
    print("Dataset Length:", len(dataset))
    print("Feature Shape:", dataset.data.shape)
    
    # Check if we have 8 features
    assert dataset.data.shape[1] == 8, f"Expected 8 features, got {dataset.data.shape[1]}"
    print("SUCCESS: 8 Features confirmed (Open, High, Low, Close, Volume, RSI, ADX, ATR)")
    
    # Check Scaler
    print("Scaler n_features:", scaler.n_features_in_)
    assert scaler.n_features_in_ == 8, "Scaler should be fitted on 8 features"
    
    print("Loader Verification Passed!")

if __name__ == "__main__":
    verify_loader()
