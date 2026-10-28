"""Build the blog from posts/*.md, reusing the head, header and footer of index.html.

Writes blog/index.html, one blog/<slug>.html per post, blog/feed.xml and sitemap.xml.
Run from the repo root:  python3 scripts/build_blog.py

Each post is a Markdown file with front matter:
    ---
    title: Accessible Ohio: the Cincinnati Zoo
    date: 2026-10-24
    slug: accessible-ohio-cincinnati-zoo
    summary: One or two sentences, under 160 characters. Used for search and link previews.
    checked: October 2026
    image: cincinnati-zoo-elephant
    image_alt: Describe the photo for screen-reader users.
    image_credit: Photo: Patrick Cassidy
    ---
The image fields are optional. "image" is a base name in img/blog/: the build expects
<name>-800.jpg and <name>-1200.jpg (3:2) and uses <name>-og.jpg (1200x630) for link previews.
Supported Markdown: ## and ### headings, paragraphs, - and 1. lists, > quotes,
**bold**, *italic* and [links](https://...).
"""
import datetime
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://cassidytravel.org"
INTAKE = "https://secure.foratravel.com/intake/AOaJHvy4Ll"
NT = '<span class="sr-only"> (opens in a new tab)</span>'
esc = html.escape

index = (ROOT / "index.html").read_text()


def up(fragment):
    """Point relative links one folder up, for pages that live in blog/."""
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"(https?:|mailto:|data:|#|/|\.\./)", url):
            return m.group(0)
        return f'{attr}="../{url}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, fragment)


head_top = index[:index.index("<title>")]
head_icon = index[index.index('<link rel="icon"'):index.index('<link rel="canonical"')]
fonts = index[index.index('<link rel="preconnect"'):index.index("</head>")]
hdr = index[index.index('<a class="skip"'):index.index('<main id="main">')]
hdr = hdr.replace('<a class="mark" href="#top" id="top">', '<a class="mark" href="index.html">')
hdr = hdr.replace('href="#', 'href="index.html#').replace('href="index.html#main"', 'href="#main"')
hdr = up(hdr).replace('href="../blog/"', 'href="./" aria-current="page"')
foot = up(index[index.index('<footer class="foot">'):index.index("</footer>") + len("</footer>")])
head_top = re.sub(r'<meta name="description"[^>]*>\n', "", head_top)


def page(title, description, path, body, og_type="website", og_image="img/patrick-640.jpg"):
    url = f"{SITE}/{path}"
    return (head_top
            + f'<meta name="description" content="{esc(description)}">\n<title>{esc(title)}</title>\n'
            + head_icon
            + f'<link rel="canonical" href="{url}">\n'
            + f'<meta property="og:type" content="{og_type}">\n<meta property="og:url" content="{url}">\n'
            + f'<meta property="og:title" content="{esc(title)}">\n'
            + f'<meta property="og:image" content="{SITE}/{og_image}">\n'
            + f'<meta property="og:description" content="{esc(description)}">\n'
            + f'<link rel="alternate" type="application/rss+xml" title="Cassidy Travel blog" href="{SITE}/blog/feed.xml">\n'
            + up(fonts) + "</head>\n<body>\n\n" + hdr + '<main id="main">\n' + body
            + "\n</main>\n\n" + foot + '\n\n<script src="../site.js"></script>\n</body>\n</html>\n')


def inline(text):
    text = esc(text, quote=False)

    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith("http"):
            return f'<a href="{url}" target="_blank" rel="noopener">{label}{NT}</a>'
        return f'<a href="{url}">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", text)
    return text


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def markdown(src):
    out, para, items, kind, quote = [], [], [], None, []

    def flush():
        nonlocal para, items, kind, quote
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        if items:
            out.append(f"<{kind}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{kind}>")
        if quote:
            out.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
        para, items, kind, quote = [], [], None, []

    for line in src.splitlines():
        s = line.strip()
        m_ul = re.match(r"[-*] (.+)", s)
        m_ol = re.match(r"\d+\. (.+)", s)
        if not s:
            flush()
        elif s.startswith("### "):
            flush()
            out.append(f'<h3 id="{slugify(s[4:])}">{inline(s[4:])}</h3>')
        elif s.startswith("## "):
            flush()
            out.append(f'<h2 id="{slugify(s[3:])}">{inline(s[3:])}</h2>')
        elif s.startswith("> "):
            if para or items:
                flush()
            quote.append(s[2:])
        elif m_ul or m_ol:
            new = "ul" if m_ul else "ol"
            if para or quote or (kind and kind != new):
                flush()
            kind = new
            items.append((m_ul or m_ol).group(1))
        elif items and line.startswith("  "):
            items[-1] += " " + s
        else:
            if items or quote:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


def read_post(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    if meta.get("image"):
        for size in ("800", "1200", "og"):
            if not (ROOT / "img" / "blog" / f'{meta["image"]}-{size}.jpg').exists():
                raise SystemExit(f'{path.name}: missing img/blog/{meta["image"]}-{size}.jpg')
        if not meta.get("image_alt"):
            raise SystemExit(f"{path.name}: an image needs image_alt")
    for key in ("title", "date", "slug", "summary"):
        if not meta.get(key):
            raise SystemExit(f"{path.name}: front matter needs {key}")
    if not re.fullmatch(r"[a-z0-9-]+", meta["slug"]):
        raise SystemExit(f"{path.name}: slug may only use a-z, 0-9 and -")
    meta["day"] = datetime.date.fromisoformat(meta["date"])
    meta["html"] = markdown(m.group(2))
    return meta


def nice(day):
    return f"{day.strftime('%B')} {day.day}, {day.year}"


posts = sorted((read_post(p) for p in (ROOT / "posts").glob("*.md")), key=lambda p: p["day"], reverse=True)
out_dir = ROOT / "blog"
out_dir.mkdir(exist_ok=True)
for old in out_dir.glob("*.html"):
    old.unlink()

for p in posts:
    figure, og_image = "", "img/patrick-640.jpg"
    if p.get("image"):
        base = f'../img/blog/{p["image"]}'
        credit = f'<figcaption>{esc(p["image_credit"])}</figcaption>' if p.get("image_credit") else ""
        figure = (f'\n    <figure class="post-figure wrap narrow"><img src="{base}-1200.jpg" srcset="{base}-800.jpg 800w, {base}-1200.jpg 1200w" '
                  f'sizes="(min-width: 860px) 820px, 100vw" width="1200" height="800" alt="{esc(p["image_alt"])}">{credit}</figure>')
        og_image = f'img/blog/{p["image"]}-og.jpg'
    checked = f' Checked {esc(p["checked"])}; confirm before you go.' if p.get("checked") else ""
    body = f'''  <article class="post" aria-labelledby="post-h">
    <header class="page-hero">
      <div class="wrap">
        <p class="eyebrow"><a href="./">Blog</a></p>
        <h1 id="post-h">{esc(p["title"])}</h1>
        <p class="post-meta">By Patrick Cassidy · <time datetime="{p["date"]}">{nice(p["day"])}</time></p>
        <p class="post-disclose">Cassidy Travel, independent travel advisor of Fora Travel.{checked}</p>
      </div>
    </header>{figure}
    <div class="block"><div class="wrap narrow post-body">
{p["html"]}
      <div class="post-cta">
        <p>Planning a trip like this? There's no planning fee for vacations.</p>
        <p><a class="btn" href="{INTAKE}" target="_blank" rel="noopener">Start planning with Patrick{NT}</a></p>
        <p><a class="back" href="./">More from the blog</a> · <a href="../guides.html">Accessibility guides</a></p>
      </div>
    </div></div>
  </article>'''
    (out_dir / f'{p["slug"]}.html').write_text(page(f'{p["title"]} | Cassidy Travel', p["summary"], f'blog/{p["slug"]}.html', body, "article", og_image))

cards = "\n".join(
    f'''      <li class="post-card"><a href="{p["slug"]}.html"><h2>{esc(p["title"])}</h2></a>
        <p class="post-meta"><time datetime="{p["date"]}">{nice(p["day"])}</time></p>
        <p>{esc(p["summary"])}</p></li>''' for p in posts) or "      <li>No posts yet.</li>"
index_body = f'''  <section class="page-hero" aria-labelledby="page-h">
    <div class="wrap">
      <p class="eyebrow">Blog</p>
      <h1 id="page-h">Notes from a travel advisor who checks the details.</h1>
      <p class="lede">Accessibility guides to places near Waynesville and beyond, planning tips for cruises and theme parks, and what I learn along the way.</p>
      <p class="cta-note">Cassidy Travel, independent travel advisor of Fora Travel. <a href="feed.xml">Subscribe by RSS</a>.</p>
    </div>
  </section>
  <section class="block" aria-label="Posts"><div class="wrap narrow">
    <ul class="post-list">
{cards}
    </ul>
  </div></section>'''
(out_dir / "index.html").write_text(page("Blog | Cassidy Travel", "Accessibility guides, cruise and theme park planning tips, and travel notes from Cassidy Travel in Waynesville, Ohio.", "blog/", index_body))

items = "\n".join(f'''  <item>
    <title>{esc(p["title"])}</title>
    <link>{SITE}/blog/{p["slug"]}.html</link>
    <guid>{SITE}/blog/{p["slug"]}.html</guid>
    <pubDate>{datetime.datetime.combine(p["day"], datetime.time(12)).strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
    <description>{esc(p["summary"])}</description>
  </item>''' for p in posts)
(out_dir / "feed.xml").write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Cassidy Travel blog</title>
  <link>{SITE}/blog/</link>
  <description>Accessibility guides and planning tips from Cassidy Travel, independent travel advisor of Fora Travel.</description>
  <language>en-us</language>
{items}
</channel>
</rss>
''')

urls = [("", "daily"), ("teams.html", None), ("guides.html", None), ("cruise-lines.html", None), ("blog/", "weekly")] + [(f'blog/{p["slug"]}.html', None) for p in posts]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url>\n    <loc>{SITE}/{u}</loc>\n" + (f"    <changefreq>{c}</changefreq>\n" if c else "") + "  </url>\n" for u, c in urls)
    + "</urlset>\n")
print(f"wrote blog/ with {len(posts)} post(s), feed.xml and sitemap.xml")
