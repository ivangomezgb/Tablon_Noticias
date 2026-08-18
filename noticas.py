import feedparser
import os
import webbrowser
from datetime import datetime, timedelta
from time import mktime
import tablon_noticias.html

# Fuentes RSS por categoría
FEEDS = {
    "Ciberseguridad Global": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/",
        "https://krebsonsecurity.com/feed/",
        "https://www.darkreading.com/rss.xml"
    ],
    "Desarrollo & IA": [
        "https://hnrss.org/frontpage",
        "https://dev.to/feed",
        "https://www.unite.ai/feed/"
    ],
    "Colombia & Regional": [
        "https://news.google.com/rss/search?q=ciberseguridad+colombia&hl=es-419&gl=CO&ceid=CO:es-419"
    ]
}

def parse_date(entry):
    """Extrae y formatea la fecha del feed."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime.fromtimestamp(mktime(entry.published_parsed))
    return datetime.now()

def get_raw_news(hours_back=48):
    """Recolecta las noticias en el rango de horas configurado."""
    time_limit = datetime.now() - timedelta(hours=hours_back)
    all_news = []

    for category, urls in FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    pub_date = parse_date(entry)
                    if pub_date >= time_limit:
                        all_news.append({
                            "category": category,
                            "title": entry.title,
                            "link": entry.link,
                            "date": pub_date.strftime("%Y-%m-%d %H:%M")
                        })
            except Exception as e:
                print(f"Error cargando {url}: {e}")

    # Ordenar por fecha reciente
    return sorted(all_news, key=lambda x: x['date'], reverse=True)

def generate_html_dashboard(news_list, output_file="tablon_noticias.html"):
    """Genera una página HTML interactiva y estilizada."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tablón de Noticias Tech & Ciberseguridad</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyber: #38bdf8;
            --accent-dev: #a855f7;
            --accent-local: #f59e0b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 2rem 1rem;
            line-height: 1.5;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
        }}

        header h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(to right, #38bdf8, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .stats-bar {{
            display: flex;
            justify-content: space-between;
            background-color: var(--card-bg);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            margin-bottom: 2rem;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.25rem;
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .card:hover {{
            transform: translateY(-3px);
            border-color: #475569;
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
            width: fit-content;
        }}

        .badge-cyber {{ background-color: rgba(56, 189, 248, 0.15); color: var(--accent-cyber); border: 1px solid rgba(56, 189, 248, 0.3); }}
        .badge-dev {{ background-color: rgba(168, 85, 247, 0.15); color: var(--accent-dev); border: 1px solid rgba(168, 85, 247, 0.3); }}
        .badge-local {{ background-color: rgba(245, 158, 11, 0.15); color: var(--accent-local); border: 1px solid rgba(245, 158, 11, 0.3); }}

        .title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-main);
        }}

        .meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--card-border);
            padding-top: 0.75rem;
        }}

        .btn-link {{
            color: var(--accent-cyber);
            text-decoration: none;
            font-weight: 500;
        }}

        .btn-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ Tablón de Noticias Tech & Ciberseguridad</h1>
            <p>Noticias directas sin intermediarios ni IA</p>
        </header>

        <div class="stats-bar">
            <span>Total noticias: <strong>{len(news_list)}</strong></span>
            <span>Última actualización: <strong>{now_str}</strong></span>
        </div>

        <div class="grid">
"""

    for item in news_list:
        cat = item['category']
        badge_class = "badge-cyber"
        if "Desarrollo" in cat:
            badge_class = "badge-dev"
        elif "Colombia" in cat:
            badge_class = "badge-local"

        html_content += f"""
            <div class="card">
                <div>
                    <span class="badge {badge_class}">{cat}</span>
                    <h2 class="title">{item['title']}</h2>
                </div>
                <div class="meta">
                    <span>{item['date']}</span>
                    <a href="{item['link']}" target="_blank" class="btn-link">Leer noticia &rarr;</a>
                </div>
            </div>
"""

    html_content += """
        </div>
    </div>
</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f" Archivo generado: {os.path.abspath(output_file)}")
    
    # Abre automáticamente el navegador predeterminado con el resultado
    webbrowser.open('file://' + os.path.abspath(output_file))

if __name__ == "__main__":
    print(" Cargando feeds RSS...")
    news = get_raw_news(hours_back=48)
    generate_html_dashboard(news)