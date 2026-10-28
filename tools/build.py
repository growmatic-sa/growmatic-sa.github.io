#!/usr/bin/env python3
"""Growmatic site build.

Run from the repo root before every commit:  python3 tools/build.py

  1. Bundles the CSS into assets/css/site.css (brand palette applied).
  2. Generates blog posts from _posts/*.md and rebuilds the blog index.
  3. Points every page at the bundle, self-hosted font, lazy images.
  4. Regenerates sitemap.xml (lastmod from git) and llms.txt.
"""
import colorsys, hashlib, html, json, os, re, subprocess, sys
from datetime import date
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
DOMAIN = "https://gorwmatic.io"

# ---------------------------------------------------------------- CSS
CSS_ORDER = ["src-fonts.css", "style.css", "experience.css", "studio.css", "motion.css", "src-brand.css"]
RECOLOR = {"experience.css", "studio.css", "motion.css"}  # older overlays with an off-brand palette


def _hls_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h / 360, l, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def brandify(r, g, b):
    """Map an off-brand colour onto the Growmatic palette, keeping its lightness."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    h *= 360
    chroma = (max(r, g, b) - min(r, g, b)) / 255
    if 60 <= h <= 115 and chroma >= 0.25:          # lime family -> Growth Green
        if l >= 0.6:
            return (143, 209, 79) if l <= 0.72 else tuple(round(c * 255) for c in colorsys.hls_to_rgb(90 / 360, l, 0.62))
        return tuple(round(c * 255) for c in colorsys.hls_to_rgb(94 / 360, l, 0.6))
    if chroma < 0.16 or (40 <= h <= 175 and l < 0.3):  # warm/green neutrals -> cool brand neutrals
        if l < 0.3:
            return tuple(round(c * 255) for c in colorsys.hls_to_rgb(220 / 360, l, 0.42))
        if l > 0.8:
            return tuple(round(c * 255) for c in colorsys.hls_to_rgb(212 / 360, l, 0.28))
        return tuple(round(c * 255) for c in colorsys.hls_to_rgb(211 / 360, l, 0.16))
    return (r, g, b)


def recolor(css):
    def hexrep(m):
        v = m.group(1)
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        if v.lower() in ("ffffff", "000000"):
            return m.group(0)
        r, g, b = brandify(*(int(v[i:i + 2], 16) for i in (0, 2, 4)))
        return "#%02X%02X%02X" % (r, g, b)

    def rgbarep(m):
        r, g, b = (int(x) for x in m.group(2, 3, 4))
        if (r, g, b) in ((255, 255, 255), (0, 0, 0)):
            return m.group(0)
        r, g, b = brandify(r, g, b)
        return f"{m.group(1)}({r},{g},{b}{m.group(5) or ''})"

    css = re.sub(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", hexrep, css)
    css = re.sub(r"(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(\s*,\s*[\d.]+)?\s*\)", rgbarep, css)
    return css


def minify(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def build_css():
    parts = []
    for name in CSS_ORDER:
        css = open(f"assets/css/{name}", encoding="utf-8").read()
        parts.append(recolor(css) if name in RECOLOR else css)
    css = minify("\n".join(parts))
    open("assets/css/site.css", "w", encoding="utf-8").write(css)
    return hashlib.md5(css.encode()).hexdigest()[:8]


# ---------------------------------------------------------------- HTML
CSS_LINKS = re.compile(r'<link rel="stylesheet" href="/assets/css/(?:style|experience|studio|motion|site)\.css[^"]*">\s*')
FONT_LINKS = re.compile(r'<link (?:rel="preconnect" href="https://fonts\.(?:googleapis|gstatic)\.com"(?: crossorigin)?|href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet"|rel="preload" as="font"[^>]*)>\s*')


def page_files():
    out = []
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if not d.startswith((".", "_")) and d not in ("tools", "assets", "lp", "node_modules")]
        out += [os.path.join(dp, f)[2:] for f in fn if f.endswith(".html") and not f.startswith("google")]
    return sorted(out)


def lazy_images(doc):
    """Lazy-load every image after the first two in <main> (logo/intro images live outside it)."""
    m = re.search(r"<main\b.*?</main>", doc, re.S)
    if not m:
        return doc
    count = 0

    def rep(t):
        nonlocal count
        tag = t.group(0)
        count += 1
        if count <= 2 or "loading=" in tag or "fetchpriority" in tag:
            return tag
        return tag[:-1].rstrip("/") + ' loading="lazy" decoding="async">'

    main = re.sub(r"<img\b[^>]*>", rep, m.group(0))
    return doc[:m.start()] + main + doc[m.end():]


def file_ver(m):
    path = m.group(1)
    try:
        h = hashlib.md5(open(path.lstrip("/"), "rb").read()).hexdigest()[:8]
    except FileNotFoundError:
        return m.group(0)
    return f"{path}?v={h}"


ASSET_REF = re.compile(r"(/assets/(?:css|js)/[\w-]+\.(?:css|js))(?:\?v=[\w]+)?")


def update_pages(css_ver):
    head = (f'<link rel="preload" href="/assets/fonts/cairo-arabic.woff2" as="font" type="font/woff2" crossorigin>\n'
            f'<link rel="stylesheet" href="/assets/css/site.css?v={css_ver}">\n')
    lp = "lp/index.html"
    doc = open(lp, encoding="utf-8").read()
    new = ASSET_REF.sub(file_ver, doc)
    if new != doc:
        open(lp, "w", encoding="utf-8").write(new)
    for f in page_files():
        doc = open(f, encoding="utf-8").read()
        new = FONT_LINKS.sub("", doc)
        new = CSS_LINKS.sub("", new)
        new = new.replace("</head>", head + "</head>", 1) if "/assets/css/site.css" not in new else new
        new = lazy_images(new)
        new = ASSET_REF.sub(file_ver, new)
        if new != doc:
            open(f, "w", encoding="utf-8").write(new)


# ---------------------------------------------------------------- sitemap / llms
def git_lastmod(path):
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], capture_output=True, text=True).stdout.strip()
    return out or date.today().isoformat()


def url_of(f):
    d = os.path.dirname(f)
    return "/" if d == "" else f"/{d}/"


def build_sitemap():
    rows = []
    for f in page_files():
        if f == "404.html":
            continue
        u = url_of(f)
        pr = "1.0" if u == "/" else "0.9" if u.startswith("/الخدمات") else "0.6" if u.count("/") > 2 and u.startswith("/المدونة") else "0.7"
        rows.append(f"  <url><loc>{DOMAIN}{quote(u)}</loc><lastmod>{git_lastmod(f)}</lastmod><priority>{pr}</priority></url>")
    rows.append(f"  <url><loc>{DOMAIN}/lp/</loc><lastmod>{git_lastmod('lp/index.html')}</lastmod><priority>0.8</priority></url>")
    open("sitemap.xml", "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows) + "\n</urlset>\n")


def title_of(f):
    doc = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)</title>", doc, re.S).group(1)
    d = re.search(r'name="description" content="([^"]*)"', doc)
    return html.unescape(t.split("|")[0].strip()), html.unescape(d.group(1)) if d else ""


def build_llms():
    lines = ["# Growmatic (جروماتيك)", "",
             "> شركة تسويق رقمي وتقنية في السعودية: إدارة الحملات الإعلانية، التسويق الإلكتروني، تحسين محركات البحث SEO، تصميم المواقع والمتاجر الإلكترونية، ولوحات التحكم. الهاتف وواتساب: +966534921098", ""]
    groups = {"الصفحات الرئيسية": [], "الخدمات": [], "المدونة": []}
    for f in page_files():
        if f == "404.html":
            continue
        u = url_of(f)
        key = "الخدمات" if u.startswith("/الخدمات/") and u != "/الخدمات/" else "المدونة" if u.startswith("/المدونة/") and u != "/المدونة/" else "الصفحات الرئيسية"
        t, d = title_of(f)
        groups[key].append(f"- [{t}]({DOMAIN}{u}): {d}")
    for k, v in groups.items():
        lines += [f"## {k}", ""] + v + [""]
    open("llms.txt", "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    ver = build_css()
    try:
        import blog
        blog.build()
    except ModuleNotFoundError:
        pass
    update_pages(ver)
    build_sitemap()
    build_llms()
    print("built: site.css v=" + ver)
