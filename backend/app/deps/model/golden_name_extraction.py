import re
from typing import Union

broken_hyphen_re = re.compile(r"(?<=[a-zа-я])- (?=[a-zа-я])")

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


def _broken_hyphen(text: str) -> str:
    return broken_hyphen_re.sub("", text)


def _filter_matches(match_: str) -> Union[str, None]:
    match_ = re.split("\n\n(?![a-zа-я])", match_)[-1].strip()
    if len(match_) > 5:
        return _broken_hyphen(match_)


def extract_main_name_candidate(m: str) -> str:
    try:
        m = closing_re.search(m).groups()[0]
        m = re.sub("(?:{})".format("|".join(CLOSINGS)),
                   "", m, flags=re.IGNORECASE).strip()
        return opening_re.search(m).groups()[1]
    except Exception as e:
        return m.split("\n\n")[-1]


def find_golden_name(documents: dict):
    """Search and extract golden names in pack of documents in load"""
    main_names = {}
    golden_name = None

    for document_name, parsed_content in documents.items():
        if type(parsed_content) != str:
            for page_num, content in parsed_content.items():
                if page_num < 2:
                    res = extract_main_name_candidate(content["text"])
                    if len(res) > 0:
                        main_names[document_name] = _filter_matches(res)
                        break

    targets = list(set(main_names.values()))
    if len(targets) > 0:
        golden_name = targets[0]

    return golden_name
