# Fruit Ripeness & Price Estimation Portal

Upload fruit photo -> YOLOv8 classifies ripeness -> ML model gives mandi base price ->
final price = base/kg x ripeness multiplier x retail markup x weight.

## 1. Setup
    python -m venv venv
    venv\Scripts\activate            (Mac/Linux: source venv/bin/activate)
    pip install -r requirements.txt

## 2. Ripeness model (Google Colab, T4 GPU)
Download ripeness datasets (Kaggle / Roboflow Universe), then once per fruit:

    python training/prepare_data.py --src <folder> --fruit banana --map "green=unripe,semi-ripe=skip,ripe=ripe,overripe=overripe"
    python training/train_ripeness.py --data data --epochs 30      # -> models/best.pt

Class folder names MUST end up as <fruit>_<unripe|ripe|overripe> (prepare_data.py does this).
Copy models/best.pt into this project's models/ folder.

## 3. Price model
Get a real mandi CSV (Kaggle "Agmarknet" / data.gov.in) with columns like
Arrival_Date, Commodity, State, Grade/Variety, Modal_Price (Rs/quintal).

    python training/train_price.py --csv prices.csv --fruits mango,banana,apple
    # -> models/price_model.joblib + price_metrics.json + price_actual_vs_predicted.png

## 4. Run
    streamlit run app.py

## 5. Test
    pip install pytest
    python -m pytest tests

(tests/make_fake_prices.py makes FAKE data only to test the code; never report its numbers.)

## Assumptions / limitations (write in report + viva)
- Mandi data has no ripeness or weight: ripeness multipliers (Unripe 0.90, Ripe 1.00, Overripe 0.60)
  and retail markup 1.25 are our own assumptions (src/price.py).
- Price model predicts monthly average per (fruit, state, grade, month); time-based split
  (last 20% of months = test).
- Classifier handles one fruit per photo; confidence below 50% asks for a new photo.

## Limitations
- Mandi data mein ripeness ka column nahi hota. Isliye ripeness ka price par asar
  assumed multipliers se laga hai: unripe 0.90, ripe 1.00, overripe 0.60.
  Retail markup 1.25 bhi ek assumption hai.
- Price model sirf fruit, state, variety aur mahine par chalta hai. Mausam ya
  mandi-specific cheezein shamil nahi hain. Variety har fruit ki sabse common wali li gayi hai.
- Galat prices (fruit ke median se 5x zyada ya 10x kam) filter kiye gaye
  (20,829 / 3.2 million rows, 0.65%).
- Final saved price model poore data par dobara train hua hai. Report ke numbers
  2024+ test set ke hain.
- Non-fruit images ke liye alag class nahi hai. 50% confidence threshold se handle kiya gaya.
- Ripeness model ki accuracy ~95% hai. Ripe aur overripe ke beech kabhi-kabhi confusion hota hai.
- tests/make_fake_prices.py sirf testing ke liye hai. Asli model MandiBench data par bana hai.

## Data
- Price: MandiBench (judicialmind/MandiBench, Hugging Face), Agmarknet mandi prices, 2002-2026.
- Ripeness images: [yahan apne dataset ka naam likho]
