import json
import os
import glob

# Load shooting data
shootings = json.load(open('data/incidents/tier2_shootings.json', encoding='utf-8'))
less_lethal = json.load(open('data/incidents/tier2_less_lethal.json', encoding='utf-8'))

def fix_entry_sources(entry):
    if entry.get('sources'):
        return False

    entry_id = entry['id']
    metadata_path = f'data/sources/{entry_id}/metadata.json'

    if not os.path.exists(metadata_path):
        return False

    try:
        metadata = json.load(open(metadata_path, encoding='utf-8'))
    except:
        return False

    sources = []

    if 'sources' in metadata and metadata['sources']:
        for s in metadata['sources']:
            url = s.get('url', '')
            archive_path = s.get('archive_path', '').replace('\\', '/')

            domain = url.split('/')[2] if '://' in url else ''
            name_map = {
                'nbcnews.com': 'NBC News',
                'cnn.com': 'CNN',
                'pressfreedomtracker.us': 'US Press Freedom Tracker',
                'wikipedia.org': 'Wikipedia',
                'abc7.com': 'ABC7',
                'cbsnews.com': 'CBS News',
            }
            name = name_map.get(domain.replace('www.', ''), domain)

            sources.append({
                'url': url,
                'name': name,
                'tier': 2,
                'primary': len(sources) == 0,
                'archived': True,
                'archive_path': archive_path
            })
    elif 'url' in metadata:
        url = metadata['url']
        domain = url.split('/')[2] if '://' in url else ''
        name_map = {
            'nbcnews.com': 'NBC News',
            'cnn.com': 'CNN',
            'pressfreedomtracker.us': 'US Press Freedom Tracker',
        }
        name = name_map.get(domain.replace('www.', ''), domain)

        archive_files = glob.glob(f'data/sources/{entry_id}/article*.txt')
        archive_path = archive_files[0].replace('\\', '/') if archive_files else ''

        sources.append({
            'url': url,
            'name': name,
            'tier': 2,
            'primary': True,
            'archived': bool(archive_path),
            'archive_path': archive_path
        })

    if sources:
        entry['sources'] = sources
        return True
    return False

fixed_shootings = 0
for entry in shootings:
    if fix_entry_sources(entry):
        fixed_shootings += 1
        print(f"Fixed {entry['id']}: {len(entry['sources'])} sources")

fixed_ll = 0
for entry in less_lethal:
    if fix_entry_sources(entry):
        fixed_ll += 1
        print(f"Fixed {entry['id']}: {len(entry['sources'])} sources")

with open('data/incidents/tier2_shootings.json', 'w', encoding='utf-8') as f:
    json.dump(shootings, f, indent=2, ensure_ascii=False)

with open('data/incidents/tier2_less_lethal.json', 'w', encoding='utf-8') as f:
    json.dump(less_lethal, f, indent=2, ensure_ascii=False)

print(f"\nFixed {fixed_shootings} shooting entries")
print(f"Fixed {fixed_ll} less-lethal entries")
