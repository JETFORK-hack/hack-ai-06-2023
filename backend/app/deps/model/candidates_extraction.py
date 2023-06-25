import re
from nltk import everygrams
import pandas as pd
import rapidfuzz
from unicodedata import normalize, category

from app.deps.model.symbols import SLASHES, DASHES, PLUSES, QUOTES

# поправить пунктуацию
char2idx_1 = re.compile(r"й")
char2idx_2 = re.compile(r"ё")
idx2char_1 = re.compile(r"<p>99</p>")
idx2char_2 = re.compile(r"<p>98</p>")

trash_punct = re.compile(f"[(),№;<>%‰*{''.join(QUOTES)}]+")
double_space = re.compile(r"\s+")
broken_hyphen_re = re.compile(r"(?<=[a-zа-я])- (?=[a-zа-я])")


def _broken_hyphen(text: str) -> str:
    return broken_hyphen_re.sub("", text)


def remove_accents(text: str) -> str:
    text = char2idx_1.sub(idx2char_1.pattern, text)
    text = char2idx_2.sub(idx2char_2.pattern, text)
    text = "".join(c for c in normalize("NFD", text)
                   if category(c) != "Mn")
    text = idx2char_1.sub("й", text)
    text = idx2char_2.sub("ё", text)
    return text


def filter_short_paragraphs(text: str, min_token_len: int = 2, min_char_len: int = 10) -> str:
    paragraphs = text.split("\n\n")
    return "\n\n".join([i for i in paragraphs
                        if len(i) >= min_char_len
                        and len(i.split()) >= min_token_len])


def preprocess_text(text: str) -> str:
    text = _broken_hyphen(filter_short_paragraphs(text))
    text = text.lower()
    text = remove_accents(text)

    for slash in SLASHES:
        text = text.replace(slash, "/")
    for dash in DASHES:
        text = text.replace(dash, "-")
    for plus in PLUSES:
        text = text.replace(plus, "+")

    text = trash_punct.sub(" ", text)
    text = double_space.sub(" ", text)
    return text.strip()


def get_candidates(documents: dict, golden_name: str):
    CANDIDATES_SIMILARITY = 50
    processed_golden_name = preprocess_text(golden_name)
    candidates = []

    for document_name, parsed_content in documents.items():
        if type(parsed_content) != str:
            for page_num, context in parsed_content.items():
                if context["text"] and len(context["text"]) > 0:
                    if golden_name is None:
                        print(f'document_name', document_name)
                    raw_candidates = [" ".join(ngram) for ngram in everygrams(preprocess_text(context["text"]).split(),
                                                                              min_len=int(
                                                                                  len(processed_golden_name.split())/2),
                                                                              max_len=len(processed_golden_name.split())+10)]
                    for candidate in raw_candidates:
                        score = rapidfuzz.fuzz.QRatio(
                            processed_golden_name, candidate)
                        if score > CANDIDATES_SIMILARITY:
                            candidates.append((golden_name,
                                               document_name,
                                               page_num,
                                               processed_golden_name,
                                               candidate))

    df = pd.DataFrame(candidates, columns=[
                      "golden_name", "doc_name", "page_num", "targets", "candidate"])
    return df
