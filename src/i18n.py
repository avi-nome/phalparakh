import streamlit as st

TEXT = {
    "en": {
        "tag": "SVSU · B.Tech CSE · AI Project",
        "title": "Phal<span>Parakh</span>",
        "tagline": "Upload a fruit photo. Find out how ripe it is and see an estimated price based on mandi rates.",
        "upload": "Fruit photo (JPG/PNG)",
        "weight": "Weight (kg)",
        "state": "State",
        "month": "Month",
        "uploaded": "Uploaded photo",
        "estimate": "Estimate price",
        "price_err": "The price could not be estimated.",
        "model_missing": "Price model not found. Run training/train_price_hist.py first.",
        "result_title": "{fruit} – {stage} (confidence: {conf})",
        "price_kg": "Price per kg",
        "total": "Total ({w} kg)",
        "how": "How was this price calculated?",
        "base": "Mandi base price ({model} model): ₹{base}/kg",
        "mult": "× ripeness multiplier ({stage}): {m}",
        "markup": "× retail markup: {m}",
        "final": "= ₹{p}/kg",
        "assump": "The multipliers and markup are assumptions (mandi data has no ripeness information).",
        "top3": "Top 3 predictions",
        "hist_title": "Price history (mandi, ₹/kg)",
        "no_state_data": "No {fruit} data found for {state}. Showing the All India average.",
        "tab_year": "Year by year",
        "tab_month": "Month by month",
        "year_label": "Year",
        "month_label": "Month",
        "month_caption": "1 = Jan, 12 = Dec",
        "best_worst": "Over the last 5 years, the highest-priced month was **{hi_m}** (₹{hi_p}/kg) and the lowest-priced month was **{lo_m}** (₹{lo_p}/kg).",
        "footer": "Data: Agmarknet (mandi prices) · The price is an estimate; ripeness multipliers are assumed",
    },
    "hi": {
        "tag": "एसवीएसयू · बी.टेक सीएसई · एआई प्रोजेक्ट",
        "title": "फल<span>परख</span>",
        "tagline": "फल की फ़ोटो अपलोड करें। जानें कि वह कितना पका है और मंडी भाव के आधार पर अनुमानित कीमत देखें।",
        "upload": "फल की फ़ोटो (JPG/PNG)",
        "weight": "वज़न (किग्रा)",
        "state": "राज्य",
        "month": "महीना",
        "uploaded": "अपलोड की गई फ़ोटो",
        "estimate": "कीमत का अनुमान लगाएँ",
        "price_err": "कीमत का अनुमान नहीं लगाया जा सका।",
        "model_missing": "कीमत का मॉडल नहीं मिला। पहले training/train_price_hist.py चलाएँ।",
        "result_title": "{fruit} – {stage} (विश्वास: {conf})",
        "price_kg": "प्रति किग्रा कीमत",
        "total": "कुल ({w} किग्रा)",
        "how": "यह कीमत कैसे बनी?",
        "base": "मंडी का आधार भाव ({model} मॉडल): ₹{base}/किग्रा",
        "mult": "× पकने का गुणक ({stage}): {m}",
        "markup": "× खुदरा मार्कअप: {m}",
        "final": "= ₹{p}/किग्रा",
        "assump": "गुणक और मार्कअप अनुमान पर आधारित हैं (मंडी के आँकड़ों में पकने की जानकारी नहीं होती)।",
        "top3": "शीर्ष 3 अनुमान",
        "hist_title": "पिछले वर्षों का भाव (मंडी, ₹/किग्रा)",
        "no_state_data": "{state} में {fruit} का आँकड़ा नहीं मिला। पूरे भारत का औसत दिखाया जा रहा है।",
        "tab_year": "साल दर साल",
        "tab_month": "महीने के अनुसार",
        "year_label": "वर्ष",
        "month_label": "महीना",
        "month_caption": "1 = जनवरी, 12 = दिसंबर",
        "best_worst": "पिछले 5 वर्षों में सबसे महँगा महीना **{hi_m}** (₹{hi_p}/किग्रा) और सबसे सस्ता महीना **{lo_m}** (₹{lo_p}/किग्रा) रहा।",
        "footer": "आँकड़े: एगमार्कनेट (मंडी भाव) · कीमत केवल अनुमान है; पकने के गुणक मान्यताओं पर आधारित हैं",
    },
}

FRUITS = {
    "apple": ("Apple", "सेब"), "banana": ("Banana", "केला"), "mango": ("Mango", "आम"),
    "orange": ("Orange", "संतरा"), "tomato": ("Tomato", "टमाटर"),
}
STAGES = {
    "unripe": ("Unripe", "कच्चा"), "ripe": ("Ripe", "पका"), "overripe": ("Overripe", "अधिक पका"),
}
MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "hi": ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"],
}
STATES_HI = {
    "Andaman and Nicobar": "अंडमान और निकोबार", "Andhra Pradesh": "आंध्र प्रदेश",
    "Arunachal Pradesh": "अरुणाचल प्रदेश", "Assam": "असम", "Bihar": "बिहार",
    "Chandigarh": "चंडीगढ़", "Chattisgarh": "छत्तीसगढ़", "Chhattisgarh": "छत्तीसगढ़",
    "Dadra and Nagar Haveli": "दादरा और नगर हवेली", "Daman and Diu": "दमन और दीव",
    "Goa": "गोवा", "Gujarat": "गुजरात", "Haryana": "हरियाणा", "Himachal Pradesh": "हिमाचल प्रदेश",
    "Jammu and Kashmir": "जम्मू और कश्मीर", "Jharkhand": "झारखंड", "Karnataka": "कर्नाटक",
    "Kerala": "केरल", "Ladakh": "लद्दाख", "Lakshadweep": "लक्षद्वीप", "Madhya Pradesh": "मध्य प्रदेश",
    "Maharashtra": "महाराष्ट्र", "Manipur": "मणिपुर", "Meghalaya": "मेघालय", "Mizoram": "मिज़ोरम",
    "NCT of Delhi": "दिल्ली", "Delhi": "दिल्ली", "Nagaland": "नागालैंड", "Odisha": "ओडिशा",
    "Pondicherry": "पुदुचेरी", "Puducherry": "पुदुचेरी", "Punjab": "पंजाब", "Rajasthan": "राजस्थान",
    "Sikkim": "सिक्किम", "Tamil Nadu": "तमिलनाडु", "Telangana": "तेलंगाना", "Tripura": "त्रिपुरा",
    "Uttar Pradesh": "उत्तर प्रदेश", "Uttarakhand": "उत्तराखंड", "Uttrakhand": "उत्तराखंड",
    "West Bengal": "पश्चिम बंगाल", "All India": "पूरे भारत",
}


def lang() -> str:
    return st.session_state.get("lang", "en")


def _i() -> int:
    return 0 if lang() == "en" else 1


def t(key: str, **kw) -> str:
    s = TEXT[lang()][key]
    return s.format(**kw) if kw else s


def fruit_label(name: str) -> str:
    k = str(name).lower()
    return FRUITS[k][_i()] if k in FRUITS else str(name)


def stage_label(stage: str) -> str:
    k = str(stage).lower()
    return STAGES[k][_i()] if k in STAGES else str(stage)


def label_name(cls: str) -> str:
    """'banana_unripe' -> 'Banana – Unripe' / 'केला – कच्चा'"""
    f, _, s = str(cls).partition("_")
    return f"{fruit_label(f)} – {stage_label(s)}"


def state_label(s: str) -> str:
    return STATES_HI.get(s, s) if lang() == "hi" else s


def month_name(m: int) -> str:
    return MONTHS[lang()][int(m) - 1] 

TEXT["en"].update({
    "bad_image": "Please upload a valid JPG or PNG photo.",
    "bad_weight": "Weight must be greater than 0.",
    "ripeness_missing": "Ripeness model (models/best.pt) not found. Run training/train_ripeness.py first.",
    "ripeness_err": "The photo could not be analysed. Please try another photo.",
    "low_conf": "The model is only {c} confident (minimum {m}). Please upload a clear, close-up photo of a single fruit in good light.",
    "spinner": "Checking ripeness...",
    "no_fruit_model": "No price model is available for '{fruit}'. Supported: {supported}",
    "bad_ripeness": "Unknown ripeness label '{label}'. Please check the training folder names.",
})
TEXT["hi"].update({
    "bad_image": "कृपया मान्य JPG या PNG फ़ोटो अपलोड करें।",
    "bad_weight": "वज़न 0 से अधिक होना चाहिए।",
    "ripeness_missing": "पकने का मॉडल (models/best.pt) नहीं मिला। पहले training/train_ripeness.py चलाएँ।",
    "ripeness_err": "फ़ोटो का विश्लेषण नहीं हो सका। कृपया दूसरी फ़ोटो आज़माएँ।",
    "low_conf": "मॉडल केवल {c} आश्वस्त है (न्यूनतम {m})। कृपया अच्छी रोशनी में एक ही फल की साफ़, नज़दीक से ली गई फ़ोटो अपलोड करें।",
    "spinner": "पकने की जाँच हो रही है...",
    "no_fruit_model": "'{fruit}' के लिए कीमत का मॉडल उपलब्ध नहीं है। उपलब्ध: {supported}",
    "bad_ripeness": "पकने का अज्ञात लेबल '{label}'। कृपया प्रशिक्षण फ़ोल्डरों के नाम जाँचें।",
})