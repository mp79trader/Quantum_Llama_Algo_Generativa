import pandas as pd
import os
import time
from datetime import datetime
from rich.console import Console

console = Console()

class NinjaTraderConnector:
    def __init__(self, exchange_dir='C:/QuantumGAN/Exchange'):
        self.exchange_dir = exchange_dir
        self.commands_file = os.path.join(self.exchange_dir, 'commands.txt')
        self.positions_file = os.path.join(self.exchange_dir, 'positions.csv')
        self.account_file = os.path.join(self.exchange_dir, 'account.csv')
        
    def get_account_info(self):
        """Reads account.csv to get balance and equity"""
        if not os.path.exists(self.account_file):
            return None
            
        try:
            df = pd.read_csv(self.account_file)
            if df.empty: return None
            
            # Expected: AccountName,CashValue,BuyingPower,Equity,RealizedPnL,UnrealizedPnL
            data = df.iloc[0].to_dict()
            
            return {
                'balance': float(data.get('CashValue', 0)),
                'equity': float(data.get('Equity', 0)),
                'margin_free': float(data.get('BuyingPower', 0)),
                'profit': float(data.get('RealizedPnL', 0)) + float(data.get('UnrealizedPnL', 0))
            }
        except Exception as e:
            # console.print(f"[red]Error reading account info: {e}[/red]")
            return None
        self.connected = False
        
    def connect(self):
        """Checks if exchange directory exists"""
        if not os.path.exists(self.exchange_dir):
            try:
                os.makedirs(self.exchange_dir)
                console.print(f"[yellow]Directorio de intercambio creado: {self.exchange_dir}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error creando directorio de intercambio: {e}[/red]")
                return False
        
        self.connected = True
        console.print(f"[green]Conector NinjaTrader listo. Directorio: {self.exchange_dir}[/green]")
        return True

    def shutdown(self):
        self.connected = False

    def get_balance(self):
        """Returns account balance (Mocked for now)"""
        return 10000.0 # Placeholder until we export account info from NT8

    def get_equity(self):
        """Returns account equity (Mocked for now)"""
        return 10000.0 # Placeholder

    def get_latest_candles(self, symbol, timeframe="1m", n=100):
        """Reads the latest candles from the CSV exported by NT8"""
        if not self.connected:
            return None
            
        # Map timeframe to NT8 format if needed (e.g., "1m" -> "1min")
        # Assuming NT8 writes files like: data_MNQ_1min.csv
        tf_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "60min",
            "4h": "240min",
            "1d": "Daily"
        }
        nt_tf = tf_map.get(timeframe, timeframe)
        
        # Try multiple symbol formats to find the CSV file
        # NT8 may export as: MNQ0326, MNQMAR26, MNQ MAR26, etc.
        symbol_variants = [
            symbol.replace("=F", "").replace("-", "").replace(" ", ""),  # MNQ0326
            symbol.replace("=F", "").replace(" ", "").replace("-", ""),  # MNQ0326
            symbol.replace("=F", "").replace(" ", ""),  # MNQ03-26
            symbol.replace("=F", "").replace("-", " ").replace(" ", ""), # MNQ0326
        ]
        
        # Also try common NT8 naming: "MNQ 03-26" -> "MNQMAR26" (month name)
        month_map = {"01": "JAN", "02": "FEB", "03": "MAR", "04": "APR", "05": "MAY", "06": "JUN",
                     "07": "JUL", "08": "AUG", "09": "SEP", "10": "OCT", "11": "NOV", "12": "DEC"}
        
        # Parse "MNQ 03-26" format -> MNQMAR26
        import re
        match = re.search(r'(\w+)\s*(\d{2})[-/](\d{2})', symbol)
        if match:
            base, month, year = match.groups()
            month_name = month_map.get(month, month)
            symbol_variants.append(f"{base}{month_name}{year}")  # MNQMAR26
            symbol_variants.append(f"{base}{month_name}26")      # MNQMAR26 (without leading 0)
        
        # Remove duplicates while preserving order
        symbol_variants = list(dict.fromkeys(symbol_variants))
        
        file_path = None
        for safe_symbol in symbol_variants:
            candidate_path = os.path.join(self.exchange_dir, f'data_{safe_symbol}_{nt_tf}.csv')
            if os.path.exists(candidate_path):
                file_path = candidate_path
                break
        
        if file_path is None:
            console.print(f"[yellow]Esperando datos de NinjaTrader. Buscando: data_*_{nt_tf}.csv en {self.exchange_dir}[/yellow]")
            return None
            
        # Retry logic for reading CSV (handle file locking)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Read CSV. Expected format: Time,Open,High,Low,Close,Volume
                # Use explicit delimiter and skip bad lines
                df = pd.read_csv(file_path, sep=',', on_bad_lines='skip')
                
                if df.empty:
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                    return None
                
                # Ensure columns match
                required_cols = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in df.columns for col in required_cols):
                    # console.print(f"[red]Formato CSV incorrecto en {file_path}[/red]")
                    return None
                    
                # Parse dates with error handling (coerce garbage to NaT)
                df['time'] = pd.to_datetime(df['Time'], errors='coerce')
                
                # Drop rows with invalid dates
                df.dropna(subset=['time'], inplace=True)
                
                # Sort and take last n
                df = df.sort_values('time').tail(n)
                
                # Debug: Log row count if small
                if len(df) < 50:
                    console.print(f"[yellow]Warning: Read {len(df)} rows from {os.path.basename(file_path)}. Need 50+ for validation.[/yellow]")
                
                return df[['time', 'Open', 'High', 'Low', 'Close', 'Volume']]
                
            except Exception as e:
                if "No columns to parse" in str(e) or "EmptyDataError" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                        
                console.print(f"[red]Error leyendo datos de NT8 (Attempt {attempt+1}): {e}[/red]")
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                    
        return None

    def get_current_price(self, symbol):
        # We can get the last close from the candles
        df = self.get_latest_candles(symbol, n=1)
        if df is not None and not df.empty:
            return df['Close'].iloc[-1]
        return None

    def get_positions(self, symbol=None):
        """Reads positions.csv"""
        if not os.path.exists(self.positions_file):
            return []
            
        try:
            df = pd.read_csv(self.positions_file)
            # Expected: Symbol,MarketPosition,Quantity,AveragePrice,UnrealizedPnL
            
            # If CSV is empty (only headers), return empty list
            if df.empty:
                return []
            
            positions = []
            for _, row in df.iterrows():
                # Filter by symbol if requested
                if symbol and symbol not in row['Symbol']: # Simple check
                    continue
                    
                # Convert to a dict-like object compatible with the system
                # The system expects an object with .ticket, .symbol, .volume, .type, .price_open, .profit
                
                # Mock object
                class Position:
                    pass
                
                pos = Position()
                pos.ticket = 0 # NT8 doesn't expose ticket easily in simple export, use 0 or hash
                pos.symbol = row['Symbol']
                pos.volume = row['Quantity']
                pos.type = 0 if row['MarketPosition'] == 'Long' else 1 # 0=Buy, 1=Sell (MT5 standard)
                pos.price_open = row['AveragePrice']
                pos.profit = row['UnrealizedPnL']
                
                # Read SL/TP from CSV if available (added in v2)
                pos.sl = float(row.get('SL', 0.0))
                pos.tp = float(row.get('TP', 0.0))
                
                positions.append(pos)
                
            return positions
            
        except Exception as e:
            # Only show error if it's not just an empty file
            if "No columns to parse" not in str(e):
                console.print(f"[red]Error leyendo posiciones: {e}[/red]")
            return []

    def place_order(self, symbol, order_type, volume, sl=None, tp=None):
        """Writes command to commands.txt"""
        if not self.connected:
            return None
            
        # Command Format: ACTION|SYMBOL|QUANTITY|SL|TP
        # Example: BUY|MNQ|1|15000|15100
        
        # Ensure volume is int
        vol_int = int(float(volume))
        
        # Round prices to 2 decimals (tick size compatible)
        sl_rounded = round(float(sl), 2) if sl else 0
        tp_rounded = round(float(tp), 2) if tp else 0
        
        cmd = f"{order_type}|{symbol}|{vol_int}|{sl_rounded}|{tp_rounded}"
        
        try:
            with open(self.commands_file, 'a') as f:
                f.write(cmd + "\n")
            console.print(f"[green]Comando enviado a NinjaTrader: {cmd}[/green]")
            
            # Mock result object
            class Result:
                retcode = 10009 # DONE
                order = 12345
                comment = "Sent to NT8"
            return Result()
            
        except Exception as e:
            console.print(f"[red]Error escribiendo comando: {e}[/red]")
            return None

    def close_position(self, ticket, symbol=None):
        """Closes position. Sends CLOSE command to NT8."""
        if not self.connected:
            return False
            
        # If symbol is not provided, we can't close specific instrument in NT8 easily via this simple connector
        # unless we stored the active symbol.
        if not symbol:
            console.print("[red]Error: Symbol required to close position in NT8[/red]")
            return False
            
        # Command Format: CLOSE|SYMBOL|QUANTITY|SL|TP
        # Quantity ignored for CLOSE in current C# impl (closes all)
        cmd = f"CLOSE|{symbol}|0|0|0"
        
        try:
            with open(self.commands_file, 'a') as f:
                f.write(cmd + "\n")
            console.print(f"[green]Comando de cierre enviado a NinjaTrader: {cmd}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error escribiendo comando de cierre: {e}[/red]")
            return False
