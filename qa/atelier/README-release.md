LUNA STAGE is a high-end spatial sales instrument for EDV Hausleitner GmbH, Linz.
The customer stands in the finished kitchen. Daylight moves. Oak becomes lacquer.
Price and delivery week sit on the worktop like engraved type.
No menus competing with the room. If a control does not belong in the kitchen, delete it.

# LUNA STAGE 2 · Atelier

## Enter the room / Betreten Sie den Raum

**EN.** Open the Pages project root or `Luna-Stage.html`. Press **F** for fullscreen, **1–6** to choose a chapter, **Space** to play/pause, and **Escape** for the quiet wide shot. A fresh, motion-enabled visit plays the six-chapter 48-second film. Drag to orbit; scroll to move closer. **E** opens the optional live-design editor.

**DE.** Öffnen Sie die GitHub-Pages-Startseite oder `Luna-Stage.html`. Mit **F** wechseln Sie ins Vollbild, mit **1–6** wählen Sie ein Kapitel, mit der **Leertaste** starten oder pausieren Sie den Film. **Escape** führt zur ruhigen Gesamtansicht. Ein frischer Besuch startet den 48-Sekunden-Film, sofern reduzierte Bewegung nicht aktiviert ist. Ziehen Sie zum Umsehen, verwenden Sie das Mausrad zum Annähern und drücken Sie **E** für die Raumgestaltung.

## Live design / Live gestalten

Press **E**, or choose **Raum gestalten**, to open **LUNA Atelier**. The editor is opt-in: the default product remains the kitchen, not an editor dashboard. Press E again to return to the room.

| Bereich | Funktion |
|---|---|
| Atmosphäre | Fünf Themen: Atelier, Nord, Olive, Nocturne, Terra. Ein Themenwechsel behält die Möbelpositionen und setzt Materialüberschreibungen zurück. |
| Objekt | 22 Ausgangselemente direkt im Raum oder aus der Liste wählen. Auf einer horizontalen Ebene verschieben, optional am 50-mm-Raster. Position und Abmessungen in mm; Drehung; duplizieren, entfernen, rückgängig und wiederholen. |
| Oberfläche | 16 Materialplätze einschließlich einer eigenen Textur. Oberfläche je Elementbereich, Farbton, Glanz und Texturmaßstab. |
| Eigene Textur | Lokale PNG/JPG/WebP-Datei bis 8 MB, auf 512 × 512 verkleinert und im Projekt eingebettet. Ein eigener Bildplatz je Projekt: Eine neue Datei ersetzt ihn überall, wo er verwendet wird. |
| Licht | Sonnenstand, angenäherte Leuchtenfarbe von 2.200–5.000 K, Intensität, Belichtung und Arbeitslicht. Die verschobene Pendelleuchte nimmt ihre Lichtquelle mit. |
| Projekt | Validierter JSON-Export und -Import, lokale Sicherung, 40 Rückgängig-Schritte. Die interne Marge wird nie aus einem Projekt oder Speicherstand wiederhergestellt. |
| Standbild | **S** speichert die aktuelle Ansicht als 1920 × 1080 PNG. Der Entwurf bleibt unverändert. |

**In der Raumgestaltung:** Ziehen Sie mit der linken Maustaste das gewählte Möbel. Die rechte Maustaste dreht die Ansicht; **Umschalt + Ziehen** verschiebt die Kamera. **R** dreht das Element um 15°. Pfeiltasten verschieben es um 50 mm, mit **Alt** um 10 mm. **Strg/⌘ Z** macht rückgängig; **Strg/⌘ Umschalt Z** stellt wieder her. Zweifingerbewegungen dienen auf Touch-Geräten dem Verschieben und Zoomen.

**EN.** Select, drag, position, resize, rotate, duplicate and delete furniture. Change finishes independently; import a local image for the custom material slot. Export the project as an independent backup. The room shell is fixed, but its finishes are editable. Named custom-theme creation is not implemented: arbitrary individual finishes and the complete project can be saved instead.

**Presenter controls:** **M** switches the global oak/sand demonstration; **P** toggles the island-worktop price. Hidden **C** toggles the fixed **31 %** internal margin, off on every load. In presentation mode, touching a front changes that element's finish. Touching a worktop toggles the inscription on the island.

## What changed from 1.0

The original 2.0 scene adds a fluted island with waterfall-stone ends, integrated tall units, a recessed sink and curved brass tap, an induction hob, a suspended linear light, upholstered stools, shelves, ceramics and an olive tree. No third-party application is embedded.

The live room is rendered by **native WebGPU rasterization**, with GPU affine transforms, reusable rounded geometry, mipmapped colour/height maps, approximate GGX material shading, sun and pendant depth-shadow maps, HDR accumulation and tone mapping. The scene resets accumulated frames on camera, geometry, material or light changes. During movement the pixel resolution is reduced; the still image converges progressively.

This is **not** an unbiased path tracer or a physical lighting calculation. Environment reflections are approximations, not traced mirrors of all furnishings. Scaling changes geometry; it does not regenerate joinery, fittings or a cutting list. There is no furniture-to-furniture collision solver and no manufacturing CAD claim. Decorative elements remain individually editable; not all loose props are parented to furniture.

## Demo, not a quotation / Demo, kein Angebot

Familie Berger, the **3,600 mm** run, **18.740 € inkl. 20 % USt**, **Montage KW38**, and **31 %** margin are fixed supplied demo values. Editing furniture or finishes does **not** calculate a new price, confirm delivery or write an invoice.

Auch nach einer Änderung sind die eingeblendeten Werte **kein Angebot, keine Kalkulation und kein bestätigter Liefertermin**. STAGE ist keine lizenzierte WAWI. Die WAWI bleibt für die Rechnung zuständig.

## One runtime file, local data

No React, npm runtime, CDN, external font, iframe, account, API or remote service. HTML, CSS, JavaScript, WGSL, material maps and six fallback stills are embedded in **`Luna-Stage.html`**. The browser does not fetch textures or send the project anywhere. The same bytes are published as `index.html` on the Pages branch; there is no wrapper or second application.

Namespaces remain `Luna.theme`, `Luna.gpu`, `Luna.cam`, `Luna.scene`, `Luna.hud` and `Luna.store`. The versioned local-storage key remains **`luna.stage.v1`**. The validated project format is `luna.stage.project` version 2. Export an independent backup; browser storage can be denied or cleared.

WebGPU needs an available adapter in a secure context. Pages uses HTTPS. For local use:

```sh
python3 -m http.server 8476 --bind 127.0.0.1
# http://127.0.0.1:8476/Luna-Stage.html
```

Without WebGPU, the application explicitly shows **still frames of the default kitchen with a filmstrip**, not a fake live editor or an empty canvas. An edited project remains stored, but the still fallback does not render arbitrary edited furniture. `?backend=canvas2d` tests that mode; `?chapter=3&paused=1&fresh=1` selects a reproducible fresh evening view. Reduced motion disables autoplay.

## Texture provenance

Two sources were downloaded from ambientCG, resized, colour-normalized and embedded. Source archive and derived-map SHA-256 values are recorded in `qa/atelier/assets.json`.

| Source | Licence | Use |
|---|---|---|
| [ambientCG Wood094](https://ambientcg.com/view?id=Wood094) | CC0 1.0 | Oak colour/height detail |
| [ambientCG Travertine003](https://ambientcg.com/view?id=Travertine003) | CC0 1.0 | Stone colour/height detail |

[ambientCG licence](https://docs.ambientcg.com/license/). Other finishes use original procedural maps or plain colours. No downloaded font files or upstream application assets are included.

## Verification

`qa/atelier/` contains development-only build/test sources, actual browser screenshots and JSON receipts; these are not runtime dependencies. The graphics preflight requires a completed native canvas render and pixel readback, not merely the presence of an adapter.

`VISION.md` and release receipts identify the reviewed frames, actual tested platform, runtime hash and remaining boundaries. **Software-adapter testing is not proof of physical-GPU performance.** Old 1.0 QA files do not validate 2.0. Visual review and executed functional checks are reported separately.

MIT licensed. Company and product identification do not grant rights to third-party marks.
