LUNA STAGE is a high-end spatial sales instrument for EDV Hausleitner GmbH, Linz.
The customer stands in the finished kitchen. Daylight moves. Oak becomes lacquer.
Price and delivery week sit on the worktop like engraved type.
No menus competing with the room. If a control does not belong in the kitchen, delete it.

## Enter the room / Betreten Sie den Raum

**DE.** Öffnen Sie `Luna-Stage.html` oder die [Webpräsentation](https://martin-hausleitner.github.io/Luna-Stage/). Mit **F** wechseln Sie in die Vollbildpräsentation. Der sechs Kapitel lange Film startet bei einem frischen Besuch automatisch und dauert 48 Sekunden. Mit **1–6** oder der schmalen Kapitelleiste wählen Sie eine Szene; die **Leertaste** pausiert bzw. setzt fort. **Escape** führt zur ruhigen Gesamtansicht. Ziehen Sie zum Umsehen, verwenden Sie das Mausrad zum Zoomen. Berühren Sie eine Front zum Materialwechsel und die Arbeitsplatte zum Ein- oder Ausblenden der Preisgravur. Die feine Linie am Fenster steuert das Tageslicht. Reduzierte Bewegung wird respektiert.

**EN.** Open the single HTML file or the hosted presentation. **F** enters fullscreen. A fresh visit plays the 48-second, six-chapter film. **1–6** selects a chapter, **Space** pauses/resumes, and **Escape** skips to the quiet wide shot. Drag to orbit and use the wheel to zoom. Touch cabinet fronts to cycle materials, the worktop to toggle its inscription, or the thin window highlight to change daylight. Reduced-motion preferences disable automatic movement.

| Control / Bedienung | Action / Wirkung |
|---|---|
| F | Fullscreen / Vollbild |
| 1–6, Space, Escape | Chapters, pause and skip / Kapitel, Pause, Überspringen |
| M / cabinet front | Six material variants / Sechs Materialvarianten |
| L / light diffuser | Switch pendant and LED lighting / Pendel- und LED-Leuchten schalten |
| P / worktop | Engraved demo price / Demo-Preisgravur |
| V / Filmsammlung | 50 additional in-engine camera sequences / 50 zusätzliche Echtzeit-Kamerasequenzen |
| S | 1920 × 1080 PNG, `STAGE-Berger-Abend.png` |
| C, presenter only | 31 % ghost-margin inscription; off on each load, never persisted |

The original chapters are **Ankunft, Holz, Abend, Oberfläche, Zahl, Stille**. The additional 50 sequences are actual camera/light/material timelines of this same 3D room, not downloaded videos or 50 MP4 files. Their selector is hidden until requested; the kitchen remains the presentation surface.

## Detailed HTML edition · 3.2

This updates the existing STAGE application. It does not replace the room with an AI-generated picture and does not embed a screenshot of a browser or operating system.

The scene contains **2,301 analytic primitives**, including an olive tree with **1,560 individually oriented three-dimensional leaves**, branching timber, a hollow stone planter, soil and pebbles. A smaller herb adds 44 leaves. The kitchen has beveled stone, a real sink opening, a curved faucet, bronze pendants and diffusers, continuous LED profiles, linen-upholstered wooden stools with piping and foot rails, boards, ceramics, bottles, citrus, oven shelves and restrained wall art. Distant buildings and their window patterns are rendered in 3D with parallax.

Photographic oak color and normal textures are embedded in the file. Stone veining, textiles, bark, ceramics, leaf surfaces and city windows are procedural. Cabinet variants include natural oak, sand lacquer, walnut, graphite, sage lacquer and smoked oak. Lighting and material changes alter the rendered geometry and pixels, rather than switching a background photograph.

## Architecture and offline use

One runtime file. No npm, framework, CDN, external font, iframe, account, login, cloud API or runtime asset fetch. `Luna.theme`, `Luna.gpu`, `Luna.cam`, `Luna.scene`, `Luna.hud` and `Luna.store` remain the small shared namespaces. Validated local preferences use **`luna.stage.v1`**. The CEO margin is intentionally not retained.

For a secure local browser context:

```sh
python3 -m http.server 8476 --bind 127.0.0.1
# http://127.0.0.1:8476/Luna-Stage.html
```

WebGPU needs a secure context and an available adapter. Direct `file:` opening depends on browser policy. When no adapter is available, the application explicitly uses a **Canvas2D still-frame filmstrip of its own native room renders**. The six small images are embedded; they are not AI-generated substitutes. Free orbit and continuously variable lighting require WebGPU. Fallback material selection uses the corresponding captured chapter.

Software WebGPU adapters require a separate distinction: the same WGSL renderer still computes the room, but STAGE reads back its real pixel buffer into a visible canvas when direct WebGPU canvas compositing is incomplete. This path is reported as **WebGPU pixels / software-adapter readback**, not as a physical GPU. Hardware adapters retain native canvas presentation. Software-adapter preview resolution is reduced while navigating; explicit PNG export remains 1920 × 1080.

## Rendering boundaries

Native WGSL traces analytic geometry through a surface-area-heuristic bounding-volume hierarchy. The renderer implements direct sun and area lighting, visibility rays, material-dependent reflections, approximate ambient contact shading, progressive sampling and restrained bloom. GPU queue backpressure avoids submitting an unbounded backlog. Snapshot pixels are copied from an actual rendered GPU texture before encoding; an empty discarded canvas is not treated as a successful export.

This is an architectural presentation, **not an unbiased path tracer, manufacturing CAD, certified lighting simulation or a pixel-identical recreation of a photographic concept**. Refraction, complex indirect light transport and physical furniture construction are approximate or absent. Software-adapter verification does not establish physical-GPU frame rates. The city is illustrative, not a surveyed view of Linz. No physical 65-inch display test is claimed.

**Demo, not a quote / Demo, kein Angebot:** Familie Berger, the 3,600 mm run, **18.740 € inkl. 20 % USt**, **Montage KW38** and **31 %** margin are fixed demo inputs. They are not live prices, an accounting calculation, a confirmed order or a delivery commitment. STAGE sells the kitchen; WAWI still writes the invoice.

## Sources and license

Original STAGE code: MIT, see `LICENSE`. The build embeds **Poly Haven** CC0 `oak_veneer_01` diffuse/normal maps and a low-weight tone-mapped `venice_sunset` environment. `qa/stage-v2/asset-receipt.json` records source URLs, image sizes and hashes. Runtime does not access Poly Haven. Company and third-party marks are not licensed by the code license.

Aster, AureonStudio, StrataForge, Formalyth and Veldra3D were inspected as implementation references in the original edition. No upstream desktop, wordmark, iframe or proprietary renderer is embedded.

## Reproducibility and evidence

The development-only scripts under `qa/stage-v2` and `qa/stage-v3` build from the pinned original STAGE source, assemble real materials and apply the 3D improvements. Python, Pillow and Playwright are development tools, not application dependencies. The generated HTML runs without these tools.

Native browser reports record the exact source hash, browser, actual adapter, visible room screenshots, PNG export, lighting/material controls, orbit/zoom, fullscreen, all 50 rendered clip definitions and film timing. Visual judgement is recorded separately from shader execution. The six fallback stills are rebaked from those native renders. `qa/v3/assembly.json` records the tested runtime hash and the final single-file hash after that data-only replacement.

Canonical file: `Luna-Stage.html` on `main`. Pages serves the same bytes as `index.html` on `gh-pages`, without an iframe, wrapper or redirect. The publication script stops rather than overwriting a concurrently changed runtime.
