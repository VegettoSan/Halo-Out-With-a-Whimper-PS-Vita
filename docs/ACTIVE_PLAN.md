# Active work — E034 collision specialization, physical validation pending

[Measurements and limitations](OPENGMK_PERFORMANCE_PROBE.md). E032 physical evidence is complete; do not repeat its graphics/audio/closure tests.

- [x] Preserve E033 bbox-pair guard; specialize exact unit/mirrored pixel transforms once per query. No persistent caches or spatial index; original generic loops/pixels/events/frame retained.
- [x] PC differential tests:20000pairs+8000queries+139053coordinates+20000mask checks,320instances/22 workloads; delta audit33/33. Final PC/ARM PASS, original30Hz simulation/resources unchanged.
- [x] Generated dense loads: pairs68.4%, rectangles68.2%, ellipse49.2%, solid53.1%, any51.9% less time. Quiet five-trial paired comparison; not native FPS. Rotated ellipse/solid still regress~10–11%; no universal speedup claim.
- [x] Seven-method counters, early rejects/stale queries, sampled inclusive timings and calibration implemented; CPU added sampled-probe cost~5ns/call. Extra point/range cached guards removed after inconsistent results.
- [ ] Determine actual native method mix, specialization prevalence and probe overhead. E032 has no per-method data; generated CPU frequencies are not Firefight frequencies. Exclude startup/pending-scene window.
- [ ] Resolve rotated ellipse/solid regressions: distinguish code layout/noise from real fallback cost using identical controls and an isolated generic fallback if justified. Preserve evaluation/event order.
- [ ] Next private device experiment: update candidate inherited E032 identity/log markers, package substantial E033/E034 group with HOWAW1178; compare reference flag versus optimized collision paths with same E032 renderer/30Hz, room6/character and rotated-heavy combat. No E034 VPK generated this session; installed00.33 unchanged.

Source/wrappers local-tools/collision-detail-verified-20261126; artifacts build/collision34-verified-host/arm; final evidence reports/local/collision-detail-20261126/{quiet-contract.txt,quiet-analysis.json,verified-delta-audit.json}. Direct main; originals/builds retained, new recovery0. Native benefit/stability of this candidate UNTESTED; full Firefight parity/30Hz performance incomplete.
