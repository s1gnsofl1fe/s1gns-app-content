# Publishing bonus content to the S1gns Of L1fe app

This folder is your **publishing kit**. It lets you add new tutorials, sample packs, presets, guides
and announcements to the iPhone app **without releasing an app update** and without writing code.

| File | What it's for |
| --- | --- |
| `composer.html` | **The Vault Composer.** Double-click it to open it in your browser. Add, edit, reorder and preview Vault items in a form, then download a finished `content.json`. Works offline. |
| `content.json` | The file the app downloads. This one is a ready-to-publish starter with the 9 current Vault items and one example announcement. |
| `validate.py` | A checker. Run it before publishing to catch typos, broken links and missing fields. |
| `vault-item.schema.json` | The technical definition of a Vault item (for developers and editors that understand JSON Schema). |

---

## 1. How it works (the 30-second version)

1. The app ships with its own content built in.
2. Every time it launches — and whenever someone **pulls down to refresh** the Vault — it quietly
   downloads one file from the internet:

   ```
   https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/content.json
   ```

3. Every section that file contains (for example `"vault"` or `"announcements"`) **replaces** the
   built-in version of that section. Sections the file doesn't mention stay as they are.
4. The app keeps a copy, so the new content still shows up offline.

So "uploading a new part to the app" = **editing that one `content.json` file online**.

> **Important:** the `"vault"` list you publish *replaces* the whole Vault — it doesn't add to it.
> Always publish the complete list of items you want people to see. The easiest way to do that is
> to load your current file into the Composer, add the new item and download the result.

If the file is missing, unreachable or broken, nothing bad happens — the app just keeps showing
what it already has.

### Everything in the Vault is free

App Store rules (guideline 3.1.1) don't allow unlocking digital content inside the app with codes,
passwords or outside payments. So the Vault has **no locks and no paywalls** — every item is free for
everyone. Don't add "members only" items, unlock codes, or links whose main purpose is to sell
something inside the Vault. Linking to a *free* download page (Squarespace, Gumroad at $0, etc.) is fine.

---

## 2. One-time setup: free hosting on GitHub (recommended)

GitHub is free, reliable, fast worldwide, and you can edit files right in your web browser.

1. Create a free account at **github.com** with the username **`s1gnsofl1fe`**.
   (If that name isn't available, use another one and ask your developer to change
   `AppConfig.remoteContentURL` in the app to match — it needs a new app release once.)
2. Click **+ → New repository**.
   - Repository name: **`s1gns-app-content`**
   - Visibility: **Public** (the app must be able to read it without a password)
   - Tick **Add a README file**, then **Create repository**.
3. In the new repository click **Add file → Upload files**, drag in the `content.json` from this
   folder, and click **Commit changes**.
4. Check it worked: open
   <https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/content.json>
   in your browser. You should see the file's text. That's the exact address the app reads.

That's it — the app is now connected.

### Updating content later

**Option A — with the Composer (easiest):**

1. Open `composer.html` (double-click it).
2. Click **Load file** and choose your current `content.json` (or **Load from URL** to pull the
   live one straight from GitHub).
3. Add or edit items, check the live preview, press **Validate**, then **Download content.json**.
4. On github.com open the repository → click `content.json` → the **pencil (Edit)** icon… or
   simply **Add file → Upload files** and drop the new `content.json` in (it replaces the old one).
5. Click **Commit changes**.

**Option B — edit directly on github.com:** open `content.json`, click the pencil icon, make your
change, click **Commit changes**. Tip: paste the text into the Composer first to check it.

GitHub's raw file address can take **up to about 5 minutes** to show the new version.

### Alternatives to GitHub

Any host works as long as it gives a **public `https://` address that returns the raw JSON text**:

- **Netlify Drop** (<https://app.netlify.com/drop>) — drag a folder containing `content.json`; you
  get an address like `https://your-site.netlify.app/content.json`.
- **Cloudflare Pages** or **GitHub Pages** — same idea, free.
- **Your Squarespace site** can't serve raw JSON files reliably — don't use it for `content.json`.

If you switch hosts, the address in `AppConfig.remoteContentURL` must be changed and a new app
version released once. After that you can publish as often as you like.

---

## 3. Where to host the media itself

`content.json` only holds *text and links*. The videos, audio, PDFs and packs live elsewhere:

| Media | Best place | Notes |
| --- | --- | --- |
| Tutorials & video | **YouTube** (public or *unlisted*) | Use `"kind": "youtube"` and paste the 11-character id. Unlisted videos play in the app but don't appear on your channel — perfect for Vault exclusives. |
| Video (alternative) | **Vimeo** | Use `"kind": "video"` with the Vimeo page link (`https://vimeo.com/123456789`). The video's privacy must allow embedding. |
| Direct video files | Any host giving a direct `.mp4` / `.m3u8` link | Plays in the native iPhone player. Keep files reasonably small (under ~200 MB). |
| Audio previews / sketches | A direct `.mp3` or `.m4a` link | GitHub (files under 25 MB via the web upload), Dropbox (see below), or any file host. |
| PDF guides | **GitHub** (same repository — upload the PDF and use its *raw* address) | Opens in the app's built-in reader, which can also share / save it. |
| Images & thumbnails | Squarespace image links, GitHub raw links, or Gumroad image links | Must start with `https://`. Square images (1:1) look best; around 1000 px is plenty. Squarespace links can end with `?format=750w` for a lighter file. |
| Sample / preset packs | **Your Squarespace store** (free $0 products) or **Gumroad** (price $0) | Use `"kind": "download"` with the product page as `mediaURL`. The app opens the page for the user to grab the files. |

**Dropbox:** share the file, copy the link, and change the ending `?dl=0` to **`?dl=1`** — otherwise
the app gets the Dropbox web page instead of the file.
**Google Drive:** its share links open a web page, not the file, and often fail inside apps.
Avoid it for audio/video/PDF; it's OK for a `download` item that simply opens a page.

GitHub raw addresses look like:
`https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/guides/modular-basics.pdf`

---

## 4. The Vault item fields

Every item is a block in curly braces inside the `"vault": [ … ]` list. Separate items with commas
(and **no** comma after the last one — the Composer handles this for you).

| Field | Required? | What it does | Example |
| --- | --- | --- | --- |
| `id` | **yes** | Permanent unique name: lowercase, numbers, dashes. **Never change it** after publishing (saves and "NEW" badges are tied to it). | `"drone-pack-2"` |
| `title` | **yes** | The headline. Under 60 characters looks best. | `"Ambient Drone Starter Pack"` |
| `kind` | **yes** | What type of thing it is (see next section). | `"download"` |
| `subtitle` | no | One short line under the title. | `"Five 24-bit drones from the modular"` |
| `category` | no | The filter chip it appears under. Reuse the same spelling each time. | `"Sample Packs"`, `"Tutorials"`, `"Presets"`, `"Articles"` |
| `summary` | no | One or two sentences. Shown big at the top of the detail page and used by search. | `"Five drone samples…"` |
| `body` | no | Longer text — a list, one entry per paragraph. `**bold**`, `*italic*` and `[links](https://…)` work. | `["First paragraph.", "Second paragraph."]` |
| `mediaURL` | depends on kind | The main file or page (see below). | `"https://www.s1gnsofl1fe.com/merch/p/…"` |
| `youtubeId` | for `youtube` | The 11 characters after `watch?v=`. On any other kind it adds a "Companion tutorial" player. | `"s0AXw7zE8iY"` |
| `thumbnail` | recommended | Cover image address. YouTube items get the video thumbnail automatically. | `"https://…/pack.jpg?format=750w"` |
| `images` | for `gallery` | List of image addresses. | `["https://…/1.jpg", "https://…/2.jpg"]` |
| `attachments` | no | Extra files/links shown under "Included". Each has `title`, `url`, and optional `kind` and `size`. PDF links open in the in-app reader. | see examples |
| `tags` | no | Little chips under the text; also searchable. | `["Vital", "Presets"]` |
| `publishedAt` | recommended | Release date `YYYY-MM-DD`. Newest items show first. Items from the last 6 months get a glowing **NEW** badge until the person opens them. | `"2026-09-25"` |
| `duration` | no | Running time for video/audio. | `"23:21"` or `"1:05:00"` |
| `featured` | no | `true` puts it in the big **Featured drops** carousel at the top. | `true` |

### Kinds and what each one needs

| `kind` | Shows as | Needs |
| --- | --- | --- |
| `youtube` | Video player at the top of the page + "Watch on YouTube" | `youtubeId` |
| `video` | Native player for `.mp4`/`.m3u8`/`.mov` links, or an embedded Vimeo/Wistia/YouTube player | `mediaURL` (or `youtubeId`) |
| `audio` | A custom player with play/pause, ±15 s, a scrubbable animated waveform and times | `mediaURL` ending in `.mp3` / `.m4a` / `.wav` |
| `article` | Big header image + long-form reading text | `body` (and a `thumbnail` for the header). `mediaURL` optional → "Read the original post" button |
| `pdf` | "Read the guide" button → in-app PDF reader with download progress and Share | `mediaURL` ending in `.pdf` |
| `download` | Artwork, "Get it free" button, Share button, "Included" list | `mediaURL` (the download page) and/or `attachments` |
| `link` | Artwork + "Open" button | `mediaURL` |
| `gallery` | Swipeable images; tap for full-screen pinch-to-zoom | `images` |

### Copy-and-paste examples

**YouTube tutorial with a free pack attached**

```json
{
  "id": "beginner-ambient-tutorial",
  "title": "Beginner Ambient Tutorial",
  "subtitle": "A 30-minute track with free Vital presets",
  "kind": "youtube",
  "category": "Tutorials",
  "youtubeId": "EWYMsvTFdUA",
  "duration": "29:29",
  "publishedAt": "2023-10-22",
  "summary": "Create an ambient track from scratch in Vital, using a free pack of presets made for this lesson.",
  "attachments": [
    { "title": "S1gns Beginner Pack 02", "url": "https://www.s1gnsofl1fe.com/merch/p/s1gns-beginner-pack-02", "kind": "8 Vital presets", "size": "Free" }
  ],
  "tags": ["Vital", "Presets", "Beginner"]
}
```

**Free sample pack with a companion video (featured)**

```json
{
  "id": "ambient-drone-starter-pack",
  "title": "Ambient Drone Starter Pack",
  "kind": "download",
  "category": "Sample Packs",
  "featured": true,
  "thumbnail": "https://images.squarespace-cdn.com/content/v1/64b43927b9957a51458f6afa/9ab37ad6-6eb3-4a1c-bf84-75a1989e847c/AmbientDroneSamplePack.jpg?format=750w",
  "mediaURL": "https://www.s1gnsofl1fe.com/merch/p/ambient-drone-starter-pack",
  "youtubeId": "s0AXw7zE8iY",
  "publishedAt": "2025-09-14",
  "summary": "Five drone samples recorded in 24-bit from my modular synthesizer."
}
```

**Unlisted bonus video (Vimeo or a direct file)**

```json
{
  "id": "studio-tour-2026",
  "title": "Studio Tour 2026",
  "kind": "video",
  "category": "Behind the Scenes",
  "mediaURL": "https://vimeo.com/123456789",
  "duration": "12:40",
  "publishedAt": "2026-10-01"
}
```

**Audio sketch**

```json
{
  "id": "night-drive-sketch",
  "title": "Night Drive (sketch)",
  "kind": "audio",
  "category": "Audio",
  "mediaURL": "https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/audio/night-drive.m4a",
  "thumbnail": "https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/audio/night-drive.jpg",
  "duration": "4:12",
  "publishedAt": "2026-10-05",
  "summary": "An unreleased idea straight from the modular."
}
```

**PDF guide**

```json
{
  "id": "modular-cheat-sheet",
  "title": "Modular Cheat Sheet",
  "kind": "pdf",
  "category": "Guides",
  "mediaURL": "https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/guides/modular-cheat-sheet.pdf",
  "thumbnail": "https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/guides/modular-cheat-sheet.jpg",
  "publishedAt": "2026-10-10"
}
```

**Article**

```json
{
  "id": "creating-icy-drones",
  "title": "Creating Icy Drones From Scratch",
  "kind": "article",
  "category": "Articles",
  "thumbnail": "https://images.squarespace-cdn.com/…/header.jpg?format=1500w",
  "mediaURL": "https://www.s1gnsofl1fe.com/s1gnsblog/creating-icy-drones-from-scratch",
  "publishedAt": "2025-01-15",
  "body": [
    "**FM is your friend.** Frequency modulation pushes shimmering harmonics into your reverb…",
    "**Embrace modular.** …"
  ]
}
```

**Link and gallery**

```json
{ "id": "texture-loom", "title": "Texture Loom 1.5", "kind": "link", "category": "Instruments",
  "mediaURL": "https://s1gnsofl1fe.gumroad.com/l/texture-loom",
  "thumbnail": "https://public-files.gumroad.com/fn9hwdo9jdaly1797sdbih2fhm9h" },

{ "id": "studio-photos", "title": "Studio Photos", "kind": "gallery", "category": "Behind the Scenes",
  "images": ["https://…/studio-1.jpg", "https://…/studio-2.jpg", "https://…/studio-3.jpg"] }
```

---

## 5. Featuring an item

Add `"featured": true` to it. Featured items appear in the large, glowing **Featured drops** carousel
at the top of the Vault (newest first). One to four featured items keeps it feeling special — remove
`featured` (or set it to `false`) from older ones when you add something new.

## 6. Posting an announcement

Announcements are banners on the app's Home screen — great for "New pack in the Vault!" or a launch.
Add an `"announcements"` list next to `"vault"` in `content.json`:

```json
"announcements": [
  {
    "id": "texture-loom-1-5",
    "title": "Texture Loom 1.5 is here",
    "message": "The free granular instrument now has independent granular engines and polyphony.",
    "url": "https://s1gnsofl1fe.gumroad.com/l/texture-loom",
    "cta": "Get it free",
    "expires": "2026-12-31"
  }
]
```

- `id` must be unique — use a new one for each announcement (the app tracks announcements by id).
- `url` + `cta` add a button. Leave them out for a message-only banner.
- `expires` (`YYYY-MM-DD`) hides it automatically after that day.
- To remove all announcements publish `"announcements": []`.

The Composer has an **Announcements** tab for this too.

---

## 7. Test before you publish

1. **Validate.** In the Composer press **Validate**, or in Terminal:

   ```bash
   cd "path/to/ContentServer"
   python3 validate.py                 # checks content.json in this folder
   python3 validate.py ~/Downloads/content.json
   python3 validate.py --online        # also opens every link to make sure none are broken
   ```

   Red ✗ lines must be fixed; yellow ⚠ lines are suggestions.
2. **Preview.** The Composer's preview card shows roughly how each item will look in the app.
3. **Publish**, wait a few minutes, then on your iPhone open the Vault and **pull down to refresh**.

## 8. When do people see changes?

- The next time they **open the app** (a fresh launch), or
- straight away if they **pull down to refresh** the Vault.

New items with a recent `publishedAt` date get a **NEW** badge until they're opened. If someone is
offline, they keep seeing the last content they downloaded.

## 9. Troubleshooting

| Problem | Fix |
| --- | --- |
| Nothing changed in the app | Wait 5 minutes (GitHub caching), then pull to refresh. Open the raw address in a browser to confirm your change is live. |
| The whole Vault disappeared or went back to the old items | Your file probably has a JSON typo — the app ignores broken files. Run `validate.py`. |
| One item is missing | That item has a problem (e.g. `kind` misspelled). Run `validate.py`. |
| Audio / PDF won't open | The link must go *straight to the file* (ends in `.mp3` / `.pdf`). Dropbox links need `?dl=1`. |
| Video shows "unavailable" | The YouTube/Vimeo video must allow embedding. |
| Image doesn't show | It must start with `https://` and be a direct image link. |
