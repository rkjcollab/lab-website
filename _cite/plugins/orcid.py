import json
import logging
from urllib.request import Request, urlopen
from _cite.util import *
from manubot.cite.handlers import prefix_to_handler as manubot_prefixes

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def configure_logging(verbose=False):
    """Enable debug-level logging if requested."""
    if verbose:
        log.setLevel(logging.DEBUG)


# ------------------------------------------------------------------------------
# Main ORCID Plugin Logic
# ------------------------------------------------------------------------------
def main(entry):
    """
    Receives a single list entry from ORCID data file.
    Returns a list of sources to cite.
    Logs progress even if no ORCID ID is present or fetching fails.
    """
    log.info("Starting ORCID plugin")

    _id = get_safe(entry, "orcid", "")
    if not _id:
        log.warning("No ORCID ID found in entry. Skipping fetching ORCID works.")
        return []

    # Basic validation: ORCID IDs are 16 digits (with or without hyphens)
    if not _id.replace("-", "").isdigit() or len(_id.replace("-", "")) != 16:
        log.warning(f"Invalid ORCID ID provided: {_id}. Skipping fetch.")
        return []

    log.info(f"Querying ORCID works for {_id}")

    endpoint = "https://pub.orcid.org/v3.0/$ORCID/works"
    headers = {"Accept": "application/json"}

    @log_cache
    @cache.memoize(name=__file__, expire=1 * (60 * 60 * 24))
    def query(_id):
        url = endpoint.replace("$ORCID", _id)
        log.debug(f"Requesting URL: {url}")
        try:
            request = Request(url=url, headers=headers)
            response = json.loads(urlopen(request).read())
        except Exception as e:
            log.error(f"Failed to fetch ORCID works for {_id}: {e}")
            return []
        return get_safe(response, "group", [])

    response = query(_id)
    log.info(f"ORCID returned {len(response)} work groups")

    sources = []
    seen_ids = set()

    for i, work in enumerate(response, start=1):
        log.debug(f"Processing work #{i}")
        ids = []
        for summary in get_safe(work, "work-summary", []):
            ids += get_safe(summary, "external-ids.external-id", [])

        _id_obj = next(
            (id for id in ids if get_safe(id, "external-id-relationship", "") in ["self", "version-of", "part-of"]),
            ids[0] if ids else None,
        )

        if not _id_obj:
            log.debug(f"Skipping work #{i} because it has no IDs")
            continue

        id_type = get_safe(_id_obj, "external-id-type", "").lower()
        id_value = get_safe(_id_obj, "external-id-value", "")

        # Only keep works that have a DOI
        if id_type != "doi":
            doi_obj = next((id for id in ids if get_safe(id, "external-id-type", "").lower() == "doi"), None)
            if doi_obj:
                id_type = "doi"
                id_value = get_safe(doi_obj, "external-id-value", "")
            else:
                log.debug(f"Skipping work #{i} because it has no DOI")
                continue

        unique_id = f"{id_type}:{id_value}".lower()
        if unique_id in seen_ids:
            continue
        seen_ids.add(unique_id)

        source = {"id": f"{id_type}:{id_value}"}

        if id_type not in manubot_prefixes:
            summaries = get_safe(work, "work-summary", [])

            def first(get_func):
                return next((v for v in map(get_func, summaries) if v), None)

            title = first(lambda s: get_safe(s, "title.title.value", ""))
            publisher = first(lambda s: get_safe(s, "journal-title.value", ""))
            date = (
                get_safe(work, "last-modified-date.value")
                or first(lambda s: get_safe(s, "last-modified-date.value"))
                or get_safe(work, "created-date.value")
                or first(lambda s: get_safe(s, "created-date.value"))
                or 0
            )
            link = first(lambda s: get_safe(s, "url.value", ""))

            if title:
                source["title"] = title
            if publisher:
                source["publisher"] = publisher
            if date:
                source["date"] = format_date(date)
            if link:
                source["link"] = link

        source.update(entry)
        sources.append(source)

    log.info(f"Processed {len(sources)} works successfully")
    log.debug("Sources: " + json.dumps(sources, indent=2))

    return sources


# ------------------------------------------------------------------------------
# CLI (for standalone debugging)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ORCID plugin debug runner")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--orcid", type=str, help="Optional ORCID ID to test plugin")
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)

    entry = {"orcid": args.orcid} if args.orcid else {}
    results = main(entry)

    if results:
        print(json.dumps(results, indent=2))
