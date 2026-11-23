"""Erzeugt die Sonderseiten "Reime auf …" für faltsch-wagoni.de/seiten/.

Die Reimwörter werden beim Erzeugen aus reime.csv in die Seite geschrieben
(damit Google sie sieht) und beim Aufruf im Browser zusätzlich frisch von
GitHub geladen (damit neue Reime ohne neues Erzeugen sofort erscheinen).

Aufruf:  python3 sonderseiten.py pfad/zu/reime.csv ausgabeordner
"""
import csv, html, json, sys
from pathlib import Path

BASIS = 'https://www.faltsch-wagoni.de/seiten/'
CSV_URL = 'https://faltschwagoni.github.io/reimprojekt/reime.csv'
LOGO = 'https://imgur.com/oYc2rIO.jpeg'
MAX_VERWANDT = 16

SEITEN = [
  {
    'wort': 'Hochzeit', 'datei': 'reime-auf-hochzeit.html', 'aktiv': False,  # vorerst nicht veröffentlicht
    'beschreibung': 'Was reimt sich auf Hochzeit? Reime auf Hochzeit und auf Braut, Paar, Ringe, Kuss und Treue – mit Tipps und Gedicht für Hochzeitsgedichte, Hochzeitslieder und Reden.',
    'intro': ['„Hochzeit“ ist ein tückisches Wort. Die Betonung liegt auf <em>Hoch</em>, und damit bleiben nur Reime, die auf <em>-och-Zeit</em> enden. Das sind nicht viele.',
              'Wer ein Hochzeitsgedicht, ein Lied für das Brautpaar oder eine gereimte Rede schreibt, braucht das Wort aber ständig. Hier sind die Reime, die wirklich funktionieren – und Wörter rund um die Hochzeit, auf die sich viel leichter reimen lässt.'],
    'tipp': 'Stell „Hochzeit“ nicht ans Zeilenende, sondern in die Mitte des Verses – und reime auf ein Wort, das leichter zu bedienen ist: Braut, Paar, Ring, Kuss. „Heute ist die Hochzeit, alle sind gekommen, / die Braut hat sich den Bräutigam genommen.“',
    'verwandt': ['Braut', 'Paar', 'Ringe', 'Kuss', 'Treue', 'Flitterwochen'],
  },
  {
    'wort': 'Geburtstag', 'datei': 'reime-auf-geburtstag.html',
    'beschreibung': 'Was reimt sich auf Geburtstag? Reime auf Geburtstag und auf Kerzen, Torte, Kuchen, Geschenk und Party – mit Tipps und Gedicht für Geburtstagsgedichte und Glückwunschkarten.',
    'intro': ['Für eine Geburtstagskarte reimt so gut wie jeder einmal im Jahr. Und dann merkt man: Auf „Geburtstag“ reimt sich fast nichts. Die Betonung liegt auf <em>-burts-</em>, und da muss der Reim mitgehen.',
              'Ein paar Reime gibt es trotzdem – nicht alle salonfähig. Weiter unten finden Sie Wörter rund um den Geburtstag, mit denen sich ein Glückwunschgedicht viel leichter reimen lässt.'],
    'tipp': 'Verstecken Sie „Geburtstag“ in der Zeile und reimen Sie auf das, was dazugehört: „Zum Geburtstag nur das Beste, / Kerzen, Kuchen, viele Gäste.“ Auch die Zahl selbst hilft: „Heute wirst du fünfzig Jahre – / und hast immer noch Haare.“',
    'vers': ['Die Nacht war lang und finster,', 'dann aber endlich wurd’s Tag.', 'Du wachtest auf und stelltest fest:', 'Ich habe heut Geburtstag!'],
    'verwandt': ['Kerzen', 'Torte', 'Kuchen', 'Geschenk', 'feiern', 'Party'],
  },
  {
    'wort': 'Monat', 'datei': 'reime-auf-monat.html', 'gruppe': 'ONAT',
    'beschreibung': 'Was reimt sich auf Monat? Klangbasierte Reime auf Monat und auf die Monatsnamen von Januar bis Dezember – mit Tipps und Gedicht.',
    'intro': ['„Monat“ gilt als eines der Wörter, auf die sich nichts reimt. Stimmt nicht ganz. Die Betonung liegt auf <em>Mo-</em>, und das <em>-nat</em> danach klingt fast wie „hat“.',
              'Wer das ausnutzt, findet Reime aus zwei Wörtern: „Lohn hat“, „schon hat“, „davon hat“. Dazu die Reime auf die Monatsnamen – bei einigen wird es überraschend leicht, bei anderen bleibt es eine Herausforderung.'],
    'tipp': 'Reime aus zwei Wörtern sind kein Notbehelf, sondern ein Klassiker des Kabaretts. Sie wirken oft witziger als ein glatter Reim, weil der Zuhörer die Pointe nicht kommen sieht. Achten Sie darauf, dass beim Sprechen die Betonung stimmt: <em>MO-nat</em> – <em>Tradi-ti-ON hat</em>.',
    'vers': ['Und zwar, weil das so ist', 'und allseits Tradition hat,', 'jahraus, jahrein am gleichen Tag', 'im immergleichen Monat.'],
    'verwandt': ['Januar / Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September / November / Dezember', 'Oktober'],
  },
  {
    'wort': 'Abend', 'datei': 'reime-auf-abend.html',
    'beschreibung': 'Was reimt sich auf Abend? Reime auf Abend, Feierabend und Polterabend sowie auf Nacht, Mond, Sterne, Ruh und Wein – mit Tipps und Gedicht für Gedichte und Liedtexte.',
    'intro': ['Der Abend ist eines der großen Themen der Lyrik – vom Abendlied bis zum Feierabend. Gereimt wird darauf meistens mit Partizipien: labend, trabend, grabend.',
              'Das klingt schnell altmodisch, kann aber gerade deshalb reizvoll sein. Hier finden Sie die Reime auf „Abend“ und auf Wörter, die zum Abend gehören.'],
    'tipp': 'Partizipien wie „labend“ oder „trabend“ wirken feierlich – oder komisch, je nachdem, wie man sie einsetzt. Wer es moderner mag, reimt auf das, was am Abend passiert: Nacht, Mond, Sterne, Wein, Bett.',
    'vers': ['Altersmüde und frustriert,', 'sich zu Haus vergrabend,', 'kannst du später immer noch –', 'doch heut ist FEIERabend.'],
    'verwandt': ['Nacht', 'Mond', 'Sterne', 'Ruh', 'Wein', 'Bett'],
  },
  {
    'wort': 'Jubiläum', 'datei': 'reime-auf-jubilaeum.html',
    'beschreibung': 'Was reimt sich auf Jubiläum? Reime auf Jubiläum wie Museum und Mausoleum sowie auf Jahre, Treue, Dank, Ehre und Kollegen – mit Tipps und Gedicht für Reden und Gedichte zum Firmenjubiläum.',
    'intro': ['Für ein Firmen- oder Dienstjubiläum wird gern gereimt – in der Rede, im Gedicht, auf der Karte. Die Reime auf „Jubiläum“ allerdings haben es in sich: Museum, Mausoleum, Tedeum.',
              'Das ist nichts für eine feierliche Rede, aber perfekt für eine humorvolle. Hier finden Sie die Reime auf „Jubiläum“ und auf Wörter, die zu jedem Jubiläum passen.'],
    'tipp': 'Ein Reim wie „Jubiläum – Museum“ funktioniert nur mit einem Augenzwinkern. Oft hilft ein Reim aus zwei Wörtern: „Tee um – Jubiläum“. Setzen Sie ihn bewusst als Pointe ans Ende. Für die ernsten Passagen reimen Sie lieber auf Treue, Dank, Jahre und Ehre.',
    'vers': ['Beim Frühstück kriegst du einen Schreck', 'und kippst ein Tässchen Tee um.', 'Schon wieder eine runde Zahl!', 'Schon wieder Jubiläum!'],
    'verwandt': ['Jahre', 'Treue', 'Dank', 'Ehre', 'Kollegen', 'Chef'],
  },
]


GEDICHT_TITEL = 'Beispiel für ein Geburtstagsgedicht'
GEDICHT = [
  ['Die Nacht war lang und finster,', 'dann aber endlich wurd’s Tag.', 'Du wachtest auf und stelltest fest:', 'Ich habe heut Geburtstag!'],
  ['Und zwar, weil das so ist', 'und allseits Tradition hat,', 'jahraus, jahrein am gleichen Tag', 'im immergleichen Monat.'],
  ['Beim Frühstück kriegst du einen Schreck', 'und kippst ein Tässchen Tee um.', 'Schon wieder eine runde Zahl!', 'Schon wieder Jubiläum!'],
  ['Da musst du durch mit Haut und Haar,', 'auch wenn du denkst: Au weia!', 'Ich bin zu alt für den Bohei –', 'wir schmeißen dir ’ne Feier.'],
  ['Altersmüde und frustriert,', 'sich zu Haus vergrabend,', 'kannst du später immer noch –', 'doch heut ist FEIERabend.'],
]

SEITEN.append({
    'wort': 'Feier', 'datei': 'reime-auf-feier.html',
    'beschreibung': 'Was reimt sich auf Feier? Reime auf Feier wie Abenteuer, Befreier und „au weia“ sowie auf Fest, Gäste, Sekt, Prost und Sause – mit Tipps und Gedicht für Einladungen, Toasts und Feiergedichte.',
    'intro': ['„Feier“ ist ein dankbares Wort. Die Endung <em>-eier</em> teilt es mit Befreier, Betreuer, Leier und Schleier – nach Klang sogar mit „Abenteuer“ und „au weia“.',
              'Für Einladungen, Trinksprüche und Gedichte zum Fest ist das ein Glück. Hier finden Sie die Reime auf „Feier“ und auf Wörter, die zu jeder Feier gehören.'],
    'tipp': 'Bei „Feier“ ist die Auswahl groß – umso mehr lohnt es sich, nicht den erstbesten Reim zu nehmen. Ein Ausruf wie „au weia“ oder ein Klangreim wie „Abenteuer“ macht den Vers lebendiger als die naheliegende „Leier“.',
    'vers': ['Da musst du durch mit Haut und Haar,', 'auch wenn du denkst: Au weia!', 'Ich bin zu alt für den Bohei –', 'wir schmeißen dir ’ne Feier.'],
    'verwandt': ['Fest', 'Gäste', 'Sekt', 'Prost', 'tanzen', 'Sause'],
})
REIHENFOLGE = ['Geburtstag', 'Monat', 'Jubiläum', 'Feier', 'Abend', 'Hochzeit']  # wie im Gedicht
SEITEN.sort(key=lambda x: REIHENFOLGE.index(x['wort']) if x['wort'] in REIHENFOLGE else 99)
SEITEN = [x for x in SEITEN if x.get('aktiv', True)]


def lese_gruppen(pfad):
    gruppen = []
    with open(pfad, encoding='utf-8-sig', newline='') as f:
        for zeile in csv.reader(f, delimiter=';'):
            felder = [x.replace('"', '').strip() for x in zeile if x.strip()]
            if len(felder) >= 2 and felder[0].lower() != 'reime':
                gruppen.append({'name': felder[0], 'words': felder[1:]})
    return gruppen


def ohne_hinweis(w):
    i = w.find(' (')
    return (w[:i] if i >= 0 else w).strip()


def finde_gruppe(gruppen, wort):
    """Gleiche Logik wie der Reimfinder: erst Wortsuche, dann Gruppenname."""
    k = wort.lower()
    treffer = [g for g in gruppen if any(ohne_hinweis(w).lower() == k for w in g['words'])]
    if treffer:
        treffer.sort(key=lambda g: len(g['words']))
        return treffer[0]
    for g in gruppen:
        if g['name'].lower() == k:
            return g
    return None


def sortiert(words, ohne):
    gesehen, liste = set(), []
    for w in words:
        if ohne_hinweis(w).lower() == ohne.lower() or w.lower() in gesehen:
            continue
        gesehen.add(w.lower())
        liste.append(w)
    gross = [w for w in liste if w[:1].isupper()]
    klein = [w for w in liste if not w[:1].isupper()]
    return gross + klein


def wort_html(w):
    e = html.escape(w)
    i = e.find(' (')
    if i >= 0:
        e = e[:i] + ' <em>' + e[i + 1:] + '</em>'
    return f'<li>{e}</li>'


def liste_html(words):
    return ''.join(wort_html(w) for w in words)


def link_reimfinder(wort):
    from urllib.parse import quote
    return 'Reimfinder.html?wort=' + quote(wort)


STIL = '''
:root{--bg:#07565a;--card:#0d6468;--rand:#3f8a8c;--text:#fff;--leise:#d7e7e5;--orange:#e87527;--rot:#ff5a78}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font-family:'Jost',Arial,Helvetica,sans-serif;font-size:1.08rem;line-height:1.7}
a{color:#fff}
.seite{max-width:1180px;margin:0 auto;padding:18px 24px 40px}
.kopf{display:grid;grid-template-columns:200px minmax(0,1fr);column-gap:50px;align-items:center;margin-bottom:26px}
.kopf img{display:block;width:100%;height:auto}
.kopf .dach{margin:0;font-size:1rem;color:var(--leise)}
.kopf .dach a{color:var(--leise)}
h1{margin:2px 0 4px;font-weight:600;font-size:clamp(1.8rem,3.5vw,2.8rem);line-height:1.1}
.slogan{margin:6px 0 0;color:var(--rot);font-style:italic;font-weight:500}
.inhalt{margin-left:250px}
.suche{display:flex;gap:10px;margin:0 0 30px}
.suche input{flex:1;min-width:0;padding:13px 16px;font:inherit;font-size:1.05rem;border:0;border-radius:4px;color:#111}
.suche button{padding:12px 24px;font:inherit;font-weight:700;border:0;border-radius:4px;background:var(--orange);color:#fff;cursor:pointer}
.intro p{margin:0 0 14px}
h2{margin:34px 0 12px;font-weight:600;font-size:1.55rem;line-height:1.25}
h3{margin:0 0 10px;font-weight:600;font-size:1.15rem;color:var(--orange)}
ul.reime{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
ul.reime li{background:var(--card);border:1px solid var(--rand);border-radius:4px;padding:10px 12px;text-align:center}
ul.reime li em{font-size:.85em;color:var(--leise)}
.hauptreime ul.reime li{font-size:1.15rem;font-weight:500}
.anzahl{margin:10px 0 0;color:var(--leise);font-size:.95rem}
.tipp,.vers{background:var(--card);border-left:4px solid var(--orange);padding:16px 20px;margin:0}
.vers{border-left-color:var(--rot);font-style:italic;font-size:1.12rem;line-height:1.75}
.vers p{margin:0 0 16px;padding-left:12px;border-left:3px solid transparent}
.vers p.passend{border-left-color:var(--orange);font-weight:500}
.gedicht-erklaerung{margin:0 0 14px}
.vers .gedicht-titel{font-style:normal;font-weight:600;padding-left:0;border:0}
.vers .gedicht-autor{margin:0;font-style:normal;color:var(--leise);font-size:.95rem;padding-left:0;border:0}
.verwandt{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px}
.verwandt ul.reime{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:6px}
.verwandt ul.reime li{padding:6px 8px;font-size:.95rem}
.mehr{display:inline-block;margin-top:8px;font-size:.95rem}
.weiter ul{margin:0;padding-left:20px}
footer{margin-top:40px;color:var(--leise);font-size:.9rem}
@media (max-width:899px){
  .kopf{grid-template-columns:110px minmax(0,1fr);column-gap:20px}
  .inhalt{margin-left:0}
}
@media (max-width:600px){
  .seite{padding:12px 16px 30px}
  .kopf{grid-template-columns:76px minmax(0,1fr);column-gap:14px;align-items:start}
  h1{font-size:1.55rem}
  .suche{flex-direction:column}
  ul.reime{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
  .verwandt{grid-template-columns:1fr}
}
'''

SKRIPT = '''
(function(){
  var KONFIG = %s;
  function ohne(w){var i=w.indexOf(' (');return (i>=0?w.slice(0,i):w).trim();}
  function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function wortHtml(w){var e=esc(w),i=e.indexOf(' (');if(i>=0)e=e.slice(0,i)+' <em>'+e.slice(i+1)+'</em>';return '<li>'+e+'</li>';}
  function finde(gr,wort){var k=wort.toLocaleLowerCase('de');
    var t=gr.filter(function(g){return g.words.some(function(w){return ohne(w).toLocaleLowerCase('de')===k;});});
    if(t.length){t.sort(function(a,b){return a.words.length-b.words.length;});return t[0];}
    for(var i=0;i<gr.length;i++){if(gr[i].name.toLocaleLowerCase('de')===k)return gr[i];}return null;}
  function sortiert(words,o){var s={},l=[];words.forEach(function(w){var k=w.toLocaleLowerCase('de');
    if(ohne(w).toLocaleLowerCase('de')===o.toLocaleLowerCase('de')||s[k])return;s[k]=1;l.push(w);});
    var g=l.filter(function(w){var c=w.charAt(0);return c!==c.toLocaleLowerCase('de');});
    var kl=l.filter(function(w){var c=w.charAt(0);return c===c.toLocaleLowerCase('de');});return g.concat(kl);}
  function zahl(n){return n.toLocaleString('de-DE');}
  function aktualisiere(gr){
    var h=finde(gr,KONFIG.wort);if(KONFIG.gruppe){for(var j=0;j<gr.length;j++){if(gr[j].name===KONFIG.gruppe){h=gr[j];break;}}}var el=document.getElementById('hauptliste');
    if(h&&el){var w=sortiert(h.words,KONFIG.wort);el.innerHTML=w.map(wortHtml).join('');
      var a=document.getElementById('hauptanzahl');if(a)a.innerHTML=zahl(w.length)+(w.length===1?' Reimwort':' Reimwörter')+' in der Reimgruppe <a href="Reimfinder.html?wort='+encodeURIComponent(h.name)+'">-'+esc(h.name.toLocaleLowerCase('de'))+'</a>';}
    KONFIG.verwandt.forEach(function(v,i){var t=v.split(' / '),g=finde(gr,t[0]),ul=document.getElementById('verwandt-'+i);if(!g||!ul)return;
      var w=sortiert(g.words,t[0]).filter(function(x){return t.every(function(n){return ohne(x).toLocaleLowerCase('de')!==n.toLocaleLowerCase('de');});});ul.innerHTML=w.slice(0,%d).map(wortHtml).join('');
      var m=document.getElementById('verwandt-mehr-'+i);if(m)m.textContent='alle '+zahl(w.length)+' Reime auf „'+v+'“ im Reimfinder →';});
  }
  function decode(buf){try{return new TextDecoder('utf-8',{fatal:true}).decode(buf);}catch(e){return new TextDecoder('windows-1252').decode(buf);}}
  fetch(KONFIG.csv,{cache:'no-cache'}).then(function(r){if(!r.ok)throw new Error(r.status);return r.arrayBuffer();})
  .then(function(b){var gr=decode(b).replace(/^\\uFEFF/,'').trim().split(/\\r?\\n/).map(function(z){
      var f=z.split(';').map(function(x){return x.replace(/"/g,'').trim();}).filter(function(x){return x.length;});
      if(f.length<2||f[0].toLocaleLowerCase('de')==='reime')return null;return {name:f[0],words:f.slice(1)};}).filter(Boolean);
    if(gr.length)aktualisiere(gr);})
  .catch(function(){/* Dann bleiben die beim Erzeugen eingetragenen Reime stehen. */});
})();
'''


def seite(s, gruppen, alle):
    wort = s['wort']
    titel = f'Reime auf {wort} – was reimt sich auf {wort}? | Faltsch Wagoni'
    url = BASIS + s['datei']
    h = finde_gruppe(gruppen, wort)
    if s.get('gruppe'):
        h = next((g for g in gruppen if g['name'] == s['gruppe']), None) or h
    if not h:
        sys.exit(f'Keine Reimgruppe für {wort} in reime.csv')
    haupt = sortiert(h['words'], wort)
    anzahl = (f"{len(haupt)} {'Reimwort' if len(haupt) == 1 else 'Reimwörter'} in der Reimgruppe "
              f'<a href="{link_reimfinder(h["name"])}">-{html.escape(h["name"].lower())}</a>')

    verwandt_html = []
    for i, v in enumerate(s['verwandt']):
        # "September / November / Dezember": Wörter mit derselben Reimgruppe zusammenfassen
        teile = v.split(' / ')
        g = finde_gruppe(gruppen, teile[0])
        if not g:
            sys.exit(f'Keine Reimgruppe für {v} in reime.csv')
        w = [x for x in sortiert(g['words'], teile[0]) if ohne_hinweis(x).lower() not in {t.lower() for t in teile}]
        verwandt_html.append(
            f'<section><h3>Reime auf {html.escape(v)}</h3>'
            f'<ul class="reime" id="verwandt-{i}">{liste_html(w[:MAX_VERWANDT])}</ul>'
            f'<a class="mehr" id="verwandt-mehr-{i}" href="{link_reimfinder(teile[0])}">alle {f"{len(w):,}".replace(",", ".")} Reime auf „{html.escape(v)}“ im Reimfinder →</a></section>')

    weitere = ''.join(f'<li><a href="{x["datei"]}">Reime auf {html.escape(x["wort"])}</a></li>'
                      for x in alle if x is not s)
    strophen = []
    for st in GEDICHT:
        klasse = ' class="passend"' if st == s.get('vers') else ''
        strophen.append(f'<p{klasse}>' + '<br>\n'.join(html.escape(z) for z in st) + '</p>')
    gedicht = ''.join(strophen)
    markiert = f' Die Strophe mit „{html.escape(wort)}“ ist markiert.' if s.get('vers') in GEDICHT else ''
    konfig = json.dumps({'wort': wort, 'gruppe': s.get('gruppe', ''), 'verwandt': s['verwandt'], 'csv': CSV_URL}, ensure_ascii=False)
    schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'WebPage', 'name': f'Reime auf {wort}', 'url': url,
        'inLanguage': 'de', 'description': s['beschreibung'],
        'isPartOf': {'@type': 'WebSite', 'name': 'Online-Reimfinder von Faltsch Wagoni', 'url': BASIS + 'Reimfinder.html'},
        'author': {'@type': 'Organization', 'name': 'Faltsch Wagoni', 'url': 'https://www.faltsch-wagoni.de/'},
    }, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(titel)}</title>
<meta name="description" content="{html.escape(s['beschreibung'])}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="Reime auf {html.escape(wort)}">
<meta property="og:description" content="{html.escape(s['beschreibung'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{LOGO}">
<meta name="theme-color" content="#07565a">
<link rel="icon" type="image/png" sizes="192x192" href="/seiten/icons/reimfinder-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap" rel="stylesheet">
<link rel="preconnect" href="https://faltschwagoni.github.io" crossorigin>
<script type="application/ld+json">{schema}</script>
<style>{STIL}</style>
</head>
<body>
<div class="seite">
  <header class="kopf">
    <a href="Reimfinder.html" aria-label="Zum Online-Reimfinder"><img src="{LOGO}" alt="Faltsch Wagoni Logo"></a>
    <div>
      <p class="dach"><a href="Reimfinder.html">Online-Reimfinder von Faltsch Wagoni</a></p>
      <h1>Reime auf {html.escape(wort)}</h1>
      <p class="slogan">Reim dich oder ich fress dich</p>
    </div>
  </header>

  <main class="inhalt">
    <form class="suche" action="Reimfinder.html" method="get" role="search">
      <input type="text" name="wort" placeholder="Anderes Wort eingeben, Reime finden …" aria-label="Suchwort" autocomplete="off">
      <button type="submit">Suchen</button>
    </form>

    <section class="intro">
      {''.join(f'<p>{p}</p>' for p in s['intro'])}
    </section>

    <section class="hauptreime">
      <h2>Was reimt sich auf {html.escape(wort)}?</h2>
      <ul class="reime" id="hauptliste">{liste_html(haupt)}</ul>
      <p class="anzahl" id="hauptanzahl">{anzahl}</p>
    </section>

    <section>
      <h2>Tipp vom Texter</h2>
      <p class="tipp">{s['tipp']}</p>
    </section>

    <section>
      <h2>Beispiel für ein Geburtstagsgedicht</h2>
      <div class="vers">
        {gedicht}
        <p class="gedicht-autor">– Faltsch Wagoni</p>
      </div>
    </section>

    <section>
      <h2>Wörter rund um „{html.escape(wort)}“ – und ihre Reime</h2>
      <div class="verwandt">
        {''.join(verwandt_html)}
      </div>
    </section>

    <section class="weiter">
      <h2>Weitere knifflige Reime</h2>
      <ul>{weitere}<li><a href="Reimfinder.html">Zum Online-Reimfinder – über 70.000 deutsche Reimwörter</a></li></ul>
    </section>

    <footer>© Faltsch Wagoni · <a href="https://www.faltsch-wagoni.de/">faltsch-wagoni.de</a></footer>
  </main>
</div>
<script>{SKRIPT % (konfig, MAX_VERWANDT)}</script>
</body>
</html>
'''


def sitemap(alle):
    urls = ['Reimfinder.html'] + [s['datei'] for s in alle]
    eintraege = ''.join(f'  <url><loc>{BASIS}{u}</loc></url>\n' for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{eintraege}</urlset>\n'


def main():
    csv_pfad, ziel = Path(sys.argv[1]), Path(sys.argv[2])
    ziel.mkdir(parents=True, exist_ok=True)
    gruppen = lese_gruppen(csv_pfad)
    for s in SEITEN:
        (ziel / s['datei']).write_text(seite(s, gruppen, SEITEN), encoding='utf-8')
        print('erstellt:', s['datei'])
    (ziel / 'sitemap-reimfinder.xml').write_text(sitemap(SEITEN), encoding='utf-8')
    print('erstellt: sitemap-reimfinder.xml')


if __name__ == '__main__':
    main()
