# Pochi on Susan’s GitHub profile

Pochi walks across the profile, pauses on section edges, reads near the contribution calendar and sometimes dozes off. The ordinary profile keeps its animated preview.

## Install

1. [Download the profile repository ZIP](https://github.com/sushan5140/sushan5140/archive/refs/heads/main.zip) and extract it to a folder you plan to keep.
2. Open `chrome://extensions` in Chrome or `edge://extensions` in Edge. Enable **Developer mode** and select **Load unpacked**.
3. Choose the **pochi-extension** folder containing `manifest.json`. Open or refresh [Susan’s profile](https://github.com/sushan5140).
4. Open **Pochi on Susan’s profile** in the browser’s Extensions menu to hide her or enable gentle break reminders. Both switches support the keyboard.

Reduced motion parks Pochi. Reminders start disabled and become eligible after 20 visible minutes on the profile. Pochi can ask “Had water?” without assuming who is visiting or what they have done. Removing the extension in the browser removes its local preferences.

## Where she can roam

| Approach | What a visitor sees | Installation |
| --- | --- | --- |
| Native profile README | An image can animate inside its own bounds. GitHub sanitizes the markup and strips scripts and inline styles. A README cannot host a page-wide overlay or an interactive iframe. | None |
| Browser extension or userscript | An installed content script can position the character across the GitHub interface and use visible landmarks. A userscript would require a userscript manager. | Each viewer installs their own copy |
| Separate hosted page | A visiting character can roam across that separate site. Following a link leaves the GitHub profile. | None |
| This hybrid | Everyone sees the README preview. People who install this extension also get Pochi on the actual profile. | Optional |

[GitHub’s markup pipeline](https://github.com/github/markup#github-markup) · [Chrome’s content-script documentation](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)

## How it works

The content script runs on the exact lowercase HTTPS profile path, including its trailing slash and query tabs. Its overlay lives in a shadow root. The sprite and bubbles pass pointer events through to GitHub. Visible borders near the calendar, repository cards and profile headings supply destinations. The viewport floor supplies a fallback when GitHub changes its layout or omits a section.

The browser port scales the desktop acceleration, braking envelope, stride lengths and distance-driven contact/passing cycle to the displayed sprite size. Horizontal walks mirror the side artwork. Depth changes use the original front and back frames. A direction reversal at the next departure has a short pivot. Idle choices include the original arms-crossed stance, a seated book, a pillow and a closed-eye doze.

Only two preferences use extension-local storage. The extension has no background worker, remote code, analytics, contribution API calls or access tokens. It reads nearby layout geometry in the current profile. No contribution celebration is generated. Closing the page releases its execution context. Navigating away tears down the overlay. Returning from a different GitHub page through a same-document navigation can require one refresh because the manifest only injects on a matching document. GitHub receives its usual page and image requests.

The manifest limits content-script injection to the profile paths. Its separate web-accessible-resource rule makes the bundled PNGs available on the GitHub origin, as required for extension images. It grants no additional script access.

## Source and verification

The 16 bundled PNGs are byte-for-byte copies from the [Pochi desktop source at fa0bbf8](https://github.com/sushan5140/Pochi/tree/fa0bbf8c8676580e3afbbd0c30688a5180827bbf/assets). The renderer actually selects `walk_cycle` for ordinary walking. Its `walk_cycle_v2` and `turnaround` collections were inspected during porting. Some filenames are misleading: the pillow pose has open eyes. The extension uses the actual closed-eye sleepy expression for dozing.

The [desktop intent scheduler](https://github.com/sushan5140/Pochi/blob/fa0bbf8c8676580e3afbbd0c30688a5180827bbf/main.js) chooses targets, coordinates interrupts, and sends pose, expression and dialogue over IPC. The [renderer](https://github.com/sushan5140/Pochi/blob/fa0bbf8c8676580e3afbbd0c30688a5180827bbf/renderer/renderer.js) integrates movement and advances frames from distance. The desktop memory store and stage-based dialogue depend on local history. The browser adaptation uses visible-session time and visitor-neutral lines.

See [browser and source checks](../pochi-tests/) for reproduction and measured results.
