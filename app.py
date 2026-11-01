"""Fruit Ripeness & Price Estimation Portal  (run: streamlit run app.py)"""
import datetime
import streamlit as st
from PIL import Image

from src.validate import validate_image, validate_weight
from src.ripeness import predict_ripeness, RipenessModelMissing, CONF_THRESHOLD
from src.price import predict_price, options, PriceModelMissing, RIPENESS_MULTIPLIER, RETAIL_MARKUP

st.set_page_config(page_title="Fruit Ripeness & Price", page_icon="🍋", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {font-family: 'IBM Plex Sans', sans-serif;}
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 2rem; max-width: 820px;}

.stApp {
  background-color: #0E0F0C;
  background-image: radial-gradient(#ffffff14 1px, transparent 1px);
  background-size: 24px 24px;
}

/* header */
.top {border-bottom: 1px solid #2A2B26; padding-bottom: 18px; margin-bottom: 26px;}
.tag {font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .12em;
  text-transform: uppercase; color: #F2C14E;}
.top h1 {font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 3.2rem; line-height: 1; margin: 10px 0 8px; padding: 0; color: #ECE8DD;}
.top h1 span {color: #F2C14E;}
.top p {color: #9C9886; margin: 0; max-width: 520px;}

/* sirf ek halka animation: sab kuch neeche se aata hai */
.element-container {animation: rise .5s ease both;}
@keyframes rise {from {opacity: 0; transform: translateY(14px);} to {opacity: 1; transform: none;}}

/* headings */
h2, h3 {font-family: 'Bricolage Grotesque', sans-serif !important; color: #ECE8DD;}

/* upload box */
[data-testid="stFileUploader"] section {
  border: 1.5px dashed #5b5a4c; border-radius: 6px; background: #12130F; transition: .2s;}
[data-testid="stFileUploader"] section:hover {border-color: #F2C14E; background: #171813;}

[data-testid="stImage"] img {border-radius: 6px; border: 1px solid #2A2B26;}

/* button: side shadow wala, dabta hai */
div.stButton > button {
  background: #F2C14E; color: #0E0F0C; font-weight: 600; border: 1.5px solid #0E0F0C;
  border-radius: 4px; padding: .55rem 1.6rem; box-shadow: 4px 4px 0 #8a6d1f;
  transition: transform .12s, box-shadow .12s;}
div.stButton > button:hover {color: #0E0F0C; transform: translate(-2px, -2px); box-shadow: 6px 6px 0 #8a6d1f;}
div.stButton > button:active {transform: translate(3px, 3px); box-shadow: 1px 1px 0 #8a6d1f;}

/* result cards */
[data-testid="stMetric"] {background: #171813; border: 1px solid #2A2B26;
  border-left: 4px solid #F2C14E; border-radius: 4px; padding: 16px 18px;}
[data-testid="stMetricLabel"] {font-family: 'IBM Plex Mono', monospace; font-size: .75rem;
  text-transform: uppercase; letter-spacing: .08em; color: #9C9886;}
[data-testid="stMetricValue"] {font-family: 'Bricolage Grotesque', sans-serif; color: #F2C14E;}

[data-testid="stExpander"] {background: #12130F; border: 1px solid #2A2B26; border-radius: 4px;}
[data-testid="stAlert"] {border-radius: 4px;}
.foot {font-family: 'IBM Plex Mono', monospace; font-size: .72rem; color: #6d6a5c;
  border-top: 1px solid #2A2B26; margin-top: 36px; padding-top: 12px;}
</style>

<div class="top">
  <span class="tag">SVSU · B.Tech CSE · AIA Project</span>
  <h1>Phal<span>Parakh</span></h1>
  <p>Fruit ki photo daalo. Ripeness pehchano, aur mandi ke rate se price ka andaza lo.</p>
</div>
""", unsafe_allow_html=True)

# ---- models must exist: no fake/demo output ----
try:
    opts = options()
except PriceModelMissing as e:
    st.error(str(e)); st.stop()

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

col1, col2 = st.columns(2)
with col1:
    upload = st.file_uploader("Fruit ki photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
with col2:
    weight = st.number_input("Weight (kg)", min_value=0.0, value=1.0, step=0.5)
    state = st.selectbox("State", opts["states"],
                         index=opts["states"].index("Haryana") if "Haryana" in opts["states"] else 0)
    month = st.selectbox("Month", range(1, 13), index=datetime.date.today().month - 1,
                         format_func=lambda m: MONTHS[m - 1])
    grade = None

if upload is not None:
    ok, msg = validate_image(upload)
    if not ok:
        st.error(msg); st.stop()
    img = Image.open(upload)
    st.image(img, caption="Uploaded image", use_container_width=True)

go = st.button("Estimate", type="primary", disabled=upload is None)

if go:
    ok, msg = validate_weight(weight)
    if not ok:
        st.error(msg); st.stop()

    try:
        with st.spinner("Ripeness check ho rahi hai..."):
            r = predict_ripeness(img)
    except RipenessModelMissing as e:
        st.error(str(e)); st.stop()

    if not r["confident"]:
        st.warning(f"Model sirf {r['confidence']:.0%} confident hai (minimum {CONF_THRESHOLD:.0%}). "
                   "Saaf light mein, ek hi fruit ki, close-up photo dobara upload karo.")
        st.stop()

    fruit_name = r["fruit"].title()
    if fruit_name not in opts["fruits"]:
        st.error(f"'{fruit_name}' ka price model available nahi hai. Supported: {', '.join(opts['fruits'])}")
        st.stop()
    if r["ripeness"] not in RIPENESS_MULTIPLIER:
        st.error(f"Unknown ripeness label '{r['ripeness']}' (training folder names check karo).")
        st.stop()

    try:
        p = predict_price(fruit_name, r["ripeness"], weight, state, month, grade)
    except Exception as e:
        st.error(f"Price estimate nahi ho paya: {e}"); st.stop()

    st.subheader(f"{fruit_name} - {r['ripeness'].title()}  ({r['confidence']:.0%} confident)")
    c1, c2 = st.columns(2)
    c1.metric("Price per kg", f"₹ {p['price_per_kg']}")
    c2.metric(f"Total ({weight:g} kg)", f"₹ {p['total_price']}")

    with st.expander("Ye price kaise bana?"):
        st.write(f"Mandi base price ({p['model']} model): ₹{p['base_price_per_kg']}/kg  \n"
                 f"× ripeness multiplier ({r['ripeness']}): {p['ripeness_multiplier']}  \n"
                 f"× retail markup: {p['retail_markup']}  \n"
                 f"= ₹{p['price_per_kg']}/kg")
        st.caption("Multipliers aur markup assumptions hain (mandi data mein ripeness nahi hoti).")
    with st.expander("Top 3 predictions"):
        for n, c in r["top3"]:
            st.write(f"{n}: {c:.1%}")
