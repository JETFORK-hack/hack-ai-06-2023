import re
import joblib
from app.deps.model.golden_name_extraction import find_golden_name
from app.deps.model.candidates_extraction import get_candidates
from app.deps.model.feature_generation import generate_features

dropcols = ["golden_name", "doc_name", "page_num", "candidate", "targets"]


def get_raw_candidate(page: str, candidate: str) -> str:
    res = re.findall(f'{candidate[:7]}.*{candidate[-7:]}', page, re.IGNORECASE)
    if res:
        return res[0]
    return candidate


def predict(all_documents: dict, golden_name: str = ''):
    artifacts = joblib.load('/app/app/deps/model/artifacts.pkl')
    classifier = artifacts['classifier']
    best_threshold = artifacts['threshold']
    if golden_name == '':
        golden_name = find_golden_name(all_documents)
    if golden_name:
        candidates = get_candidates(all_documents, golden_name)
        candidates = candidates.drop_duplicates(
            ['golden_name', 'doc_name', 'page_num', 'candidate'])
        candidates_featured = generate_features(candidates)
        candidates_featured['probability'] = classifier.predict_proba(
            candidates_featured.drop(dropcols, axis=1))[:, 1]
        candidates_featured['page_num'] = candidates_featured['page_num'] + 1
        candidates_featured.loc[candidates_featured["targets"]
                                == candidates_featured["candidate"], "probability"] = 1.
        final_entities = candidates_featured[(
            candidates_featured['probability'] > best_threshold)]
        final_entities = final_entities.sort_values('probability', ascending=False)\
            .groupby(["doc_name", "page_num", "golden_name", "targets"], sort=False) \
            .agg({"candidate": "first",
                  "probability": max}) \
            .reset_index() \
            .sort_values(["page_num"])
        final_entities['candidate'] = final_entities.apply(lambda x:
                                                           get_raw_candidate(all_documents[x['doc_name']][x['page_num']-1]['text'],
                                                                             x['candidate']), axis=1)
        return final_entities[["doc_name", "page_num", "golden_name", "targets", "candidate", "probability"]]

    return None
