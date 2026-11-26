import asyncio, ssl, os, json, sys
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
V={'AUGUSTO':('pt-BR-AntonioNeural','-7%','-9Hz'),'HENRIQUE':('en-US-BrianMultilingualNeural','+2%','+0Hz')}
items=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
sem=asyncio.Semaphore(5); px=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
async def one(i,it):
    f=f"{out}/{i:03d}.mp3"
    if os.path.exists(f) and os.path.getsize(f)>1000: return
    v,r,p=V[it['who']]
    async with sem:
        for k in range(4):
            try:
                await edge_tts.Communicate(it['text'],v,rate=r,pitch=p,proxy=px).save(f); return
            except Exception as e: print('retry',i,e); await asyncio.sleep(2*(k+1))
async def main():
    await asyncio.gather(*[one(i,it) for i,it in enumerate(items) if it['type']=='say'])
asyncio.run(main())
