<div align="center">

# Susan

### Prospective AI / Computer Science Undergraduate

**Interested in trustworthy machine learning, physiological AI, language technology, and research-oriented software systems.**

`Python` · `Machine Learning` · `TypeScript` · `Next.js` · `Computer Vision` · `Research Engineering`

</div>

---

## About

I’m **Susan**, an incoming undergraduate student from India preparing to study **Artificial Intelligence / Computer Science**.

I like working on problems where building the model is only part of the challenge. I’m especially interested in **how models fail, how uncertainty should be communicated, how evaluation can accidentally become misleading, and how research ideas can be turned into usable systems**.

Most of my current work falls into two directions:

**Research-oriented ML**
- uncertainty and conformal prediction
- subject variability in physiological signals
- leakage-safe evaluation and calibration
- scientific / biomedical applications of machine learning

**Applied AI systems**
- language-learning technology
- education and community platforms
- computer vision interaction
- privacy-aware full-stack products

---

## Research Questions I’m Exploring

- **Can uncertainty guarantees remain reliable for individual subjects when population averages hide difficult cases?**
- **How does personalization change calibration and selective prediction in physiological ML?**
- **When does an apparently better model metric hide a worse failure mode?**
- **How can AI systems expose limitations and provenance instead of presenting every prediction as equally trustworthy?**

These questions currently shape much of what I build and read.

---

## Selected Research Work

<table>
<tr>
<td width="50%" valign="top">

### [bioconformal](https://github.com/sushan5140/bioconformal)

**Subject-conditional conformal prediction for biosignal ML**

Explores distribution-free uncertainty for ECG, PPG, HRV and EDA models, with particular attention to **per-subject coverage rather than population-average coverage**.

Highlights:
- Mondrian / subject-conditional calibration
- leakage-safe subject splitting
- worst-subject coverage analysis
- explicit insufficient-calibration handling
- synthetic multi-subject benchmarking with limitations documented

`Python` `Conformal Prediction` `Biosignals` `Statistical ML`

</td>
<td width="50%" valign="top">

### [pactstress](https://github.com/sushan5140/pactstress)

**Personalized calibration for wearable stress detection**

Studies whether physiological features should be interpreted relative to each subject’s own resting baseline instead of only through population statistics.

Highlights:
- Leave-One-Subject-Out evaluation
- WESAD validation
- subject-specific baseline calibration
- selective prediction / abstention
- documented failure cases where personalization and conformal calibration do **not** simply improve each other

`Python` `scikit-learn` `Wearable ML` `Signal Processing`

</td>
</tr>

<tr>
<td width="50%" valign="top">

### [DPP-4 Scaffold Conformal](https://github.com/sushan5140/dpp4-scaffold-conformal)

**Chemotype-aware uncertainty for molecular docking**

Combines structure-based virtual screening with scaffold-conditional conformal calibration to study whether pooled uncertainty estimates can fail on specific molecular families.

Highlights:
- AutoDock Vina pipeline
- Morgan fingerprints + Butina clustering
- pooled vs. Mondrian calibration
- bootstrap robustness analysis
- explicit discussion of small-group and docking limitations

`Python` `RDKit` `Docking` `Conformal Prediction`

</td>
<td width="50%" valign="top">

### Meno-J Falsification Engine

**Agentic framework for hypothesis generation, criticism and controlled falsification**

An ignorance-first research system for turning uncertain observations into competing explanations, explicit predictions and tests that can actually fail — rather than treating a persuasive LLM answer as a conclusion.

Core loop:
- evidence retrieval and independent reasoning
- strict filtering and pattern extraction
- competing / rival hypothesis generation
- critique and falsification
- executable or statistically testable checks
- working-theory revision after failures

Selected experimental evidence:
- **Experiment 4:** reduced **9 surviving explanations → 5 competing patterns → 10 distinguishing experiments**, backed by **8 validated primary sources**; every proposed experiment included an effect-size target and explicit failure condition
- **Experiment 5 (P4-F2):** **falsified** the finite-sample-only explanation; at `n=300`, a sparse-subgroup + inverse-probability + marginal setup retained a **0.7462 coverage gap** with **0.1538 minimum group coverage**, including **14 persistent-failure cells**
- **Experiment 6 (P4-F1):** confirmed a **structural failure** pattern; the safest tested pairing reached **0.0645 mean gap / 0.8656 minimum coverage / 0 persistent failures**, while inverse-probability + marginal remained the most dangerous at **0.4209 mean gap / 0.4838 minimum coverage**
- **Experiment 7 v4:** Q1 finished with **9 PASS / 1 SALVAGEABLE** and Q2 with **10 PASS**; Q3 preserved valid checkpoints when execution was blocked by a sandbox network restriction before an external API call

Reproducibility work also preserved **34 historical outputs byte-for-byte**, with manifest/hash checks, compilation checks and credential scanning completed during the architecture refactor.

`LLM Reasoning` `Falsification` `Evaluation` `Trustworthy AI`

</td>
</tr>
</table>

---

## Applied Systems

<table>
<tr>
<td width="50%" valign="top">

### [KMate](https://github.com/sushan5140/kmate)

**Community and preparation platform for GKS applicants**

A full-stack system built around structured applicant discovery, scholarship data, privacy-aware connections and moderation.

Technical areas I worked with:
- Next.js + TypeScript
- Supabase authentication and database flows
- access control and privacy-sensitive profile data
- structured scholarship / university data
- moderation and admin workflows

`Next.js` `TypeScript` `Supabase` `Full-stack`

</td>
<td width="50%" valign="top">

### [Manhua Lens](https://github.com/sushan5140/manhua-lens)

**Multilingual reading assistant for native web content**

A Chromium extension for word-level reading support across Korean, Japanese, Chinese and other languages.

Technical areas:
- Manifest V3 extension architecture
- offline dictionary lookup
- language-specific segmentation / hints
- browser text-to-speech
- explicit dictionary provenance documentation

`JavaScript` `Browser Extensions` `NLP` `Language Tech`

</td>
</tr>
</table>

---

## Research & Engineering Habits

I’m still early in my academic journey, so I care more about developing **good research habits** than trying to present myself as an expert.

I try to:

- separate **training, calibration and evaluation** correctly
- use subject-disjoint or LOSO evaluation when the research question requires it
- inspect **failure cases**, not only average metrics
- report when an approach makes results worse
- document assumptions and limitations
- keep upstream work and my own contribution clearly attributed
- make experiments reproducible enough that someone else can inspect the reasoning

---

## Tools I Currently Work With

<div align="center">

<img src="https://img.shields.io/badge/Python-111827?style=flat-square&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/scikit--learn-111827?style=flat-square&logo=scikitlearn&logoColor=white" />
<img src="https://img.shields.io/badge/NumPy-111827?style=flat-square&logo=numpy&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-111827?style=flat-square&logo=pandas&logoColor=white" />
<img src="https://img.shields.io/badge/OpenCV-111827?style=flat-square&logo=opencv&logoColor=white" />
<img src="https://img.shields.io/badge/TypeScript-111827?style=flat-square&logo=typescript&logoColor=white" />
<img src="https://img.shields.io/badge/Next.js-111827?style=flat-square&logo=nextdotjs&logoColor=white" />
<img src="https://img.shields.io/badge/Supabase-111827?style=flat-square&logo=supabase&logoColor=white" />

</div>

---

## What I’m Working Toward

My goal before and during undergraduate study is to strengthen the fundamentals behind the systems I already enjoy building — **machine learning, probability, algorithms, data structures, optimization, statistics and research methodology**.

I’m particularly interested in learning from researchers working on **trustworthy AI, biomedical / physiological ML, intelligent systems, language technology, and applied machine learning**.

<div align="center">

**Curious enough to build · careful enough to question the result**

</div>
