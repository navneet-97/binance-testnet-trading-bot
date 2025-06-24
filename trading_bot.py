import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import argparse
import time

class TradingBot:
    """
    A comprehensive trading bot for Binance Futures Testnet
    Supports market orders, limit orders, and advanced order types
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize Binance client
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        
        # Set testnet base URL
        if testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com'
        
        # Setup logging
        self.setup_logging()
        
        # Validate connection
        self.validate_connection()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"trading_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Trading bot initialized")
        self.logger.info(f"Testnet mode: {self.testnet}")
    
    def validate_connection(self):
        """Validate API connection and permissions"""
        try:
            # Test connectivity
            status = self.client.get_system_status()
            self.logger.info(f"System status: {status}")
            
            # Test account access
            account_info = self.client.futures_account()
            self.logger.info("Successfully connected to Binance Futures API")
            self.logger.info(f"Account balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Binance API: {str(e)}")
            raise
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance information"""
        try:
            account_info = self.client.futures_account()
            balances = account_info.get('assets', [])
            
            usdt_balance = next((asset for asset in balances if asset['asset'] == 'USDT'), None)
            
            balance_info = {
                'total_balance': account_info.get('totalWalletBalance', '0'),
                'available_balance': account_info.get('availableBalance', '0'),
                'usdt_balance': usdt_balance.get('walletBalance', '0') if usdt_balance else '0'
            }
            
            self.logger.info(f"Account balance retrieved: {balance_info}")
            return balance_info
            
        except Exception as e:
            self.logger.error(f"Error getting account balance: {str(e)}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information and validate if it exists"""
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == symbol.upper():
                    self.logger.info(f"Symbol {symbol} found and active")
                    return symbol_info
            
            raise ValueError(f"Symbol {symbol} not found or not active")
            
        except Exception as e:
            self.logger.error(f"Error getting symbol info: {str(e)}")
            raise
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            
        Returns:
            Order details
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Get symbol info for validation
            self.get_symbol_info(symbol)
            
            # Place market order
            self.logger.info(f"Placing market order: {side} {quantity} {symbol}")
            
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type=Client.FUTURE_ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            self.logger.info(f"Market order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Binance order error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing market order: {str(e)}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                         time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Order price
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order details
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if price <= 0:
                raise ValueError("Price must be positive")
            
            # Get symbol info for validation
            self.get_symbol_info(symbol)
            
            # Place limit order
            self.logger.info(f"Placing limit order: {side} {quantity} {symbol} at {price}")
            
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type=Client.FUTURE_ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce=time_in_force
            )
            
            self.logger.info(f"Limit order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Binance order error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing limit order: {str(e)}")
            raise
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                             price: float, stop_price: float, 
                             time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a stop-limit order (Advanced order type)
        
        Args:
            symbol: Trading symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            stop_price: Stop price
            time_in_force: Time in force
            
        Returns:
            Order details
        """
        try:
            # Validate inputs
            if side.upper() not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if price <= 0 or stop_price <= 0:
                raise ValueError("Price and stop price must be positive")
            
            # Get symbol info for validation
            self.get_symbol_info(symbol)
            
            # Place stop-limit order
            self.logger.info(f"Placing stop-limit order: {side} {quantity} {symbol} at {price}, stop at {stop_price}")
            
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type=Client.FUTURE_ORDER_TYPE_STOP,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce=time_in_force
            )
            
            self.logger.info(f"Stop-limit order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API error: {e}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Binance order error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error placing stop-limit order: {str(e)}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status"""
        try:
            order = self.client.futures_get_order(symbol=symbol.upper(), orderId=order_id)
            self.logger.info(f"Order status retrieved: {order}")
            return order
            
        except Exception as e:
            self.logger.error(f"Error getting order status: {str(e)}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            result = self.client.futures_cancel_order(symbol=symbol.upper(), orderId=order_id)
            self.logger.info(f"Order cancelled: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {str(e)}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get all open orders"""
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol.upper())
            else:
                orders = self.client.futures_get_open_orders()
            
            self.logger.info(f"Retrieved {len(orders)} open orders")
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting open orders: {str(e)}")
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price = float(ticker['price'])
            self.logger.info(f"Current price for {symbol}: {price}")
            return price
            
        except Exception as e:
            self.logger.error(f"Error getting current price: {str(e)}")
            raise

def print_banner():
    """Print application banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                    BINANCE FUTURES TRADING BOT                ║
    ║                         TESTNET VERSION                       ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_user_credentials():
    """Get API credentials from user input or environment variables"""
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key:
        api_key = input("Enter your Binance API Key: ").strip()
    
    if not api_secret:
        api_secret = input("Enter your Binance API Secret: ").strip()
    
    if not api_key or not api_secret:
        raise ValueError("API credentials are required")
    
    return api_key, api_secret

def interactive_mode(bot: TradingBot):
    """Interactive command-line interface"""
    print("\n🚀 Interactive Trading Mode")
    print("Available commands:")
    print("1. balance - Show account balance")
    print("2. price <symbol> - Get current price")
    print("3. market <symbol> <side> <quantity> - Place market order")
    print("4. limit <symbol> <side> <quantity> <price> - Place limit order")
    print("5. stop <symbol> <side> <quantity> <price> <stop_price> - Place stop-limit order")
    print("6. orders [symbol] - Show open orders")
    print("7. status <symbol> <order_id> - Get order status")
    print("8. cancel <symbol> <order_id> - Cancel order")
    print("9. quit - Exit")
    print("-" * 60)
    
    while True:
        try:
            command = input("\n💰 Enter command: ").strip().lower()
            
            if command == 'quit':
                print("👋 Goodbye!")
                break
            
            elif command == 'balance':
                balance = bot.get_account_balance()
                print(f"💼 Account Balance:")
                print(f"   Total: {balance['total_balance']} USDT")
                print(f"   Available: {balance['available_balance']} USDT")
                print(f"   USDT Balance: {balance['usdt_balance']} USDT")
            
            elif command.startswith('price '):
                parts = command.split()
                if len(parts) != 2:
                    print("❌ Usage: price <symbol>")
                    continue
                
                symbol = parts[1]
                price = bot.get_current_price(symbol)
                print(f"💹 Current price for {symbol.upper()}: {price} USDT")
            
            elif command.startswith('market '):
                parts = command.split()
                if len(parts) != 4:
                    print("❌ Usage: market <symbol> <side> <quantity>")
                    continue
                
                symbol, side, quantity = parts[1], parts[2], float(parts[3])
                order = bot.place_market_order(symbol, side, quantity)
                print(f"✅ Market order placed: {order['orderId']}")
                print(f"   Symbol: {order['symbol']}")
                print(f"   Side: {order['side']}")
                print(f"   Quantity: {order['origQty']}")
                print(f"   Status: {order['status']}")
            
            elif command.startswith('limit '):
                parts = command.split()
                if len(parts) != 5:
                    print("❌ Usage: limit <symbol> <side> <quantity> <price>")
                    continue
                
                symbol, side, quantity, price = parts[1], parts[2], float(parts[3]), float(parts[4])
                order = bot.place_limit_order(symbol, side, quantity, price)
                print(f"✅ Limit order placed: {order['orderId']}")
                print(f"   Symbol: {order['symbol']}")
                print(f"   Side: {order['side']}")
                print(f"   Quantity: {order['origQty']}")
                print(f"   Price: {order['price']}")
                print(f"   Status: {order['status']}")
            
            elif command.startswith('stop '):
                parts = command.split()
                if len(parts) != 6:
                    print("❌ Usage: stop <symbol> <side> <quantity> <price> <stop_price>")
                    continue
                
                symbol, side, quantity, price, stop_price = parts[1], parts[2], float(parts[3]), float(parts[4]), float(parts[5])
                order = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
                print(f"✅ Stop-limit order placed: {order['orderId']}")
                print(f"   Symbol: {order['symbol']}")
                print(f"   Side: {order['side']}")
                print(f"   Quantity: {order['origQty']}")
                print(f"   Price: {order['price']}")
                print(f"   Stop Price: {order['stopPrice']}")
                print(f"   Status: {order['status']}")
            
            elif command.startswith('orders'):
                parts = command.split()
                symbol = parts[1] if len(parts) > 1 else None
                orders = bot.get_open_orders(symbol)
                
                if not orders:
                    print("📋 No open orders")
                else:
                    print(f"📋 Open orders ({len(orders)}):")
                    for order in orders:
                        print(f"   Order ID: {order['orderId']}")
                        print(f"   Symbol: {order['symbol']}")
                        print(f"   Side: {order['side']}")
                        print(f"   Type: {order['type']}")
                        print(f"   Quantity: {order['origQty']}")
                        print(f"   Price: {order['price']}")
                        print(f"   Status: {order['status']}")
                        print("-" * 30)
            
            elif command.startswith('status '):
                parts = command.split()
                if len(parts) != 3:
                    print("❌ Usage: status <symbol> <order_id>")
                    continue
                
                symbol, order_id = parts[1], int(parts[2])
                order = bot.get_order_status(symbol, order_id)
                print(f"📊 Order Status:")
                print(f"   Order ID: {order['orderId']}")
                print(f"   Symbol: {order['symbol']}")
                print(f"   Side: {order['side']}")
                print(f"   Type: {order['type']}")
                print(f"   Status: {order['status']}")
                print(f"   Quantity: {order['origQty']}")
                print(f"   Executed: {order['executedQty']}")
                print(f"   Price: {order['price']}")
            
            elif command.startswith('cancel '):
                parts = command.split()
                if len(parts) != 3:
                    print("❌ Usage: cancel <symbol> <order_id>")
                    continue
                
                symbol, order_id = parts[1], int(parts[2])
                result = bot.cancel_order(symbol, order_id)
                print(f"✅ Order cancelled: {result['orderId']}")
            
            else:
                print("❌ Unknown command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Main application entry point"""
    print_banner()
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    parser.add_argument('--api-key', help='Binance API Key')
    parser.add_argument('--api-secret', help='Binance API Secret')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--symbol', help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('--side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--quantity', type=float, help='Order quantity')
    parser.add_argument('--price', type=float, help='Order price (for limit orders)')
    parser.add_argument('--type', choices=['market', 'limit', 'stop'], default='market', help='Order type')
    parser.add_argument('--stop-price', type=float, help='Stop price (for stop-limit orders)')
    
    args = parser.parse_args()
    
    try:
        # Get API credentials
        if args.api_key and args.api_secret:
            api_key, api_secret = args.api_key, args.api_secret
        else:
            api_key, api_secret = get_user_credentials()
        
        # Initialize trading bot
        print("🔧 Initializing trading bot...")
        bot = TradingBot(api_key, api_secret, testnet=True)
        print("✅ Trading bot initialized successfully!")
        
        # Show account balance
        balance = bot.get_account_balance()
        print(f"\n💼 Account Balance: {balance['total_balance']} USDT")
        
        # Interactive mode or single command
        if args.interactive or not all([args.symbol, args.side, args.quantity]):
            interactive_mode(bot)
        else:
            # Execute single command
            print(f"\n🚀 Executing single command...")
            
            if args.type == 'market':
                order = bot.place_market_order(args.symbol, args.side, args.quantity)
                print(f"✅ Market order placed: {order['orderId']}")
            
            elif args.type == 'limit':
                if not args.price:
                    print("❌ Price is required for limit orders")
                    return
                order = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
                print(f"✅ Limit order placed: {order['orderId']}")
            
            elif args.type == 'stop':
                if not args.price or not args.stop_price:
                    print("❌ Price and stop-price are required for stop-limit orders")
                    return
                order = bot.place_stop_limit_order(args.symbol, args.side, args.quantity, args.price, args.stop_price)
                print(f"✅ Stop-limit order placed: {order['orderId']}")
    
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logging.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()