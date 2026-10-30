# Road markings: official standards and lane-level data (2026-10-28)

Reference for revamping the road-marking renderer. All numbers come from the primary documents unless
marked *(secondary)* or *(memory, verify)*. Metric is used throughout; US values are also given in feet/inches.
Conversions: 4 in = 0.10 m, 6 in = 0.15 m, 8 in = 0.20 m, 12 in = 0.30 m, 24 in = 0.61 m, 10 ft = 3.05 m, 30 ft = 9.14 m.

Primary sources read:
- MUTCD 11th ed. (Dec 2023), Part 3: https://mutcd.fhwa.dot.gov/pdfs/11th_Edition/part3.pdf
- FHWA Standard Highway Signs (SHS), pavement markings chapter (arrow/symbol drawings): https://mutcd.fhwa.dot.gov/SHSe/Pavement.pdf
- UK Traffic Signs Manual ch. 5 Road Markings (2018/2019): https://assets.publishing.service.gov.uk/media/5c4ace6ded915d38a0611abc/traffic-signs-manual-chapter-05.pdf
- UK Traffic Signs Manual ch. 3 Regulatory Signs (2019, stop/give-way lines): https://assets.publishing.service.gov.uk/media/5c78f895e5274a0ebfec719b/traffic-signs-manual-chapter-03.pdf
- France IISR 7e partie (consolidated 2025-04-04): https://equipementsdelaroute.cerema.fr/IMG/pdf/iisr_7epartie_vc_20250404.pdf
- Japan MLIT circular 1974-12-26 "区画線の設置様式について": https://www.mlit.go.jp/road/sign/kijyun/pdf/19741226kukakusenn.pdf
- Germany RMS Teil 1 (1993) via OCR copy: https://www.slideshare.net/slideshow/rms-1/2824771
- Australia: IPWEA/TfNSW standard drawing (AS 1742.2 based), Cessnock CC: https://www.cessnock.nsw.gov.au/files/assets/public/v/1/hptrim/website-forms-do-not-change/04-ipwea-sd-tc-set-rev1.pdf

---

## 1. United States: MUTCD 11th edition (2023), Part 3

### 1.1 Line widths, patterns, colours (3A.03, 3A.04)
| Item | Value | Ref |
|---|---|---|
| Normal line | 4-6 in (0.10-0.15 m). 6 in recommended as a safety measure and for automated driving; many states now use 6 in on state highways | 3A.04 P2, P5 |
| Wide line | at least 2x normal, so 8-12 in (0.20-0.30 m); 8 in is the common choice | 3A.04 P2 |
| Double line | two lines; the space between them should be no more than 2x one line's width (4 in lines with a 4-8 in gap) | 3A.04 P3 |
| Broken line | 10 ft line / 30 ft gap (3.05 / 9.14 m; 40 ft cycle), "or similar ratio" | 3A.04 P6 |
| Dotted lane line (lane drop, through vs auxiliary lane) | 3 ft line / 9 ft gap (0.91 / 2.74 m) | 3A.04 P7, 3B.07 P11 |
| Dotted extension (through intersections, tapers, ramp areas) | 2 ft line / 2-6 ft gap (0.61 / 0.61-1.83 m); at least as wide as the line it extends | 3A.04 P7, 3B.11 P3 |
| Colours | yellow = separates opposing directions, left edge of divided/one-way roads and ramps, TWLTL/reversible lanes. White = same-direction separation, right edge. Also red (wrong-way RPMs), blue (accessible parking), purple (ETC-only lanes). Black may outline lines on light (concrete) pavement | 3A.03 |
| Raised pavement markers | N = one broken-line cycle (40 ft). Positioning guides at 2N (80 ft); N or less on curves; 3N on straight freeways | 3B.14-3B.15 |

### 1.2 Centre lines (3B.01-3B.05)
- Always yellow. Two-lane two-way road: (A) one broken yellow line = passing allowed both ways; (B) solid + broken
  yellow = passing allowed only from the broken side; (C) double solid yellow = no passing. **A single solid yellow
  centre line is not allowed** (3B.01 P5).
- Undivided roads with 4+ lanes: double solid yellow (3B.01 P6).
- Required on urban arterials/collectors with traveled way >= 20 ft and ADT >= 6000, and on any road with 3+ lanes;
  recommended on rural roads >= 18 ft wide with ADT >= 3000; possible on roads >= 16 ft (4.9 m); judgement below 16 ft (3B.02).
  Renderer rule: **no centre line on paved roads narrower than about 4.9 m (16 ft)**; residential streets often have none.
- No-passing zones: at curves where passing sight distance < Table 3B-1 (450 ft at 25 mph ... 1,200 ft at 70 mph);
  join zones closer than 400 ft (3B.03).
- Reversible lane: broken **double** yellow on each side (3B.04).
- Two-way left-turn lane (TWLTL): solid yellow on the outside, broken yellow on the inside (facing the TWLTL) on each
  side, plus white opposing turn arrows near the start (3B.05). Should not reach the intersection; turns into a left-turn bay or a painted median.
- Through intersections, centre-line extensions must be dotted (3B.11 P5). A double line is extended as a single line.

### 1.3 Lane lines, lane drops, ramps (3B.06-3B.08, 3B.12)
- Lane line: broken white (10/30). Solid white where crossing is discouraged (turn-lane approaches, toll lanes; optional
  on through lanes near intersections and crosswalks). Double solid white where crossing is prohibited (3B.06).
  Required on all freeways and Interstates.
- Ramps (3B.07):
  - Exit with parallel decel lane: normal-width dotted white from the start of the taper to the theoretical gore.
  - Tapered exit: dotted extension from the gore through the taper to the edge line.
  - Entrance with parallel accel lane: dotted white lane line from the gore for at least half the gore-to-taper-end distance,
    optionally continued to the end of the taper.
  - **Wide dotted white** (3 ft/9 ft, 8 in) for lane drops at exits and intersections, route splits, and through vs
    continuous auxiliary lanes. On freeways it starts **>= 1/2 mile** before the theoretical gore.
- Channelizing line (gore / neutral area edges): solid **wide** or double solid white. All markings inside the neutral area are white (3B.08).
- Lane-reduction taper: L = W*S (S >= 45 mph) or L = W*S^2/60 (S < 45 mph), L and W in ft, S in mph; minimum 100 ft urban, 200 ft rural (3B.12).

### 1.4 Edge lines (3B.09-3B.11)
- Right edge: normal solid white. Left edge on divided roads, one-way streets and ramps: normal solid **yellow**.
- Wide edge lines are optional for emphasis; 4 in -> 6 in is a recommended crash countermeasure.
- Required on freeways, expressways and rural arterials >= 20 ft wide with ADT >= 6000. Often left out on curbed urban streets with parking.
- Edge lines stop at intersecting approaches (dotted extension optional). They continue across driveways and the far side of T-junctions.

### 1.5 Transverse markings
| Item | Value | Ref |
|---|---|---|
| Stop line | solid white, **12-24 in** (0.30-0.61 m) wide, across the approach lanes. At least 4 ft before the crosswalk; with no crosswalk, 4-30 ft from the edge of the crossing road; 20-50 ft before an uncontrolled multi-lane crosswalk. May be staggered per lane | 3B.19 |
| Yield line ("shark teeth") | white triangles pointing at approaching traffic: base 12-24 in, height 1.5x base, 3-12 in apart. SHS drawing: 12 in base, 18 in height | 3B.19 P10-12, SHS |
| Crosswalk, transverse ("lines") | two white lines 6-24 in wide (wide where there's no stop line or speeds > 35 mph); crosswalk at least **6 ft** wide (8 ft at mid-block crossings >= 40 mph) | 3C.03-3C.04 |
| Longitudinal bar ("continental"/zebra) | bars 12-24 in wide, gaps 12-60 in and <= 2.5x bar width, at least 3 bars, bars parallel to traffic, may be shifted off wheel paths. Typical: 24 in bars, 24-48 in gaps | 3C.05-3C.06 |
| Ladder | continental bars plus two 6-24 in transverse lines; bars may be rotated up to 45 deg | 3C.07 |
| Bar pair | pairs of 8-12 in bars with a gap of one bar width; 24-60 in between pairs; no transverse lines | 3C.08 |
| Chevrons (gore, same direction) | white, pointing toward traffic | 3B.25 |
| Diagonals (opposing traffic / left shoulder) | yellow; right shoulder or no-parking areas: white; slant away from adjacent traffic | 3B.25 |
| Chevron/diagonal width and angle | >= 12 in at speed limits >= 45 mph, >= 8 in below 45; 4 in allowed at < 25 mph. 30-45 deg to the lines; spacing by judgement (practice: 20-50 ft on freeways, 10-20 ft urban) | 3B.25 P10-11 |
| Do Not Block box | wide white outline + white crosshatch (4-6 in) and/or "DO NOT BLOCK"/"KEEP CLEAR" | 3B.26 |
| Parking stalls | white (blue for accessible) | 3B.27 |

### 1.6 Arrows, words, symbols (3B.20-3B.23, 3E.03, SHS)
- White, no wider than one lane, scaled to the lane. Up to 3 lines per message; spacing 4x-10x the character height.
  May shrink 25 % on roads < 25 mph.
- Turn lanes: at least **2 arrows** per turn lane, one near the start of the full-width lane and one before the stop line.
  Arrows are required where through lanes become mandatory turn lanes, usually with "ONLY".
- Sizes (SHS drawings): conventional-road through arrow about **7.5 ft** long (5 ft head, 12 in stem); combined
  through+left about 12.75 ft; **freeway/expressway/ramp arrow 23.5 ft** long (head 7 ft, stem 16.5 ft, 6-8 in strokes,
  30 in head width); lane-drop arrow 18 ft; wrong-way arrow 23.5 ft.
- Word letters >= 6 ft tall, 8 ft typical ("ONLY", "STOP", "BUS ONLY", "XING").
- HOV / preferential lane: white **diamond** 13 ft 1.5 in long x 3 ft wide, 6 in stroke (SHS). HOV lanes also use wide solid white
  (crossing discouraged), double solid white (prohibited) or wide dotted white (permitted) separators; buffers > 4 ft get chevrons (3E.02).
- Red / green / purple coloured pavement: bus lanes (red), bike lanes (green), ETC-only lanes (purple) (3H).

### 1.7 Rumble strips (3K)
The MUTCD does not set their geometry, only how markings combine with them: an edge or centre line may be painted
over a rumble strip ("rumble stripe"), and an edge line must not be added to a shoulder rumble stripe.

### 1.8 Typical US practice by road type (MUTCD + common state practice)
| Road | Centre | Lane line | Edge | Other |
|---|---|---|---|---|
| Interstate / freeway | none (median barrier) or yellow left edge | 6 in white 10/30 | 6 in (some states 8 in) white right, yellow left | 8 in wide dotted 3/9 lane drops; wide channelizing gore + 12 in white chevrons; 23.5 ft arrows |
| Rural two-lane highway | 4-6 in yellow, broken 10/30 or solid/broken or double solid by passing zone | - | 4-6 in white | rumble stripes common |
| Urban arterial | double solid yellow (4+ lanes) or TWLTL | 4-6 in white 10/30, solid on turn approaches | often none with curbs/parking | 12-24 in stop bars, continental crosswalks, 7.5 ft arrows |
| Local / residential | usually none (< 16-20 ft or low ADT) | - | none | stop bar + crosswalk at signals and stops |

---

## 2. United Kingdom: TSRGD 2016 + Traffic Signs Manual ch. 5 (2018) and ch. 3 (2019)

All longitudinal lines are **white**. Yellow is only for kerbside waiting/loading restrictions, yellow box
junctions and yellow bars at roundabouts. Two modules: a **6 m** module (speed limit <= 40 mph) and a **9 m**
module (> 40 mph) (TSM5 2.1).

| Diagram | Use | Mark / gap | Width | Ref |
|---|---|---|---|---|
| 1008 | centre line, <= 40 mph | **2 m / 4 m** | 100 mm (150 on roads >= 10 m or 3-4+ lanes) | TSM5 Table 2-1, Fig 2-1 |
| 1008.1 | centre line, > 40 mph | **3 m / 6 m** | 100 / 150 mm | Table 2-1 |
| 1005 | lane line, <= 40 mph | **1 m / 5 m** | 100 (150) mm | Table 2-2, Fig 2-3 |
| 1005.1 | lane line, > 40 mph and motorways | **2 m / 7 m** | 100; **150 mm on 70 mph dual carriageways and motorways** | Table 2-2, 2.3.5 |
| 1004 | warning line (bends, crests, junction approaches), <= 40 | **4 m / 2 m** | 100 / 150 mm | Table 2-3, Fig 2-4 |
| 1004.1 | warning line, > 40 | **6 m / 3 m** | 100 / 150 mm | Table 2-3 |
| 1013.1 | double white line (no overtaking) | solid + solid, or solid + broken **1 m / 5 m** | each 100 min, **150 normal**, 175 mm apart (90 min); total <= 900 mm (B: 1200) | TSM5 3.2.1 |
| 1009A | edge at junction mouths / private accesses | 600 mm / 300 mm | 100/150/200 | Fig 2-6 |
| 1010 | edge at lay-bys, merges/diverges, lane drops, bus lane starts | **1 m / 1 m** | 100-300 (100 <= 40 mph, 150 at 50-60, 200 at 70) | Table 2-5, Fig 2-6 |
| 1012.1 | continuous edge line | solid | 100 (no hard strip), 150, **200 mm on motorways** | Table 2-5 |
| 1012.2 / .3 | raised-rib edge line (motorways) | solid with ribs | 200 (150) mm | Table 2-5 |
| 1002.1 | STOP line | solid | about 200-300 mm (TSM3 Fig 2-5) | TSM3 2.3 |
| 1003 / 1003A | GIVE WAY | double broken, **600 mm / 300 mm** | 200 mm, **300 mm** with the 9 m module | TSM3 Fig 3-1, TSM5 6.2.2 |
| 1023A | give-way triangle | 2.1-2.75 m before the give-way line (up to 15 m) | - | TSM3 3.2.5 |
| 1001 | stop line at signals | solid | 200-300 mm | TSM5 |

Hatched areas and chevrons (TSM5 2.7, 2.11, Fig 2-8):
- 1040 (centre hatching between opposing flows): white diagonals **150/200 mm** at **45 deg**. Boundary is broken
  4 m/2 m (<= 40 mph) or 6 m/3 m (> 40), or solid. Hatched area is 0.8-8 m wide. The size and spacing of the diagonals follow the boundary module.
- 1040.3 / 1040.4 (lane loss, edge hatching): 200 mm solid boundary. Deflection arrows 4.5 m (<= 40 mph), 6 m (41-60) or 9 m (61-70)
  long, the first one 13.75-37.5 m before the taper (Table 2-6).
- 1041 (chevrons between same-direction streams; drivers should not enter) and 1042 (mandatory, slip-road gore):
  chevrons point toward traffic, 200 mm boundary (150 at roundabouts or roads without hard shoulders).
- Yellow box (1043): yellow 150 mm diagonals, about 2 m apart (box side < 9 m) or 2.5 m apart (>= 9 m), 200 mm border (TSM5 8.4).
- Yellow transverse bars at roundabout approaches: 90 bars (45 on slip roads), each 600 mm wide (6.10.5).
- Kerbside waiting lines: single yellow (1017) and double yellow (1018.1). Councils use 50, 75 or 100 mm, with 75 mm
  most common and 50 mm in sensitive areas *(secondary: council TRO drawings)*.
- Bus lane boundary (1049A): solid white **250 or 300 mm**. The lane start/break uses 1010 (TSM3 ch. 9).
- Motorway layout: 1005.1 lane lines (150 mm), 1012.1/1012.2 200 mm edges, 1010 for lane drops (studs every 18 m, then 8 m to the nose).
- UK crossings (zebra stripes, zig-zags) are in TSRGD Schedule 14. I did not read the figures (not covered in TSM5).

---

## 3. Continental Europe

### 3.1 Germany (StVO Anlage 2/3 + RMS Teil 1 1993 / RMS-A 2019)
- Widths (RMS 2.1.1): **Schmalstrich 0.12 m (Autobahn 0.15 m)**, **Breitstrich 0.25 m (Autobahn 0.30 m)**.
- Leitlinie (Z 340, broken lane/centre line): ratio 1:2. Usually **6 m / 12 m** outside towns and on Autobahns,
  **3 m / 6 m** in towns; 1:1 inside junctions *(absolute lengths: secondary sources; RMS gives the ratios)*.
  Leitlinien only on roads >= 5.50 m wide outside towns (RMS 3.2.2.1).
- Warnlinie (lead-in to a solid line): ratio 2:1, **6 m / 3 m** outside towns, **3 m / 1.5 m** in towns *(secondary)*.
- Fahrstreifenbegrenzung (Z 295, solid, no crossing) = Schmalstrich. Einseitige Fahrstreifenbegrenzung (Z 296) = solid + broken.
- Fahrbahnbegrenzung (edge, Z 295 as edge): Autobahn solid Breitstrich 0.30 m; other roads Schmalstrich 0.12 m,
  or Breitstrich if the paved shoulder is >= 1.0 m (RMS 3.1.3). At junctions/entries the edge is a broken Breitstrich, 1:1.
- Bus/special lane: Breitstrich; broken 2:1 where crossing is allowed or time-limited (3.3.2).
- Reversible lanes: double broken Schmalstrich, 2:1 (3.4.2).
- Haltlinie (Z 294): **0.50 m**, usually 3.5 m before signals (2.5 m min), >= 1.0 m before crossings (4.6).
- Wartelinie (Z 341, give way): 0.50 m wide, **0.50 m / 0.25 m** dashes (4.7.2).
- Fußgängerüberweg (Z 293, zebra): 0.50 m stripes, 0.50 m gaps, parallel to traffic (4.9). Pedestrian
  furt edges: Schmalstrich 0.50/0.20. Cycle furt: Breitstrich 0.50/0.20 (RASt 06: 0.50/0.25), 2.0 m wide.
- Sperrfläche (Z 298): white diagonal hatching, at least 3 stripes. The border width matches the adjoining lines (small areas: Schmalstrich).
- Richtungspfeile: **7.50 m Autobahn, 5.00 m elsewhere, 3.00 m on cycle lanes** (RMS 2.5).
- Colours: white. **Yellow lines are temporary (roadworks) and override white.**

### 3.2 France (IISR 7e partie, art. 113)
Width unit **u**: 7.5 cm (motorways, dual carriageways, 4-lane rural roads), 6 cm (major roads), 5 cm (others), 3 cm (cycle tracks).

| Modulation | Line / gap | Use |
|---|---|---|
| T1 | **3 m / 10 m** | rural centre line and lane lines (width 2u) |
| T'1 | 1.5 m / 5 m | urban centre/lane lines |
| T3 | 3 m / 1.33 m | warning before a solid line (2u; 3u on 3-lane roads); slow-vehicle lanes, bus lanes, cycle lanes (5u) |
| T2 | 3 m / 3.5 m | edge line on roads (**ligne de rive, 3u**); accel/decel lanes (5u) |
| T'3 | 20 m / 6 m | edge |
| T4 | 39 m / 13 m | hard-shoulder edge on motorways (3u) |
| t'2 | 0.5 m / 0.5 m | transverse "cédez le passage" line (50 cm wide) |

- Solid centre line 2u; 5u on 4-lane undivided roads; 3u on 3-lane roads. Mixed line = solid + T1 or T3.
- STOP line: solid, **50 cm**. Give-way line: T'2 dashes, 50 cm wide. Signal "ligne d'effet": T'2, 15 cm wide.
- Passage piétons: white bars **0.50 m** wide with **0.50-0.80 m** gaps, at least 2.50 m long in towns and 4-6 m in the countryside.
  Centre/lane lines stop 0.50 m short of the crossing (art. 118).
- Yellow: no stopping (solid 2u), no parking (T'2 2u), bus-stop zig-zag, delivery bays. Also temporary roadworks lines.
- "Zébras" (hachures) in gores and medians, with an unpainted 2u gap next to the solid lines.

### 3.3 Netherlands (CROW publication "Richtlijnen Bebakening en Markering"; brief, secondary)
Dutch drawings write dashes as "line-gap" in metres:
- **3-9**: deelstreep (lane line), rural and motorway.
- **9-3**: warning line before a solid line.
- **1-3** (wide, 0.30-0.45 m): "blokmarkering" at entries/exits and weaving sections.
- **1-1**: through junctions.
- **3-3**: broken edge line on 80/60 km/h roads.
Widths are 0.10 m on municipal roads and 0.15 m on rural roads/motorways.
Under the EHK (essential recognisability) scheme, 80 km/h distributor roads have a double solid centre line (often with
green in between) and broken edge lines; 60 km/h access roads have no centre line and broken edge lines.
*(Secondary: project drawings on officiele-overheidspublicaties.nl; verify against CROW.)*

---

## 4. Japan, Australia, Canada, others

### 4.1 Japan (MLIT circular 1974, 区画線の設置様式; 道路標識令)
| Line | Urban roads | Rural / motorways | Expressway (>= 80 km/h) |
|---|---|---|---|
| Centre, double solid (t / gap d) | 0.15 / 0.15 m | same | same |
| Centre, single solid | 0.20 m | 0.20 | 0.20 |
| Centre, broken | **5 m / 5 m**, 0.15 (0.12 on quiet urban streets) | 5/5, 0.15 | 5/5, 0.15 |
| Lane line, solid | 0.15 | 0.15 | 0.15 |
| Lane line, broken | **6 m / 9 m** (or 5/5 in dense areas or sharp curves) | 6/9 | **8 m / 12 m** |
| Outer edge (車道外側線) | 0.15 | 0.15 | **0.20** |
- The centre line is solid where one direction is >= 6 m wide or overtaking is banned, otherwise broken.
- Centre lines are **white**. **Yellow** solid centre = no crossing for overtaking (はみ出し禁止). Yellow lane line = no lane change.
- Stop lines and crosswalk bars are **0.45 m** wide; crosswalk bars have 0.45-0.90 m gaps *(secondary: webcartop.jp)*.

### 4.2 Australia (AS 1742.2; TfNSW/IPWEA drawing)
All markings are **white** (yellow only for no-stopping kerb lines, bus/tram, snow areas and temporary works).

| Type | Pattern | Width |
|---|---|---|
| S1 separation (centre) line, 2-lane road | **3 m / 9 m** | 0.10 m |
| S2 separation line, multi-lane undivided | 6 m / 6 m | 0.15 m |
| BB / BS barrier lines (no overtaking) | double solid, or solid + 3/9 broken; about 0.08 m lines with a 0.08 m gap (drawing) | ~0.08-0.10 m |
| L1 lane line | **3 m / 9 m** | 0.08-0.10 m (0.15 on some freeways; NT: 0.20 on expressways) |
| C1 continuity line (through lane next to turn lane, ramp, bus bay, auxiliary lane) | **1 m / 3 m** | **0.20 m** |
| E1/E2 edge | solid | 0.12 m (general), 0.15 m (freeway) |
| E4/E5 island / gore / painted median outline | solid | 0.20 m |
| T1 turn lines in intersections | 0.6 m / 0.6 m | 0.10 m |
| Holding (give-way) line TB | 0.6 m / 0.6 m | 0.30 m |
| Stop line TF | solid | 0.30-0.45 m |

Austroads (AP-R578-18) recommends 150 mm edge lines for automated vehicles.

### 4.3 Canada (TAC MUTCDC; Ontario OTM Book 11)
Like the US: yellow centre lines and white lane and edge lines. Broken lines are commonly **3 m / 6 m**; 3-3 and 3-9 also
appear on OTM drawings. Widths are 10-15 cm *(secondary: Durham Region spec S-301.020; the MUTCDC text was not read)*.

### 4.4 Yellow vs white centre lines (Wikipedia "Road surface marking" + national docs)
- **Yellow centre** (opposing traffic): USA, Canada, Mexico and most of the Americas (Brazil, Colombia, Peru ...), Norway, Finland
  (no-passing yellow, passing white), South Korea, China and Taiwan *(memory: GB 5768.3 uses yellow centre lines and
  white lane lines; lanes 6/9 m at >= 60 km/h, 2/4 m below)*, Thailand. Russia allows yellow since 2018.
- **White centre**: UK, Ireland (yellow is the *edge* line), almost all of continental Europe, Australia, Japan
  (yellow = no overtaking), Israel, Hong Kong, India, Venezuela. Philippines: white, yellow for no overtaking.
  Argentina/Uruguay: white where passing is allowed, yellow where it is not. New Zealand: white centre with yellow no-passing lines.
- Yellow for **temporary roadworks** lines: Germany, Austria, Switzerland, Netherlands, France and others (these override the white lines).
- Yellow **left edge** on divided roads: US/Canada. Yellow kerbside parking restrictions: UK, Ireland, France, Australia (no stopping), Japan (none).

---

## 5. OpenStreetMap lane-level tagging a renderer can use

Way-level keys (the order of `:lanes` values is **left to right as seen in the lane's direction of travel**, separated by `|`):

| Key | Use for markings |
|---|---|
| `lanes=*` | total motor lanes, including bus lanes and centre turn lanes, but **not** bike lanes |
| `lanes:forward` / `lanes:backward` / `lanes:both_ways` | lane split by direction; `lanes:both_ways=1` + `turn:lanes:both_ways=left` = **two-way left-turn lane** (yellow solid+broken pair) |
| `oneway=yes` | yellow left edge (US) / no centre line |
| `turn:lanes(:forward/:backward)` | `left`, `slight_left`, `through`, `right`, `merge_to_left`, `reverse`, `none` ... gives arrows per lane; `merge_to_*` = lane drop |
| `change:lanes(:forward/:backward)`, `change=*` | `yes` / `no` / `not_left` / `not_right` per lane. Between two lanes: both allowed = broken; one side only = solid+broken; neither = solid (US: single solid = discouraged, double solid = prohibited) |
| `overtaking=*` (`overtaking:forward/backward`) | `no` -> double solid centre; one direction only -> solid+broken; `yes` -> broken |
| `divider=*` | `dashed_line`, `solid_line`, `double_solid_line`, `no` (centre divider; experimental, low use) |
| `lane_markings=yes/no` | `no` = draw no lane lines (an edge line may still exist); de facto |
| `width`, `width:lanes`, `width:carriageway` | geometry; fall back to a road-type default |
| `placement`, `placement:forward/backward` | `left_of:N` / `middle_of:N` / `right_of:N` / `transition`; lanes counted from the left, in way direction, per direction. **No tag = the way is the centre of the carriageway.** Needed to keep lanes continuous where lane counts change or roads fork. Draft proposal, but used by JOSM's lane style and osm2streets |
| `bus:lanes`, `psv:lanes`, `busway=lane` (`busway:left/right`) | bus lanes (red surface / wide solid white / "BUS" text) |
| `hgv:lanes`, `access:lanes`, `motor_vehicle:lanes`, `hov:lanes`, `hov=designated` | lane-use symbols (HOV diamond) and restrictions |
| `cycleway(:left/:right/:both)=lane / track / shared_lane` | bike lane (not counted in `lanes`), buffer, green paint; `cycleway:lanes=no\|lane\|no` places it inside the lane list |
| `parking:left/right/both=lane/street_side/no` (+ `:orientation`) | parking-lane edge lines and stall marks |
| `shoulder=*`, `shoulder:left/right`, `sidewalk=*` | where the edge line sits relative to the kerb |
| `destination:lanes`, `maxspeed:lanes`, `minspeed:lanes` | optional route shields / speed text |
| `surface`, `smoothness` | no markings on unpaved surfaces |
| `junction=roundabout` | roundabout lane/edge rules (MUTCD 3D) |
| `highway=motorway_link` + `oneway` | ramp: yellow left edge, white right edge; gore at the split |

Point and area tags:
- `highway=stop` / `highway=give_way` / `highway=traffic_signals` (+ `direction=*`, `stop=all/minor`) -> stop bar or give-way line.
- `highway=crossing` node + `footway=crossing` way, `crossing=marked/uncontrolled/traffic_signals/unmarked`,
  **`crossing:markings=*`** (approved): `zebra`, `lines`, `ladder`, `ladder:skewed`, `ladder:paired`, `dashes`, `dots`,
  `zebra:double`, `zebra:paired`, `zebra:bicolour`, `lines:paired`, `surface`, `pictograms`, `no`, `yes`.
  Mapping to MUTCD: zebra = longitudinal bar, lines = transverse, ladder = ladder, zebra:paired = bar pair.
- `road_marking=*` (approved key, sparse): `stop_line` (node or way), `lane_divider` + `stroke=solid/dashed`,
  `edge_line`, `crossing_edge`, `restriction` + `pattern=chevron/crosshatch/stripes` (gores, hatched areas), `arrow` + `arrow=*`,
  `text` + `inscription=*`, `symbol`. The wiki says straight lines should come from way tags; separate geometry is for markings inside intersections and area markings.
- `area:highway=*` polygons (rare) give exact carriageway outlines.

Implementation notes:
- Missing tags: lanes defaults by `highway` (motorway: 2 per direction; trunk/primary: 1-2; residential: 1 per direction, often unmarked),
  `oneway` by type (motorway, link, roundabout). If `lanes` is odd on a two-way road and there are no `:forward/backward` tags,
  assume the extra lane is a centre turn lane only when `turn:lanes:both_ways` says so; otherwise split the extra lane to forward.
- Count consistency: `lanes` = forward + backward + both_ways; each `:lanes` value list must have the same number of entries
  (JOSM's "Lane and Road Attributes" style flags mismatches).

Projects that build lane geometry from these tags:
- **osm2streets** (https://github.com/a-b-street/osm2streets, **Apache-2.0**, Rust + WASM/JS + Python bindings; replaces osm2lanes).
  It turns OSM ways into a road network with a left-to-right list of lanes per road (type, direction, width), **lane and intersection
  polygons**, and **lane markings** (lines between lanes, turn arrows, access symbols) as GeoJSON. It handles `placement`, dual
  carriageways and short-road merging; crosswalks and turn movements are still planned. Used by A/B Street and the osm2streets web
  viewer. It is the best reference to port or call (our server is moving to Rust).
- **A/B Street**: traffic sim built on osm2streets; per-lane widths and markings.
- **JOSM "Lane and Road Attributes" style**: a 2-D lane renderer with `placement` and `change:lanes` support (ruleset logic worth copying).
- **Streets GL** (MIT, https://github.com/StrandedKitty/streets-gl): 3-D OSM renderer; the README does not document lane-marking support.
- OSM Carto does not draw lanes.

---

## 6. Other lane-level / marking data sources
- **Overture transportation `segment`** (schema v2): **no lane property**; there is `width_rules`, `speed_limits`,
  `access_restrictions`, `road_surface`, `road_flags`, `level_rules`, `destinations`, `prohibited_transitions`.
  Lanes still have to come from OSM tags (Overture copies OSM tags only partly).
  https://docs.overturemaps.org/schema/reference/transportation/segment/
- **Mapillary map features** (points from street-image detection, API v4 `map_features`, CC-BY-SA):
  `marking--discrete--arrow--left/right/straight/split-left-or-straight/split-right-or-straight`,
  `marking--discrete--crosswalk-zebra`, `marking--discrete--stop-line`, `marking--discrete--give-way-row/single`,
  `marking--discrete--symbol--bicycle`, `marking--discrete--text`, `marking--discrete--other-marking`.
  Useful for crosswalk and stop-line positions and arrow presence. It has no continuous lane lines (those exist only in the Vistas
  segmentation classes). https://www.mapillary.com/developer/api-documentation/points
- **US government**: FHWA HPMS (through lanes, lane width, median type, shoulder width, on all federal-aid roads, public
  shapefiles by state); state road inventories; city pavement-marking GIS layers (e.g. Austin "markings short line" for
  crosswalks/stop/yield lines on data.gov; Montgomery County MD pavement-marking FeatureServer; NYC, SF, Seattle publish crosswalk layers).
- **Netherlands**: NWB + Rijkswaterstaat "Wegkenmerken" (lane counts and markings on national roads).
- **Aerial imagery**: NAIP (US, 0.6 m) and state orthos (0.15-0.3 m) show lane lines and crosswalks for our photo checks (`ortho_naip`).
- HD-map datasets (HERE, TomTom, Japan DMP, Lanelet2/OpenDRIVE samples) are commercial or limited to small areas.

---

## 7. Recommended defaults by road type and region (renderer table)

Notation: pattern = line / gap in metres; W = width in metres; Y = yellow, Wh = white. "US" also covers Canada
(Canada: 3/6 broken). "EU-W" = UK/IE/DE/FR/NL-style white-only countries (use the specific row where one is given).

| Region | Road type | Centre line | Lane line | Edge line | Lane drop / ramp | Stop / give-way | Crosswalk |
|---|---|---|---|---|---|---|---|
| US | motorway | - (Y left edge 0.15) | Wh 0.15, 3.05/9.14 | Wh right 0.15 (0.20 some states), Y left 0.15 | Wh 0.20 dotted 0.91/2.74; gore: Wh 0.20 solid + 0.30 chevrons at 45 deg; arrows 7.2 m | - | - |
| US | trunk/primary (multi-lane, undivided) | Y double solid 0.10-0.15, gap 0.10 | Wh 0.10-0.15, 3.05/9.14; solid near turn bays | Wh 0.10-0.15 (rural only) | Wh 0.20 dotted 0.91/2.74 | stop Wh 0.45 (0.30-0.61) | continental: 0.61 bars, 0.61-1.2 gaps, 3.0 m wide (min 1.8) |
| US | rural two-lane | Y 0.10-0.15: broken 3.05/9.14 / solid+broken / double solid by `overtaking` | - | Wh 0.10-0.15 | - | stop 0.45 | rare |
| US | TWLTL (`lanes:both_ways=1`) | Y solid outside + Y broken 3.05/9.14 inside, both sides | - | - | - | - | - |
| US | residential / service | none if < 4.9 m or unmarked; else Y double 0.10 | - | none | - | stop 0.30-0.45 at stop signs | transverse 0.15-0.30 lines, 1.8-3.0 m |
| UK | motorway | - | Wh 0.15, 2/7 (1005.1) | Wh 0.20 solid (1012.1/.2) | 1010 Wh 1/1 W 0.20-0.30; 1042 chevrons 0.20 boundary | - | - |
| UK | rural single carriageway > 40 mph | Wh 0.10, 3/6 (1008.1); warning 6/3 before hazards; double white 0.15 + 0.175 gap where no overtaking | Wh 0.10, 2/7 | Wh 0.10-0.15 solid | 1010 1/1 | give-way 2x 0.30 dashes 0.6/0.3 | - |
| UK | urban <= 40 mph | Wh 0.10, 2/4 (1008); warning 4/2 | Wh 0.10, 1/5 | usually none; Y kerbside 0.075 single/double | 1010 1/1 0.10 | stop 0.20-0.30 solid; give-way 2x 0.20 dashes 0.6/0.3 | zebra (TSRGD Sch 14) |
| DE | Autobahn | - | Wh 0.15, 6/12 | Wh 0.30 solid | Wh 0.30 broken 6/6 (1:1) at entries/exits; arrows 7.5 m | - | - |
| DE | Landstraße | Wh 0.12, 6/12; Warnlinie 6/3; solid Z 295 | Wh 0.12, 6/12 | Wh 0.12 solid (0.25 if shoulder >= 1 m) | - | Haltlinie 0.50; Wartelinie 0.50, 0.5/0.25 | - |
| DE | innerorts | Wh 0.12, 3/6; Warnlinie 3/1.5 | Wh 0.12, 3/6 | usually none | - | 0.50 / 0.50-0.25 | zebra 0.50/0.50, >= 3-4 m |
| FR | autoroute (u = 0.075) | - | Wh 0.15 (2u), T1 3/10 | Wh T4 39/13 W 0.225 (hard shoulder) | T2 3/3.5 W 0.375 (5u) | - | - |
| FR | route (u = 0.05-0.06) | Wh 2u, T1 3/10; T3 3/1.33 before solid | Wh 2u, T1 | Wh T2 3/3.5, W 3u | - | STOP 0.50 solid; cédez 0.50, 0.5/0.5 | bars 0.50, gaps 0.5-0.8, 2.5 m (town) / 4-6 m |
| FR | agglomération | Wh 2u, T'1 1.5/5 | Wh 2u, T'1 | rarely | - | as above | as above |
| NL | autosnelweg | - | Wh 0.15, 3/9 | Wh 0.15-0.20 solid | blok 1/3 W 0.30-0.45 | - | - |
| JP | expressway | (median) | Wh 0.15, 8/12 | Wh 0.20 | - | - | - |
| JP | general road | Wh 0.15, 5/5 broken; Wh 0.20 solid; **Y solid = no overtaking** | Wh 0.15, 6/9 (5/5 urban) | Wh 0.15 | - | stop 0.45 | bars 0.45, gaps 0.45-0.90 |
| AU/NZ | freeway | - | Wh 0.10-0.15, 3/9 | Wh 0.15 | continuity 1/3 W 0.20 | - | - |
| AU | rural / urban | Wh 0.10, 3/9 (multi-lane 6/6, 0.15); barrier double solid | Wh 0.08-0.10, 3/9 | Wh 0.12 | continuity 1/3 W 0.20 | holding 0.6/0.6 W 0.30; stop 0.30-0.45 | zebra 0.6 bars typical *(verify)* |
| Fallback | any | white-centre countries: Wh 0.12, 3/6 urban, 6/12 rural; yellow-centre countries: Y 0.12 same patterns | Wh 0.12, 3/9 | Wh 0.15 | Wh 0.30 1/3 | stop 0.40 | zebra 0.5/0.5 |

Rules a renderer should follow everywhere:
1. Decide the centre-line colour per country: yellow in the Americas, Norway, Finland, South Korea, China, Taiwan and Thailand; white elsewhere.
2. No centre line on paved two-way roads narrower than ~5.0-5.5 m (US 16-20 ft; DE 5.50 m; UK 5.5 m), or with `lane_markings=no`.
3. Lane lines only between same-direction lanes. Pattern by speed class: urban 3/6-ish, rural/motorway 3/9 to 6/12.
4. Use dotted/short patterns (US 0.6/0.6-1.8; UK 1/1; DE 1:1; FR T'2/T2; AU 1/3) for extensions through junctions and alongside merge/diverge/auxiliary lanes. Use the wide (0.20-0.30) version where a lane drops.
5. Solid lane lines on the last ~30-60 m before signalised stop lines and between turn lanes (from `change:lanes` or `turn:lanes` changes).
6. Stop line 0.30-0.60 m across the approach lanes only, ~1.2 m (4 ft) before the crosswalk. Crosswalk style from `crossing:markings`, default zebra/continental.
7. Arrows from `turn:lanes`: 2 per turn lane (start of the full-width lane and ~15-30 m before the stop line). Size about 5 m (EU urban), 7.5 m (EU motorway / US conventional), 7.2 m (US freeway).
8. Gores where a `motorway_link` leaves: wide solid channelizing lines along both sides of the neutral area, chevrons (white) pointing at oncoming traffic, 30-45 deg, 0.30 m wide, ~6-15 m apart.
