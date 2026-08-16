from pathlib import Path
import re
import sys

QUELLE = Path("Reimlexikon_2.02.html")
ZIEL = Path("Reimlexikon_2.03.html")

if not QUELLE.exists():
    print("Fehler: Reimlexikon_2.02.html wurde nicht gefunden.")
    print("Lege update_2_03.py in denselben Ordner wie Reimlexikon_2.02.html.")
    sys.exit(1)

html = QUELLE.read_text(encoding="utf-8")

if "const csvData = `" not in html:
    print("Fehler: Die Reimdatenbank wurde nicht gefunden.")
    sys.exit(1)

html = html.replace(
    'placeholder="Reimwort eingeben …"',
    'placeholder="Reim oder Wort suchen"'
)
html = html.replace(
    '<span id="statusMessage">Reimwort eingeben.</span>',
    '<span id="statusMessage">Reim oder Wort suchen.</span>'
)
html = html.replace(
    'Gib oben ein Wort ein, um passende Reime anzuzeigen.',
    'Gib oben einen Reim oder ein Wort ein.'
)

if ".case-separator" not in html:
    html = html.replace(
        "</style>",
        """    .case-separator {
      grid-column: 1 / -1;
      height: 10px;
    }
  </style>""",
        1
    )

html = re.sub(
    r"<footer>.*?</footer>",
    "<footer>Reimlexikon – Version 2.03<br>© Faltsch Wagoni 2026</footer>",
    html,
    count=1,
    flags=re.S
)

html = html.replace(
    "status.innerText = 'Reimwort eingeben.';",
    "status.innerText = 'Reim oder Wort suchen.';"
)
html = html.replace(
    "'<div class=\"empty-state\">Gib oben ein Reimwort ein, um passende Reime anzuzeigen.</div>'",
    "'<div class=\"empty-state\">Gib oben einen Reim oder ein Wort ein.</div>'"
)

old_block = "      if (sortByEnding) {\n        results.sort(compareByEnding);\n      }\n\n      status.innerText =\n        `${results.length.toLocaleString('de-DE')} Wörter in der Reimgruppe für „${rawInput}“`;\n\n      const grid = document.createElement('div');\n      grid.className = 'results-grid';\n\n      results.forEach(word => {\n        const card = document.createElement('div');\n        card.className = 'word-card';\n\n        if (normalizeWord(word, ignoreCase) === normalizedInput) {\n          card.classList.add('search-word');\n          card.setAttribute('aria-label', `${word}, gesuchtes Wort`);\n        }\n\n        if (word.length >= 24) {\n          card.classList.add('very-long-word');\n        } else if (word.length >= 18) {\n          card.classList.add('long-word');\n        }\n\n        card.innerText = word;\n        card.title = word;\n        grid.appendChild(card);\n      });\n\n      container.innerHTML = '';\n      container.appendChild(grid);"
new_block = "      const lowercaseWords = results.filter(word => {\n        const firstLetter = word.match(/[A-Za-zÄÖÜäöüß]/);\n        return !firstLetter || firstLetter[0] === firstLetter[0].toLocaleLowerCase('de');\n      });\n\n      const uppercaseWords = results.filter(word => {\n        const firstLetter = word.match(/[A-Za-zÄÖÜäöüß]/);\n        return firstLetter && firstLetter[0] === firstLetter[0].toLocaleUpperCase('de')\n          && firstLetter[0] !== firstLetter[0].toLocaleLowerCase('de');\n      });\n\n      if (sortByEnding) {\n        lowercaseWords.sort(compareByEnding);\n        uppercaseWords.sort(compareByEnding);\n      }\n\n      const groupName = selectedGroups.length > 0\n        ? selectedGroups[0].name.toLocaleLowerCase('de')\n        : rawInput.toLocaleLowerCase('de');\n\n      status.innerText =\n        `Reim auf -${groupName} · ${results.length.toLocaleString('de-DE')} Reimwörter`;\n\n      const grid = document.createElement('div');\n      grid.className = 'results-grid';\n\n      function appendWordCard(word) {\n        const card = document.createElement('div');\n        card.className = 'word-card';\n\n        if (normalizeWord(word, ignoreCase) === normalizedInput) {\n          card.classList.add('search-word');\n          card.setAttribute('aria-label', `${word}, gesuchtes Wort`);\n        }\n\n        if (word.length >= 24) {\n          card.classList.add('very-long-word');\n        } else if (word.length >= 18) {\n          card.classList.add('long-word');\n        }\n\n        card.innerText = word;\n        card.title = word;\n        grid.appendChild(card);\n      }\n\n      lowercaseWords.forEach(appendWordCard);\n\n      if (lowercaseWords.length > 0 && uppercaseWords.length > 0) {\n        const separator = document.createElement('div');\n        separator.className = 'case-separator';\n        separator.setAttribute('aria-hidden', 'true');\n        grid.appendChild(separator);\n      }\n\n      uppercaseWords.forEach(appendWordCard);\n\n      container.innerHTML = '';\n      container.appendChild(grid);"

if old_block not in html:
    print("Fehler: Die Ergebnisdarstellung der Version 2.02 wurde nicht gefunden.")
    sys.exit(1)

html = html.replace(old_block, new_block, 1)

ZIEL.write_text(html, encoding="utf-8")

print("Fertig!")
print("Erstellt:", ZIEL.name)
