# The wave, traced

The bridge decoration is TRACED from `art/wave_reference.png` (Jon's
mockup), not hand-drawn. Pipeline: `tools/trace_wave.py` classifies the
image into blue-plate / white-gap / gray-rim, finds the disc, and turns
each white wave-gap into a millimetre polygon in `art/wave_traced.py`.
`revc_parts.traced_wave_faces()` subtracts those polygons from the bridge
with structural keep-outs removed first, so the art can never cut a
load-bearing feature.

## To change the wave
1. Edit the mockup image (any tool), keep it a blue plate with white
   wave-gaps and a gray rim, save over `art/wave_reference.png`.
2. `PYTHONPATH=. .venv/bin/python tools/trace_wave.py [rotate_deg]`
3. Rebuild — the new curves flow straight through to the STL.

An SVG-path pipeline (draw the curves directly in a vector tool) is a
small addition if pixel-tracing ever loses fidelity.
