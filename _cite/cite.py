"""
cite process to convert sources and metasources into full citations
"""

import traceback
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from util import *

# load environment variables
load_dotenv()

# save errors/warnings for reporting at end
errors = []
warnings = []

# output citations file
output_file = "_data/citations.yaml"

log()
log("Compiling sources")

# compiled list of sources
sources = []

# in-order list of plugins to run
plugins = ["google-scholar", "pubmed", "orcid", "sources"]

# loop through plugins
for plugin in plugins:
    plugin_path = Path(f"plugins/{plugin}.py")
    log(f"Running {plugin_path.stem} plugin")

    # get all data files to process with current plugin
    files = Path.cwd().glob(f"_data/{plugin_path.stem}*.*")
    files = list(filter(lambda p: p.suffix in [".yaml", ".yml", ".json"], files))
    log(f"Found {len(files)} {plugin_path.stem}* data file(s)", indent=1)

    # loop through data files
    for file in files:
        log(f"Processing data file {file.name}", indent=1)

        # load data from file
        try:
            data = load_data(file)
            if not list_of_dicts(data):
                raise Exception(f"{file.name} data file not a list of dicts")
        except Exception as e:
            log(e, indent=2, level="ERROR")
            errors.append(e)
            continue

        # loop through data entries
        for index, entry in enumerate(data):
            log(f"Processing entry {index + 1} of {len(data)}, {label(entry)}", level=2)

            # run plugin on data entry to expand into multiple sources
            try:
                expanded = import_module(f"plugins.{plugin_path.stem}").main(entry)
                if not list_of_dicts(expanded):
                    raise Exception(f"{plugin_path.stem} plugin didn't return list of dicts")
            except Exception as e:
                print(traceback.format_exc())
                log(e, indent=3, level="ERROR")
                errors.append(e)
                continue

            # loop through sources
            for source in expanded:
                if plugin_path.stem != "sources":
                    log(label(source), level=3)

                # include meta info about source
                source["plugin"] = plugin
                source["file"] = file.name

                # add source to compiled list
                sources.append(source)

            if plugin_path.stem != "sources":
                log(f"{len(expanded)} source(s)", indent=3)

# -------------------------
# Deduplicate all sources by ID (case-insensitive)
# -------------------------
log("Deduplicating all sources by ID (case-insensitive)")

seen_ids = set()
deduped_sources = []

for s in sources:
    _id = get_safe(s, "id", "").strip().lower()
    if not _id:
        deduped_sources.append(s)  # keep entries without ID
        continue
    if _id in seen_ids:
        log(f"Skipping duplicate {_id}", indent=2)
        continue
    seen_ids.add(_id)
    deduped_sources.append(s)

sources = deduped_sources
log(f"{len(sources)} total source(s) to cite after deduplication")

# -------------------------
# Generate citations
# -------------------------
log()
log("Generating citations")

citations = []

for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    # skip explicitly removed sources
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
                errors.append(f"Manubot could not generate citation for source {_id}")
            else:
                log(e, indent=3, level="WARNING")
                warnings.append(
                    f"Manubot could not generate citation for source {_id} (from {file_name} with {plugin_name})"
                )
                continue

    # preserve input source fields
    citation.update(source)

    # ensure date formatting for sorting
    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    citations.append(citation)

# -------------------------
# Save citations
# -------------------------
log()
log("Saving updated citations")

try:
    save_data(output_file, citations)
except Exception as e:
    log(e, level="ERROR")
    errors.append(e)

log()

# -------------------------
# Show errors/warnings summary
# -------------------------
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
