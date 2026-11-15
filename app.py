"""PhalParakh: fruit ripeness and price estimation (run: streamlit run app.py)"""
import datetime

import pandas as pd
import streamlit as st
from PIL import Image

from src.validate import validate_image, validate_weight
from src.ripeness import predict_ripeness, RipenessModelMissing, CONF_THRESHOLD
from src.price import predict_price, options, PriceModelMissing, RIPENESS_MULTIPLIER
from src.i18n import t, fruit_label, stage_label, state_label, month_name, label_name

st.set_page_config(page_title="PhalParakh", page_icon="🍋", layout="centered")

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

.top {border-bottom: 1px solid #2A2B26; padding-bottom: 18px; margin-bottom: 26px;}
.tag {font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .12em;
  text-transform: uppercase; color: #F2C14E;}
.top h1 {font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 3.2rem; line-height: 1; margin: 10px 0 8px; padding: 0; color: #ECE8DD;}
.top h1 span {color: #F2C14E;}
.top p {color: #9C9886; margin: 0; max-width: 520px;}

.element-container {animation: rise .5s ease both;}
@keyframes rise {from {opacity: 0; transform: translateY(14px);} to {opacity: 1; transform: none;}}

h2, h3 {font-family: 'Bricolage Grotesque', sans-serif !important; color: #ECE8DD;}

[data-testid="stFileUploader"] section {
  border: 1.5px dashed #5b5a4c; border-radius: 6px; background: #12130F; transition: .2s;}
[data-testid="stFileUploader"] section:hover {border-color: #F2C14E; background: #171813;}

[data-testid="stImage"] img {border-radius: 6px; border: 1px solid #2A2B26;}

div.stButton > button {
  background: #F2C14E; color: #0E0F0C; font-weight: 600; border: 1.5px solid #0E0F0C;
  border-radius: 4px; padding: .55rem 1.6rem; box-shadow: 4px 4px 0 #8a6d1f;
  transition: transform .12s, box-shadow .12s;}
div.stButton > button:hover {color: #0E0F0C; transform: translate(-2px, -2px); box-shadow: 6px 6px 0 #8a6d1f;}
div.stButton > button:active {transform: translate(3px, 3px); box-shadow: 1px 1px 0 #8a6d1f;}

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
""", unsafe_allow_html=True)

# ---- language switch ----
st.radio("Language / भाषा", ["en", "hi"],
         format_func=lambda x: "English" if x == "en" else "हिन्दी",
         horizontal=True, key="lang")

st.markdown(f"""
<div class="top">
  <span class="tag">{t("tag")}</span>
  <h1>{t("title")}</h1>
  <p>{t("tagline")}</p>
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_history():
    return pd.read_csv("assets/price_history.csv")


# ---- price model must exist ----
try:
    opts = options()
except PriceModelMissing:
    st.error(t("model_missing")); st.stop()

# ---- input form ----
col1, col2 = st.columns(2)
with col1:
    st.caption(t("upload"))
    upload = st.file_uploader("photo", type=["jpg", "jpeg", "png"],
                              label_visibility="collapsed")
with col2:
    st.caption(t("weight"))
    weight = st.number_input("weight", min_value=0.0, value=1.0, step=0.5,
                             label_visibility="collapsed")
    st.caption(t("state"))
    state = st.selectbox("state", opts["states"],
                         index=opts["states"].index("Haryana") if "Haryana" in opts["states"] else 0,
                         format_func=state_label, label_visibility="collapsed")
    st.caption(t("month"))
    month = st.selectbox("month", range(1, 13), index=datetime.date.today().month - 1,
                         format_func=month_name, label_visibility="collapsed")
    grade = None

# ---- uploaded photo ----
if upload is not None:
    ok, _ = validate_image(upload)
    if not ok:
        st.error(t("bad_image")); st.stop()
    img = Image.open(upload)
    st.image(img, caption=t("uploaded"), use_container_width=True)

go = st.button(t("estimate"), type="primary", disabled=upload is None)

# result stays on screen when the language is switched
show = False
if upload is not None:
    key = f"{upload.name}-{upload.size}"
    if go:
        st.session_state["done_for"] = key
    show = st.session_state.get("done_for") == key

if show:
    ok, _ = validate_weight(weight)
    if not ok:
        st.error(t("bad_weight")); st.stop()

    try:
        with st.spinner(t("spinner")):
            r = predict_ripeness(img)
    except RipenessModelMissing:
        st.error(t("ripeness_missing")); st.stop()
    except Exception:
        st.error(t("ripeness_err")); st.stop()

    if not r["confident"]:
        st.warning(t("low_conf", c=f"{r['confidence']:.0%}", m=f"{CONF_THRESHOLD:.0%}"))
        st.stop()

    fruit_name = r["fruit"].title()
    if fruit_name not in opts["fruits"]:
        st.error(t("no_fruit_model", fruit=fruit_label(fruit_name),
                   supported=", ".join(fruit_label(f) for f in opts["fruits"])))
        st.stop()
    if r["ripeness"] not in RIPENESS_MULTIPLIER:
        st.error(t("bad_ripeness", label=r["ripeness"]))
        st.stop()

    try:
        p = predict_price(fruit_name, r["ripeness"], weight, state, month, grade)
    except Exception:
        st.error(t("price_err")); st.stop()

    st.subheader(t("result_title", fruit=fruit_label(fruit_name),
                   stage=stage_label(r["ripeness"]), conf=f"{r['confidence']:.0%}"))
    c1, c2 = st.columns(2)
    c1.metric(t("price_kg"), f"₹ {p['price_per_kg']}")
    c2.metric(t("total", w=f"{weight:g}"), f"₹ {p['total_price']}")

    with st.expander(t("how")):
        st.write(
            t("base", model=p["model"], base=p["base_price_per_kg"]) + "  \n"
            + t("mult", stage=stage_label(r["ripeness"]), m=p["ripeness_multiplier"]) + "  \n"
            + t("markup", m=p["retail_markup"]) + "  \n"
            + t("final", p=p["price_per_kg"]))
        st.caption(t("assump"))
    with st.expander(t("top3")):
        for n, c in r["top3"]:
            st.write(f"{label_name(n)}: {c:.1%}")

    # ---- price history ----
    st.subheader(t("hist_title"))
    hist = load_history()
    fk = fruit_name.lower()
    hh = hist[(hist["fruit"] == fk) & (hist["state"] == state)]
    if hh.empty:
        st.info(t("no_state_data", fruit=fruit_label(fruit_name), state=state_label(state)))
        hh = hist[(hist["fruit"] == fk) & (hist["state"] == "All India")]

    t1, t2 = st.tabs([t("tab_year"), t("tab_month")])
    with t1:
        yearly = hh.groupby("year")["price_kg"].mean().round(2)
        yearly.index.name = t("year_label")
        st.line_chart(yearly, color="#F2C14E")
    with t2:
        last3 = sorted(hh["year"].unique())[-3:]
        piv = hh[hh["year"].isin(last3)].pivot_table(index="month", columns="year", values="price_kg")
        piv.index.name = t("month_label")
        st.line_chart(piv)
        st.caption(t("month_caption"))
        recent = hh[hh["year"] >= hh["year"].max() - 4].groupby("month")["price_kg"].mean()
        st.write(t("best_worst",
                   hi_m=month_name(recent.idxmax()), hi_p=f"{recent.max():.0f}",
                   lo_m=month_name(recent.idxmin()), lo_p=f"{recent.min():.0f}"))

st.markdown(f'<div class="foot">{t("footer")}</div>', unsafe_allow_html=True)