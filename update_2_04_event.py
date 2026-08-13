from pathlib import Path
import re
import sys

QUELLE = Path("Reimlexikon_2.03.html")
ZIEL = Path("Reimlexikon_2.04.html")

if not QUELLE.exists():
    print("Fehler: Reimlexikon_2.03.html wurde nicht gefunden.")
    print("Lege dieses Programm in denselben Ordner wie Reimlexikon_2.03.html.")
    sys.exit(1)

html = QUELLE.read_text(encoding="utf-8")

if "Version 2.03" not in html:
    print("Fehler: Die Ausgangsdatei scheint nicht Version 2.03 zu sein.")
    sys.exit(1)

if 'id="resultsContainer"' not in html:
    print("Fehler: Der Ergebnisbereich wurde nicht gefunden.")
    sys.exit(1)

css = """
    .word-card {
      cursor: pointer;
      position: relative;
      transition: background-color 0.15s ease,
                  border-color 0.15s ease,
                  color 0.15s ease,
                  transform 0.08s ease;
      user-select: none;
    }
    .word-card:hover {
      background: #27364b;
      border-color: var(--primary-color);
    }
    .word-card:active {
      transform: scale(0.98);
    }
    .word-card.copied {
      background: #14532d;
      border-color: #4ade80;
      color: #dcfce7;
    }
    .word-card.copied::after {
      content: "✓";
      position: absolute;
      top: 4px;
      right: 8px;
      color: #86efac;
      font-weight: 800;
      font-size: 1rem;
    }
"""

if ".word-card.copied" not in html:
    if "</style>" not in html:
        print("Fehler: Das Ende des CSS-Bereichs wurde nicht gefunden.")
        sys.exit(1)
    html = html.replace("</style>", css + "\n  </style>", 1)

js = """
    async function copyRhymingWord(word, card) {
      let copied = false;

      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(word);
          copied = true;
        }
      } catch (error) {
        copied = false;
      }

      // Ersatzmethode für lokal geöffnete HTML-Dateien.
      if (!copied) {
        const helper = document.createElement('textarea');
        helper.value = word;
        helper.setAttribute('readonly', '');
        helper.style.position = 'fixed';
        helper.style.left = '-9999px';
        helper.style.opacity = '0';
        document.body.appendChild(helper);
        helper.select();

        try {
          copied = document.execCommand('copy');
        } catch (error) {
          copied = false;
        }

        document.body.removeChild(helper);
      }

      if (copied) {
        card.classList.add('copied');
        window.setTimeout(() => {
          card.classList.remove('copied');
        }, 700);
      }
    }

    function activateWordCopying() {
      const results = document.getElementById('resultsContainer');
      if (!results || results.dataset.copyActive === 'yes') return;

      results.dataset.copyActive = 'yes';

      // Ereignisdelegation: funktioniert auch für Karten,
      // die erst nach einer Suche erzeugt werden.
      results.addEventListener('click', event => {
        const card = event.target.closest('.word-card');
        if (!card || !results.contains(card)) return;

        const word = card.textContent.replace('✓', '').trim();
        if (word) copyRhymingWord(word, card);
      });

      results.addEventListener('mouseover', event => {
        const card = event.target.closest('.word-card');
        if (card) card.title = card.textContent.trim() + ' – zum Kopieren anklicken';
      });
    }

    activateWordCopying();
"""

if "function activateWordCopying" not in html:
    if "</script>" not in html:
        print("Fehler: Das Ende des JavaScript-Bereichs wurde nicht gefunden.")
        sys.exit(1)
    html = html.replace("</script>", js + "\n  </script>", 1)

html = html.replace("Version 2.03", "Version 2.04")

ZIEL.write_text(html, encoding="utf-8")

print("Fertig!")
print("Erstellt:", ZIEL.name)
print("Keine E-Mail-Abfrage enthalten.")
