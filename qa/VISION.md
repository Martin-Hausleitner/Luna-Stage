# LUNA STAGE — visual acceptance

**Local PASS / GitHub Pages PASS.** Reviewed at **1920 × 1080**, 14 September 2026.

This release reuses the existing, working single-file room rather than replacing it with another application. The runtime is byte-for-byte unchanged during this verification:

`Luna-Stage.html` / Pages `index.html`, SHA-256:
`17e052f77651eace4c663a23bd2aa39fecd9e6249df100d318e0142a0b0ca5f8`

## What was actually checked

A fresh repository checkout was served on localhost on the connected Mac. Python Playwright drove real Chrome **152.0.7977.83**, with native WebGPU on the reported **Apple / metal-3** adapter. All seven required views were re-rendered and captured after 28 accumulated samples. The complete film and interactive controls were exercised, then a new browser context opened the public Pages root and captured the requested live views 03 and 05. These are browser screenshots, not mockups.

The screenshots were visually reviewed as a seven-frame contact sheet, with full-size inspection of morning grain, evening, worktop price, and CEO margin. The fresh local screenshots have exactly the same SHA-256 values as the downloaded images that were inspected. Both fresh live captures are also byte-identical to those inspected local images; equality is verified by SHA-256 below and in the machine-readable reports. Thus the live visual assessment uses the exact captured live pixels, not an assumption that an HTTP 200 is a visual PASS.

| Required visual gate | Result | Evidence |
|---|---|---|
| First glance is a kitchen film, not a website | PASS | 01, 03, 06; room fills the viewport, no dashboard |
| No dense toolbar eating the room | PASS | Thin bottom chapter rail only; no application chrome |
| Morning and evening are obviously different | PASS | 02 bright window daylight vs 03 navy exterior and warm task lighting |
| Oak grain is readable | PASS | 02; vertical grain visible across the island and cabinet fronts |
| Price lives in the scene | PASS | 05; price follows the worktop plane and camera perspective |
| Typography feels engraved, not a badge | PASS | 05 and 07; dark lettering on stone, no card or badge container |
| EDV Hausleitner / LUNA STAGE appears once, quietly | PASS | Single lower-right product identification |
| Composition suitable for a 65-inch showroom wall | PASS (visual judgement) | Room-dominant 16:9 composition; full-size price and restrained rail |
| No Aster branding, lorem or empty black canvas | PASS | All seven views plus explicit Canvas2D fallback |

The 65-inch row is a composition/readability judgement from 1920 × 1080 images, not a claim that a physical 65-inch panel was connected or measured. Material lighting and shadows are a sales visualization, not certified photometry or CAD/manufacturing output.

## Required frames

| Capture | Result |
|---|---|
| `01-arrival.png` | PASS — entrance view |
| `02-grain-morning.png` | PASS — oak close-up and morning daylight |
| `03-evening.png` | PASS — dusk and warm under-cabinet lighting |
| `04-lacquer.png` | PASS — sand-lacquer fronts |
| `05-price-on-worktop.png` | PASS — 18.740 €, 20 % USt, Montage KW38 on stone |
| `06-wide-still.png` | PASS — quiet wide shot; chapter rail and footer hidden |
| `07-ceo-margin.png` | PASS — 31 % second inscription, hidden by default |
| `live-03-evening.png` | PASS — live Pages capture, same pixels as local 03 |
| `live-05-price-on-worktop.png` | PASS — live Pages capture, same pixels as local 05 |

Live/local 03 SHA-256: `f1f2c9155480629e93ae1bf36952df202688de6cb6292e1fa7fb1768659816a4`.

Live/local 05 SHA-256: `911ff92b0f1983f11d2598573ec77af80fe789b9a612fc12b4065da27c0024be`.

## Executed acceptance checks

`local-report.json`: native WebGPU, 1920 × 1080 screenshots, material and price keys, real door/worktop picking, window light slider, free orbit, fullscreen including after slider focus, chapter skip, exact-size PNG download, local persistence, CEO default-off, six 600 mm modules, and the still-frame filmstrip fallback all passed. No page errors, console errors, GPU errors or external application resource requests were recorded.

`behaviour-report.json`: the fresh-visit film ran **48.1162 seconds**, visited all six chapters, switched oak → lacquer → oak, displayed the price in chapter five, and finished in Stille. Reduced-motion, unavailable-GPU, denied-storage and restored-preference cases passed. CEO margin remained off for the entire film and was not restored from storage. The PNG contains actual room pixels at exactly 1920 × 1080.

`live-report.json`: HTTP 200, served HTML SHA-256 equals the local runtime, real Apple WebGPU, both requested live screenshots, and no recorded runtime errors or external application resource requests.

Measured first image: **75.4 ms local**, **616.7 ms live**. Measured first GPU submission completion: **235.3 ms local**, **727.9 ms live**. These are observed run measurements, not a guarantee for every network or device.

**Visual fix loops in this verification: 0 / 3.** No room changes were necessary. The missing visual acceptance document and fresh live evidence are now included.
