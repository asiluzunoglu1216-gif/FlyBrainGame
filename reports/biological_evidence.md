# Janelia MaleCNS v1.0 Biological Evidence & Functional Mapping Catalog

This catalog documents every connected boundary circuit, sensory peripheral interface, descending motor pool, and associative memory compartment in FlyBrainGame, with associated scientific literature evidence, biological confidence levels, and physical modeling assumptions.

## 1. Summary Statistics

- **Total Neurons Simulated**: 166,700 (100% active in sparse LIF graph)
- **Total Synapses**: 25,582,938
- **Total Cell Types Analyzed**: 11,863

### Category Breakdown

| Functional Category | Cell Types | Neuron Count | Percentage |
|---|:---:|:---:|:---:|
| local interneuron | 9489 | 128,095 | 76.8% |
| sensory peripheral/input | 357 | 17,026 | 10.2% |
| sensory projection | 323 | 9,204 | 5.5% |
| mushroom body | 75 | 4,501 | 2.7% |
| motor | 213 | 2,245 | 1.3% |
| ascending | 646 | 1,906 | 1.1% |
| central complex | 176 | 1,747 | 1.0% |
| descending | 462 | 1,310 | 0.8% |
| unknown/uncertain | 107 | 574 | 0.3% |
| endocrine-related | 15 | 92 | 0.1% |

### Status Breakdown

| Interface Status | Neuron Count | Description |
|---|:---:|---|
| `INTERNAL_ONLY` | 131,600 | Operates purely through connectomic synapses within the 166,700-neuron graph |
| `UNKNOWN_FUNCTION` | 26,577 | Preserved in graph without artificial behavioral semantics |
| `CONNECTED_TO_WORLD` | 7,892 | Receives physical sensory stimulus from virtual environment |
| `CONNECTED_TO_BODY` | 631 | Commands physical body actuators / kinematics in physics engine |

## 2. Evidence Catalog for Connected Circuits

| Circuit / Population | Modeled Biological Role | Game Interface | Confidence | Source / Literature Evidence |
|---|---|---|:---:|---|
| **BM_Hau** (7 cells) | Haustellum mechanosensory and taste bristles | `Proboscis Taste/Contact Sensilla` | **HIGH** | Stocker 1994 |
| **BM_MaPa** (15 cells) | Maxillary palp gustatory and olfactory sensilla | `Palp Chemoreceptors` | **HIGH** | Singh 1997 |
| **BM_Taste** (40 cells) | Tarsal and labellar sucrose taste hairs (sweet GRNs) | `Tarsal & Labellar Sugar Taste Contact` | **HIGH** | Dethier 1976, Jaeger et al. 2018 |
| **CEM** (6 cells) | Cibarial / esophageal motor neuron controlling pharyngeal pumping | `Cibarial Ingestion Pumping` | **HIGH** | Manzo et al. 2012 |
| **DL5_adPN** (2 cells) | Projection neuron relaying fruit alcohols to MB and LH | `Antennal Lobe Odor Channel DL5` | **HIGH** | Bhandawat et al. 2007 |
| **DLMn a, b** (2 cells) | Dorsal longitudinal flight motor neurons (wing downstroke power) | `Downstroke Wing Power Actuator` | **HIGH** | Levine & Wyman 1973 |
| **DLMn c-f** (8 cells) | Dorsal longitudinal flight motor neurons (wing downstroke power) | `Downstroke Wing Power Actuator` | **HIGH** | Levine & Wyman 1973 |
| **DM1_lPN** (2 cells) | Projection neuron relaying apple/ethyl acetate to MB and LH | `Antennal Lobe Odor Channel DM1` | **HIGH** | Marin et al. 2002, Wong et al. 2002 |
| **DM2_lPN** (4 cells) | Projection neuron relaying ester odors to MB and LH | `Antennal Lobe Odor Channel DM2` | **HIGH** | Jefferis et al. 2007 |
| **DM4_adPN** (2 cells) | Projection neuron relaying acetic acid to MB and LH | `Antennal Lobe Odor Channel DM4` | **HIGH** | Grabe et al. 2015 |
| **DM4_vPN** (2 cells) | Projection neuron relaying acetic acid to MB and LH | `Antennal Lobe Odor Channel DM4` | **HIGH** | Grabe et al. 2015 |
| **DNa01** (2 cells) | Co-active descending steering neuron modulating turn velocity | `Co-active Yaw Trim Actuator` | **HIGH** | Namiki et al. 2018 |
| **DNa02** (2 cells) | Unilateral descending steering command neuron governing yaw turn rate | `Yaw Steering Rate Actuator` | **HIGH** | Rayshubskiy et al. 2020, Namiki et al. 2018 |
| **DNg100** (2 cells) | Bilateral descending flight and walking forward propulsion command | `Forward Propulsion & Wing Beat Amplitude` | **HIGH** | Rayshubskiy et al. 2020 |
| **DNg11** (6 cells) | Front leg strike / defensive punch descending neuron | `Front Leg Strike / Agonistic Actuator` | **HIGH** | Zacarias et al. 2018 |
| **DNg110_a** (6 cells) | Front leg strike / defensive punch descending neuron | `Front Leg Strike / Agonistic Actuator` | **HIGH** | Zacarias et al. 2018 |
| **DNg110_b** (6 cells) | Front leg strike / defensive punch descending neuron | `Front Leg Strike / Agonistic Actuator` | **HIGH** | Zacarias et al. 2018 |
| **DNg111** (2 cells) | Front leg strike / defensive punch descending neuron | `Front Leg Strike / Agonistic Actuator` | **HIGH** | Zacarias et al. 2018 |
| **DNg12_a** (8 cells) | Head and antennal grooming descending neuron | `Antennal & Head Grooming Actuator` | **HIGH** | Seeds et al. 2014 |
| **DNg12_b** (16 cells) | Head and antennal grooming descending neuron | `Antennal & Head Grooming Actuator` | **HIGH** | Seeds et al. 2014 |
| **DNg12_c** (5 cells) | Head and antennal grooming descending neuron | `Antennal & Head Grooming Actuator` | **HIGH** | Seeds et al. 2014 |
| **DNg12_d** (4 cells) | Head and antennal grooming descending neuron | `Antennal & Head Grooming Actuator` | **HIGH** | Seeds et al. 2014 |
| **DNg12_e** (6 cells) | Head and antennal grooming descending neuron | `Antennal & Head Grooming Actuator` | **HIGH** | Seeds et al. 2014 |
| **DNp01** (2 cells) | Giant Fiber descending escape neuron driving rapid jump takeoff | `Giant Fiber Emergency Jump Takeoff` | **HIGH** | Tanouye & Wyman 1980, Allen et al. 2006 |
| **DNp02** (2 cells) | Landing and approach deceleration descending neuron | `Landing Deceleration & Leg Extension` | **HIGH** | Ache et al. 2019 |
| **DNp09** (2 cells) | Visually guided forward flight acceleration descending neuron | `Forward Acceleration Actuator` | **HIGH** | Suver et al. 2016 |
| **DVMn 1a-c** (6 cells) | Dorsoventral flight motor neurons (wing upstroke power) | `Upstroke Wing Power Actuator` | **HIGH** | Tanouye & King 1983 |
| **DVMn 2a, b** (4 cells) | Dorsoventral flight motor neurons (wing upstroke power) | `Upstroke Wing Power Actuator` | **HIGH** | Tanouye & King 1983 |
| **DVMn 3a, b** (4 cells) | Dorsoventral flight motor neurons (wing upstroke power) | `Upstroke Wing Power Actuator` | **HIGH** | Tanouye & King 1983 |
| **Fe reductor MN** (20 cells) | Femur reductor motor neuron controlling leg yaw orientation | `Femur Yaw Orientation Actuator` | **HIGH** | Cruse 1990 |
| **JO-A** (24 cells) | Johnston's organ high-frequency sound receptor | `Acoustic / Vibration JO-A` | **HIGH** | Göpfert & Robert 2002 |
| **JO-A1** (8 cells) | Johnston's organ high-frequency sound receptor | `Acoustic / Vibration JO-A` | **HIGH** | Göpfert & Robert 2002 |
| **JO-A2** (13 cells) | Johnston's organ high-frequency sound receptor | `Acoustic / Vibration JO-A` | **HIGH** | Göpfert & Robert 2002 |
| **JO-A3** (2 cells) | Johnston's organ high-frequency sound receptor | `Acoustic / Vibration JO-A` | **HIGH** | Göpfert & Robert 2002 |
| **JO-A4** (3 cells) | Johnston's organ high-frequency sound receptor | `Acoustic / Vibration JO-A` | **HIGH** | Göpfert & Robert 2002 |
| **JO-B** (13 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B1_a** (17 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B1_b** (12 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B1_c** (10 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B2** (9 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B3** (12 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B4_a** (3 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-B4_b** (12 cells) | Johnston's organ courtship song receptor | `Acoustic Pulse JO-B` | **HIGH** | Tootoonian et al. 2012 |
| **JO-CA1** (10 cells) | Johnston's organ vibration/sound and steady airflow receptor | `Antennal Wind Airflow JO-C` | **HIGH** | Kamikouchi et al. 2009, Yorozu et al. 2009 |
| **JO-CA2** (9 cells) | Johnston's organ vibration/sound and steady airflow receptor | `Antennal Wind Airflow JO-C` | **HIGH** | Kamikouchi et al. 2009, Yorozu et al. 2009 |
| **JO-CL** (19 cells) | Johnston's organ vibration/sound and steady airflow receptor | `Antennal Wind Airflow JO-C` | **HIGH** | Kamikouchi et al. 2009, Yorozu et al. 2009 |
| **JO-CM** (30 cells) | Johnston's organ vibration/sound and steady airflow receptor | `Antennal Wind Airflow JO-C` | **HIGH** | Kamikouchi et al. 2009, Yorozu et al. 2009 |
| **JO-ED1** (18 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-ED2_a** (38 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-ED2_b** (21 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-ED2_c** (14 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV1** (50 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV2** (36 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV3** (45 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV4** (1 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV5** (23 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **JO-EV6** (21 cells) | Johnston's organ gravity and steady wind deflection receptor | `Antennal Gravity/Wind JO-E` | **HIGH** | Matsuo et al. 2014, Patella & Wilson 2018 |
| **KC** (2 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCa'b'-ap1** (2 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCab** (1681 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCab-p** (129 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCapbp-ap1** (197 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCapbp-ap2** (291 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCapbp-m** (205 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCg** (1 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCg-d** (206 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCg-m** (1346 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCg-s1** (2 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **KCg-s2** (2 cells) | Kenyon cells encoding sparse multi-modal associative odor representations | `Sparse Multi-modal Odor Context` | **HIGH** | Aso et al. 2014 |
| **LC10_unclear** (11 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10a** (275 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10b** (95 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10c** (255 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10d** (214 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10e** (110 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC10f** (4 cells) | Visual small-object / target tracking projection neuron | `LC10 Target Azimuth & Elevation` | **HIGH** | Ribeiro et al. 2018, Sten et al. 2021 |
| **LC4** (126 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC40** (34 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC41** (13 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC43** (14 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC44** (5 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC45** (23 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC46** (12 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LC9** (219 cells) | Optic flow / translation motion projection neuron | `LC9 Retinal Optic Flow` | **HIGH** | Städele et al. 2020 |
| **LPLC2** (185 cells) | Visual looming detector sensitive to expanding radial edges | `LC4/LPLC2 Retinal Looming` | **HIGH** | Klapoetke et al. 2017 |
| **LPLC4** (97 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **LgAG1** (25 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG2** (11 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG3** (6 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG4** (8 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG5** (4 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG6** (4 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG7** (5 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG8** (9 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgAG9** (3 cells) | Leg chordotonal organ proprioceptors | `Leg Joint Angle Proprioception` | **HIGH** | Maniates-Selvin et al. 2020 |
| **LgLG1a** (136 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG1b** (134 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG2** (130 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG3** (162 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG4** (43 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG5** (13 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG6** (16 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG7** (21 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **LgLG8** (14 cells) | Leg campaniform sensilla and chordotonal mechanoreceptors (T1-T3) | `6-Leg Ground Contact & Load Mechanoreceptors` | **HIGH** | Tuthill & Wilson 2016, Mamiya et al. 2018 |
| **MBON01** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON02** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON03** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON04** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON05** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON06** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON07** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON09** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON10** (9 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON11** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON12** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON13** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON14** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON15** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON15-like** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON16** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON17** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON17-like** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON18** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON19** (4 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON20** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON21** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON22** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON23** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON24** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON25,MBON34** (7 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON25-like** (1 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON26** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON27** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON28** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON29** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON30** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON31** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON32** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON33** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MBON35** (2 cells) | Mushroom body output neurons driving learned approach and avoidance | `Learned Valence (Appetitive / Aversive)` | **HIGH** | Aso et al. 2014 |
| **MDN** (4 cells) | Moonwalker descending neuron commanding backward walking and flight braking | `Backward Locomotion & Brake Actuator` | **HIGH** | Bidaye et al. 2014 |
| **MN10** (3 cells) | Labellar motor neuron driving proboscis extension response (PER) | `Proboscis Extension Actuator` | **HIGH** | Gordon & Scott 2009, McKellar 2020 |
| **ORN_DL5** (43 cells) | Ripening fruit alcohol volatile receptor | `Bilateral Ripening Alcohol Odor Field` | **HIGH** | Ebrahim et al. 2015 |
| **ORN_DM1** (74 cells) | Apple/fruit volatile receptor (ethyl acetate / cider vinegar) | `Bilateral Ethyl Acetate Odor Field` | **HIGH** | Semmelhack & Wang 2009 |
| **ORN_DM2** (54 cells) | Fruit ester odor receptor (ethyl butyrate) | `Bilateral Ethyl Butyrate Odor Field` | **HIGH** | Stensmyr et al. 2012 |
| **ORN_DM4** (32 cells) | Fermentation volatile receptor (acetic acid) | `Bilateral Fermentation Odor Field` | **HIGH** | Ai et al. 2010 |
| **ORN_DP1m** (31 cells) | General fruit aldehyde volatile receptor | `Bilateral Volatile Aldehyde Odor Field` | **HIGH** | Dweck et al. 2015 |
| **PAM01** (44 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM02** (17 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM03** (12 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM04** (32 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM05** (20 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM06** (28 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM07** (14 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM08** (50 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM09** (9 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM10** (15 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM11** (15 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM12** (22 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM13** (16 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM14** (18 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PAM15** (4 cells) | Dopaminergic reward neurons reinforcing appetitive food odor memories | `Appetitive Nutrient Ingestion Reward` | **HIGH** | Burke et al. 2012, Liu et al. 2012 |
| **PFL3** (24 cells) | Goal-directed steering descending projection neurons | `Central Complex Steering Bias` | **HIGH** | Rayshubskiy et al. 2020, Hulse et al. 2021 |
| **PPL101** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL102** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL103** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL104** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL105** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL106** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL107** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **PPL108** (2 cells) | Dopaminergic punishment neurons reinforcing aversive threat memories | `Aversive Predator Strike Punishment` | **HIGH** | Claridge-Chang et al. 2009, Aso et al. 2012 |
| **Ta depressor MN** (9 cells) | Tarsus depressor motor neuron securing claw adhesion to substrate | `Tarsal Substrate Grip Actuator` | **HIGH** | Radnikow & Bässler 1991 |
| **Ta levator MN** (5 cells) | Tarsus levator motor neuron releasing substrate grip | `Tarsal Release Actuator` | **HIGH** | Groll et al. 2014 |
| **Ti extensor MN** (12 cells) | Tibia extensor motor neuron driving leg extension and pushing | `Tibia Extension Actuator` | **HIGH** | Bässler 1983, Tuthill & Wilson 2016 |
| **Ti flexor MN** (37 cells) | Tibia flexor motor neuron driving leg flexion and stance pull | `Tibia Flexion Actuator` | **HIGH** | Ache et al. 2019 |
| **Tr extensor MN** (11 cells) | Trochanter extensor motor neuron driving femur depression | `Trochanter Stance Extensor` | **HIGH** | Burrows 1996 |
| **Tr flexor MN** (35 cells) | Trochanter flexor motor neuron driving leg swing lift | `Trochanter Swing Levator` | **HIGH** | Mamiya et al. 2018 |
| **b1 MN** (2 cells) | Basalar steering muscle 1 motor neuron (wing stroke amplitude) | `Wing Stroke Amplitude Actuator` | **HIGH** | Dickinson & Tu 1997 |
| **b2 MN** (2 cells) | Basalar steering muscle 2 motor neuron (wing stroke pitch angle) | `Wing Pitch Angle Actuator` | **HIGH** | Dickinson et al. 1993 |
| **hDVM MN** (2 cells) | Haltere dorsoventral motor neuron (haltere oscillation) | `Haltere Oscillatory Stabilizer` | **HIGH** | Chan et al. 1998 |
| **hi1 MN** (2 cells) | First axillary sclerite steering motor neuron (stroke deviation) | `Wing Stroke Deviation Actuator` | **HIGH** | Balint & Dickinson 2001 |
| **hi2 MN** (4 cells) | Second axillary sclerite steering motor neuron | `Wing Sclerite Deflection Actuator` | **HIGH** | Tu & Dickinson 1996 |
| **hiii2 MN** (2 cells) | Second axillary sclerite steering motor neuron | `Wing Sclerite Deflection Actuator` | **HIGH** | Tu & Dickinson 1996 |
| **i1 MN** (2 cells) | First axillary sclerite steering motor neuron (stroke deviation) | `Wing Stroke Deviation Actuator` | **HIGH** | Balint & Dickinson 2001 |
| **i2 MN** (2 cells) | Second axillary sclerite steering motor neuron | `Wing Sclerite Deflection Actuator` | **HIGH** | Tu & Dickinson 1996 |
| **iii1 MN** (2 cells) | First axillary sclerite steering motor neuron (stroke deviation) | `Wing Stroke Deviation Actuator` | **HIGH** | Balint & Dickinson 2001 |
| **mALC4** (2 cells) | Visual looming detector responding to expanding dark discs/predators | `LC4/LPLC2 Retinal Looming` | **HIGH** | von Reyn et al. 2014, Ache et al. 2019 |
| **pIP10** (2 cells) | Defensive rear-leg kick descending neuron | `Defensive Rear Leg Kick Actuator` | **HIGH** | von Philipsborn et al. 2011 |
| **ps1 MN** (2 cells) | Pleurosternal muscle motor neuron (wing beat tension) | `Thoracic Wingbeat Resonance Actuator` | **HIGH** | Nachtigall & Wilson 1967 |
| **CB0007,CB0739** (12 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0336,CB0796** (8 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0700** (3 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0701** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0703** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0704** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0705** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0706** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0707** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0708** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0709** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0710** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0713** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0715** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0716** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0717** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0718** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0719,CB2276** (6 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0720** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0721** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0722** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0723** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0724** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0727a** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0727b** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0727c** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0727d** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0728** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0731** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0732** (8 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0733** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0734** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0736** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0737** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0738** (11 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0740** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0743** (10 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0744** (5 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0746** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0747** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0749** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0750** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0751** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0752** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0753** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0754** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0755** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0756** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0757** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0758** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0759** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0761** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0762** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0763** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0765** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0766** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0768** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0769** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0770** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0771** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0772** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0773** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0774** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0775** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0778** (1 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0779** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0781** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0783** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0784** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0785** (3 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0786** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0787** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0788** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0789** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0791** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0792** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0795** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0797** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0798** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB0799** (2 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **CB3444,CB0793** (4 cells) | Subesophageal zone proboscis and rostrum motor neurons | `Proboscis Articulation Actuators` | **MEDIUM** | Hampel et al. 2020 |
| **LC11** (143 cells) | Small moving target detector | `Visual Small Object Detector` | **MEDIUM** | Keleş & Frye 2017 |
| **LPLC1** (134 cells) | Visual motion parallax and wide-field flow | `Widefield Optic Flow` | **MEDIUM** | Busch et al. 2018 |
