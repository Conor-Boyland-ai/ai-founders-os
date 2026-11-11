"""Auto color grade (approved by the user 2026-10-01): pulls out the yellow/orange cast and brightens.
Gray-world white balance at 50% strength (keeps natural skin warmth), a gentle lift curve,
+5% contrast, +4% saturation. grade_filter(raw) returns an ffmpeg filter string tuned to that clip."""
import subprocess, numpy as np
import onset
def grade_filter(raw, strength=0.5, lift=1.0, samples=6):
    """strength: how much of the color cast to remove (0-1). lift: brightness multiplier on the default lift curve (1.0 = approved look)."""
    FF=onset.FF
    probe=subprocess.run([FF,"-i",raw],capture_output=True,text=True).stderr
    hh,mm,ss=probe.split("Duration: ")[1].split(",")[0].split(":"); total=int(hh)*3600+int(mm)*60+float(ss)
    means=[]
    for k in range(samples):
        t=total*(k+0.5)/samples
        b=subprocess.run([FF,"-loglevel","error","-ss",f"{t:.2f}","-i",raw,"-frames:v","1","-vf","scale=160:-1",
                          "-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
        if b: means.append(np.frombuffer(b,np.uint8).reshape(-1,3).astype(float).mean(0))
    m=np.mean(means,0); gains=m.mean()/m
    r,g,bb=[1+(x-1)*strength for x in gains]
    c=lambda x,y: min(0.99, x+(y-x)*lift)
    curve=f"0/0 0.25/{c(0.25,0.31):.3f} 0.5/{c(0.5,0.58):.3f} 0.75/{c(0.75,0.83):.3f} 1/1"
    return (f"colorchannelmixer=rr={r:.4f}:gg={g:.4f}:bb={bb:.4f},"
            f"curves=all='{curve}',eq=contrast=1.05:saturation=1.04")
