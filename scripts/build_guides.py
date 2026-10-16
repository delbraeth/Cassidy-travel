"""Build guides.html from data/guides.json, reusing the head, header and footer of index.html.

Run from the repo root:  python3 scripts/build_guides.py
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "guides.json").read_text())
index = (ROOT / "index.html").read_text()

NT = '<span class="sr-only"> (opens in a new tab)</span>'
esc = html.escape

head = index[:index.index('<link rel="canonical"')]
head = head.replace("<title>Cassidy Travel</title>", "<title>Accessibility Guides</title>")
head = head.replace(
    'content="Cassidy Travel: cruises, resorts, theme parks and family getaways planned from Waynesville, Ohio, with a focus on accessible and multi-generational travel."',
    'content="Links to official accessibility guides for attractions near Waynesville, Ohio, regional getaways, Orlando, cruise lines, resorts and airports."',
)
hdr = index[index.index('<a class="skip"'):index.index('<main id="main">')]
hdr = hdr.replace('<a class="mark" href="#top" id="top">', '<a class="mark" href="index.html">')
hdr = hdr.replace('href="#', 'href="index.html#').replace('href="index.html#main"', 'href="#main"')
foot = index[index.index('<footer class="foot">'):index.index("</footer>") + len("</footer>")]

def item(i):
    extra = ""
    if i.get("extra"):
        x = i["extra"]
        extra = f' <a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x["text"])}{NT}</a>'
    return (f'<li><a class="g-name" href="{esc(i["url"])}" target="_blank" rel="noopener">{esc(i["name"])}{NT}</a>'
            f'<span class="g-about">{esc(i["about"])}{extra}</span></li>')

jump, body = [], []
for s in data["sections"]:
    jump.append(f'<a class="pill" href="#{s["id"]}">{esc(s["title"])}</a>')
    parts = [f'<section class="block" id="{s["id"]}" aria-labelledby="{s["id"]}-h"><div class="wrap narrow">',
             f'<div class="sec-head"><h2 id="{s["id"]}-h">{esc(s["title"])}</h2>' + (f'<p>{esc(s["sub"])}</p>' if s["sub"] else "") + "</div>"]
    for g in s["groups"]:
        if g["place"]:
            parts.append(f'<h3 class="g-place" id="{g["id"]}">{esc(g["place"])}</h3>')
        parts.append('<ul class="g-list">' + "".join(item(i) for i in g["items"]) + "</ul>")
    parts.append("</div></section>")
    body.append("\n".join(parts))

page = head + f'''<link rel="canonical" href="https://cassidytravel.org/guides.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://cassidytravel.org/guides.html">
<meta property="og:title" content="Accessibility Guides | Cassidy Travel">
<meta property="og:image" content="https://cassidytravel.org/img/patrick-640.jpg">
<meta property="og:description" content="Official accessibility guides for attractions near Waynesville, regional getaways, Orlando, cruise lines, resorts and airports.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Nunito:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="styles.css">
</head>
<body>

{hdr}<main id="main">
  <section class="page-hero" aria-labelledby="page-h">
    <div class="wrap">
      <p class="eyebrow">Accessibility guides</p>
      <h1 id="page-h">Every place's own accessibility guide, in one list.</h1>
      <p class="lede">Before I plan a trip, I read the venue's own accessibility page. Here they are for the places my clients go most, from Waynesville to Orlando, plus the cruise lines, resorts and airports I book. Each link goes to the official page.</p>
      <p class="cta-note">Links checked {esc(data["checked"])}. Policies change, so confirm before you go, or <a href="https://secure.foratravel.com/intake/AOaJHvy4Ll" target="_blank" rel="noopener">ask me to check for you{NT}</a>.</p>
      <nav class="g-jump" aria-label="Jump to a section">{"".join(jump)}</nav>
    </div>
  </section>
{chr(10).join(body)}
  <section class="block"><div class="wrap narrow">
    <p><a class="btn" href="https://secure.foratravel.com/intake/AOaJHvy4Ll" target="_blank" rel="noopener">Start planning with Patrick{NT}</a></p>
    <p style="margin-top:18px">Know a guide I should add? Mention it on the planning form. <a class="back" href="index.html">Back to Cassidy Travel</a></p>
  </div></section>
</main>

{foot}

<script src="site.js"></script>
</body>
</html>
'''
(ROOT / "guides.html").write_text(page)
print("wrote guides.html with", sum(len(g["items"]) for s in data["sections"] for g in s["groups"]), "links")
