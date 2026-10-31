import re,sys,glob
for f in sorted(glob.glob(sys.argv[1])):
    s=open(f).read()
    ms=[m.start() for m in re.finditer(r'(?i)item\s*2\.?\s*[\-—–:]?\s*(description of )?propert',s)]
    best=None
    for st in ms:
        seg=s[st:st+14000]
        m3=re.search(r'(?i)item\s*3\.?\s*[\-—–:]?\s*legal',seg[20:])
        if m3 and m3.start()>300: best=seg[:m3.start()+20]
    print('=====',f)
    if not best: print('NOT FOUND'); continue
    t=re.sub(r'\s*\|\s*(\|\s*)*',' | ',best); t=re.sub(r'\n+',' ',t); t=re.sub(r'(\| )+','| ',t)
    print(t[:int(sys.argv[2])])
