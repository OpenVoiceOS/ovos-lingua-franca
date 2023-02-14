
# Language Support Status


- :heavy_check_mark: - fully implemented
- :construction: - lang agnostic fallback implementation
- :x: - not implemented


## Supported Languages


- [az-az](#az)
- [ca-es](#ca)
- [cs-cz](#cs)
- [da-dk](#da)
- [de-de](#de)
- [en-us](#en)
- [es-es](#es)
- [fr-fr](#fr)
- [hu-hu](#hu)
- [it-it](#it)
- [nl-nl](#nl)
- [pl-pl](#pl)
- [pt-pt](#pt)
- [ru-ru](#ru)
- [sl-si](#sl)
- [sv-se](#sv)
- [fa-ir](#fa)
- [eu-eu](#eu)
       
### az

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :heavy_check_mark:  |

       
### ca

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :x:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :heavy_check_mark:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### cs

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### da

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :heavy_check_mark:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :heavy_check_mark:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### de

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :heavy_check_mark:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :heavy_check_mark:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### en

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :heavy_check_mark:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :heavy_check_mark:  |
|  format  |  nice_duration  |  :construction:  |

       
### es

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :heavy_check_mark:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :x:  |
|  format  |  nice_date_time  |  :x:  |
|  format  |  nice_year  |  :x:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### fr

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### hu

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :x:  |
|  parse  |  extract_number  |  :x:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :x:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### it

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :heavy_check_mark:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### nl

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :heavy_check_mark:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :construction:  |

       
### pl

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :heavy_check_mark:  |

       
### pt

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :x:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :heavy_check_mark:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :heavy_check_mark:  |
|  parse  |  get_color  |  :heavy_check_mark:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :x:  |
|  format  |  nice_date_time  |  :x:  |
|  format  |  nice_year  |  :x:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :heavy_check_mark:  |
|  format  |  nice_duration  |  :construction:  |

       
### ru

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :construction:  |
|  parse  |  get_color  |  :construction:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :construction:  |
|  format  |  nice_duration  |  :heavy_check_mark:  |

       
### sl

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :x:  |
|  parse  |  extract_number  |  :x:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :x:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :x:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :x:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### sv

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :x:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :heavy_check_mark:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :heavy_check_mark:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### fa

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :heavy_check_mark:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :x:  |
|  parse  |  normalize  |  :x:  |
|  parse  |  get_gender  |  :x:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :x:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |

       
### eu

|  module  |  method  | status  |
|----------|----------|---------|
|  parse  |  extract_numbers  |  :heavy_check_mark:  |
|  parse  |  extract_number  |  :heavy_check_mark:  |
|  parse  |  extract_duration  |  :x:  |
|  parse  |  extract_datetime  |  :heavy_check_mark:  |
|  parse  |  extract_langcode  |  :construction:  |
|  parse  |  normalize  |  :heavy_check_mark:  |
|  parse  |  get_gender  |  :heavy_check_mark:  |
|  parse  |  yes_or_no  |  :heavy_check_mark:  |
|  parse  |  is_fractional  |  :x:  |
|  parse  |  extract_color_spans  |  :x:  |
|  parse  |  get_color  |  :x:  |
|  parse  |  is_ordinal  |  :x:  |
|  format  |  nice_number  |  :heavy_check_mark:  |
|  format  |  nice_time  |  :heavy_check_mark:  |
|  format  |  nice_date  |  :heavy_check_mark:  |
|  format  |  nice_date_time  |  :heavy_check_mark:  |
|  format  |  nice_year  |  :heavy_check_mark:  |
|  format  |  pronounce_number  |  :heavy_check_mark:  |
|  format  |  pronounce_lang  |  :heavy_check_mark:  |
|  format  |  nice_response  |  :x:  |
|  format  |  describe_color  |  :x:  |
|  format  |  nice_duration  |  :construction:  |
