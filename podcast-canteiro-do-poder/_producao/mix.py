import json, subprocess, numpy as np, wave, sys
SR=44100
def load(f):
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",f,"-f","s16le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
def fade(x,fi,fo):
    x=x.copy(); a=int(fi*SR); b=int(fo*SR)
    if a: x[:a]*=np.linspace(0,1,a)
    if b: x[-b:]*=np.linspace(1,0,b)
    return x
items=json.load(open('items.json')); M={n:load(f'mus/{n}.wav') for n in ['vinheta','transicao','tensao','silencio','leito','encerramento']}
voice=[]; music=[]  # (start, array, gain)
t=0.0; rng=np.random.default_rng(1)
def addm(x,g,at): music.append((at,x,g))
started=False
for i,it in enumerate(items):
    if it['type']=='cue':
        c=it['cue']
        if c=='VINHETA':
            addm(M['vinheta'],0.55,t); addm(fade(M['leito'],2,6),0.10,t+14.5); t+=15.2
        elif c=='TRANSIÇÃO':
            t+=0.5; addm(M['transicao'],0.40,t); t+=4.2
        elif c=='TENSÃO':
            t+=0.3; addm(fade(M['tensao'],3,8),0.16,t); t+=2.5
        elif c=='SILÊNCIO':
            t+=0.8; addm(M['silencio'],0.22,t); t+=2.6
        elif c=='ENCERRAMENTO':
            t+=0.8; addm(fade(M['encerramento'],0.5,6),0.55,t); t+=len(M['encerramento'])/SR
        continue
    if it['type']=='section': t+=0.35; continue
    x=load(f'voz/{i:03d}.mp3')
    nz=np.abs(x)>0.01; idx=np.where(nz)[0]
    x=x[max(0,idx[0]-800):idx[-1]+2500]
    rms=np.sqrt(np.mean(x[np.abs(x)>0.02]**2)); x=x*(0.12/rms)
    voice.append((t,x)); t+=len(x)/SR+0.32+rng.uniform(0,0.18)
N=int((t+1)*SR); V=np.zeros(N,np.float32); Mu=np.zeros(N,np.float32)
for at,x in voice: i=int(at*SR); V[i:i+len(x)]+=x
for at,x,g in music:
    i=int(at*SR); j=min(N,i+len(x)); Mu[i:j]+=x[:j-i]*g
# ducking: reduz música quando há voz
env=np.convolve(np.abs(V),np.ones(4410)/4410,'same'); duck=np.where(env>0.01,0.55,1.0)
duck=np.convolve(duck,np.ones(8820)/8820,'same')
out=V+Mu*duck; out=out/np.max(np.abs(out))*0.95
s=(np.stack([out,out],1)*32767).astype(np.int16)
with wave.open('ep01_master.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
print('dur min', round(t/60,2))
