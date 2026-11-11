import subprocess, numpy as np
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
STEP=0.005  # 5 ms windows
def _env(path, af=None):
    cmd=[FF,"-loglevel","error","-i",path,"-ac","1","-ar","16000"]+(["-af",af] if af else [])+["-f","f32le","-"]
    x=np.frombuffer(subprocess.run(cmd,capture_output=True,check=True).stdout,np.float32)
    n=int(16000*STEP); k=len(x)//n
    return 20*np.log10(np.sqrt(np.mean(x[:k*n].reshape(k,n)**2,axis=1)+1e-12))
def _pitch(path, n):
    """Periodicity per 5 ms step (0-1): peak of the normalized autocorrelation at 70-400 Hz over a 40 ms window.
    Voice is periodic (> ~0.45). Breaths into the mic, typing, rustle and scratches are not, even when they're loud."""
    cmd=[FF,"-loglevel","error","-i",path,"-ac","1","-ar","8000","-af","highpass=f=60,lowpass=f=1200","-f","f32le","-"]
    x=np.frombuffer(subprocess.run(cmd,capture_output=True,check=True).stdout,np.float32)
    hop=40; W=320; out=np.zeros(n)
    k=min(n,(len(x)-W)//hop)
    if k<=0: return out
    idx=np.arange(W)[None,:]+hop*np.arange(k)[:,None]
    fr=x[idx]; fr=fr-fr.mean(1,keepdims=True)
    F=np.fft.rfft(fr,2*W,axis=1); ac=np.fft.irfft(F*np.conj(F),axis=1)[:,:W]
    lo,hi=8000//400,8000//70
    out[:k]=ac[:,lo:hi].max(1)/(ac[:,0]+1e-9)
    return out
def analyze(path):
    v=_env(path); h=_env(path,"highpass=f=3500")
    m=min(len(v),len(h)); v,h=v[:m],h[:m]
    vs,hs=np.percentile(v,90),np.percentile(h,90)
    voiced = v > vs-24                       # clear voice
    active = voiced | (h > hs-28)            # voice OR hiss (s, th, f, t release)
    return dict(v=v,h=h,voiced=voiced,active=active,vs=vs,hs=hs,pitch=_pitch(path,m))
T=lambda t:int(round(t/STEP))
def voice_onset(A, first_word_s):
    voiced,active=A["voiced"],A["active"]; need=T(0.08)
    for i in range(max(0,T(first_word_s-1.5)), min(len(voiced),T(first_word_s+0.8))):
        if voiced[i:i+need].all():
            k=i; gap=0; j=i-1
            while j>=0:                      # walk back through sound that runs straight into the word
                if active[j]: k=j; gap=0
                else:
                    gap+=1
                    if gap*STEP>0.025: break
                j-=1
            return max(0.0,(k-1)*STEP)       # 5 ms before first sound
    raise SystemExit("no onset found")
def voice_offset(A, last_word_s):
    active=A["active"]; i=T(last_word_s); last=i; gap=0
    while i<len(active):
        if active[i]: last=i; gap=0
        else:
            gap+=1
            if gap*STEP>=0.12: break
        i+=1
    return (last+1)*STEP+0.03                # 30 ms after the final sound
def speech_mask(A, tail=0.12):
    """His voice, plus consonant hiss (s, t, f) only where it touches a word, max `tail` s. Breaths and room noise don't count."""
    v=A["voiced"]; act=A["active"]; m=v.copy(); k=int(tail/STEP); n=len(v)
    for i in range(1,n):                                     # hiss running straight out of a word
        if v[i-1] and not v[i]:
            j=i
            while j<n and j<i+k and act[j] and not v[j]: m[j]=True; j+=1
    for i in range(n-2,-1,-1):                               # hiss running straight into a word
        if v[i+1] and not v[i]:
            j=i
            while j>=0 and j>i-k and act[j] and not v[j]: m[j]=True; j-=1
    return m
