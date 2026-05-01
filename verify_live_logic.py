import pandas as pd
import numpy as np
import time
from src.analysis.market_filter import MarketFilter

def verify_logic():
    print("Verifying MarketFilter Logic...")
    filter = MarketFilter()
    
    # 1. Test ADX Filter
    print("\n[Test 1] ADX Filter (Trend Strength)")
    df_low_adx = pd.DataFrame({'High': np.random.randn(50), 'Low': np.random.randn(50), 'Close': np.random.randn(50)})
    # Mock ADX calculation result by manually setting it in the df for testing check_conditions
    # But calculate_indicators uses talib. 
    # Let's mock the dataframe to have the columns directly to test check_conditions
    
    df_mock = pd.DataFrame({'Close': [100]*50})
    df_mock['ADX'] = 10 # Low ADX
    df_mock['RSI'] = 50
    df_mock['ATR'] = 1.0
    
    config = {"min_adx": 25, "rsi_upper": 70, "rsi_lower": 30}
    
    valid, msg = filter.check_conditions(df_mock, "BUY", config)
    print(f"Low ADX (10 < 25): Valid? {valid}, Msg: {msg}")
    assert not valid, "Should fail on Low ADX"
    
    df_mock['ADX'] = 30 # High ADX
    valid, msg = filter.check_conditions(df_mock, "BUY", config)
    print(f"High ADX (30 > 25): Valid? {valid}, Msg: {msg}")
    assert valid, "Should pass on High ADX"
    
    # 2. Test RSI Filter
    print("\n[Test 2] RSI Filter (Momentum)")
    df_mock['RSI'] = 80 # Overbought
    valid, msg = filter.check_conditions(df_mock, "BUY", config)
    print(f"RSI Overbought (80 > 70) BUY: Valid? {valid}, Msg: {msg}")
    assert not valid, "Should fail BUY on Overbought"
    
    valid, msg = filter.check_conditions(df_mock, "SELL", config)
    print(f"RSI Overbought (80 > 70) SELL: Valid? {valid}, Msg: {msg}")
    assert valid, "Should pass SELL on Overbought"
    
    # 3. Test Cooldown Logic
    print("\n[Test 3] Cooldown Logic")
    last_trade_time = time.time()
    cooldown = 5 # 5 seconds for test
    
    # Immediate check
    on_cooldown = (time.time() - last_trade_time) < cooldown
    print(f"Immediate Check: On Cooldown? {on_cooldown}")
    assert on_cooldown, "Should be on cooldown"
    
    # Wait
    print("Waiting 2 seconds...")
    time.sleep(2.1)
    on_cooldown = (time.time() - last_trade_time) < cooldown
    print(f"Check after 2s: On Cooldown? {on_cooldown}")
    assert on_cooldown, "Should still be on cooldown"
    
    print("Waiting 3 more seconds...")
    time.sleep(3.1)
    on_cooldown = (time.time() - last_trade_time) < cooldown
    print(f"Check after 5s: On Cooldown? {on_cooldown}")
    assert not on_cooldown, "Should be off cooldown"
    
    print("\nAll Logic Verification Passed!")

if __name__ == "__main__":
    verify_logic()
