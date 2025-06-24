# 📈 Binance Futures Trading Bot (Testnet)

A comprehensive and fully-featured Binance Futures trading bot for the **Binance Testnet**.
Supports market, limit, and stop-limit orders with real-time data, account balance tracking, order management, and more.

---

## 📋 Requirements

### ✅ Python Requirements (`requirements.txt`)

```
python-binance==1.0.19
argparse
logging
datetime
typing
```

### ✅ System Requirements

* Python 3.7 or higher
* Internet connection
* Binance Testnet account with API credentials

---

## 🚀 Setup Instructions

### 🔹 Step 1: Create Binance Testnet Account

1. Go to the [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Log in with GitHub or create a testnet account.
3. Access the Futures interface.

### 🔹 Step 2: Generate API Credentials

1. Navigate to **API Management** in the testnet.
2. Generate an `HMAC_SHA256` key.
3. **Copy and store** your API Key and Secret securely.
4. Ensure the key has **futures trading permissions** enabled.

### 🔹 Step 3: Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv trading_bot_env

# Activate virtual environment
# On Windows:
trading_bot_env\Scripts\activate
# On macOS/Linux:
source trading_bot_env/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 🔹 Step 4: Set Environment Variables (Optional)

```bash
# On Windows (Command Prompt)
set BINANCE_API_KEY=your_api_key
set BINANCE_API_SECRET=your_api_secret
```

### 🔹 Step 5: Run the Trading Bot

#### ✅ Interactive Mode (recommended)

```bash
python trading_bot.py --interactive
```

## 🔧 Configuration Details

### ⚙️ Testnet Configuration

* Base URL: `https://testnet.binancefuture.com`
* Environment: Binance Futures Testnet (no real funds)
* Default Leverage: 1x (configurable on interface)

### ↻ Supported Order Types

* **Market Orders**: Execute instantly at best price
* **Limit Orders**: Execute at specified price or better
* **Stop-Limit Orders**: Triggered by stop price, executed as limit

### 📈 Trading Pairs

All USDT-M perpetual contracts supported
Popular pairs: `BTCUSDT`, `ETHUSDT`, `BNBUSDT`, `ADAUSDT`, etc.

---

## 🎯 Interactive Mode Commands

```bash
balance                         # Show account balance
price BTCUSDT                   # Get real-time price
market BTCUSDT BUY 0.002       # Place market order
limit BTCUSDT SELL 0.002 53000 # Place limit order
stop BTCUSDT SELL 0.003 52000 52500 # Place stop-limit order
orders                          # List open orders
status BTCUSDT 12345678         # Order status
cancel BTCUSDT 12345678         # Cancel order
quit                            # Exit
```

---

## ⚙️ Command-Line Arguments

```bash
--api-key          Binance API Key
--api-secret       Binance API Secret
--interactive, -i  Run in interactive mode
--symbol           Trading pair (e.g. BTCUSDT)
--side             BUY or SELL
--quantity         Amount to trade
--price            Price for limit/stop-limit orders
--type             Order type (market / limit / stop)
--stop-price       Stop price for stop-limit orders
```

---

## 📊 Features

### ✅ Core Trading Features

* Market, Limit, and Stop-Limit Orders
* Real-time Price Fetching
* Account Balance Checking
* Order Status & Cancellation
* Open Orders Listing

### ✅ Technical Features

* Robust error handling with logging
* Input validation for all actions
* Console + file logging
* API connectivity verification
* Symbol validation
* CLI-based architecture
* Type annotations for maintainability

---

## 🛠 License

---

## 📨 Contact

Have questions or feedback?
Feel free to reach out or open an issue.
