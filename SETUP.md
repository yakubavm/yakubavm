# GitHub profile installation — `yakubavm`

This bundle is designed specifically for the existing **public** repository:

**https://github.com/yakubavm/yakubavm** (`main` branch)

## 1. Copy the files into your profile repository

Your profile repository root should look like this:

```text
yakubavm/
├── README.md
├── SETUP.md
├── tools/
│   └── build_assets.py
├── assets/
│   ├── hero.svg
│   ├── terminal.gif
│   ├── identity.svg
│   ├── toolbox.svg
│   ├── environment.svg
│   ├── focus.svg
│   ├── metrics.svg
│   └── footer.svg
└── .github/
    ├── scripts/
    │   └── update_metrics.py
    └── workflows/
        └── update-metrics.yml
```

If cloning with Git on Windows 11 Pro:

```powershell
git clone https://github.com/yakubavm/yakubavm.git
cd yakubavm
```

Copy **all** the bundle contents into the cloned folder, including the hidden `.github` directory. Commit and push when you're satisfied with the preview:

```powershell
git add README.md SETUP.md assets .github tools
git commit -m "design: rebuild animated GitHub profile"
git push origin main
```

The initial `metrics.svg` intentionally shows dashes until its first successful data update. This avoids fabricated repository metrics.

## 2. Enable automated, self-hosted metrics

1. Open **https://github.com/yakubavm/yakubavm/actions**.
2. Find **Update profile metrics**, then select **Run workflow** on `main`.
3. The included workflow requests `contents: write` and uses the built-in `GITHUB_TOKEN` (no personal access token needed).
4. If the commit step fails due to branch protection or repository Actions policy, allow GitHub Actions to write to this repository under **Settings → Actions → General → Workflow permissions** (where applicable), or adjust the branch rule. No change is needed if the first run succeeds.
5. After the run, `assets/metrics.svg` will contain real **public** project counts, stars received, last-12-month contribution counts, contribution heatmap, and language proportions.
6. GitHub Actions runs daily at 05:23 UTC. A commit happens only when the rendered card changes. Scheduled workflows can occasionally be delayed by GitHub.

The script uses Python's standard library and official GitHub APIs. It intentionally excludes the `yakubavm` profile repository and forks from project/language metrics and never reads private repository contents. The contribution calendar reflects the data the API makes visible to the workflow token.

## 3. Change the left-hand GitHub sidebar separately

The profile README **cannot** change GitHub's actual sidebar, avatar, pronouns, followers, or the native contribution chart. Those are GitHub's own interface.

Open **https://github.com/settings/profile** and consider:

- **Name:** `Viktor Yakuba`
- **Bio:** `Python Developer · DevOps & Automation · Software, Scripts & Bots`
- **Location:** `Ukraine`
- **Public email:** `yakubavm@proton.me` (only if you want it publicly shown)
- **Pronouns:** leave blank if you no longer want them displayed
- **Avatar:** keep the current monochrome avatar to complement the new design

## 4. Edit the design later

- Text, navigation links and featured work: `README.md`.
- Animated gradient and mesh banner: `assets/hero.svg`.
- Terminal typing animation: `assets/terminal.gif` (pre-rendered for reliable GitHub playback).
- Identity, toolbox, environment, focus and footer: corresponding SVGs in `assets/`.
- GitHub metrics behavior: `.github/scripts/update_metrics.py`.
- Daily update schedule: `.github/workflows/update-metrics.yml`.

The SVG assets are plain editable XML; GitHub supports them when included through `<img>` links. Animated content and layout can differ subtly by client, and README markup does not provide custom page-level CSS or JavaScript.

## Notes

- If you want to regenerate the banner and animated typing strip after changing the visual source: run `python -m pip install pillow`, then `python tools/build_assets.py`. The script detects common Windows, Linux, and macOS monospaced fonts. Its output is reproducible SVG/GIF assets.
- The design intentionally does **not** depend on `github-readme-stats`, activity-graph Vercel instances, shield services, profile view counters or other third-party stat endpoints.
- No visitor-tracking pixels are used.
- The design is responsive in the sense that the images scale to the README width. Small-screen text is best read by zooming; a true CSS grid is not supported within GitHub README markdown.
- GitHub image proxy caching may temporarily display older assets after an update.
