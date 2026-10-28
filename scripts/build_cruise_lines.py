"""Build cruise-lines.html from data/cruise-lines.html, reusing the head, header and footer of index.html.

data/cruise-lines.html holds the page body: the cruise line cards, the Alaska spotlight and the comparison tables.
Its styles are the "cruise line guide" block at the end of styles.css.
Run from the repo root:  python3 scripts/build_cruise_lines.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
index = (ROOT / "index.html").read_text()
body = (ROOT / "data" / "cruise-lines.html").read_text()

TITLE = "Cruise Line Guide"
DESC = "Compare ten cruise lines side by side: who each suits, price tier, what's included, dining, destinations and Alaska options."
URL = "https://cassidytravel.org/cruise-lines.html"

head = index[:index.index('<link rel="canonical"')]
head = head.replace("<title>Cassidy Travel</title>", f"<title>{TITLE} | Cassidy Travel</title>")
head = head.replace(
    'content="Cassidy Travel: cruises, resorts, theme parks and family getaways planned from Waynesville, Ohio, with a focus on accessible and multi-generational travel."',
    f'content="{DESC}"',
)
hdr = index[index.index('<a class="skip"'):index.index('<main id="main">')]
hdr = hdr.replace('<a class="mark" href="#top" id="top">', '<a class="mark" href="index.html">')
hdr = hdr.replace('href="#', 'href="index.html#').replace('href="index.html#main"', 'href="#main"')
hdr = hdr.replace('<a href="cruise-lines.html">', '<a href="cruise-lines.html" aria-current="page">')
foot = index[index.index('<footer class="foot">'):index.index("</footer>") + len("</footer>")]

page = head + f'''<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{TITLE} | Cassidy Travel">
<meta property="og:image" content="https://cassidytravel.org/img/cruise/alaska-deck.jpg">
<meta property="og:description" content="{DESC}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Nunito:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="styles.css">
</head>
<body>

{hdr}<main id="main">
{body}</main>

{foot}

<script src="site.js"></script>
</body>
</html>
'''
(ROOT / "cruise-lines.html").write_text(page)
print("wrote cruise-lines.html")
