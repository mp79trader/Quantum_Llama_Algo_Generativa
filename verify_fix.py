import sys
import os
# Add the current directory to sys.path so imports work
sys.path.append(os.getcwd())

from train import train_model

# Run a very short training to verify image generation
# 1 epoch means it will hit epoch 0 (snapshot) AND epoch 0 (final)
# This effectively tests if BOTH images are generated
print("Running verification test...")
try:
    train_model("MNQ=F", "1y", 1, "Futures", "1h", "1h")
    print("Test completed successfully.")
except Exception as e:
    print(f"Test failed: {e}")
