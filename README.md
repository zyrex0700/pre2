# MT5 AI-Driven Trading Bot (Phase 1 MVP)

ربات معاملاتی Production-oriented با Python برای اتصال به **MetaTrader 5** و ترید روی `XAUUSD` و `EURUSD` با حالت‌های Backtest / Paper / Live(Small Risk).

## ⚠️ Important Safety Notes
- هیچ تضمین سودی وجود ندارد.
- پیش‌فرض روی Demo/Paper است.
- برای Live باید `BOT_MODE=live` و `AUTO_TRADE=true` را آگاهانه فعال کنید.

## Features (Phase 1)
- اتصال پایدار به MT5 (`MetaTrader5` Python package)
- دریافت دیتای تاریخی OHLCV (M15/H1)
- Pipeline فیچر: returns/log_returns/ATR/RSI/MACD/rolling stats/time features
- Labeling با Triple Barrier ساده
- ML مدل پایه (Logistic Regression) با خروجی احتمال سیگنال
- سیگنال `BUY/SELL/NO_TRADE` + confidence + reason
- بک‌تست با spread/slippage/commission
- موتور اجرای سفارش با retry/backoff
- Risk Manager + Kill-Switch:
  - max daily/weekly loss
  - max trades per day
  - max consecutive errors
  - spread filter
- لاگ JSON قابل Audit در `logs/bot.log`
- Telegram alerts (اختیاری)

---

## Repo Structure

```text
src/
  config.py
  mt5_connector.py
  data_collector.py
  data_cleaner.py
  feature_engine.py
  labeler.py
  model_train.py
  model_infer.py
  backtester.py
  signal_engine.py
  risk_manager.py
  execution_engine.py
  position_manager.py
  monitoring.py
  utils.py
scripts/
  health_check.py
  fetch_history.py
  train_model.py
  backtest.py
  run_live.py
tests/
  test_risk_manager.py
  test_feature_engine.py
config.yaml
.env.example
requirements.txt
```

---

## Windows Setup (MT5 VPS)

1) نصب MetaTrader 5 و Login به حساب Demo.
2) فعال‌سازی Algo Trading در MT5.
3) نصب Python 3.10+.
4) ایجاد virtualenv و نصب dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

5) تنظیم env:

```bash
copy .env.example .env
```

`.env` را با مقادیر واقعی پر کنید:
- `MT5_LOGIN`
- `MT5_PASSWORD`
- `MT5_SERVER`
- `MT5_PATH`
- `BOT_MODE=paper` (پیش‌فرض امن)
- `AUTO_TRADE=false`

---

## Step-by-step Run

### 1) Health Check
```bash
python scripts/health_check.py
```
باید اتصال، account_info و symbol_select برای XAUUSD/EURUSD را OK بدهد.

### 2) Fetch History
```bash
python scripts/fetch_history.py
```
خروجی در `data/raw/*.parquet`.

### 3) Train Model
```bash
python scripts/train_model.py
```
خروجی مدل در `models/model.joblib`.

### 4) Backtest
```bash
python scripts/backtest.py
```
خروجی:
- `reports/backtest_trades.csv`
- `reports/backtest_metrics.csv`

### 5) Run Paper/Demo Live Loop
```bash
python scripts/run_live.py
```
- اگر `AUTO_TRADE=false`: فقط سیگنال/لاگ.
- اگر `AUTO_TRADE=true`: ارسال سفارش مارکت با SL/TP و Risk Checks.

---

## Config Highlights (`config.yaml`)
- `app.timeframe`: `M15` یا `H1`
- `app.lookback_bars`, `app.horizon_bars`
- `risk.risk_per_trade`, `risk.max_daily_loss`, `risk.max_trades_per_day`
- `risk.spread_max_points`
- `backtest.commission_per_lot`, `backtest.slippage_points`
- `execution.retry_attempts`, `execution.retry_backoff_sec`
- `telegram.enabled`

---

## Troubleshooting

### MT5 initialize failed
- چک کنید MT5 باز است و credential صحیح است.
- `MT5_PATH` را دقیق به `terminal64.exe` بدهید.
- نسخه python/MT5 package سازگار باشد.

### symbol_select false
- نام سمبل در بروکر متفاوت است (مثلاً `XAUUSDm`).
- در `config.yaml -> symbols` اصلاح کنید.

### order_send fail / retcode error
- spread بالا، market closed، یا volume نامعتبر.
- `logs/bot.log` را چک کنید.
- deviation/spread filters/risk limits را بازبینی کنید.

### No trades
- confidence thresholdها بالا هستند.
- spread filter سخت‌گیرانه است.
- Kill-switch فعال شده.

---

## Phase 2 Upgrade Path (ONNX + MQL5 EA)
مسیر ارتقا در فایل `src/model_utils_phase2.md` آمده است:
- Export مدل به ONNX
- EA در MQL5 برای inference داخل MT5
- تطبیق سیگنال Python و EA روی داده یکسان

---

## Dev Test
```bash
pytest -q
```
