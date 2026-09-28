import json

with open('data/india/phcs.json', encoding='utf-8') as f:
    in_data = json.load(f)['phcs']
with open('data/brazil/phcs.json', encoding='utf-8') as f:
    br_data = json.load(f)
with open('data/south_africa/phcs.json', encoding='utf-8') as f:
    za_data = json.load(f)
with open('data/china/phcs.json', encoding='utf-8') as f:
    cn_data = json.load(f)['phcs']
with open('data/russia/phcs.json', encoding='utf-8') as f:
    ru_data = json.load(f)['phcs']

total = len(in_data) + len(br_data) + len(za_data) + len(cn_data) + len(ru_data)
print(f"Canonical Counts: India={len(in_data)}, Brazil={len(br_data)}, South Africa={len(za_data)}, China={len(cn_data)}, Russia={len(ru_data)}, Total={total}")

for name, dataset in [('India', in_data), ('Brazil', br_data), ('South Africa', za_data), ('China', cn_data), ('Russia', ru_data)]:
    for p in dataset:
        geo = p.get('geography', {})
        lat = geo.get('latitude')
        lon = geo.get('longitude')
        pid = p.get('phc_id')
        assert lat is not None and -90 <= lat <= 90, f"Invalid lat {lat} in {pid}"
        assert lon is not None and -180 <= lon <= 180, f"Invalid lon {lon} in {pid}"
        assert p.get('country') == name, f"Country mismatch in {pid}: {p.get('country')} vs {name}"

assert total == 271, f"Expected 271 total PHCs, got {total}"
print(f"All {total} canonical PHC coordinates and countries verified successfully across 5 countries!")
