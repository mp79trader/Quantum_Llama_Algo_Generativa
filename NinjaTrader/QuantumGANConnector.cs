#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
using System.IO;
#endregion

//This namespace holds Strategies in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Strategies
{
	public class QuantumGANConnector : Strategy
	{
		private string exchangeDir = @"C:\QuantumGAN\Exchange";
		private string commandsFile;
		private string positionsFile;
		private string accountFile;
		private System.Windows.Threading.DispatcherTimer timer;
		
		// Variables to store current SL/TP for visualization
		private double currentSL = 0;
		private double currentTP = 0;
		private MarketPosition lastMarketPosition = MarketPosition.Flat;
		private DateTime lastExportTime = DateTime.MinValue;
		
		protected override void OnStateChange()
		{
			if (State == State.SetDefaults)
			{
				Description									= @"Connects NinjaTrader 8 to QuantumGAN AI via file exchange.";
				Name										= "QuantumGANConnector";
				Calculate									= Calculate.OnEachTick; // Changed to OnEachTick for faster command processing
				EntriesPerDirection							= 1;
				EntryHandling								= EntryHandling.AllEntries;
				IsExitOnSessionCloseStrategy				= false;
				ExitOnSessionCloseSeconds					= 30;
				IsFillLimitOnTouch							= false;
				MaximumBarsLookBack							= MaximumBarsLookBack.TwoHundredFiftySix;
				OrderFillResolution							= OrderFillResolution.Standard;
				Slippage									= 0;
				StartBehavior								= StartBehavior.WaitUntilFlat;
				TimeInForce									= TimeInForce.Gtc;
				TraceOrders									= false;
				RealtimeErrorHandling						= RealtimeErrorHandling.StopCancelClose;
				StopTargetHandling							= StopTargetHandling.PerEntryExecution;
				BarsRequiredToTrade							= 60; // Increased to 60 to ensure enough data for EMA 50
				// Disable this property for performance gains in Strategy Analyzer optimizations
				// See the Help Guide for additional information
				IsInstantiatedOnEachOptimizationIteration	= true;
			}
			else if (State == State.Configure)
			{
				commandsFile = Path.Combine(exchangeDir, "commands.txt");
				positionsFile = Path.Combine(exchangeDir, "positions.csv");
				accountFile = Path.Combine(exchangeDir, "account.csv");
				
				if (!Directory.Exists(exchangeDir))
				{
					Directory.CreateDirectory(exchangeDir);
				}
			}
			else if (State == State.DataLoaded)
			{
				Print("QuantumGANConnector v2 Loaded - Debug Mode");
				// Start timer to check for commands every 1 second
				if (timer == null)
				{
					System.Windows.Threading.Dispatcher dispatcher = System.Windows.Threading.Dispatcher.CurrentDispatcher;
					timer = new System.Windows.Threading.DispatcherTimer();
					timer.Tick += new EventHandler(CheckCommands);
					timer.Interval = new TimeSpan(0, 0, 1); // 1 second
					timer.Start();
				}
			}
			else if (State == State.Terminated)
			{
				if (timer != null)
				{
					timer.Stop();
					timer = null;
				}
			}
		}

		protected override void OnBarUpdate()
		{
			if (CurrentBar < BarsRequiredToTrade) return;
			
			// Check commands on every tick as well (fallback)
			CheckCommands(null, null);
			
			// Export Data
			ExportData();
			
			// Update Positions File
			ExportPositions();
			
			// Export Account Info
			ExportAccount();
			
			// Visualize SL/TP
			DrawSLTP();
			
			// Update last state
			lastMarketPosition = Position.MarketPosition;
		}
		
		private void DrawSLTP()
		{
			// Only reset if we TRANSITIONED to Flat from a position
			// This prevents resetting during pending order state (where we are Flat but waiting for fill)
			if (Position.MarketPosition == MarketPosition.Flat && lastMarketPosition != MarketPosition.Flat)
			{
				// Clear lines if closed
				RemoveDrawObject("SL_Line");
				RemoveDrawObject("TP_Line");
				currentSL = 0;
				currentTP = 0;
			}
			
			// Always try to draw if values exist (even if pending/flat, so user sees where SL/TP will be)
			if (currentSL > 0)
			{
				Draw.Line(this, "SL_Line", false, 10, currentSL, 0, currentSL, Brushes.Red, DashStyleHelper.Solid, 2);
			}
			if (currentTP > 0)
			{
				Draw.Line(this, "TP_Line", false, 10, currentTP, 0, currentTP, Brushes.Green, DashStyleHelper.Solid, 2);
			}
		}
		
		private void ExportData()
		{
			// Throttle export to avoid file locking issues (max 4 times per second)
			if ((DateTime.Now - lastExportTime).TotalMilliseconds < 250) return;
			lastExportTime = DateTime.Now;

			try
			{
				string symbol = Instrument.FullName;
				// Sanitize symbol name if needed
				string safeSymbol = symbol.Replace("=F", "").Replace("-", "").Replace(" ", "");
				
				// Timeframe string (e.g., 1min, 5min, Daily)
				string timeframe = "";
				if (BarsPeriod.BarsPeriodType == BarsPeriodType.Minute)
				{
					timeframe = BarsPeriod.Value + "min";
				}
				else if (BarsPeriod.BarsPeriodType == BarsPeriodType.Day)
				{
					timeframe = "Daily";
				}
				else 
				{
					timeframe = BarsPeriod.ToString().Replace(" ", "");
				}
				
				string filename = Path.Combine(exchangeDir, String.Format("data_{0}_{1}.csv", safeSymbol, timeframe));
				
				// We want to export the last N bars. 
				// For efficiency, we can just append the latest bar if file exists, 
				// or rewrite if we want to ensure consistency. 
				// Rewriting last 100 bars is safer for sync.
				
				StringBuilder sb = new StringBuilder();
				sb.AppendLine("Time,Open,High,Low,Close,Volume");
				
				int lookback = Math.Min(CurrentBar, 200);
				
				// Debug log if low data
				if (lookback < 60)
				{
					LogDebug("ExportData: Low data count. CurrentBar: " + CurrentBar + ", Lookback: " + lookback);
				}
				
				for (int i = lookback; i >= 0; i--)
				{
					string time = Time[i].ToString("yyyy-MM-dd HH:mm:ss");
					double open = Open[i];
					double high = High[i];
					double low = Low[i];
					double close = Close[i];
					double volume = Volume[i];
					
					// Use InvariantCulture to ensure decimal point (not comma)
					sb.AppendLine(String.Format(System.Globalization.CultureInfo.InvariantCulture, 
						"{0},{1},{2},{3},{4},{5}", time, open, high, low, close, volume));
				}
				
				File.WriteAllText(filename, sb.ToString());
			}
			catch (Exception ex)
			{
				Print("Error exporting data: " + ex.Message);
			}
		}
		
		private void ExportPositions()
		{
			try
			{
				StringBuilder sb = new StringBuilder();
				sb.AppendLine("Symbol,MarketPosition,Quantity,AveragePrice,UnrealizedPnL,SL,TP");
				
				if (Position.MarketPosition != MarketPosition.Flat)
				{
					// Use InvariantCulture to ensure decimal point (not comma)
					sb.AppendLine(String.Format(System.Globalization.CultureInfo.InvariantCulture,
						"{0},{1},{2},{3},{4},{5},{6}", 
						Instrument.FullName, 
						Position.MarketPosition, 
						Position.Quantity, 
						Position.AveragePrice, 
						Position.GetUnrealizedProfitLoss(PerformanceUnit.Currency, Close[0]),
						currentSL,
						currentTP));
				}
				
				File.WriteAllText(positionsFile, sb.ToString());
			}
			catch (Exception ex)
			{
				Print("Error exporting positions: " + ex.Message);
			}
		}

		private void ExportAccount()
		{
			try
			{
				StringBuilder sb = new StringBuilder();
				sb.AppendLine("AccountName,CashValue,BuyingPower,Equity,RealizedPnL,UnrealizedPnL");
				
				// Use InvariantCulture to ensure decimal point (not comma)
				// Note: Account.Get might return different values depending on connection.
				// We use standard AccountItem keys.
				sb.AppendLine(String.Format(System.Globalization.CultureInfo.InvariantCulture,
					"{0},{1},{2},{3},{4},{5}", 
					Account.Name,
					Account.Get(AccountItem.CashValue, Currency.UsDollar),
					Account.Get(AccountItem.BuyingPower, Currency.UsDollar),
					Account.Get(AccountItem.GrossRealizedProfitLoss, Currency.UsDollar) + Account.Get(AccountItem.CashValue, Currency.UsDollar), // Approx Equity
					Account.Get(AccountItem.RealizedProfitLoss, Currency.UsDollar),
					Account.Get(AccountItem.UnrealizedProfitLoss, Currency.UsDollar)
				));
				
				File.WriteAllText(accountFile, sb.ToString());
			}
			catch (Exception ex)
			{
				// Only print error once to avoid spamming log if account is null
				// Print("Error exporting account: " + ex.Message);
			}
		}

		private void CheckCommands(object sender, EventArgs e)
		{
			if (!File.Exists(commandsFile)) return;
			
			try
			{
				string[] lines = File.ReadAllLines(commandsFile);
				if (lines.Length == 0) return;
				
				LogDebug("Found commands file with " + lines.Length + " lines.");
				
				// Process commands
				foreach (string line in lines)
				{
					if (string.IsNullOrWhiteSpace(line)) continue;
					
					LogDebug("Processing line: " + line);
					
					// Format: ACTION|SYMBOL|QUANTITY|SL|TP
					string[] parts = line.Split('|');
					if (parts.Length < 3) 
					{
						LogDebug("Invalid command format: " + line);
						continue;
					}
					
					string action = parts[0];
					string symbol = parts[1];
					
					// Robust parsing: Parse as double first to handle "1.0", then cast to int
					double qtyDouble = double.Parse(parts[2], System.Globalization.CultureInfo.InvariantCulture);
					int quantity = (int)qtyDouble;
					
					double sl = parts.Length > 3 ? double.Parse(parts[3], System.Globalization.CultureInfo.InvariantCulture) : 0;
					double tp = parts.Length > 4 ? double.Parse(parts[4], System.Globalization.CultureInfo.InvariantCulture) : 0;
					
					// Only process if symbol matches current instrument
					// Check both FullName (e.g., "MNQ 03-26") and MasterInstrument.Name (e.g., "MNQ")
					bool symbolMatches = Instrument.FullName.Contains(symbol) || 
					                     symbol.Contains(Instrument.MasterInstrument.Name) ||
					                     Instrument.MasterInstrument.Name.Contains(symbol);
					
					if (!symbolMatches) 
					{
						LogDebug("Symbol mismatch. Command: " + symbol + ", Instrument: " + Instrument.FullName + " / " + Instrument.MasterInstrument.Name);
						continue;
					}
					
					LogDebug("Symbol matched! Executing " + action);
					
					if (action == "BUY")
					{
						// Set SL/TP if provided (Price mode)
						if (sl > 0) 
						{
							SetStopLoss(CalculationMode.Price, sl);
							currentSL = sl; // Store for visualization
						}
						else 
						{
							SetStopLoss(CalculationMode.Price, 0);
							currentSL = 0;
						}
						
						if (tp > 0) 
						{
							SetProfitTarget(CalculationMode.Price, tp);
							currentTP = tp; // Store for visualization
						}
						else
						{
							currentTP = 0;
						}
						
						EnterLong(quantity);
					}
					else if (action == "SELL")
					{
						if (sl > 0) 
						{
							SetStopLoss(CalculationMode.Price, sl);
							currentSL = sl; // Store for visualization
						}
						else
						{
							currentSL = 0;
						}
						
						if (tp > 0) 
						{
							SetProfitTarget(CalculationMode.Price, tp);
							currentTP = tp; // Store for visualization
						}
						else
						{
							currentTP = 0;
						}
						
						EnterShort(quantity);
					}
					else if (action == "CLOSE")
					{
						if (Position.MarketPosition == MarketPosition.Long) ExitLong();
						else if (Position.MarketPosition == MarketPosition.Short) ExitShort();
					}
				}
				
				// Clear file after processing
				File.WriteAllText(commandsFile, string.Empty);
			}
			catch (Exception ex)
			{
				LogDebug("Error processing commands: " + ex.Message);
			}
		}
		
		private void LogDebug(string message)
		{
			try
			{
				string logFile = Path.Combine(exchangeDir, "debug_log.txt");
				string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
				File.AppendAllText(logFile, timestamp + " | " + message + Environment.NewLine);
				Print(message); // Also print to NT8 output
			}
			catch {}
		}
	}
}
