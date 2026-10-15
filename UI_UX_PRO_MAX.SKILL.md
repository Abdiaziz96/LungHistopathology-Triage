# UI/UX Pro Max — Design Intelligence (DSH Skill)

## Source
Originally `ui-ux-pro-max` Claude Code plugin (v2.13.0, MIT, NextLevelBuilder).
Local source: `C:\Users\Abdurrahman\Downloads\ui-ux-pro-max-skill-main\`
Original install: `npx ui-ux-pro-max-cli init --ai dsh` (BLOCKED — npm scripts disabled, approval=never).

## What It Provides
Searchable local UI/UX guidance:
- 79 UI styles (50 active)
- 192 product palettes + reasoning profiles
- 74 font pairings
- 119 UX guidelines
- 105 curated icons
- 17 GSAP animation presets
- 25 chart types
- 22 technology stacks

## When to Apply
Use this Skill when the task involves **UI structure, visual design, interaction patterns, or UX quality**:
- Designing new pages / components
- Choosing color / typography / spacing / layout systems
- Reviewing UI for accessibility, consistency
- Implementing navigation, animation, responsive behavior
- Improving perceived quality and usability

Skip for: pure backend logic, API/DB design, infrastructure/DevOps.

## Rule Categories (Priority 1→10)

| Pri | Category | Domain | Key Checks | Anti-Patterns |
|-----|----------|--------|------------|---------------|
| 1 | Accessibility | `ux` | Contrast 4.5:1, Alt text, Keyboard nav, Aria-labels | Removing focus rings, Icon-only without labels |
| 2 | Touch & Interaction | `ux` | Min 44×44px, 8px+ spacing, Loading feedback | Hover-only, Instant 0ms changes |
| 3 | Performance | `ux` | WebP/AVIF, Lazy load, CLS < 0.1 | Layout thrashing, unreserved space |
| 4 | Style Selection | `style`,`product` | Match product type, SVG icons (no emoji) | Mixing flat & skeuomorphic, emoji as icons |
| 5 | Layout & Responsive | `ux` | Mobile-first, Viewport meta, No horizontal scroll | Fixed px widths, disable zoom |
| 6 | Typography & Color | `typography`,`color` | Base 16px, Line-height 1.5, Semantic tokens | Text < 12px body, gray-on-gray, raw hex |
| 7 | Animation | `ux`,`gsap` | Context-aware timing, Spatial continuity, reduced-motion | One duration for all, animate width/height |
| 8 | Forms & Feedback | `ux` | Visible labels, Error near field, Helper text | Placeholder-only labels, errors at top only |
| 9 | Navigation | `ux` | Predictable back, Bottom nav ≤5, Deep links | Overloaded nav, broken back |
| 10 | Charts & Data | `chart` | Legends, Tooltips, Accessible colors | Color-only meaning |

## Search Tool (DSH usage)

The search script is at:
```
C:\Users\Abdurrahman\Downloads\ui-ux-pro-max-skill-main\ui-ux-pro-max-skill-main\.claude\skills\ui-ux-pro-max\scripts\search.py
```

Run from PowerShell with the project venv Python (no external deps, Python 3.x only):
```powershell
& "C:\Users\Abdurrahman\Documents\DeepSeekHarness-Projects\LungHistopathology-Triage\.venv\Scripts\python.exe" "<path-to-search.py>" "<query>" --domain <domain>
```

### Domain Search
- `product` — Product type recommendations (SaaS, e-commerce, dashboard)
- `style` — UI styles (glassmorphism, minimalism, brutalism) + AI prompts + CSS
- `typography` — Font pairings with Google Fonts imports
- `color` — Color palettes by product type
- `landing` — Page structure & CTA strategies
- `chart` — Chart types & library recommendations
- `ux` — Best practices & anti-patterns
- `icons` — Phosphor, Heroicons, Lucide imports
- `react` — React/Next.js performance patterns
- `web` — iOS/Android/React Native guidelines
- `google-fonts` — Individual Google Fonts lookup
- `gsap` — GSAP animation skeletons (hover, scroll, stagger, page transition, parallax, loading)

### Design System Search (REQUIRED for new pages)
```powershell
& python "<search.py>" "<product_type> <industry> <keywords>" --design-system -p "Project Name"
```
Returns: pattern, style, colors, typography, effects, anti-patterns.

### Design Dials (optional)
- `--variance <1-10>` — centered/minimal → bold/asymmetric
- `--motion <1-10>` — subtle → standard → complex choreography
- `--density <1-10>` — spacious → standard → dense/dashboard

### Stack Search
```powershell
& python "<search.py>" "<keyword>" --stack <stack>
```
Stacks: `react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `nuxt-ui`, `angular`, `laravel`, `swiftui`, `react-native`, `flutter`, `jetpack-compose`, `html-tailwind`, `shadcn`, `threejs`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`.

## Workflow

### Step 1: Analyze
- **Product type**: SaaS, e-commerce, portfolio, dashboard, entertainment, tool
- **Audience & context**: age group, commute/leisure/work
- **Style keywords**: playful, vibrant, minimal, dark mode, content-first
- **Stack**: check `package.json` deps; this project has **FastAPI backend + Wix template HTML** (no JS framework detected — use `html-tailwind`)

### Step 2: Generate Design System
For new pages, run `--design-system` first.

### Step 3: Supplement with Detail
Use targeted `--domain` queries for specific concerns (contrast, focus, animation timing).

### Step 4: Stack Guidelines
Run `--stack <stack>` for implementation specifics.

## If 0 Results
1. Retry once with narrower query or explicit domain
2. Fall back to priority table defaults
3. State explicitly that the recommendation came from defaults, not a database match
4. **Never** present 0 results as data

## Output Formats
- `-f ascii` (default)
- `-f markdown`
- `--json` (machine-readable)

## Application to Lung Histopathology Triage Project

This workspace already has:
- `api.py` (FastAPI backend) — no UI framework
- `wix_template_raw.html` (Wix template, handyman design)
- `template_preview.jpg` (visual reference)

To design the **NHS triage dashboard**:
1. `python search.py "medical clinical dashboard triage" --design-system -p "LungTriage"` 
2. `python search.py "healthcare color palette trust" --domain color`
3. `python search.py "medical chart accuracy accessible" --domain chart`
4. `python search.py "tailwind form upload" --stack html-tailwind`

## Tip
Keep one dominant intent and 2-5 meaningful terms per query. Retry once with narrower phrase. Pass stack explicitly.

## Why Not Running It
- `npx ui-ux-pro-max-cli init` requires `npm` (blocked by PowerShell `ExecutionPolicy`)
- Approval policy is `never` — no escalation possible
- Python script can be invoked directly if needed (no install required)
