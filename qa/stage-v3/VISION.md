# LUNA STAGE 3.2 — visual review

Reviewed native browser output at 1920 × 1080, not an image-generation result. Native test run: `34840145356`; source commit `c31daabd9b55686bd1583b0fe87c7ede6062c13c`; tested runtime SHA-256 `c69359b4565a2a827c4303953f172c9979800569e14e15dec9b4af454ce4e4ce`.

The WebGPU test adapter identifies itself as Google SwiftShader. WGSL actually executes and its pixel buffers are displayed by the application's software-adapter presenter. This does not establish physical-GPU frame rates.

## Observed improvements

The room is the main surface, without an operating-system or browser imitation. The bottom chapter rail is restrained. The olive plant has fine, independently oriented leaves, actual branching, a hollow planter, soil and pebbles; it is no longer a cluster of large green ellipsoids. Photograph-derived wood grain is visible in the morning close-up. Evening LED and pendant lighting is visibly warmer than the morning chapter. The price and CEO margin use perspective on the worktop, not a sidebar. Material cycling, light switching, free camera, 50 clip definitions and PNG export have independent machine-readable native test evidence.

The first visual iteration exposed oversized leaf shadows and a black software-adapter browser surface despite a populated native render texture. Neither was accepted as a visual PASS. The second iteration moved and softened the broad window light, restrained reflections, refined leaf orientation and implemented a real native-pixel presenter. Browser screenshots now show the room; the tests explicitly reject a blank image area.

## Remaining visual limits

This is a more detailed interactive architectural demo, **not a pixel-identical or photorealistic recreation of the earlier concept picture**. City facades remain illustrative and repetitive, eight-sample acceptance frames retain some reflection/lighting sampling artifacts, and some small decor/contact placements and stone detail remain approximate. These limitations prevent claiming that the full original luxury-photorealism ambition has been achieved. A physical 65-inch showroom test has not been performed.

## Packaging verification

After the native tests, the six fallback images are replaced with current native renders. The price fallback uses a clean plate so that toggling the fallback inscription does not double the text. A Canvas2D-only optimization pre-tints the lettering atlas once instead of applying a brightness filter to every projected tile. The native geometry, WGSL renderer, camera and controls remain unchanged. Local fallback tests use a real managed Chromium page with supplied HTML content and an unavailable adapter; they are not labelled as local WebGPU execution.

The runtime is delivered as an HTML application. No AI-generated reference image is used as the room, and no external website is framed inside it.
