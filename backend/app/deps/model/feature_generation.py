import re
import pandas as pd
import rapidfuzz
import textdistance
from logging import getLogger

logger = getLogger()

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("calculate editions")
    df["qratio"] = df.apply(lambda x: rapidfuzz.fuzz.QRatio(x["candidate"], x["targets"]),
                            axis=1).astype(float)
    df["partial_token_set_ratio"] = df.apply(
        lambda x: rapidfuzz.fuzz.partial_token_set_ratio(x["candidate"], x["targets"]),
        axis=1).astype(float)
    df["token_set_ratio"] = df.apply(
        lambda x: rapidfuzz.fuzz.token_set_ratio(x["candidate"], x["targets"]),
        axis=1).astype(float)

    logger.info("calculate string sims")
    df["jaro_winkler"] = df.apply(
        lambda x: textdistance.jaro_winkler(x["candidate"], x["targets"]), axis=1).astype(
        float)
    df["levenshtein"] = df.apply(
        lambda x: textdistance.levenshtein(x["candidate"], x["targets"]) / len(
            x["candidate"]), axis=1).astype(float)
    df["damerau_levenshtein"] = df.apply(
        lambda x: textdistance.damerau_levenshtein(x["candidate"], x["targets"]) / len(
            x["candidate"]), axis=1).astype(float)
    df["cosine"] = df.apply(lambda x: textdistance.cosine(x["candidate"], x["targets"]),
                            axis=1).astype(float)

    logger.info("calculate union chars")
    df["chars_in_common"] = df.apply(
        lambda x: len(set(x["candidate"]) & set(x['targets'])) / len(set(x["candidate"])),
        axis=1).astype(float)
    df["words_in_common"] = df.apply(
      lambda x: len(set(x["candidate"].split()) & set(x['targets'].split())) / len(set(x["candidate"].split())),
                                     axis=1).astype(float)
    df["target_in_candidate"] = df.apply(lambda x: int(x['targets'] in x["candidate"]),
                                         axis=1).astype(int)
    df["candidate_in_targets"] = df.apply(lambda x: int(x["candidate"] in x['targets']),
                                          axis=1).astype(int)

    logger.info("calculate candidates characteristics")
    df["candidate_contains_num"] = df["candidate"].str.contains("\d", regex=True).astype(int)
    df["candidate_contains_special_chars"] = df["candidate"].str.contains("[^\w\s]", regex=True).astype(int)

    logger.info("calculate targets characteristics")
    df["target_contains_num"] = df["targets"].apply(
        lambda x: int(re.search("\d", x) is not None)).astype(int)
    df["target_contains_special_chars"] = df["targets"].apply(
        lambda x: int(re.search("[^\w\s]", x) is not None)).astype(int)
    return df
