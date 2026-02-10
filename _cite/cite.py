"""
cite process to convert sources and metasources into full citations
"""

import traceback
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from _cite.util import *

# -------------------------------------------------
# Setup
# -------------------------------------------------

load_dotenv()

errors = []
warnings = []

output_file = "_data/citations.yaml"

log()
log("Compiling sources")

sources = []

plugins = ["google-scholar", "pubmed", "orcid", "sources"]

# -------------------------------------------------
# Run plugins
# -------------------------------------------------

for plugin in plugins:
    plugin_path = Path(f"plugins/{plugin}.py")
    log(f"Running {plugin_path.stem} plugin")

    files = list(
        filter(
            lambda p: p.suffix in [".yaml", ".yml", ".json"],
            Path.cwd().glob(f"_data/{plugin_path.stem}*.*"),
        )
    )

    log(f"Found {len(files)} {plugin_path.stem}* data file(s)", indent=1)

    for file in files:
        log(f"Processing data file {file.name}", indent=1)

        try:
            data = load_data(file)
            if not list_of_dicts(data):
                raise Exception(f"{file.name} data file not a list of dicts")
        except Exception as e:
            log(e, indent=2, level="ERROR")
            errors.append(e)
            continue

        for index, entry in enumerate(data):
            log(
                f"Processing entry {index + 1} of {len(data)}, {label(entry)}",
                level=2,
            )

            try:
                expanded = import_module(
                    f"plugins.{plugin_path.stem}"
                ).main(entry)

                if not list_of_dicts(expanded):
                    raise Exception(
                        f"{plugin_path.stem} plugin didn't return list of dicts"
                    )

            except Exception as e:
                print(traceback.format_exc())
                log(e, indent=3, level="ERROR")
                errors.append(e)
                continue

            # -----------------------------------------
            # ORCID: keep DOI-only (DO NOT exclude DOI+PMID)
            # -----------------------------------------
            if plugin_path.stem == "orcid":
                before = len(expanded)
                expanded = [
                    s for s in expanded
                    if get_safe(s, "id", "").lower().startswith("doi:")
                ]
                after = len(expanded)
                log(
                    f"Filtered ORCID sources: {before} → {after} (DOI-only)",
                    indent=3,
                )

            for source in expanded:
                if plugin_path.stem != "sources":
                    log(label(source), level=3)

                source["plugin"] = plugin
                source["file"] = file.name

                sources.append(source)

            if plugin_path.stem != "sources":
                log(f"{len(expanded)} source(s)", indent=3)

# -------------------------------------------------
# Deduplicate + merge (sources.yaml WINS)
# -------------------------------------------------

log("Deduplicating all sources by ID (case-insensitive)")
log("Preferring metadata from sources.yaml")

by_id = {}

for s in sources:
    _id = get_safe(s, "id", "").strip().lower()

    if not _id:
        # no ID → keep as-is
        by_id[id(s)] = s
        continue

    if _id not in by_id:
        by_id[_id] = s
        continue

    existing = by_id[_id]

    # If new entry is from sources.yaml, merge it on top
    if get_safe(s, "plugin") == "sources":
        merged = existing.copy()
        merged.update(s)  # sources.yaml overrides everything
        by_id[_id] = merged
        log(f"Merged metadata for {_id} from sources.yaml", indent=2)
    else:
        log(f"Skipping duplicate {_id} from {get_safe(s,'plugin')}", indent=2)

sources = list(by_id.values())
log(f"{len(sources)} total source(s) to cite after deduplication")

# -------------------------------------------------
# Generate citations
# -------------------------------------------------

log()
log("Generating citations")

citations = []

for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    if get_safe(source, "remove", False) is True:
        continue

    citation = {}
    _id = get_safe(source, "id", "").strip()

    if _id:
        log("Using Manubot to generate citation", indent=1)
        try:
            citation = cite_with_manubot(_id)
        except Exception as e:
            plugin_name = get_safe(source, "plugin", "")
            file_name = get_safe(source, "file", "")

            if plugin_name == "sources":
                log(e, indent=3, level="ERROR")
                errors.append(
                    f"Manubot could not generate citation for source {_id}"
                )
            else:
                log(e, indent=3, level="WARNING")
                warnings.append(
                    f"Manubot could not generate citation for source {_id} "
                    f"(from {file_name} with {plugin_name})"
                )
                continue

    # Merge curated metadata LAST
    citation.update(source)

    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    citations.append(citation)

# -------------------------------------------------
# Save citations
# -------------------------------------------------

log()
log("Saving updated citations")

try:
    save_data(output_file, citations)
except Exception as e:
    log(e, level="ERROR")
    errors.append(e)

log()

# -------------------------------------------------
# Summary
# -------------------------------------------------

if warnings:
    log(f"{len(warnings)} warning(s) occurred above", level="WARNING")
    for w in warnings:
        log(w, indent=1, level="WARNING")

if errors:
    log(f"{len(errors)} error(s) occurred above", level="ERROR")
    for e in errors:
        log(e, indent=1, level="ERROR")
    log()
    exit(1)
else:
    log("All done!", level="SUCCESS")

log()
