# 🖼️ E-Commerce Image Fixer

Turn raw phone product photos into clean, studio-white marketplace-ready
images — automatically.

**Live demo:** _add your Streamlit Cloud link here after deploying_
**Stack:** Python · Computer Vision (U^2-Net via `rembg`) · Pillow · Streamlit

---

## The problem this solves

Small sellers shoot product photos on a phone against a cluttered
background (a bed, a desk, a floor) — but Amazon/Shopify/Instagram all
reward (or require) clean, consistent product shots. A studio photographer
is expensive and slow. This tool gets most of the way there in seconds.

## How it works

```
 ┌───────────────┐    ┌──────────────────┐    ┌───────────────┐    ┌────────────────┐
 │ Raw phone photo│ →  │ Background removal│ →  │ Sharpen +     │ →  │ Centered on     │
 │ (cluttered bg)│    │ (U^2-Net segmentation)│  │ enhance colors│    │ white canvas    │
 └───────────────┘    └──────────────────┘    └───────────────┘    └────────────────┘
```

1. **Background removal** — `rembg` runs a U^2-Net deep segmentation model
   to separate the product from its background, producing a transparent
   (RGBA) cutout. No manual masking or green screen needed.
2. **Sharpen + enhance** — An unsharp-mask filter plus a small contrast/
   color boost makes the product look crisper, closer to a lit studio shot
   than a flat phone photo.
3. **Crop + center** — The cutout is cropped tight to its actual content
   (ignoring transparent padding), scaled to fit the target canvas with
   consistent padding, and pasted centered onto a pure white square.
4. **Output** — One studio-finished JPEG per input photo.

## Run it locally

```bash
git clone https://github.com/<your-username>/ecommerce-image-fixer.git
cd ecommerce-image-fixer
pip install -r requirements.txt

streamlit run app.py
```

The first run downloads the segmentation model (~170MB), which `rembg`
caches locally — later runs are fast.

Or run the batch/CLI version with no browser needed:

```bash
python cli.py --input ./raw_photos --output ./studio_photos --canvas 1600 --padding 0.10
```

## Deploy it (free, Streamlit Community Cloud)

1. Push this repo to your own GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → point
   it at this repo, main file `app.py`.
3. Deploy. No API keys needed — everything runs locally on the model.

> Note: `rembg`'s model download can make the *first* load on a fresh
> Streamlit Cloud instance slow (30-60s). Subsequent loads are fast once
> cached.

## Project structure

```
ecommerce-image-fixer/
├── app.py            # Streamlit UI (upload, preview before/after, ZIP download)
├── cli.py            # terminal/batch entry point
├── image_fixer.py     # core CV pipeline (shared by app.py & cli.py)
└── requirements.txt
```

## Adjustable parameters

| Parameter | What it controls | Default |
|---|---|---|
| `canvas_size` | Output image size in pixels (square) | 1600 |
| `padding_ratio` | Empty margin around the product, as a fraction of canvas | 0.10 |

## Roadmap / ideas for extending

- Batch export at multiple sizes at once (thumbnail + full-size)
- Optional colored/branded background instead of white
- Auto-detect and fix over/under-exposed source photos before enhancing
- Shadow generation under the product for a more "photographed" look

---

Built as a freelance portfolio project. Feedback and issues welcome.
