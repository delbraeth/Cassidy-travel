"""Build standalone landing pages from data/pages/<slug>.html, reusing the head, header and footer of index.html.

Each page body lives in data/pages/<slug>.html; titles and descriptions are listed in PAGES below.
Run from the repo root:  python3 scripts/build_pages.py
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://cassidytravel.org"
PAGES = [
    ("accessible-cruises", "Wheelchair-Accessible Cruises | Patrick Cassidy Travel",
     "Accessible cruise travel agent in Ohio: wheelchair-accessible cabins, tender ports, equipment delivery and drive-to ports, planned by a wheelchair user.",
     "img/cruise/alaska-deck.jpg"),
    ("accessible-disney-world", "Accessible Disney World Planning | Patrick Cassidy Travel",
     "Wheelchair-accessible and autism-friendly Disney World trips planned from Ohio: resorts, rooms, rides, scooters and Disability Access Service.",
     "img/patrick-640.jpg"),
]
esc = html.escape
index = (ROOT / "index.html").read_text()
head_top = index[:index.index('<meta name="description"')]
head_icon = index[index.index('<link rel="icon"'):index.index('<link rel="canonical"')]
fonts = index[index.index('<link rel="preconnect"'):index.index("</head>")]
hdr = index[index.index('<a class="skip"'):index.index('<main id="main">')]
hdr = hdr.replace('<a class="mark" href="#top" id="top">', '<a class="mark" href="index.html">')
hdr = hdr.replace('href="#', 'href="index.html#').replace('href="index.html#main"', 'href="#main"')
foot = index[index.index('<footer class="foot">'):index.index("</footer>") + len("</footer>")]

for slug, title, desc, img in PAGES:
    body = (ROOT / "data" / "pages" / f"{slug}.html").read_text()
    url = f"{SITE}/{slug}.html"
    page = (head_top + f'<meta name="description" content="{esc(desc)}">\n<title>{esc(title)}</title>\n' + head_icon
            + f'<link rel="canonical" href="{url}">\n<meta property="og:type" content="website">\n<meta property="og:url" content="{url}">\n'
            + f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:image" content="{SITE}/{img}">\n'
            + f'<meta property="og:description" content="{esc(desc)}">\n' + fonts + "</head>\n<body>\n\n" + hdr
            + '<main id="main">\n' + body + "</main>\n\n" + foot + '\n\n<script src="site.js"></script>\n</body>\n</html>\n')
    (ROOT / f"{slug}.html").write_text(page)
    print(f"wrote {slug}.html ({len(desc)}-char description)")
