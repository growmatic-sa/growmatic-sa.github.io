# Growmatic site — how it works

Static site. `main` on GitHub is the source of truth; pushing to `main` deploys to Hostinger
(`.github/workflows/deploy.yml`) and pings IndexNow with the changed pages.

## Add a blog post

1. Create `_posts/<anything>.md` (copy an existing post for the front-matter format).
   `category` must be one of the categories in `tools/blog.py`.
2. `python3 tools/build.py`
3. Commit and push.

The build regenerates the post pages, the blog index, `assets/css/site.css`, `sitemap.xml` and `llms.txt`.

## Change styles

Edit `assets/css/src-brand.css` (brand layer, loaded last) or the original files, then run the build.
Pages load only `/assets/css/site.css`; `/lp/` keeps its own CSS.
