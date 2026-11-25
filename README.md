# PhalParakh

Upload a fruit photo, find out how ripe it is, and get an estimated price based on mandi rates.
The app supports English and Hindi (switch at the top of the page).

**Flow:** photo → YOLOv8 classifies the fruit and its ripeness → an XGBoost model gives the mandi base price →
final price = base price per kg × ripeness multiplier × retail markup × weight.
The app also shows historical mandi prices (year by year and month by month).

Academic project, SVSU, B.Tech CSE.

## Results

| Part | Model | Result |
|---|---|---|
| Ripeness | YOLOv8n-cls, 30 epochs, 5 fruits × 3 stages = 15 classes | Top-1 accuracy about 95% on the validation set |
| Price (baseline: past average) | None | MAE 15.99 ₹/kg, R² 0.48 |
| Price (final) | XGBoost | MAE 9.11 ₹/kg, RMSE 13.86, R² 0.81 |

Price model: trained on 2002 to 2023, tested on 2024 onwards (time-based split, 22,355 train rows and 4,206 test rows).
The saved model is retrained on all the data, so the numbers above are the test-set numbers.

## Project structure

    app.py                      Streamlit app
    src/ripeness.py             YOLOv8 inference
    src/price.py                price model + ripeness multiplier + retail markup
    src/validate.py             image and weight checks
    src/i18n.py                 English and Hindi text
    training/                   data preparation and training scripts
    models/                     best.pt, price_model_hist.joblib
    assets/price_history.csv    monthly mandi prices used for the history charts

## 1. Setup

    python -m venv venv
    venv\Scripts\activate            (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt

Developed with Python 3.14 on Windows.

## 2. Ripeness model (Google Colab, T4 GPU)

Download a ripeness image dataset (Kaggle / Roboflow Universe), then once per fruit:

    python training/prepare_data.py --src <folder> --fruit banana --map "green=unripe,ripe=ripe,overripe=overripe"
    python training/train_ripeness.py --data data --epochs 30      # creates models/best.pt

Class folders must be named `<fruit>_<unripe|ripe|overripe>` (prepare_data.py does this).
Copy `models/best.pt` into the `models/` folder of this project.

## 3. Price model

Price data comes from MandiBench (Hugging Face, gated dataset, request access first).

    set HF_TOKEN in your terminal (PowerShell: $env:HF_TOKEN="your_token")
    python training/explore_mandibench.py     # downloads series/all.parquet (about 1.3 GB)
    python training/check_fruits.py           # filters our fruits into data/fruits_raw.csv
    python training/train_price_hist.py       # creates models/price_model_hist.joblib
    python training/make_history.py           # creates assets/price_history.csv

Never put your token in a file or commit it.

## 4. Run

    streamlit run app.py

The app needs `models/best.pt`, `models/price_model_hist.joblib` and `assets/price_history.csv`.

## Limitations

- Mandi data has no ripeness information. The ripeness multipliers (unripe 0.90, ripe 1.00, overripe 0.60)
  and the retail markup (1.25) are our own assumptions (see `src/price.py`).
- The price model uses only fruit, state, variety, month and year. It has no weather or market-specific
  information. For each fruit, the most common variety is used.
- Wrong prices (more than 5× or less than 1/10 of the fruit's median) were removed
  (20,829 of 3.2 million rows, 0.65%).
- The classifier handles one fruit per photo. There is no "not a fruit" class, so photos with confidence
  below 50% are rejected, but a non-fruit photo can still pass.
- Ripe and overripe are sometimes confused. The overripe classes of apple, orange and tomato have few
  training images.
- Historical prices are wholesale mandi prices and end in May 2026.
- `tests/make_fake_prices.py` creates fake data for code testing only. The real model is trained on MandiBench.

## Data

- Prices: MandiBench (`judicialmind/MandiBench` on Hugging Face), built from Agmarknet mandi prices, 2002 to 2026.
  Please check the dataset's own licence terms before reuse. This project is for academic use.
- Ripeness images: [add your dataset name and link here]