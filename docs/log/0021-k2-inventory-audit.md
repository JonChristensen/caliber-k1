# 0021 — K2 inventory audit: the massing was missing 18 parts

**Date:** 2026-07-05 · **Trigger:** Jon — "are you certain you identified
all the parts and skeletal pieces before you ran your massing?"

Honest answer: no. K1 has an explicit `INVENTORY` + a test that fails if
the massing forgets a part. K2 never got that discipline; massing r5
placed the major rotating masses and the winding line but nothing forced
a full recital first.

## The audit (`test_k2_inventory_complete`)

20 of ~38 parts were in the r5 model. The 18 missing, by whether they
move the massing:

**Change the plate (should have been in the massing):**
- the two-position clutch works — `m_clutch`, `m_setting_lever`,
  `m_detent`, `m_clutch_spring` (the whole novel keyless mechanism; only
  its crown wheels were present)
- the metronome balance cock `m_cock` + its feet
- the metronome train bridge + pillars `m_bridge`/`m_pillar`
- the barrel click `m_click`; the impulse roller `m_roller`

**Live inside a placed part (parts-stage, now listed):** mainspring +
drum cover (in the drum), balance staff, banking pins + pallet strap,
hammer return spring + pivot, pusher spring + pen-stop, train cock.

## What adding them proved

The clock core and every rotating metronome mass stay clean on O250.
But the metronome's own **bridge pillars have nowhere to stand** — the
r5 solve minimized plate radius and packed the met train with no reserved
pillar sites, so hand-placed pillars land on its own wheels. The keyless
clutch train also needs real spacing along the stem. Both belong in the
`m_click`/`m_roller`/`m_cock` were absorbed fine; the structural skeleton
was not. `test_k2_full_cast_debt` proves the masses are clean and pins the
remaining conflicts to exactly {pillars, clutch train}.

## Consequence

**O250 is provisional.** K2 needs a full-cast RE-SOLVE that reserves
pillar sites for the metronome bridge and spaces the keyless clutch train
— and the plate will grow. K1's inventory-first discipline is now
mirrored in K2 so this can't recur silently.
