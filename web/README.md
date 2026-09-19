# qscreen-filing-tool marketing site

Static site deployed to Vercel. No build step, no npm install, no framework
runtime. Three pages plus 404:

| Page | File | What |
|---|---|---|
| `/` | `index.html` | Hero + 3 bets + bench + install + supply chain + kit + final CTA |
| `/whitepaper.html` | `whitepaper.html` | Embedded whitepaper PDF viewer + download CTA |
| `/one-pager.html` | `one-pager.html` | Embedded investor one-pager + sponsor tiers |
| `/404.html` | `404.html` | Static fallback for missing routes |

## Why static + no build step

- Marketing content changes once a quarter; rebuilding on every push adds
  latency for zero benefit.
- The hero video and whitepaper are embedded via `iframe`/`video` tags
  pointing at the GitHub repo's `main` branch — single source of truth.
- Total page weight (excluding the embedded video + iframe) is ~50 KB
  gzipped. Vercel's edge serves it in <100 ms globally.

## Local preview

```bash
cd web
python3 -m http.server 8080
open http://localhost:8080
```

## Deploy

```bash
cd web
vercel --prod --yes
```

First deploy will prompt for project name; subsequent deploys are
non-interactive. Output URL is `<project>.vercel.app`.
