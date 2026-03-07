import json, os, re
path = 'assets/knowledge_base/learning_stats/knowledge_index.json'
print('exists', os.path.exists(path))
with open(path,'r',encoding='utf-8') as f:
    data=json.load(f)
entries=data.get('entries',{})
print('entries', len(entries))
count=0
for entry_id,meta in list(entries.items())[:50]:
    selectors=[]
    examples=meta.get('examples') or []
    if isinstance(examples,list):
        for ex in examples:
            if isinstance(ex,str):
                found=re.findall(r'([.#][a-zA-Z_-][\\w\\-\\[\\]="\\']*)', ex)
                selectors.extend(found)
    if not selectors:
        title = meta.get('title','') or ''
        found=re.findall(r'([.#][a-zA-Z_-][\\w\\-\\[\\]="\\']*)', title)
        selectors.extend(found)
    print(entry_id, 'selcount', len(selectors))
    count+=1
print('processed', count)
