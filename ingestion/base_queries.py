# ingestion/base_queries.py
# Broad search terms for each disruption domain.
# Never use specific keywords — the AI decides what is relevant.

BROAD_QUERIES = {
    'pandemic':  ['disease outbreak health emergency', 'virus epidemic WHO alert'],
    'conflict':  ['geopolitical tension military border', 'sanctions trade restrictions'],
    'weather':   ['natural disaster flood typhoon cyclone earthquake'],
    'labour':    ['workers strike protest industrial action walkout'],
    'political': ['trade policy tariff regulation government'],
    'economic':  ['commodity price inflation currency exchange rate'],
}