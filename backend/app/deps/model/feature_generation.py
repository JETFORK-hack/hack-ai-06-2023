import re
import pandas as pd
import rapidfuzz
import textdistance
from logging import getLogger

logger = getLogger()


def matching_numbers(external_name, internal_name):

    external_numbers = set(re.findall(r'[0-9]+', external_name))
    internal_numbers = set(re.findall(r'[0-9]+', internal_name))
    union = external_numbers.union(internal_numbers)
    intersection = external_numbers.intersection(internal_numbers)

    if len(external_numbers) == 0 and len(internal_numbers) == 0:
        return 1
    else:
        return len(intersection) / len(union)


def generate_features(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("calculate editions")
    df["qratio"] = df \
        .apply(lambda x: rapidfuzz.fuzz.QRatio(x["candidate"],
                                               x["targets"]), axis=1) \
        .astype(float)
    df["partial_token_set_ratio"] = df \
        .apply(lambda x: rapidfuzz.fuzz.partial_token_set_ratio(x["candidate"],
                                                                x["targets"]), axis=1) \
        .astype(float)
    df["token_set_ratio"] = df.apply(lambda x: rapidfuzz.fuzz.token_set_ratio(x["candidate"],
                                                                              x["targets"]), axis=1) \
        .astype(float)

    logger.info("calculate string sims")
    df["jaro_winkler"] = df \
        .apply(lambda x: textdistance.jaro_winkler(x["candidate"],
                                                   x["targets"]), axis=1) \
        .astype(float)

    print('df.columns', df.columns)
    print('df.columns2', df.apply(lambda x: textdistance.levenshtein(x["candidate"],
                                                                     x["targets"]) / len(x["candidate"]), axis=1)
          )
    print(df.head(25))

    df["levenshtein"] = df \
        .apply(lambda x: textdistance.levenshtein(x["candidate"],
                                                  x["targets"]) / len(x["candidate"]), axis=1) \
        .astype(float)
    df["damerau_levenshtein"] = df \
        .apply(lambda x: textdistance.damerau_levenshtein(x["candidate"],
                                                          x["targets"]) / len(x["candidate"]), axis=1) \
        .astype(float)
    df["cosine"] = df \
        .apply(lambda x: textdistance.cosine(x["candidate"],
                                             x["targets"]), axis=1) \
        .astype(float)

    logger.info("calculate union chars")
    df["chars_in_common"] = df \
        .apply(lambda x: len(set(x["candidate"]) & set(x["targets"])) / len(set(x["candidate"] + x["targets"])), axis=1) \
        .astype(float)
    df["matching_numbers"] = df \
        .apply(lambda x: matching_numbers(x["candidate"], x["targets"]), axis=1) \
        .astype(float)
    df["words_in_common"] = df \
        .apply(lambda x: len(set(x["candidate"].split()) & set(x["targets"].split())) / len(set(x["candidate"].split()+x["targets"].split())), axis=1) \
        .astype(float)
    df["target_in_candidate"] = df \
        .apply(lambda x: int(x["targets"] in x["candidate"]), axis=1) \
        .astype(int)
    df["candidate_in_targets"] = df \
        .apply(lambda x: int(x["candidate"] in x["targets"]), axis=1) \
        .astype(int)

    logger.info("calculate candidates characteristics")
    df["candidate_contains_special_chars"] = df["candidate"] \
        .str.contains("[^\w\s]", regex=True) \
        .astype(int)

    logger.info("calculate targets characteristics")
    df["target_contains_special_chars"] = df["targets"] \
        .str.contains("[^\w\s]", regex=True) \
        .astype(int)
    return df
