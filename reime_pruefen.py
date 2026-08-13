from pathlib import Path
import csv
import re
import sys
from collections import defaultdict, Counter

CSV_DATEI = Path("reime.csv")
BERICHT_DATEI = Path("reime_fehlerbericht.txt")


def sichtbarer_text(text: str) -> str:
    """Macht Leerzeichen und leere Einträge im Bericht besser erkennbar."""
    if text == "":
        return "<leer>"
    return text.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def ist_grossgeschriebene_gruppe(gruppe: str) -> bool:
    """Prüft, ob die Reimgruppe wie vorgesehen groß geschrieben ist."""
    buchstaben = [c for c in gruppe if c.isalpha()]
    return bool(buchstaben) and gruppe == gruppe.upper()


def main() -> None:
    if not CSV_DATEI.exists():
        print("Fehler: reime.csv wurde nicht gefunden.")
        print("Lege reime_pruefen.py in denselben Ordner wie reime.csv.")
        sys.exit(1)

    fehler = []
    warnungen = []
    hinweise = []

    gruppen_vorkommen = defaultdict(list)
    wort_gruppen_exakt = defaultdict(set)
    wort_gruppen_ohne_grossklein = defaultdict(set)

    anzahl_zeilen = 0
    anzahl_gruppen = 0
    anzahl_woerter = 0

    with CSV_DATEI.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")

        for zeilennummer, rohe_zeile in enumerate(reader, start=1):
            anzahl_zeilen += 1

            # Vollständig leere Zeile
            if not rohe_zeile or all(feld == "" for feld in rohe_zeile):
                warnungen.append(
                    f"Zeile {zeilennummer}: vollständig leere Zeile."
                )
                continue

            # Leerzeichen am Anfang oder Ende
            for spaltennummer, feld in enumerate(rohe_zeile, start=1):
                if feld != feld.strip():
                    warnungen.append(
                        f"Zeile {zeilennummer}, Spalte {spaltennummer}: "
                        f"überflüssige Leerzeichen bei „{sichtbarer_text(feld)}“."
                    )

            zeile = [feld.strip() for feld in rohe_zeile]

            # Leere Felder innerhalb der benutzten Zeile
            letzte_belegte_spalte = -1
            for i, feld in enumerate(zeile):
                if feld:
                    letzte_belegte_spalte = i

            if letzte_belegte_spalte >= 0:
                for i, feld in enumerate(zeile[:letzte_belegte_spalte + 1]):
                    if feld == "":
                        warnungen.append(
                            f"Zeile {zeilennummer}, Spalte {i + 1}: "
                            "leeres Feld zwischen belegten Feldern."
                        )

            belegte_felder = [feld for feld in zeile if feld]

            if not belegte_felder:
                continue

            gruppe = belegte_felder[0]
            woerter = belegte_felder[1:]

            gruppen_vorkommen[gruppe].append(zeilennummer)
            anzahl_gruppen += 1
            anzahl_woerter += len(woerter)

            if not ist_grossgeschriebene_gruppe(gruppe):
                warnungen.append(
                    f"Zeile {zeilennummer}: Reimgruppe „{gruppe}“ "
                    "ist nicht vollständig großgeschrieben."
                )

            if not woerter:
                fehler.append(
                    f"Zeile {zeilennummer}: Gruppe „{gruppe}“ enthält kein Reimwort."
                )
                continue

            # Doppelte Wörter innerhalb derselben Gruppe
            exakt_counter = Counter(woerter)
            for wort, anzahl in exakt_counter.items():
                if anzahl > 1:
                    fehler.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ steht {anzahl}× exakt doppelt."
                    )

            # Doppelte Wörter nur mit unterschiedlicher Groß-/Kleinschreibung
            klein_counter = defaultdict(list)
            for wort in woerter:
                klein_counter[wort.casefold()].append(wort)

            for varianten in klein_counter.values():
                eindeutige_varianten = sorted(set(varianten))
                if len(eindeutige_varianten) > 1:
                    hinweise.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        "gleiche Schreibform mit unterschiedlicher Groß-/Kleinschreibung: "
                        + ", ".join(f"„{v}“" for v in eindeutige_varianten)
                    )

            for wort in woerter:
                wort_gruppen_exakt[wort].add(gruppe)
                wort_gruppen_ohne_grossklein[wort.casefold()].add(gruppe)

                # Verdächtige Trennzeichen – nur melden, nicht automatisch ändern
                if ":" in wort:
                    warnungen.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ enthält einen Doppelpunkt."
                    )

                if "," in wort:
                    warnungen.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ enthält ein Komma."
                    )

                if "|" in wort:
                    warnungen.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ enthält einen senkrechten Strich |."
                    )

                if ";" in wort:
                    # Normalerweise wird ein Semikolon bereits als neue Spalte gelesen.
                    warnungen.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ enthält ein Semikolon."
                    )

                # Sehr kurze Fragmente sind manchmal gewollt, daher nur Hinweis
                if len(wort) == 1 and wort.isalpha():
                    hinweise.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"Einzelbuchstabe „{wort}“ – bitte prüfen, ob beabsichtigt."
                    )

                # Mehrfache Leerzeichen innerhalb eines Eintrags
                if re.search(r"\s{2,}", wort):
                    warnungen.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{wort}“ enthält mehrere aufeinanderfolgende Leerzeichen."
                    )

                # Unsichtbare Steuerzeichen
                if any(ord(c) < 32 and c not in "\t\n\r" for c in wort):
                    fehler.append(
                        f"Zeile {zeilennummer}, Gruppe „{gruppe}“: "
                        f"„{sichtbarer_text(wort)}“ enthält ein unsichtbares Steuerzeichen."
                    )

    # Doppelte Gruppennamen
    for gruppe, zeilen in sorted(gruppen_vorkommen.items()):
        if len(zeilen) > 1:
            fehler.append(
                f"Gruppe „{gruppe}“ kommt mehrfach vor, in den Zeilen: "
                + ", ".join(map(str, zeilen))
            )

    # Exakt dasselbe Wort in mehreren Gruppen: nur Hinweis, weil das gewollt sein kann
    mehrgruppen = []
    for wort, gruppen in wort_gruppen_exakt.items():
        if len(gruppen) > 1:
            mehrgruppen.append((wort, sorted(gruppen)))

    for wort, gruppen in sorted(mehrgruppen, key=lambda x: x[0].casefold()):
        hinweise.append(
            f"„{wort}“ steht in mehreren Gruppen: {', '.join(gruppen)}"
        )

    # Bericht schreiben
    with BERICHT_DATEI.open("w", encoding="utf-8") as out:
        out.write("REIMLEXIKON – DATENBANKPRÜFUNG\n")
        out.write("=" * 40 + "\n\n")

        out.write("ZUSAMMENFASSUNG\n")
        out.write("-" * 40 + "\n")
        out.write(f"Gelesene Zeilen: {anzahl_zeilen}\n")
        out.write(f"Reimgruppen: {anzahl_gruppen}\n")
        out.write(f"Reimwörter: {anzahl_woerter}\n")
        out.write(f"Eindeutige Fehler: {len(fehler)}\n")
        out.write(f"Warnungen: {len(warnungen)}\n")
        out.write(f"Hinweise: {len(hinweise)}\n\n")

        out.write("EINDEUTIGE FEHLER\n")
        out.write("-" * 40 + "\n")
        if fehler:
            for punkt in fehler:
                out.write(f"- {punkt}\n")
        else:
            out.write("Keine eindeutigen Fehler gefunden.\n")
        out.write("\n")

        out.write("WARNUNGEN – BITTE PRÜFEN\n")
        out.write("-" * 40 + "\n")
        if warnungen:
            for punkt in warnungen:
                out.write(f"- {punkt}\n")
        else:
            out.write("Keine Warnungen.\n")
        out.write("\n")

        out.write("HINWEISE – KÖNNEN BEABSICHTIGT SEIN\n")
        out.write("-" * 40 + "\n")
        if hinweise:
            for punkt in hinweise:
                out.write(f"- {punkt}\n")
        else:
            out.write("Keine zusätzlichen Hinweise.\n")

    print("Prüfung abgeschlossen.")
    print("Bericht erstellt:", BERICHT_DATEI.name)
    print("Eindeutige Fehler:", len(fehler))
    print("Warnungen:", len(warnungen))
    print("Hinweise:", len(hinweise))
    print()
    print("Die CSV-Datei wurde nicht verändert.")


if __name__ == "__main__":
    main()
