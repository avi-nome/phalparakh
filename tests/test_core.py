import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pytest
from PIL import Image
from src.price import predict_price, options
from src.validate import validate_image, validate_weight
from src.ripeness import split_label


class F(io.BytesIO):                       # mimics Streamlit UploadedFile
    def __init__(self, data, name):
        super().__init__(data); self.name = name; self.size = len(data)


def img_bytes(size=(200, 200), fmt="JPEG"):
    b = io.BytesIO(); Image.new("RGB", size, "yellow").save(b, fmt); return b.getvalue()


def test_price_ordering():
    kw = dict(fruit="Mango", weight_kg=2, state="Haryana", month=6)
    un, ri, ov = (predict_price(ripeness=r, **kw) for r in ("unripe", "ripe", "overripe"))
    assert ov["total_price"] < un["total_price"] < ri["total_price"]
    assert abs(ri["total_price"] - ri["price_per_kg"] * 2) < 0.02


def test_price_bad_inputs():
    with pytest.raises(ValueError): predict_price("Durian", "ripe", 1, "Haryana", 5)
    with pytest.raises(ValueError): predict_price("Mango", "rotten", 1, "Haryana", 5)


def test_validate_image():
    assert validate_image(F(img_bytes(), "a.jpg"))[0]
    assert not validate_image(F(img_bytes(), "a.gif"))[0]
    assert not validate_image(F(b"not an image", "a.jpg"))[0]
    assert not validate_image(F(img_bytes((20, 20)), "a.png"))[0]


def test_validate_weight():
    assert validate_weight(1.5)[0]
    assert not validate_weight(0)[0] and not validate_weight("abc")[0] and not validate_weight(-3)[0]


def test_split_label():
    assert split_label("banana_overripe") == ("banana", "overripe")
