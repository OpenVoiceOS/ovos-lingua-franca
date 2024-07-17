from os.path import dirname, exists

from lingua_franca.format import _REGISTERED_FUNCTIONS as format_methods
from lingua_franca.internal import _SUPPORTED_LANGUAGES as langs, get_full_lang_code
from lingua_franca.parse import _REGISTERED_FUNCTIONS as parse_methods

lf_root = f"{dirname(dirname(__file__))}/lingua_franca"
res_dir = f"{lf_root}/res"
lang_root = f"{lf_root}/lang"
mdfile = f"{dirname(dirname(__file__))}/lang_support.md"

parse = {l: {} for l in langs}
fmt = {l: {} for l in langs}

res_files = {"extract_langcode": "text/{lang}/langs.json",
             "pronounce_lang": "text/{lang}/langs.json",
             "yes_or_no": "text/{lang}/yesno.json",
             "nice_date": "text/{lang}/date_time.json",
             "nice_date_time": "text/{lang}/date_time.json",
             "nice_year": "text/{lang}/date_time.json",
             "describe_color": "text/{lang}/colors.json",
             "get_color": "text/{lang}/colors.json",
             "extract_color_spans": "text/{lang}/colors.json"}

fallback_methods = {
    'nice_duration': ["pronounce_number"]
}

generics = {l: ["extract_langcode",
                "describe_color",
                "get_color",
                'nice_duration',
                "extract_color_spans"] for l in langs}


def check_resource_file_methods():
    global parse, fmt

    for lang in langs:
        for mname in parse_methods:
            if mname in res_files:
                rfile = res_files[mname].format(lang=get_full_lang_code(lang))
                impl = exists(f"{res_dir}/{rfile}")
                parse[lang][mname] = impl
            else:
                parse[lang][mname] = False

        for mname in format_methods:
            if mname in res_files:
                rfile = res_files[mname].format(lang=get_full_lang_code(lang))
                impl = exists(f"{res_dir}/{rfile}")
                fmt[lang][mname] = impl
            else:
                fmt[lang][mname] = False


def check_lang_files():
    global parse, fmt
    for lang in langs:
        lparse = f"{lang_root}/parse_{lang}.py"
        if exists(lparse):
            with open(lparse) as f:
                code = f.read()
                for mname in parse_methods:
                    impl = f"def {mname}_{lang}(" in code
                    parse[lang][mname] = parse[lang].get(mname) or impl
                    if impl and mname in generics[lang]:
                        generics[lang].remove(mname)

        lfmt = f"{lang_root}/format_{lang}.py"
        if exists(lfmt):
            with open(lfmt) as f:
                code = f.read()
                for mname in format_methods:
                    impl = f"def {mname}_{lang}(" in code
                    fmt[lang][mname] = fmt[lang].get(mname) or impl
                    if impl and mname in generics[lang]:
                        generics[lang].remove(mname)


def check_fallback_impls():
    global parse, fmt
    for lang in langs:
        lparse = f"{lang_root}/parse_{lang}.py"
        if exists(lparse):
            with open(lparse) as f:
                code = f.read()
                for mname in parse_methods:
                    if mname in fallback_methods and not parse[lang].get(mname):
                        parse[lang][mname] = any([f"def {m}_{lang}(" in code
                                                  for m in fallback_methods[mname]])

        lfmt = f"{lang_root}/format_{lang}.py"
        if exists(lfmt):
            with open(lfmt) as f:
                code = f.read()
                for mname in format_methods:
                    if mname in fallback_methods and not fmt[lang].get(mname):
                        fmt[lang][mname] = any([f"def {m}_{lang}(" in code
                                                for m in fallback_methods[mname]])


def get_mkdown():
    print(generics)
    mkdown = """
# Language Support Status


- :heavy_check_mark: - fully implemented
- :construction: - lang agnostic fallback implementation
- :x: - not implemented


## Supported Languages

"""

    for lang in langs:
        mkdown += f"\n- [{get_full_lang_code(lang)}](#{lang})"

    for lang in langs:
        mkdown += f"""
       
### {lang}
"""

        table = """
|  module  |  method  | status  |
|----------|----------|---------|
"""
        template = "|  {module}  |  {method}  |  {status}  |\n"

        for m in parse_methods:
            if m not in generics[lang]:
                s = ":heavy_check_mark:" if parse[lang].get(m) else ":x:"
            else:
                s = ":construction:" if parse[lang].get(m) else ":x:"
            a = template.format(module="parse", method=m,
                                lang=lang, status=s)
            table += a

        for m in format_methods:
            if m not in generics[lang]:
                s = ":heavy_check_mark:" if fmt[lang].get(m) else ":x:"
            else:
                s = ":construction:" if fmt[lang].get(m) else ":x:"
            a = template.format(module="format", method=m,
                                lang=lang, status=s)
            table += a

        mkdown += table

    with open(mdfile, "w") as f:
        f.write(mkdown)
    print(mkdown)


check_resource_file_methods()
check_lang_files()
check_fallback_impls()
get_mkdown()
