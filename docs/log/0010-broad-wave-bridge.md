# 0010 — The broad wave bridge (Jon's NH35 correction)

Vocabulary bug found by Jon: "bridge" meant a narrow finger bridge to me,
but the NH35-style BROAD train/barrel bridge to him — the wide decorated
plate that covers the movement's back and defines its face. He is right:
that is the showpiece, and it is also better engineering.

## Revised step 2b (supersedes the narrow band bridge)

- ONE broad bridge covers barrel + train: upper bearings for barrel,
  center, third, fourth, escape in a single plate (z16-19). Replaces
  three planned parts. Feet become a bolted perimeter, NH35-style.
- Large round BALANCE OPENING (~Ø54): the balance swims visible in its
  own well; balance cock spans the opening; staff upper bearing + cap
  jewel in the cock. The enclosed-tube-as-bearing idea is retired — the
  open-mouthed rev A curl returns at the opening's rim.
- Art direction (Jon): the crest breaks AWAY from the balance — the
  balance emerges from the wave into calm water. Serenity over drama.
- Surface finishing pass later: printed Cotes de Geneve — literal
  "Geneva waves" striping flowing in the swell direction.
- The narrow wave_bridge_b stays in git history as a study.

Inspection gate for the rebuild: exports/revb/wave_bridge.step over the
massing — swells legible at arm's length, curl open at the balance well,
five bearing bosses over their arbors, stem sector untouched.

## Print-vs-metal deviation register (running)

- Stem line at z29.5: forced by the 20.5mm printed drum the stem must
  overfly. Metal variant: ~5mm barrel, stem drops to plate level
  (NH35-style). Crown moved to r88, overhanging the plate edge with
  >=0.5mm proven clearance to the bridge's north edge.

## 0012-in-place: the variant switch (Jon's clean-flip requirement)

Variant is now a first-class build parameter (revb.VARIANTS, K1_VARIANT
env): print and metal share every coordinate and tooth count; they
differ only in dimension TABLES (drum height, clearances, spring,
escapement type), and derived values like the stem line are FORMULAS
of the variant — flip the switch, the movement reflows. Migration plan:
every part function gains variant-awareness as it is next touched; CI
will build and test BOTH variants; exports split into
exports/revb/{print,metal}/. The CNC drawing will be the metal variant
of the same tested code — never a translation.
