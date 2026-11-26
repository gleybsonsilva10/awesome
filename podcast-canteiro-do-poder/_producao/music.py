# Trilha original sintetizada: piano, cordas (pad), sintetizador e percussão discreta.
import numpy as np, sys, wave
SR=44100
rng=np.random.default_rng(7)
def midi(n): return 440*2**((n-69)/12)
def env_adsr(n,a,d,s,r):
    t=np.arange(n)/SR; e=np.ones(n)*s
    A=int(a*SR); D=int(d*SR); R=int(r*SR)
    e[:A]=np.linspace(0,1,A); e[A:A+D]=np.linspace(1,s,D)
    e[-R:]*=np.linspace(1,0,R); return e
def piano(note,dur,vel=0.5):
    n=int(dur*SR); t=np.arange(n)/SR; f=midi(note); y=np.zeros(n)
    for k,amp in enumerate([1,.5,.28,.16,.09,.05],1):
        fk=f*k*(1+0.0004*k*k)
        y+=amp*np.sin(2*np.pi*fk*t)*np.exp(-t*(1.2+0.9*k)*(f/260)**0.35)
    hammer=np.exp(-t*60)*rng.normal(0,.04,n)
    y=(y+hammer)*np.minimum(1,t/0.004); y[-2000:]*=np.linspace(1,0,2000)
    return vel*y/2.2
def strings(notes,dur,vol=0.18,att=1.5,rel=2.0):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for nt in notes:
        for det in (-0.12,0,0.11):
            f=midi(nt)*2**(det/12)
            vib=1+0.003*np.sin(2*np.pi*5.2*t+rng.random()*6)
            ph=2*np.pi*np.cumsum(f*vib)/SR
            saw=sum(np.sin(k*ph)/k for k in range(1,9))
            y+=saw
    # low-pass simples (média móvel dupla)
    k=np.ones(18)/18; y=np.convolve(np.convolve(y,k,'same'),k,'same')
    return vol*y/len(notes)/3*env_adsr(n,att,0.5,0.9,rel)
def synth_pad(notes,dur,vol=0.12):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for nt in notes:
        f=midi(nt); y+=np.sin(2*np.pi*f*t+0.6*np.sin(2*np.pi*f*2.001*t))*(0.6+0.4*np.sin(2*np.pi*0.15*t))
    return vol*y/len(notes)*env_adsr(n,2.0,0.5,1,2.5)
def kick(vol=0.5):
    n=int(0.6*SR); t=np.arange(n)/SR
    f=45+70*np.exp(-t*25); return vol*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)
def tick(vol=0.08):
    n=int(0.08*SR); t=np.arange(n)/SR
    return vol*rng.normal(0,1,n)*np.exp(-t*70)
def boom(vol=0.6):
    n=int(4*SR); t=np.arange(n)/SR
    f=38+30*np.exp(-t*3); return vol*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.1)
def place(buf,x,at):
    i=int(at*SR); j=min(len(buf),i+len(x)); buf[i:j]+=x[:j-i]
def reverb(y,mix=0.25):
    out=y.copy()
    for d,g in [(0.029,.5),(0.037,.45),(0.053,.4),(0.079,.35),(0.113,.3),(0.167,.25),(0.241,.18)]:
        s=int(d*SR); z=np.zeros_like(y); z[s:]=y[:-s]*g; out+=z*mix
    return out
# Progressão em Ré menor: Dm - Bb - F - C  (cinematográfica, executiva)
CH=[[50,57,62,65],[46,53,58,62],[41,48,53,57],[48,55,60,64]]
MEL=[74,72,69,70, 69,65,67,64]
def vinheta():
    L=16.0; b=np.zeros(int(L*SR)); beat=0.75
    for i,c in enumerate(CH):
        at=i*3.0
        place(b,strings(c,4.0,0.22,0.6,1.2),at)
        for j,nt in enumerate([c[0]+12,c[1]+12,c[2]+12,c[3]+12]):
            place(b,piano(nt,2.5,0.35),at+j*beat)
        place(b,kick(0.45),at); place(b,kick(0.25),at+1.5)
        for j in range(4): place(b,tick(),at+j*beat+beat/2)
    place(b,boom(0.55),12.0)
    place(b,piano(74,4,0.6),12.0); place(b,piano(62,4,0.5),12.0); place(b,piano(57,4,0.45),12.0)
    place(b,strings([50,57,62,69],4.0,0.25,0.3,2.5),12.0)
    return reverb(b,0.3)
def transicao():
    L=5.0; b=np.zeros(int(L*SR))
    for j,nt in enumerate([62,65,69,74]): place(b,piano(nt,3.0,0.32),j*0.28)
    place(b,synth_pad([50,57,62],4.6,0.10),0)
    return reverb(b,0.35)
def tensao():
    L=40.0; b=np.zeros(int(L*SR))
    place(b,synth_pad([38,45,50],L,0.10),0)
    place(b,strings([50,53,56],L,0.08,4,6),0)  # trítono discreto = tensão
    for k in range(int(L/1.2)): place(b,kick(0.18 if k%2==0 else 0.10),k*1.2)
    return reverb(b,0.2)
def silencio_bell():
    b=np.zeros(int(3.0*SR)); place(b,piano(81,3,0.12),0.2); return reverb(b,0.5)
def leito_abertura():
    L=24.0; b=np.zeros(int(L*SR))
    for i in range(8):
        place(b,strings(CH[i%4],3.6,0.10,1.0,1.4),i*3.0)
    return reverb(b,0.3)
def encerramento():
    L=26.0; b=np.zeros(int(L*SR))
    for r in range(2):
        for i,c in enumerate(CH):
            at=r*12+i*3.0
            place(b,strings(c,4.0,0.2,0.8,1.5),at)
            place(b,piano(MEL[(r*4+i)%8],2.8,0.42),at)
            place(b,piano(c[0]+12,2.8,0.25),at+1.5)
            place(b,kick(0.3),at)
    place(b,piano(62,5,0.45),24.0); place(b,piano(50,5,0.4),24.0)
    return reverb(b,0.35)
def save(name,y):
    y=y/np.max(np.abs(y))*0.85; s=(np.stack([y,y],1)*32767).astype(np.int16)
    with wave.open(name,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
out=sys.argv[1]
for n,f in [('vinheta',vinheta),('transicao',transicao),('tensao',tensao),('silencio',silencio_bell),('leito',leito_abertura),('encerramento',encerramento)]:
    save(f"{out}/{n}.wav",f())
print("ok")
