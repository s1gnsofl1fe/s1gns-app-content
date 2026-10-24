# Updating S1gns Of L1fe app content (instructions for agents)

This repo is the live content feed for the S1gns Of L1fe iPhone app. The app downloads
`https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/content.json` on every launch
and pull-to-refresh. **Pushing to `main` publishes to every listener within ~5 minutes. Get Chris's
OK before every push.** For a person rather than an agent, `README.md` explains the same thing and
`composer.html` edits the Vault and announcements without touching JSON.

## How the feed works

- Each top-level section in `content.json` **replaces** the app's built-in section of the same name;
  sections not in the file keep the app's built-in version. Publish complete lists, never partial ones.
- Sections the app accepts and their fields: `ContentPatch` and the model structs in
  `~/Developer/S1gns-Of-L1fe-iOS/S1gnsOfL1fe/Models/Content.swift`. The app's built-in content
  (`.../S1gnsOfL1fe/Resources/Content/Content.json`) is the reference for every section's shape.
- Sections in this file today: `announcements`, `artist`, `stats`, `timeline`, `stories`, `quotes`,
  `interviews`, `labels`, `plugins` (since 2026-10-24: the full plugin list now lives here; edit it in
  place), `links`, `vault`.

| Want to… | Edit | Shows in the app |
|---|---|---|
| Announce something | `announcements` (`id`, `title`, `message`, optional `url`, `cta`, `expires` yyyy-MM-dd) | Home banners, newest first, until `expires` |
| Update a plugin / add a new one | `plugins` (copy an existing entry's shape) | Shop. `status` "New …" or a date within 60 days shows a NEW badge |
| Add a preset pack or other link | `links` (`category` "Presets" etc., newest first in its category) | Shop → Presets, Links |
| Add a free download, tutorial or guide | `vault` (see `vault-item.schema.json`) | Home → Bonus Vault |

## Rules (App Review — the app was rejected three times over these)

- **No prices, "buy" buttons or store links for paid digital goods** in announcements or anywhere a
  call to action appears (Guideline 3.1.1). Announcing paid desktop plugins or preset packs is fine;
  leave out the price and leave `url`/`cta` empty or point at a free or non-store page. App Store
  links for iPad apps are fine. The app hides plugin prices itself; keep `price` accurate anyway.
- **Everything in the Vault is free.** No members-only items, codes or paid links.
- `announcements` and `links` have **no image field**. Images work for plugins (`image`, `gallery`),
  Vault items and push notifications.

## Images

Put new images in `images/<slug>/` as JPEG (≈1440 px wide for screenshots, quality ~82; convert
with `sips -s format jpeg -s formatOptions 82 in.png --out out.jpg`) and reference
`https://raw.githubusercontent.com/s1gnsofl1fe/s1gns-app-content/main/images/<slug>/<file>.jpg`.
Gumroad (`public-files.gumroad.com/…`) and Bandcamp (`f4.bcbits.com/img/…_10.jpg`) image URLs also
work. Every image URL must return 200 before you push.

## Where the facts come from

- Plugins: Chris's project folders in `~/Developer/<Plugin>/` (release notes, changelog,
  `output/release-x.y/Screenshots`), the Gumroad product page, the existing plugin entry.
- Preset packs: the Material Bandcamp page (`material.bandcamp.com/album/<slug>`).
- Don't invent features, dates or numbers; ask Chris when something isn't written down.

## Steps

1. `git pull`, then edit `content.json` with a script that keeps the formatting:
   `json.dumps(data, indent=2, ensure_ascii=False) + "\n"` (the file round-trips exactly).
2. Bump `version` by 1 and set `updatedAt` to today.
3. `python3 validate.py content.json` must end with "Looks good".
4. Show Chris the change; push only after his OK. Commit message: what changed, in plain words.
5. Verify: the raw URL above returns the new `version`, and all new image URLs return 200.

## Push notifications (Transmissions) are separate

They are sent by Chris from the S1gns Transmission companion app, not from this repo. Draft them
for him: kind (New Releases, News & Updates, Live & Events, Studio & Learning, Bonus Vault Drops),
title ≤ 60 characters, body ≤ 157, the in-app page to open (a release, plugin, story, Vault item,
course or service by id, or Studio, Vault, Links, Timeline, Bio) and an optional image URL. The same
3.1.1 rule applies. The page it opens must already exist, so publish content first, then send.
