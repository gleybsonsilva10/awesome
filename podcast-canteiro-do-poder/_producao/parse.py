import re, json, sys
src=open(sys.argv[1],encoding='utf-8').read().split('\n')
items=[]; stop=False
for ln in src:
    if ln.startswith('### Notas de rigor'): break
    m=re.match(r'^(AUGUSTO|HENRIQUE): (.*)$',ln)
    c=re.match(r'^\[(VINHETA|TRANSIÇÃO|TENSÃO|SILÊNCIO|ENCERRAMENTO)\]',ln)
    if m:
        t=re.sub(r'\*\*\([A-ZÁÉÍÓÚÇ]+\)\*\* ?','',m.group(2)).replace('**','')
        items.append({'type':'say','who':m.group(1),'text':t})
    elif c: items.append({'type':'cue','cue':c.group(1)})
    elif ln.startswith('## ') or ln.startswith('### Situação'):
        items.append({'type':'section'})
json.dump(items,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(items))
