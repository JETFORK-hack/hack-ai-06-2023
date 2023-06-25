import re
from typing import Union
from app.deps.model.candidates_extraction import _broken_hyphen

CLOSINGS = ['материалы инженерных изысканий',
            'технический отч[ёе]т',
            'проектная документация',
            'отч[ёе]тная документация',
            'инженерные изыскания',
            'отч[ёе]тная техническая документация']

OPENINGS = ['государственный контракт',
            'технический отч[ёе]т',
            'научно-проектная документация',
            'размещение объекта']


closing_re = re.compile(
    r"([\S\s]+)((?<=\n\n)(?:{}))".format("|".join(CLOSINGS)), re.IGNORECASE)
opening_re = re.compile(
    r"((?<=\n\n)(?:{}))([\S\s]+)".format("|".join(OPENINGS)), re.IGNORECASE)


def extract_main_name_candidate(m: str) -> str:
    try:
        m = closing_re.search(m).groups()[0]
        m = re.sub("(?:{})".format("|".join(CLOSINGS)),
                   "", m, flags=re.IGNORECASE).strip()
        return opening_re.search(m).groups()[1]
    except Exception as e:
        print(e)
        return m.split("\n\n")[-1]


def _filter_matches(match_: str) -> Union[str, None]:
    match_ = re.split("\n\n(?![a-zа-я])", match_)[-1].strip()
    if len(match_) > 5:
        return _broken_hyphen(match_)


def find_golden_name(documents: dict):
    """Search and extract golden names in pack of documents in load"""
    main_names = {}
    golden_name = None

    for document_name, parsed_content in documents.items():
        if type(parsed_content) == str:
            return golden_name
        for page_num, content in parsed_content.items():
            if page_num < 2:
                res = extract_main_name_candidate(content["text"])
                if (len(res) > 0) and (_filter_matches(res)):
                    main_names[document_name] = _filter_matches(res)
                    break

    names = list(main_names.values())
    if len(names) == 0:
        return golden_name
    golden_name = max(names, key=names.count)

    return golden_name
