# Cassidy Travel

Website for Cassidy Travel, an independent travel advisor of Fora Travel, based in Waynesville, Ohio.

The site is a single static page, `index.html`, served by GitHub Pages from the `main` branch at https://cassidytravel.org/.

## Generated pages

- `guides.html` is built from `data/guides.json`: `python3 scripts/build_guides.py`
- The blog is built from `posts/*.md`: `python3 scripts/build_blog.py` writes `blog/index.html`, one `blog/<slug>.html` per post, `blog/feed.xml` and `sitemap.xml`. See the top of the script for the front matter each post needs.

Both scripts copy the head, header and footer from `index.html`, so rerun them after changing those.
