"""Blog generator: _posts/*.md -> المدونة/<slug>/index.html, plus the blog index.

Post format:

    ---
    slug: دليل-شيء-ما
    title: عنوان المقال
    description: وصف 120-160 حرفًا
    category: تحسين محركات البحث
    date: 2026-10-28
    read: 7
    keywords: كلمة, كلمة, كلمة
    ---
    ::: tldr
    - نقطة
    :::
    فقرة...
    ## عنوان
    ::: faq
    ? سؤال
    جواب
    :::
"""
import glob, html, json, os, re

DOMAIN = "https://gorwmatic.io"
BLOG = "المدونة"
TEMPLATE = f"{BLOG}/دليل-السيو-للمواقع-العربية/index.html"

ICONS = {
    "ads": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l15-6v14L3 13z"/><path d="M7 13v5a2 2 0 0 0 4 0v-3.5"/></svg>',
    "store": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 7h14l-1.5 10.5a2 2 0 0 1-2 1.5h-7a2 2 0 0 1-2-1.5z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>',
    "seo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    "web": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M8 4v5"/></svg>',
    "auto": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
    "mkt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>',
}

# category -> (icon, cover banner, service page, service name)
CATEGORIES = {
    "الإعلانات المدفوعة": ("ads", "growth", "/الخدمات/إدارة-الحملات-الإعلانية/", "إدارة الحملات الإعلانية"),
    "التسويق الرقمي": ("mkt", "creative-orbit", "/الخدمات/التسويق-الإلكتروني/", "التسويق الإلكتروني"),
    "تحسين محركات البحث": ("seo", "growth", "/الخدمات/تحسين-محركات-البحث-سيو/", "تحسين محركات البحث SEO"),
    "المتاجر الإلكترونية": ("store", "studio", "/الخدمات/إنشاء-المتاجر-الإلكترونية/", "إنشاء المتاجر الإلكترونية"),
    "تصميم المواقع": ("web", "studio", "/الخدمات/تصميم-المواقع/", "تصميم المواقع"),
    "الأتمتة والأنظمة": ("auto", "creative-orbit", "/الخدمات/لوحات-التحكم-والموارد-البشرية/", "لوحات التحكم والأنظمة"),
}

# Hand-built posts that predate the generator (kept as-is, listed in the index)
LEGACY = [
    dict(slug="أسباب-صرف-ميزانية-الإعلانات-بدون-مبيعات", title="7 أسباب تجعل إعلاناتك تصرف الميزانية بدون مبيعات، وكيف تعالجها",
         description="لماذا تنفق على إعلانات سناب شات وتيك توك وجوجل ولا تبيع؟ سبعة أخطاء شائعة في الحملات الإعلانية وحلول عملية لكل منها.",
         category="الإعلانات المدفوعة", date="2026-09-29", read="6"),
    dict(slug="اختيار-منصة-المتجر-الإلكتروني", title="سلة أم زد أم شوبيفاي أم ووكومرس؟ دليل اختيار منصة متجرك",
         description="مقارنة عملية تساعدك على اختيار منصة المتجر الإلكتروني المناسبة لنشاطك في السعودية: سهولة الإدارة، المرونة، التكلفة، وخطط التوسع.",
         category="المتاجر الإلكترونية", date="2026-09-29", read="5"),
    dict(slug="دليل-السيو-للمواقع-العربية", title="دليل السيو للمواقع العربية: من أين تبدأ لتظهر في جوجل؟",
         description="خطوات عملية لتحسين ظهور موقعك العربي في نتائج جوجل: Search Console، الكلمات المفتاحية العربية، تحسين الصفحات، السرعة، والسيو المحلي.",
         category="تحسين محركات البحث", date="2026-09-29", read="7"),
]

esc = html.escape


# ------------------------------------------------------------ markdown
def inline(t):
    t = esc(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


def slugify(t):
    return re.sub(r"[^\w؀-ۿ]+", "-", t).strip("-")


def md_to_html(md):
    out, toc, faq = [], [], []
    lines = md.strip("\n").split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("::: "):
            kind = ln[4:].strip()
            block = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                block.append(lines[i])
                i += 1
            i += 1
            if kind == "tldr":
                items = "".join(f"<li>{inline(b[2:])}</li>" for b in block if b.startswith("- "))
                out.append(f'<div class="tldr"><strong>الخلاصة السريعة</strong><ul>{items}</ul></div>')
            elif kind == "faq":
                q = None
                for b in block:
                    if b.startswith("? "):
                        q = b[2:].strip()
                    elif b.strip() and q:
                        faq.append((q, b.strip()))
                        q = None
                out.append('<h2 id="الأسئلة-الشائعة">الأسئلة الشائعة</h2><div class="faq">' + "".join(
                    f"<details><summary>{inline(q)}</summary><p>{inline(a)}</p></details>" for q, a in faq) + "</div>")
                toc.append(("الأسئلة-الشائعة", "الأسئلة الشائعة"))
            continue
        if ln.startswith("## "):
            t = ln[3:].strip()
            toc.append((slugify(t), t))
            out.append(f'<h2 id="{slugify(t)}">{inline(t)}</h2>')
        elif ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:].strip())}</h3>")
        elif ln.startswith("> "):
            out.append(f"<blockquote>{inline(ln[2:].strip())}</blockquote>")
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        elif re.match(r"^(- |\d+\. )", ln):
            ordered = not ln.startswith("- ")
            items = []
            while i < len(lines) and re.match(r"^(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i]).strip())
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        else:
            para = [ln.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|>|\||- |\d+\. |::: )", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
            continue
        i += 1
    return out, toc, faq


def parse(path):
    raw = open(path, encoding="utf-8").read()
    _, fm, body = raw.split("---", 2)
    meta = {}
    for ln in fm.strip().split("\n"):
        k, v = ln.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["body"] = body
    return meta


# ------------------------------------------------------------ pages
def url(slug):
    return f"/{BLOG}/{slug}/"


def card(p):
    icon = ICONS[CATEGORIES[p["category"]][0]]
    return (f'<a class="post-card" href="{url(p["slug"])}" data-cat="{esc(p["category"])}"><div class="post-cover">{icon}</div>'
            f'<div class="post-body"><span class="tag" style="align-self:flex-start">{esc(p["category"])}</span>'
            f'<h3>{esc(p["title"])}</h3><p>{esc(p["description"])}</p>'
            f'<span class="post-meta">وقت القراءة: {p["read"]} دقائق</span></div></a>')


def jsonld(p, faq):
    full = DOMAIN + url(p["slug"])
    tpl = open(TEMPLATE, encoding="utf-8").read()
    org = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S).group(1))["@graph"][0]
    graph = [org,
             {"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
              "datePublished": p["date"], "dateModified": p.get("updated", p["date"]), "inLanguage": "ar",
              "articleSection": p["category"], "keywords": p.get("keywords", ""),
              "author": {"@id": f"{DOMAIN}/#org"}, "publisher": {"@id": f"{DOMAIN}/#org"},
              "mainEntityOfPage": full, "image": f"{DOMAIN}/assets/img/og.png"},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{DOMAIN}/"},
                 {"@type": "ListItem", "position": 2, "name": "المدونة", "item": f"{DOMAIN}/{BLOG}/"},
                 {"@type": "ListItem", "position": 3, "name": p["title"], "item": full}]}]
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def render_post(p, all_posts):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    icon, banner, svc_url, svc_name = CATEGORIES[p["category"]]
    blocks, toc, faq = md_to_html(p["body"])
    title = p["title"]
    full = DOMAIN + url(p["slug"])
    t = esc(title)
    d = esc(p["description"])

    toc_html = ""
    if len(toc) >= 3:
        toc_html = '<nav class="toc" aria-label="محتويات المقال"><strong>محتويات المقال</strong><ol>' + "".join(
            f'<li><a href="#{a}">{esc(b)}</a></li>' for a, b in toc) + "</ol></nav>"
    # TOC goes after the tldr box (if present) at the top
    if blocks and blocks[0].startswith('<div class="tldr"'):
        blocks.insert(1, toc_html)
    else:
        blocks.insert(0, toc_html)
    cta = (f'<div class="cta-band" style="margin-top:40px"><div><h2 style="font-size:26px">تحتاج مساعدة في {esc(svc_name)}؟</h2>'
           f'<p>احجز استشارة مجانية ونراجع وضعك معك، أو تعرّف على <a href="{svc_url}" style="color:var(--lime)">خدمة {esc(svc_name)}</a>.</p></div>'
           '<div class="acts"><button class="btn btn-lime" data-open-booking>احجز استشارة مجانية</button>'
           '<a class="btn btn-ghost" href="https://wa.me/966534921098" target="_blank" rel="noopener" style="color:#fff;box-shadow:inset 0 0 0 2px rgba(255,255,255,.6)">واتساب</a></div></div>')
    article = "\n".join(blocks) + "\n" + cta

    related = [x for x in all_posts if x["slug"] != p["slug"] and x["category"] == p["category"]]
    related += [x for x in all_posts if x["slug"] != p["slug"] and x not in related]
    related_html = ('<section class="alt"><div class="wrap"><div class="sec-head"><h2>مقالات ذات صلة</h2></div><div class="blog-grid">'
                    + "".join(card(x) for x in related[:3]) + "</div></div></section>")

    kws = [k.strip() for k in p.get("keywords", "").split(",") if k.strip()] or [p["category"]]
    ticker = "".join(f"<span>{esc(k)}</span>" for k in (kws * 8)[:32])

    s = tpl
    s = re.sub(r"<title>.*?</title>", f"<title>{t} | Growmatic</title>", s, 1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + d, s, 1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + t + " | Growmatic", s, 1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + d, s, 1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + full, s, 1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + full, s, 1)
    s = s.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">', 1)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda m: f'<script type="application/ld+json">{jsonld(p, faq)}</script>', s, 1, re.S)
    s = s.replace("/assets/img/banners/growth.webp", f"/assets/img/banners/{banner}.webp")
    s = re.sub(r'(<a href="/المدونة/">المدونة</a><span aria-hidden="true">/</span><span>)[^<]*', lambda m: m.group(1) + esc(p["category"]), s, 1)
    s = re.sub(r"<h1([^>]*)>.*?</h1>", lambda m: f"<h1{m.group(1)}>{t}</h1>", s, 1, re.S)
    s = re.sub(r'<div class="article-meta">.*?</div>',
               lambda m: f'<div class="article-meta"><span>{esc(p["category"])}</span><span>وقت القراءة: {p["read"]} دقائق</span>'
                         f'<span><time datetime="{p["date"]}">{p["date"]}</time></span><span>فريق Growmatic</span></div>', s, 1, re.S)
    s = re.sub(r'(<div class="gm-cover-chips" aria-hidden="true">).*?(</div>)',
               lambda m: f'{m.group(1)}<span class="gm-chip"><i>↑</i>{esc(p["category"])}</span>{m.group(2)}', s, 1, re.S)
    s = re.sub(r'(<div class="gm-ticker-track">).*?(</div>)', lambda m: m.group(1) + ticker + m.group(2), s, 1, re.S)
    s = re.sub(r'(<article class="prose">).*?(</article>)', lambda m: m.group(1) + "\n" + article + "\n" + m.group(2), s, 1, re.S)
    s = re.sub(r'<section class="alt"><div class="wrap"><div class="sec-head"><h2>مقالات (?:أخرى|ذات صلة)</h2>.*?</section>',
               lambda m: related_html, s, 1, re.S)
    return s


FILTER_JS = ("<script>document.querySelectorAll('.blog-filters button').forEach(function(b){b.addEventListener('click',function(){"
             "var c=b.dataset.cat;document.querySelectorAll('.blog-filters button').forEach(function(x){x.setAttribute('aria-pressed',String(x===b))});"
             "document.querySelectorAll('.blog-grid .post-card').forEach(function(p){p.hidden=!!c&&p.dataset.cat!==c})})})</script>")


def render_index(posts):
    path = f"{BLOG}/index.html"
    s = open(path, encoding="utf-8").read()
    cats = [c for c in CATEGORIES if any(p["category"] == c for p in posts)]
    filters = ('<div class="blog-filters" role="group" aria-label="تصفية حسب التصنيف"><button type="button" data-cat="" aria-pressed="true">الكل</button>'
               + "".join(f'<button type="button" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats) + "</div>")
    grid = f'<section id="posts"><div class="wrap">{filters}<div class="blog-grid">' + "".join(card(p) for p in posts) + "</div></div></section>"
    s = re.sub(r'<section(?: id="posts")?><div class="wrap">(?:<div class="blog-filters".*?</div>)?<div class="blog-grid">.*?</div></div></section>',
               lambda m: grid, s, 1, re.S)
    s = re.sub(r"<script>document\.querySelectorAll\('\.blog-filters button'\).*?</script>", "", s, flags=re.S)
    s = s.replace("</main>", "</main>\n" + FILTER_JS, 1)
    open(path, "w", encoding="utf-8").write(s)


def build():
    posts = [parse(f) for f in sorted(glob.glob("_posts/*.md"))]
    for p in posts:
        assert p["category"] in CATEGORIES, (p["slug"], p["category"])
    all_posts = sorted(posts + LEGACY, key=lambda p: (p["date"], p["title"]), reverse=True)
    for p in posts:
        os.makedirs(f"{BLOG}/{p['slug']}", exist_ok=True)
        open(f"{BLOG}/{p['slug']}/index.html", "w", encoding="utf-8").write(render_post(p, all_posts))
    render_index(all_posts)
    print(f"blog: {len(posts)} generated, {len(all_posts)} total")
