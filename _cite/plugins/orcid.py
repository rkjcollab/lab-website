import json
from urllib.request import Request, urlopen
from util import *
from manubot.cite.handlers import prefix_to_handler as manubot_prefixes

def main(entry):
    """
    receives single list entry from orcid data file
    returns list of sources to cite
    """

    endpoint = "https://pub.orcid.org/v3.0/$ORCID/works"
    headers = {"Accept": "application/json"}

    _id = get_safe(entry, "orcid", "")
    if not _id:
        raise Exception('No "orcid" key')

    @log_cache
    @cache.memoize(name=__file__, expire=1 * (60 * 60 * 24))
    def query(_id):
        url = endpoint.replace("$ORCID", _id)
        request = Request(url=url, headers=headers)
        response = json.loads(urlopen(request).read())
        return get_safe(response, "group", [])

    response = query(_id)

    sources = []
    seen_ids = set()

    for work in response:
        ids = []
        for summary in get_safe(work, "work-summary", []):
            ids += get_safe(summary, "external-ids.external-id", [])

        _id_obj = next(
            (id for id in ids if get_safe(id, "external-id-relationship", "") in ["self", "version-of", "part-of"]),
            ids[0] if ids else None,
        )

        if not _id_obj:
            continue

        id_type = get_safe(_id_obj, "external-id-type", "")
        id_value = get_safe(_id_obj, "external-id-value", "")

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

    return sources
