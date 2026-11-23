"""Erzeugt die Seite "Lieber kein Reim als ein schlechter" (warum-dieser-reimfinder.html).

Aufruf:  python3 vergleichsseite.py ausgabeordner
"""
import html, json, sys
from pathlib import Path
import sonderseiten as S

DATEI = 'warum-dieser-reimfinder.html'
URL = S.BASIS + DATEI
TITEL = 'Bessere Reime statt mehr Reime – was diesen Reimfinder anders macht | Faltsch Wagoni'
BESCHREIBUNG = ('Warum der Online-Reimfinder von Faltsch Wagoni nach Klang und Betonung sucht statt nach '
                'Endbuchstaben – mit Beispielen zu Monat, Geburtstag, Jubiläum, Mensch und Dezember.')

BEISPIELE = [
  {
    'wort': 'Monat', 'titel': 'Die Betonung entscheidet',
    'schrift': ['Senat', 'Spinat', 'Salat', 'Kandidat'],
    'schrift_text': 'Alle enden auf <em>-at</em>. Aber sie werden hinten betont: Se-<strong>NAT</strong>, Spi-<strong>NAT</strong>. „Monat“ betont man vorn: <strong>MO</strong>-nat. Laut gelesen reimt sich da nichts.',
    'klang': ['Lohn hat', 'Tradition hat', 'Balkon hat', 'Illusion hat', 'Doughnut'],
    'klang_text': 'Betonung und Klang stimmen: <strong>MO</strong>-nat – <strong>LOHN</strong> hat.',
  },
  {
    'wort': 'Geburtstag', 'titel': 'Gleiche Endung, kein Reim',
    'schrift': ['Montag', 'Feiertag', 'Dienstag', 'Sonntag'],
    'schrift_text': 'Alle enden auf <em>-tag</em>. Doch bei „Geburtstag“ liegt der Ton auf <em>-burts-</em>. „Geburtstag – Montag“ reimt sich nur auf dem Papier.',
    'klang': ['Furztag', 'Kurztag', 'wurd’s Tag'],
    'klang_text': 'Nur drei Vorschläge – aber alle drei klingen.',
  },
  {
    'wort': 'Jubiläum', 'titel': 'Reime aus zwei Wörtern',
    'schrift': [],
    'schrift_text': 'Auf <em>-äum</em> endet kaum ein deutsches Wort. Eine Suche nach Endbuchstaben bleibt leer.',
    'klang': ['Tee um', 'Museum', 'Mausoleum', 'Kolosseum', 'Tedeum'],
    'klang_text': 'Was zählt, ist der Klang: Jubi-<strong>LÄ</strong>-um – Mu-<strong>SE</strong>-um. Dazu kommt ein Reim aus zwei Wörtern: „… und kippst ein Tässchen <strong>Tee um</strong>“.',
  },
  {
    'wort': 'Mensch', 'titel': 'Englisch ausgesprochen',
    'schrift': [],
    'schrift_text': 'Auf <em>-ensch</em> reimt sich im Deutschen fast nichts. Eine Wortliste gibt auf.',
    'klang': ['French (engl.)', 'Trench (engl.)'],
    'klang_text': 'Englisch ausgesprochen klingen sie fast gleich. Dasselbe gilt für „Dezember – remember“ oder „September – Camper“.',
  },
  {
    'wort': 'Psychoanalytiker', 'titel': 'Anders geschrieben, gleich gehört',
    'schrift': ['Politiker', 'Kritiker', 'Analytiker'],
    'schrift_ok': True,
    'schrift_text': 'Die naheliegenden Treffer findet auch eine Suche nach Endbuchstaben – aber nur Wörter, die genauso geschrieben werden.',
    'klang': ['gütiger', '-minütiger', 'Politiker', 'Kritiker'],
    'klang_text': '<em>-iker</em> und <em>-iger</em> klingen beim Sprechen fast gleich. So entstehen überraschende Paare: „Psychoanalytiker – gütiger“.',
  },
]


def wortliste(words, klasse):
    if not words:
        return f'<p class="leer">keine brauchbaren Treffer</p>'
    return f'<ul class="reime {klasse}">' + ''.join(S.wort_html(w) for w in words) + '</ul>'


ZUSATZ_STIL = '''
.beispiel{background:var(--card);border:1px solid var(--rand);border-radius:6px;padding:18px 20px;margin:0 0 22px}
.beispiel h3{margin:0 0 12px;font-size:1.3rem;color:#fff}
.beispiel h3 span{color:var(--orange);font-weight:500}
.spalten{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.spalte h4{margin:0 0 8px;font-size:.95rem;font-weight:600;letter-spacing:.02em;text-transform:uppercase}
.spalte.schrift h4{color:var(--leise)}
.spalte.klang h4{color:var(--orange)}
.spalte p{margin:10px 0 0;font-size:1rem;line-height:1.55}
ul.reime.schrift li{background:transparent;border-style:dashed;color:var(--leise);text-decoration:line-through;text-decoration-color:rgba(255,90,120,.8)}
ul.reime.schrift.ok li{text-decoration:none;color:#fff}
ul.reime.klang li{border-color:var(--orange)}
.beispiel ul.reime{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:6px}
.beispiel ul.reime li{padding:6px 8px;font-size:1rem}
.leer{margin:0;padding:6px 10px;border:1px dashed var(--rand);border-radius:4px;color:var(--leise);font-style:italic}
.beispiel .mehr{margin-top:12px}
.leitsatz{font-size:1.25rem;font-style:italic;color:var(--rot);margin:0 0 18px}
@media (max-width:700px){.spalten{grid-template-columns:1fr;gap:16px}}
'''


def seite():
    beispiele = []
    for b in BEISPIELE:
        beispiele.append(f'''
      <article class="beispiel">
        <h3>{html.escape(b['wort'])} <span>– {html.escape(b['titel'])}</span></h3>
        <div class="spalten">
          <div class="spalte schrift">
            <h4>Nach Schreibweise</h4>
            {wortliste(b['schrift'], 'schrift ok' if b.get('schrift_ok') else 'schrift')}
            <p>{b['schrift_text']}</p>
          </div>
          <div class="spalte klang">
            <h4>Im Reimfinder</h4>
            {wortliste(b['klang'], 'klang')}
            <p>{b['klang_text']}</p>
          </div>
        </div>
        <a class="mehr" href="{S.link_reimfinder(b['wort'])}">Alle Reime auf „{html.escape(b['wort'])}“ im Reimfinder →</a>
      </article>''')

    weitere = ''.join(f'<li><a href="{x["datei"]}">Reime auf {html.escape(x["wort"])}</a></li>' for x in S.SEITEN)
    schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'Article', 'headline': 'Lieber kein Reim als ein schlechter',
        'url': URL, 'inLanguage': 'de', 'description': BESCHREIBUNG,
        'isPartOf': {'@type': 'WebSite', 'name': 'Online-Reimfinder von Faltsch Wagoni', 'url': S.BASIS + 'Reimfinder.html'},
        'author': {'@type': 'Organization', 'name': 'Faltsch Wagoni', 'url': 'https://www.faltsch-wagoni.de/'},
    }, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(TITEL)}</title>
<meta name="description" content="{html.escape(BESCHREIBUNG)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="article">
<meta property="og:title" content="Lieber kein Reim als ein schlechter">
<meta property="og:description" content="{html.escape(BESCHREIBUNG)}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{S.LOGO}">
<meta name="theme-color" content="#07565a">
<link rel="icon" type="image/png" sizes="192x192" href="/seiten/icons/reimfinder-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap" rel="stylesheet">
<script type="application/ld+json">{schema}</script>
<style>{S.STIL}{ZUSATZ_STIL}</style>
</head>
<body>
<div class="seite">
  <header class="kopf">
    <a href="Reimfinder.html" aria-label="Zum Online-Reimfinder"><img src="{S.LOGO}" alt="Faltsch Wagoni Logo"></a>
    <div>
      <p class="dach"><a href="Reimfinder.html">Online-Reimfinder von Faltsch Wagoni</a></p>
      <h1>Lieber kein Reim als ein schlechter</h1>
      <p class="slogan">Reim dich oder ich fress dich</p>
    </div>
  </header>

  <main class="inhalt">
    <form class="suche" action="Reimfinder.html" method="get" role="search">
      <input type="text" name="wort" placeholder="Wort eingeben, Reime finden …" aria-label="Suchwort" autocomplete="off">
      <button type="submit">Suchen</button>
    </form>

    <section class="intro">
      <p>Die meisten Reimlisten im Netz arbeiten nach der Schreibweise: Sie suchen Wörter, die mit denselben Buchstaben enden. Das liefert schnell Hunderte Treffer – nur reimen sich viele davon nicht, sobald man sie laut ausspricht.</p>
      <p>Dieser Reimfinder geht den umgekehrten Weg. Jede Reimgruppe ist von Hand nach <strong>Klang und Betonung</strong> zusammengestellt. Das ergibt weniger Treffer, aber solche, die man in einem Gedicht oder Song wirklich verwenden kann. Fünf Beispiele zeigen den Unterschied.</p>
    </section>

    <section>
      <h2>Fünf Beispiele</h2>
      {''.join(beispiele)}
    </section>

    <section>
      <h2>Warum manchmal so wenige Treffer?</h2>
      <p class="leitsatz">Lieber kein Reim als ein schlechter Reim.</p>
      <p>Bei manchen Wörtern liefert der Reimfinder nur zwei, drei Vorschläge – oder gar keinen. Das ist Absicht. Ein Reim, der beim Vortragen holpert, schadet einem Text mehr, als er nützt. Lieber zeige ich ehrlich, dass es schwierig wird, und biete Auswege an: Reime aus zwei Wörtern, unreine Reime, die gut klingen, oder ein anderes Wort am Zeilenende.</p>
    </section>

    <section>
      <h2>Wie die Reimgruppen entstehen</h2>
      <p>Jede Reimgruppe habe ich als Texter für das Musikkabarett Faltsch Wagoni über Jahre zusammengetragen, und ich erweitere sie laufend. Über 70.000 Wörter sind es inzwischen – sortiert nach dem, was man hört, nicht nach dem, was man liest.</p>
    </section>

    <section class="weiter">
      <h2>Knifflige Reime – mit Tipps vom Texter</h2>
      <ul>{weitere}<li><a href="Reimfinder.html">Zum Online-Reimfinder</a></li></ul>
    </section>

    <footer>© Faltsch Wagoni · <a href="https://www.faltsch-wagoni.de/">faltsch-wagoni.de</a></footer>
  </main>
</div>
</body>
</html>
'''


if __name__ == '__main__':
    ziel = Path(sys.argv[1])
    (ziel / DATEI).write_text(seite(), encoding='utf-8')
    print('erstellt:', DATEI)
