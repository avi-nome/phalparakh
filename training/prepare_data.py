"""Turn a downloaded ripeness dataset into the folder layout YOLOv8 classification needs:

    data/train/<fruit>_<ripeness>/*.jpg
    data/val/<fruit>_<ripeness>/*.jpg

Run once per fruit / dataset (results are added into the same data/ folder).

MODE 1: dataset already has one folder per class  (src/Green/*.jpg, src/Ripe/*.jpg ...)
  python training/prepare_data.py --src BananaStages --fruit banana \
         --map "green=unripe,semi-ripe=skip,ripe=ripe,overripe=overripe"

MODE 2: dataset is in YOLO-label format (images + .txt files). Each image gets the
        most frequent class in its label file.
  python training/prepare_data.py --src MangoYolo --fruit mango --yolo \
         --names "unripe,ripe,overripe"
"""
import argparse, random, re, shutil
from collections import Counter
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png"}


def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--fruit", required=True)
    ap.add_argument("--out", default="data")
    ap.add_argument("--map", default="unripe=unripe,ripe=ripe,overripe=overripe")
    ap.add_argument("--yolo", action="store_true")
    ap.add_argument("--names", default="unripe,ripe,overripe", help="YOLO class names in id order")
    ap.add_argument("--only", default="",
                    help="keep only images whose path has a folder/file-name part containing this text "
                         "(use when one dataset holds many fruits, e.g. --only apple)")
    ap.add_argument("--val", type=float, default=0.2)
    ap.add_argument("--max-per-class", type=int, default=600)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    random.seed(a.seed)
    src, fruit = Path(a.src), a.fruit.lower()
    cmap = {norm(k): v.strip() for k, v in (p.split("=") for p in a.map.split(","))}

    items = {}  # ripeness -> [image paths]
    images = [p for p in src.rglob("*") if p.suffix.lower() in IMG_EXT]
    if a.only:
        key = norm(a.only)
        images = [p for p in images
                  if any(key in norm(part) for part in p.relative_to(src).parts)]
        print(f"--only {a.only}: {len(images)} images kept")

    if a.yolo:
        names = [n.strip() for n in a.names.split(",")]
        labels = {p.stem: p for p in src.rglob("*.txt")}
        for img in images:
            lab = labels.get(img.stem)
            if not lab:
                continue
            ids = [int(l.split()[0]) for l in lab.read_text().splitlines() if l.strip()]
            if not ids:
                continue
            name = names[Counter(ids).most_common(1)[0][0]]
            ripeness = cmap.get(norm(name), None)
            if ripeness and ripeness != "skip":
                items.setdefault(ripeness, []).append(img)
    else:
        for img in images:
            ripeness = cmap.get(norm(img.parent.name), None)
            if ripeness and ripeness != "skip":
                items.setdefault(ripeness, []).append(img)

    if not items:
        raise SystemExit("No images matched. Check --src, --map / --names.")

    for ripeness, files in items.items():
        random.shuffle(files)
        files = files[: a.max_per_class]
        n_val = max(1, int(len(files) * a.val))
        for split, chunk in (("val", files[:n_val]), ("train", files[n_val:])):
            dest = Path(a.out) / split / f"{fruit}_{ripeness}"
            dest.mkdir(parents=True, exist_ok=True)
            for f in chunk:
                uniq = "_".join(f.relative_to(src).parts)      # unique even if names repeat (1.jpg in Train & Test)
                shutil.copy2(f, dest / uniq)
        print(f"{fruit}_{ripeness}: {len(files)} images ({len(files) - n_val} train / {n_val} val)")


if __name__ == "__main__":
    main()
