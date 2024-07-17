from typing import Optional, List

from ovos_plugin_manager.templates.transformers import UtteranceTransformer
from ovos_utils.log import LOG

from lingua_franca.parse import normalize


class UtteranceNormalizer(UtteranceTransformer):

    def __init__(self, name="ovos-lf-utterance-normalizer", priority=5):
        super().__init__(name, priority)

    @staticmethod
    def strip_punctuation(utterance: str):
        return utterance.rstrip('.').rstrip('?').rstrip('!').rstrip(',').rstrip(';')

    def transform(self, utterances: List[str],
                  context: Optional[dict] = None) -> (list, dict):
        context = context or {}
        norm = [self.strip_punctuation(u) for u in utterances] + utterances
        try:
            lang = context.get("lang") or self.config.get("lang", "en-us")
            norm += [normalize(u, lang=lang, remove_articles=False) for u in norm] + \
                    [normalize(u, lang=lang, remove_articles=True) for u in norm]
        except:
            LOG.exception("lingua_franca utterance normalization failed")

        return list(set(norm)), context
