# My Animation Wall

A single-page personal gallery of every animated movie and TV show I've watched, with ratings pulled from my Notion database. Each title gets a colorful generated "poster", and a taste-profile section charts what I rate highest.

No build step, no dependencies, no server: it's one file, [index.html](index.html).

## Run it

Open `index.html` in any modern browser:

```sh
open index.html
```

## Features

- **Poster wall**: every title is shown as a high-resolution movie/show poster with subtle cinematic hover zoom, gradient overlays for legible typography, and fallback color gradients.
- **Search**: filter by title as you type.
- **Type filter**: all, Movie, or TV Series.
- **Sort**: highest rated, lowest rated, A → Z, or most recently watched.
- **Tag chips**: click one or more genre/tag chips to narrow the wall (a title must have all selected tags).
- **🎲 Pick one for me**: picks a random title from whatever is currently showing. Click anywhere to close it.
- **📊 Taste profile**: summary stats (titles watched, average rating, perfect 10s) plus four charts:
  - average rating per tag (tags with 3+ titles, top 12)
  - distribution of scores
  - movies vs. shows (titles with no type are left out)
  - which platform I watch on (only titles with a platform set)

## Click a poster: notes + IMDb

Clicking a poster opens a pop-up with my rating, the IMDb rating and vote count, a link to IMDb, a link to the Notion page, and my notes from Notion, shown with Notion-style formatting (headings, bullets, underline, `code`, columns, callouts, images that have a public web address).

- All of that extra info lives in [data.js](data.js), loaded by `index.html` before the main script. It sets `window.DETAILS`, keyed by exact title: `{ notes, imdbUrl, imdbRating, imdbVotes, notionUrl }`. If `data.js` is missing the pop-up still opens with less info.
- `notes` holds the raw Notion page content (Notion-flavoured markdown). `renderNotion()` in `index.html` turns it into HTML.
- IMDb ratings come from IMDb's public ratings dataset (as of 2026-10-16), not live, so they are a snapshot.
- Images that were uploaded to Notion (rather than linked from the web) are not shown, since Notion only exposes them through temporary private links. Bookmark blocks are skipped for the same reason.
- Like the rest of the data, `data.js` is a copy and does not update when Notion changes.

## Posters & Images

- Posters are saved locally in the `posters/` folder so the wall works completely offline without broken links or third-party rate limits.
- To fetch posters for newly added titles in `RAW`, run:
  ```sh
  python3 fetch_posters.py
  ```

## Updating the data

The data lives in the `RAW` array inside the `<script>` in [index.html](index.html). Each row is:

```js
[name, type, rating, dateWatched, [tags]]
// ["Coco", "Movie", 10, "2025-10-06", ["family", "fantasy"]]
```

- `type` is `"Movie"`, `"TV Series"`, or `""` if unknown.
- `rating` is a number from 0 to 10 (halves allowed).
- `dateWatched` is `"YYYY-MM-DD"` or `""`.
- Streaming platforms are set separately in the `PLATFORMS` object, keyed by exact title.
- Poster images are mapped in the `POSTERS` object in `index.html`.

The data is a manual copy of the Notion database, so re-copy it when the database changes.

## Customizing

- Theme colors are CSS variables at the top of the `<style>` block (`--bg`, `--text`, `--muted`, `--accent`).
- Poster colors and fallback glowing circles come from `posterStyle()`; chart bar colors from `colorFor()`.
