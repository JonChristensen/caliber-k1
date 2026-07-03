# 0008 — Moon phase: drive point found, storey decision pending

Findings from M5 geometry kickoff:

1. **M4 bug found & fixed**: the hour wheel's Ø9 pipe collided with the
   dial cock's Ø6.4 bore. Cock bore opened to Ø9.4 — the pipe now journals
   in the cock (a feature: extra hour-wheel steadiness). Hands stack shifts
   up ~3mm in the next export pass.
2. **Moon drive**: a 14-leaf pinion integral with the hour pipe, ABOVE the
   cock (z~56+, open sky). The committed 46/9x104/9 ratios assumed a 9-leaf
   pinion that cannot exist on a Ø6.8-bore pipe (zero root depth) — ratios
   must be re-searched with s1_pinion=14 (target (A/14)(C/d) = 59.061176).
3. **Moon train runs module 0.8** (display torque only): the 104t-class
   moon disc shrinks to ~Ø85, which fits the rim with center <= r40.
4. **Open decision**: the moon disc plane vs hands sweep — either the disc
   flies above the minute hand (tower grows ~5mm) or the classic move: a
   fixed DIAL ring over the works with the double-hump moon aperture, hands
   above the dial. The dial option is more watch, less tower. Recommended.

Next: re-run ratio search (s1=14), model disc + s1 arbor + moon cock +
aperture dial, module clearance tests. The module mounts on the dial cock
+ one deck pillar — the module bay's first tenant.
