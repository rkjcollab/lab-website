"""
cite process to convert sources and metasources into full citations
"""

import traceback
import re
import requests
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from util import *

# load environment variables
load_dotenv()

errors = []
warnings = []

output_file = "_data/citations.yaml"


def normalize_title(title):
    return re.sub(r'\W+', '', title.lower().strip())


def deduplicate_citations(citations):
    seen = set()
    deduped = []
    for citation in citations:
        key = citation.get("doi")
        if not key:
            key = normalize_title(citation.get("title", ""))
        if key and key not in seen:
            seen.add(key)
            deduped.append(citation)
    return deduped


def identify_publisher(doi):
    """
    Identify publisher by DOI prefix.
    Extend this mapping with other prefixes as needed.
    """
    prefix = doi.lower().split("/")[0] if "/" in doi else doi.lower()
    if prefix.startswith("10.1016"):
        return "Elsevier"
    elif prefix.startswith("10.1007"):
        return "Springer"
    elif prefix.startswith("10.1038"):
        return "Nature"
    # Add other DOI prefix mappings here
    else:
        return None


def fetch_figure_from_crossref(doi):
    """
    Try to fetch figure URL from Crossref metadata links.
    """
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        links = data["message"].get("link", [])
        for link in links:
            content_type = link.get("content-type", "").lower()
            url = link.get("URL")
            if ("figure" in content_type or "image" in content_type) and url:
                return url
    except Exception as e:
        log(f"Crossref figure fetch failed for DOI {doi}: {e}", level="WARNING")
    return None


def fetch_figure_from_elsevier(doi):
    """
    Placeholder: Implement Elsevier API figure fetching here.
    Requires Elsevier API key in environment variable.
    """
    # TODO: Add Elsevier API call with API key
    return None


def fetch_figure_from_springer(doi):
    """
    Placeholder: Implement Springer API figure fetching here.
    """
    # TODO: Add Springer API call if available
    return None


def fetch_figure_from_europe_pmc(doi):
    """
    Original Europe PMC figure fetch fallback.
    """
    try:
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=doi:{doi}&format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            return None
        article = results[0]
        figures = article.get("figures", [])
        if not figures:
            return None
        first_figure = figures[0]
        image_url = first_figure.get("url") or first_figure.get("thumbnail")
        return image_url
    except Exception as e:
        log(f"Could not fetch figure1 image for DOI {doi}: {e}", level="WARNING")
        return None


def fetch_figure1_image(doi):
    print(f"Looking for figure for DOI: {doi}")
    # Try Crossref first
    image_url = fetch_figure_from_crossref(doi)
    if image_url:
        return image_url

    # Identify publisher
    publisher = identify_publisher(doi)

    if publisher == "Elsevier":
        image_url = fetch_figure_from_elsevier(doi)
        if image_url:
            return image_url

    elif publisher == "Springer":
        image_url = fetch_figure_from_springer(doi)
        if image_url:
            return image_url

    # Fallback to Europe PMC
    return fetch_figure_from_europe_pmc(doi)


log()

log("Compiling sources")

sources = []

plugins = ["google-scholar", "pubmed", "orcid", "sources"]

for plugin in plugins:
    plugin_path = Path(f"plugins/{plugin}.py")
    log(f"Running {plugin_path.stem} plugin")
    files = list(Path.cwd().glob(f"_data/{plugin_path.stem}*.*"))
    files = list(filter(lambda p: p.suffix in [".yaml", ".yml", ".json"], files))
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
            log(f"Processing entry {index + 1} of {len(data)}, {label(entry)}", level=2)
            try:
                expanded = import_module(f"plugins.{plugin_path.stem}").main(entry)
                if not list_of_dicts(expanded):
                    raise Exception(f"{plugin_path.stem} plugin didn't return list of dicts")
            except Exception as e:
                print(traceback.format_exc())
                log(e, indent=3, level="ERROR")
                errors.append(e)
                continue
            for source in expanded:
                if plugin_path.stem != "sources":
                    log(label(source), level=3)
                source["plugin"] = plugin_path.name
                source["file"] = file.name
                sources.append(source)
            if plugin_path.stem != "sources":
                log(f"{len(expanded)} source(s)", indent=3)

log("Merging sources by id")

for a in range(0, len(sources)):
    a_id = get_safe(sources, f"{a}.id", "")
    if not a_id:
        continue
    for b in range(a + 1, len(sources)):
        b_id = get_safe(sources, f"{b}.id", "")
        if b_id == a_id:
            log(f"Found duplicate {b_id}", indent=2)
            sources[a].update(sources[b])
            sources[b] = {}
sources = [entry for entry in sources if entry]

log(f"{len(sources)} total source(s) to cite")

log()

log("Generating citations")

citations = []

for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    if get_safe(source, "remove", False) == True:
        continue

    citation = {}

    _id = get_safe(source, "id", "").strip()

    if _id:
        log("Using Manubot to generate citation", indent=1)
        try:
            citation = cite_with_manubot(_id)
        except Exception as e:
            plugin = get_safe(source, "plugin", "")
            file = get_safe(source, "file", "")
            if plugin == "sources.py":
                log(e, indent=3, level="ERROR")
                errors.append(f"Manubot could not generate citation for source {_id}")
            else:
                log(e, indent=3, level="WARNING")
                warnings.append(
                    f"Manubot could not generate citation for source {_id} (from {file} with {plugin})"
                )
                continue

    # Fetch Figure 1 image URL if DOI available
    doi = citation.get("doi") or citation.get("ID") or None
    if doi:
        figure1_url = fetch_figure1_image(doi)
        if figure1_url:
            citation["figure1_image_url"] = figure1_url
            log(f"Fetched Figure 1 image URL for {doi}", indent=2)

    citation.update(source)

    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    citations.append(citation)

log()

log("Deduplicating citations")

deduped_citations = deduplicate_citations(citations)
log(f"{len(deduped_citations)} unique citation(s) after deduplication")

log("Saving updated citations")

try:
    save_data(output_file, deduped_citations)
except Exception as e:
    log(e, level="ERROR")
    errors.append(e)

log()

if len(warnings):
    log(f"{len(warnings)} warning(s) occurred above", level="WARNING")
    for warning in warnings:
        log(warning, indent=1, level="WARNING")

if len(errors):
    log(f"{len(errors)} error(s) occurred above", level="ERROR")
    for error in errors:
        log(error, indent=1, level="ERROR")
    log()
    exit(1)
else:
    log("All done!", level="SUCCESS")

log()
