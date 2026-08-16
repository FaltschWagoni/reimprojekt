from pathlib import Path
import re
import sys

QUELLE = Path("Reimlexikon_2.00.html")
ZIEL = Path("Reimlexikon_2.02.html")

if not QUELLE.exists():
    print("FEHLER NEUE VERSION: Reimlexikon_2.00.html wurde nicht gefunden.")
    sys.exit(1)

html = QUELLE.read_text(encoding="utf-8")

if not html.lstrip().startswith("<!DOCTYPE html>"):
    print("FEHLER NEUE VERSION: Die Ausgangsdatei beginnt nicht mit <!DOCTYPE html>.")
    sys.exit(1)

if "const csvData = `" not in html:
    print("FEHLER NEUE VERSION: Die Reimdatenbank wurde nicht gefunden.")
    sys.exit(1)

html, n_grid = re.subn(
    r"\.results-grid\s*\{[^}]*\}",
    """.results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 12px;
      align-items: stretch;
    }""",
    html,
    count=1,
    flags=re.S
)

html, n_card = re.subn(
    r"\.word-card\s*\{[^}]*\}",
    """.word-card {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      padding: 14px 16px;
      border-radius: 8px;
      text-align: center;
      font-size: 1.05rem;
      font-weight: 500;
      min-width: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: clip;
    }""",
    html,
    count=1,
    flags=re.S
)

if n_grid != 1 or n_card != 1:
    print(f"FEHLER NEUE VERSION: CSS nicht eindeutig gefunden (grid={n_grid}, card={n_card}).")
    sys.exit(1)

zusatz_css = """
    .word-card.long-word {
      font-size: 0.96rem;
    }
    .word-card.very-long-word {
      font-size: 0.88rem;
      grid-column: span 2;
    }
    @media (max-width: 620px) {
      .results-grid {
        grid-template-columns: 1fr;
      }
      .word-card.very-long-word {
        grid-column: span 1;
      }
    }
"""

if ".word-card.long-word" not in html:
    html = html.replace("</style>", zusatz_css + "  </style>", 1)

alte_stelle = """        card.innerText = word;
        grid.appendChild(card);"""

neue_stelle = """        if (word.length >= 24) {
          card.classList.add('very-long-word');
        } else if (word.length >= 18) {
          card.classList.add('long-word');
        }

        card.innerText = word;
        card.title = word;
        grid.appendChild(card);"""

if alte_stelle not in html:
    print("FEHLER NEUE VERSION: JavaScript-Stelle für Wortkarten wurde nicht gefunden.")
    sys.exit(1)

html = html.replace(alte_stelle, neue_stelle, 1)

html = re.sub(
    r"Reimlexikon(?: Version)? 2\.\d{1,2}\s*[–-]\s*August 2026",
    "Reimlexikon Version 2.02 – August 2026",
    html,
    count=1
)

ZIEL.write_text(html, encoding="utf-8")

print("FERTIG – NEUE VERSION")
print("Erstellt:", ZIEL.name)
