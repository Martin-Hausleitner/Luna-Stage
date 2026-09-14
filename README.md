LUNA STAGE is a high-end spatial sales instrument for EDV Hausleitner GmbH, Linz.
The customer stands in the finished kitchen. Daylight moves. Oak becomes lacquer.
Price and delivery week sit on the worktop like engraved type.
No menus competing with the room. If a control does not belong in the kitchen, delete it.

## Enter the room / Betreten Sie den Raum

**EN.** Open `Luna-Stage.html`. Press **F** for fullscreen. The six-chapter film plays automatically for **48 seconds** on a fresh, motion-enabled visit. Click a chapter, or press **1–6**, to go directly to it. **Space** pauses or resumes; **Escape** skips to the quiet wide shot. Drag to orbit, scroll to move closer. Touch a cabinet front to switch between natural oak and sand lacquer. Touch the worktop to show or hide the price. The thin highlight on the window sill changes the daylight.

**DE.** Öffnen Sie `Luna-Stage.html`. Mit **F** wechseln Sie in die Vollbildpräsentation. Der **48 Sekunden** lange Film startet bei einem frischen Besuch automatisch, sofern Sie reduzierte Bewegung nicht aktiviert haben. Wählen Sie ein Kapitel oder drücken Sie **1–6**. Mit der **Leertaste** pausieren Sie den Film oder setzen ihn fort; mit **Escape** überspringen Sie ihn zur ruhigen Gesamtansicht. Ziehen Sie zum Umsehen; mit dem Mausrad kommen Sie näher. Berühren Sie eine Front für Eiche natur oder Sandlack, die Arbeitsplatte für die Preiseinblendung und die schmale Linie am Fenster für das Tageslicht.

| Chapter / Kapitel | Experience / Erlebnis |
|---|---|
| 01 · Ankunft | Entrance dolly / Kamerafahrt aus dem Vorraum |
| 02 · Holz | Oak grain in morning daylight / Eiche im Morgenlicht |
| 03 · Abend | Evening city light and warm pendants / Abendlicht und warme Leuchten |
| 04 · Oberfläche | Oak → sand lacquer → oak / Eiche → Sandlack → Eiche |
| 05 · Zahl | Engraved worktop price / Preis in der Arbeitsplatte |
| 06 · Stille | Wide shot; only the quiet brand remains / Gesamtansicht ohne Bedienflächen |

**Snapshot / Standbild:** **S** exports a real 1920 × 1080 PNG, `STAGE-Berger-Abend.png`, marked **STAGE / Berger / Abend**, then restores the presentation state. No cloud upload is involved. **M** and **P** are keyboard alternatives for material and price. Presenter-only **C** toggles the **31 %** ghost-margin inscription; it is off on every load and never persisted.

**Demo, not a quote / Demo, kein Angebot:** Familie Berger, the 3,600 mm run, **18.740 € inkl. 20 % USt**, **Montage KW38**, and **31 %** margin are the fixed scenario supplied for this demonstration. They are not live pricing, an accounting calculation, a confirmed order, or a delivery commitment. STAGE does not write invoices and is not licensed WAWI.

## One file, no runtime dependencies

No npm, package installation, framework, CDN, external fonts, fetched imagery, iframe, account, API, or application server. Six WebP stills rendered by this very application are embedded inside the HTML for the first image and the offline filmstrip. They are not fetched assets. The inline JavaScript and WGSL implement the room, geometry, lighting, procedural oak, stone, materials, picking, camera and export. The browser does not send customer data anywhere. Saved presentation preferences use the origin-local key **`luna.stage.v1`**; inaccessible or invalid local storage is handled safely.

For a local secure browser context, serve the directory using Python's standard library:

```sh
python3 -m http.server 8476 --bind 127.0.0.1
# Open http://127.0.0.1:8476/Luna-Stage.html
```

WebGPU needs a browser exposing an available adapter in a secure context (HTTPS or localhost). Direct file opening may use WebGPU or the fallback according to browser policy. The **Canvas2D fallback is an explicitly labelled still-frame filmstrip made from the actual room renders**, never an empty canvas and never reported as GPU rendering. Query `?backend=canvas2d` exercises it. `?chapter=3&paused=1` selects a deterministic chapter for QA. Reduced-motion preference disables autoplay.

### Small shared architecture

| Namespace | Responsibility |
|---|---|
| `Luna.theme` | Navy, warm materials, quiet typography, #0078C8 hairline |
| `Luna.gpu` | Native WebGPU room, cabinet geometry, sun, material shading; still fallback and PNG export |
| `Luna.cam` | Six cinematic chapters, 48-second film, free orbit, projection and rays |
| `Luna.scene` | One kitchen, six 600 mm modules, materials, exact ray-hit interactions |
| `Luna.hud` | World-coordinate worktop lettering and window highlight; thin chapter rail |
| `Luna.store` | Versioned, validated, local `luna.stage.v1` preferences; no CEO persistence |

### Rendering boundaries

The room is real 3D, rendered by original WGSL using analytic boxes, cylinders and ellipsoids, jittered area-light shadow rays, 28-sample linear-light accumulation, procedural materials, approximate ambient occlusion and single-bounce reflections. This is not an unbiased path tracer or a manufacturing CAD model. Furniture is illustrative, not a cutting list. Display lighting is approximate, not certified Kelvin photometry. Material selection in still mode jumps between the oak and lacquer chapters; free orbit and continuously variable light are WebGPU features. Pixel density adapts while the camera moves and settles at up to 1920 × 1080; PNG export is exactly 1920 × 1080.

## Sources studied, not embedded

The following public project READMEs were inspected for spatial and implementation principles. No upstream source code, wordmarks, assets or runtime components are copied or embedded.

| Source | Applied principle | Inspected README blob |
|---|---|---|
| [Aster](https://github.com/wieslawsoltes/Aster) | Local-first, explicit capabilities; omit desktop chrome entirely | `fba3f53ac01b72994bae331c4b3ef81b0fa31635` |
| [Aureon Studio](https://github.com/wieslawsoltes/AureonStudio) | Plain HTML/JS/WGSL; verify actual shader execution | `184804f83d3066a45073cc94b6039630e82c485e` |
| [StrataForge](https://github.com/wieslawsoltes/StrataForge) | Procedural materials and analytic intersections | `8a4e4ff4428ce1159df2b433e870f929237f6eb8` |
| [Formalyth](https://github.com/wieslawsoltes/Formalyth) | Direct model interaction with sparse controls | `1ec302623258be935e9b199296437c44955d396a` |
| [Veldra 3D](https://github.com/wieslawsoltes/Veldra3D) | Clean rendered output without modelling overlays | `c0a17ba130c0f3e47e9e86a74baf47751f4c1284` |

## Publication and evidence

Canonical source: `Luna-Stage.html` on `main`. GitHub Pages publishes the **same bytes** as `index.html` on the dedicated `gh-pages` branch, so the project root opens the room directly. There is no redirect, wrapper, iframe or second application.

`qa/verify.py` is a development-only Python Playwright harness. `qa/behaviour.py` independently times the full film, tests storage/reduced-motion resilience, and inspects the exported PNG pixels; it also uses Pillow. `qa/bake_stills.py` reproduces the six embedded native-GPU stills. It serves the local file, uses a real Chromium browser, requires WebGPU initialization, captures the seven requested 1920 × 1080 views, and exercises keyboard, hit testing, sun, orbit, fullscreen, snapshot, persistence and the explicit Canvas2D fallback. `--live --url ...` checks the deployed room. JSON reports and PNG hashes record observed results. Visual judgements are recorded separately in `qa/VISION.md`; an executed shader is not by itself a visual PASS.

```sh
python3 qa/verify.py --full
python3 qa/verify.py --live --url https://Martin-Hausleitner.github.io/Luna-Stage/
```

MIT licensed. The company name and product identification do not grant rights to third-party marks.
