# Make it yours: style.json

Every Rocha Coded tool reads one style file.
Make it once and every tool wears your look.
Rocha's look ships as the example, so you can see a finished one.

## Where it lives
The tools look in this order and use the first one they find:
1. a file you name with `--style path/to/style.json`
2. `style.json` in the folder you're working in (your Cowork folder, or where you run Claude Code)
3. `~/.rocha-coded/style.json`, for one style across every project
4. the bundled example, `examples/style.rocha-coded.json`

Anything you leave blank falls back to the example. Start from `style.example.json`.

## The keys
| Key | What it is | Used in Analog Bag |
|---|---|---|
| `name` | Your brand or studio name | printed when a page renders |
| `owner` | Your name | not yet |
| `handle` | Your Instagram or social handle | card backs, launch page, week page |
| `site` | Your website | not yet |
| `palette.hero` | Your loudest colour | mastheads, labels |
| `palette.accent` | The soft version of it | page lines, card names |
| `palette.paper` | Plain paper | page backgrounds |
| `palette.paper_pink` | Tinted paper | lined paper |
| `palette.ink` | Text | text, tick boxes |
| `palette.marker` | Your pen colour | scrawls, the margin line |
| `palette.plum` | A deep dark | card fronts and backs, moon strips |
| `palette.gold` | A metallic or bright line colour | card art, moons |
| `palette.cool` | A rare cool accent | not yet |
| `fonts.masthead` | Big headlines | card names, THIS WEEK, the offer name |
| `fonts.label` | Small caps labels | tags |
| `fonts.body` | Reading text | card text, beats |
| `fonts.scrawl` | Handwriting | the to-do line, card-back stamp |
| `fonts.mono` | Typewriter | dates on the launch page |
| `motif` | `guest-check`, `front-page`, `magazine-scrawl`, `pink-paper`, `sticker-collage`, `rotary`, `leopard`, `retro-tv` or `neutral` | not yet |
| `lines.todo` | Your to-do line | top of the week page |
| `lines.stamp` | One big word | card backs |
| `lines.scrawl` | Your handwritten line | card backs, launch page footer |
| `lines.masthead`, `headline`, `celebrate`, `affirm` | More of your words | other Rocha Coded tools |
| `references` | Images or links Claude looks at when you say "make it mine" | read by Claude, not the scripts |
| `notes` | Your taste in a sentence or two | read by Claude |

Colours are `#RRGGBB`. Fonts are Google Fonts names, like `Cormorant Garamond`. A font that isn't on Google Fonts falls back to a system font. A colour or font name that looks wrong is skipped, and the example's value is used instead.

Your own words go in `lines`. Leave a line blank and that spot uses the example's line.
