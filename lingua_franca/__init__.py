from .internal import get_default_lang, set_default_lang, get_default_loc, \
    get_active_langs, _set_active_langs, get_primary_lang_code, \
    get_full_lang_code, resolve_resource_file, load_language, \
    load_languages, unload_language, unload_languages, get_supported_langs

from lingua_franca import config

# honor the global OVOS language preferences unless configured to do otherwise
if config.ovos_defaults:
    try:
        from ovos_config.locale import setup_locale
        from ovos_config.config import Configuration
        # if running in a OVOS system, set default lang/timezone from config file
        setup_locale()
        # pre load all secondary_langs
        secondary_langs = Configuration().get("secondary_langs", [])
        if secondary_langs:
            load_languages(secondary_langs)
    except ImportError:
        pass
