# NoCatch feature map

This is a map of the shipped static app, not a feature wish list. Use it to locate a control or reproduce a vague bug report. The production entry point is `index.html`; GitHub Pages serves the same file at https://aeiouvcode.github.io/nocatch/. There is no backend or account.

| Feature | Where to find it | How to trigger it | State and expected result |
| --- | --- | --- | --- |
| Top navigation | Header: Directory, Method, Refresh log | Follow an anchor link or scroll | Opens the corresponding section on the same page (`#directory`, `#method`, `#refresh`). |
| Script unavailable | Above Directory | Open the page with JavaScript disabled | An explanation says listings cannot load and links to the method and refresh criteria. No fake empty dataset is shown. |
| Browser tab identity | `<head>` of `index.html` | Load the directory | Descriptive title and meta description; local `favicon.svg` supplies the tab icon. |
| Not-found page | `404.html` on GitHub Pages | Visit a missing path under `/nocatch/` | A branded, noindex 404 links back to the directory; this is a standalone static page. |
| Coverage metrics | Hero, below the introduction | Load the page | Tool, category and distinct valid official-source counts are computed from the embedded `D` dataset; paid placements are shown as zero. |
| Data-check status | Header at upper right | Load the page | Displays the latest parsed `CHECKED` date among listings. A listing's own checked date is shown on its card. |
| Category selection | Chip strip above the directory results | Tap a category or All; horizontally scroll the strip on narrow screens | Filters cards by category. Selected chip uses a pressed state and is scrolled into view if the strip overflows. |
| Search | Search field above category chips | Type a term from a tool's name, category, description, offer, license, limit or risk | Substring match is case-insensitive; results update as you type. Search text is not sent to a server. |
| Surprise me | Button beside search | Tap the button | Selects a random listing, filters to its category and name, then scrolls to the directory. |
| Filters and sort panel | `Filters & sort` disclosure below category chips | Open the disclosure; on desktop it opens automatically | Access, license, card, freshness, saved view and sort live inside. An active-filter count appears beside the heading. |
| Access filter | Filters and sort > Access | Choose All, Free, Freemium, Trial or Paid | Access class is derived from the listing offer and limit text. Trial access is separate from a lasting free tier. |
| License filter | Filters and sort > License | Choose All, Open, Source available or Closed | Class is derived from the listing's license label; the card retains its fuller label. |
| Card filter | Filters and sort > Card | Choose All, No card, Card required or Not stated | Class is parsed from `Card:` in the listing's dated limit field; absent, prose-only or unclear status stays Not stated. |
| Freshness filter | Filters and sort > Freshness | Choose All dates, Last 7 days or Older checks | Uses the parsed check date and the browser's current local date. Cards older than 30 days receive a stale marker. |
| Saved view | Filters and sort > View | Choose Saved | Shows only cards saved in this browser. An empty saved view uses the same empty-result state. |
| Sort | Filters and sort > Sort | Choose Category, A-Z or Recently checked | Reorders matching cards without changing the underlying dataset. |
| Result count and empty state | Above and inside the card grid | Change search or filters until results change or none match | Count reads `matching of total tools`; an empty state describes the gap and offers Clear filters. Saved view with no saved tools explains how to add one. |
| Reset | Empty-result Clear filters button | Tap Clear filters | Restores all category, search, filter and sort defaults. The button appears in the empty state, not persistently. |
| Listing detail | Each result card | Read card | Shows category, check date, offer/access, license, dated real limit, main catch and an official-source link. |
| Official source | Each card's `Official source` link | Open link | HTTPS links open in a new tab. Invalid source URLs are not clickable. Vendor pages can change after the shown check date. |
| Save feedback and storage error | Below search, above category chips | Tap a star, or open the page where local browser storage is disabled | Accessible status text confirms a saved/removed tool. If storage is unavailable, it says saves may not persist. No stack trace is exposed. |
| Save/unsave | Star at bottom right of each card | Tap star, then optionally select Saved view | Toggles the listing name in browser `localStorage` (`nocatch-saved`); stays on this device/browser, not shared. The star has a pressed state and accessible label. |
| Shareable filter state | URL hash after using controls | Copy the URL with `#cat=...`, `q=...`, or other parameters; open it directly | Current non-default selections go into the hash. On page load, invalid category/select values fall back to defaults. Saving stars is not shared by URL. |
| Method | Method section, linked in header | Scroll or follow Method | Explains source, license, date and local-first policies. |
| Refresh loop and coverage roadmap | Refresh log section, linked in header | Scroll or follow Refresh log | Describes recheck criteria and the 100 / 250 tool coverage targets; it is explanatory, not an automated refresh job. |

## Source and QA entry points

- Dataset and browser logic: inline script in `index.html`. Each `D` row is `[category, name, description, offer, license, dated limit and card text, catch, official URL]`. Source links should be checked against the vendor before editing rows.
- Layout, phone breakpoint, pressed/focus/reduced-motion states and CSP: inline CSS and CSP meta tag in `index.html`. Any CSS/JS edit must regenerate the matching SHA-256 CSP hash; check the browser console for CSP failures.
- Run locally with `python3 -m http.server 8000`, then open `http://localhost:8000/`. Check the directory at 390px first, then desktop, and exercise controls, filtered and unsaved empty states, save success/storage failure, direct hash URLs and source links. Check the favicon, real page title and description, JavaScript-disabled notice, and visit a missing path on Pages for the branded 404. No placeholders or raw traces belong in user-visible states. A screenshot alone does not prove interaction behavior.
- `scripts/check.py` enforces metadata, local favicon, 404 page and critical feature states in CI; `README.md` is the short public project overview; `docs/screenshot.jpg` is an existing project image.
