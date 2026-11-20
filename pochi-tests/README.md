# Verification

Windows, November 21, 2026. Browser checks used Chromium for Testing 151.0.7922.34 and disposable, signed-out profiles. The public desktop source was pinned to `fa0bbf8c8676580e3afbbd0c30688a5180827bbf`.

[14-second browser recording](./pochi-on-github.mp4) · [Pochi reading at the contribution calendar](./calendar.png)

| Check | Evidence |
| --- | --- |
| Desktop locomotion | `npm run check` in the pinned desktop checkout passed syntax checks and 57 renderer regression tests. These exercise the renderer in a Node harness. No manual Electron, battery or OS activity test was performed. |
| Character identity | SHA-256 compared every one of the 16 bundled PNGs against the pinned original. All matched. Source and browser images were inspected visually. |
| Browser locomotion | Five Node tests passed for the port’s stride, facing, acceleration, braking, short trips and bounded time steps. The live recording shows horizontal movement across the profile. |
| Page interactions | Checked scrolling, resizing from 1280 × 870 to 900 × 660, pointer hit testing through the sprite, a repository link, Back, profile query tabs and absence on direct repository and unrelated account loads. With the extension absent the original GIF decoded and the R&D disclosure opened. |
| Context | The signed-out profile loaded its own contribution fragment. Pochi’s seated book sprite was decoded and observed at a real calendar edge. No activity events were inferred. |
| Accessibility | Keyboard Space toggled the settings switch. Hiding/showing took effect on the profile. Reminder opt-in survived a settings reload. Reduced motion produced the same position and pose throughout a three-second sample with zero active shadow-root animations. |
| Closing and hiding | A separate native Chromium tab test observed real `hidden` and `visible` states, zero sprite subtree mutations for 4.5 seconds hidden, updates after return, and destruction of the closed profile target. The manifest declares no background process. |
| Rare interactions | A local Chromium fixture supplied repeatable timing. Twenty-one hidden minutes produced no reminder. Active time allowed “Had water?” and subsequently a stretch break. The bubbles fit the viewport and passed pointer events through. The fixture also exercised seated reading and same-document departure/return. |

## Performance sample

In a one-second interval during a live walk, Chromium reported 31 style recalculations, **0 layouts** and **10.7 ms of script time** across the page. During a three-second reduced-motion sample it reported **0 style recalculations**, **0 layouts** and script time rounded to **0.0 ms**. The total main-thread task durations were 108.5 ms and 3.2 ms respectively. The timings include GitHub’s own work. They describe this machine and these short samples, and do not establish a sustained CPU percentage or memory budget.

## Repeat the checks

From the profile repository root, use Node 22 or newer and Python 3.10 or newer. For Playwright, install the Python package and its Chromium binary. For the native visibility check, set `CHROMIUM_EXECUTABLE` to the full path of Chromium for Testing. The scripts create temporary profiles and write the evidence into `POCHI_EVIDENCE` or the local `pochi-evidence` directory.

```text
node --test pochi-tests/gait.test.js
python -m pip install playwright
python -m playwright install chromium
python pochi-tests/live.py
python pochi-tests/interactions.py
python pochi-tests/fixture.py
node pochi-tests/visibility.js
```

The live checks require network access and GitHub’s current markup. GitHub’s calendar can load after the initial page. Calendar screenshots depend on a real visit to that landmark. The deterministic fixture covers cooldowns and calendar behavior independently of public-site timing. Edge and Firefox were not browser-tested.
