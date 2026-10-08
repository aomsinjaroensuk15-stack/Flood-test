#!/usr/bin/env python3
"""สร้าง data/hazard.json — ประเมินความเสี่ยงทั้งประเทศเป็นตาราง (ไม่ขึ้นกับการซูมของผู้ใช้)
ใช้กฎเดียวกับ assess() ใน index.html: ฝน 24/48 ชม., ฝนรายวัน 7 วัน, น้ำในแม่น้ำ (GloFAS) เทียบ 90 วัน
ค่า 0=ไม่พบสัญญาณเสี่ยง 1=เฝ้าระวัง 2=เสี่ยง 3=อันตราย 9=ไม่มีข้อมูล"""
import json, time, datetime, urllib.request, sys
STEP=0.4; LAT0,LAT1,LON0,LON1=5.5,20.5,97.3,105.7
R24=(35,90); R48=(50,120)  # เกณฑ์ตั้งต้น (placeholder) ต้องตรงกับ index.html
FC='https://api.open-meteo.com/v1/forecast?hourly=precipitation&daily=precipitation_sum&past_days=1&forecast_days=7&timeformat=unixtime&timezone=Asia%2FBangkok&'
FL='https://flood-api.open-meteo.com/v1/flood?daily=river_discharge&past_days=90&forecast_days=7&'

def get(url):
    for i in range(5):
        try:
            rq=urllib.request.Request(url,headers={'User-Agent':'flood-check-hazard-bot'})
            with urllib.request.urlopen(rq,timeout=90) as r: return json.load(r)
        except Exception as e:
            print('retry',i+1,e,file=sys.stderr); time.sleep(20*(i+1))  # รอแล้วลองใหม่ (รวมกรณีถูกจำกัดการเรียก)
    return None

def calc(R,F):
    h=R['hourly']; n=time.time(); p=f=0.0; c=0
    for t,x in zip(h['time'],h['precipitation']):
        if x is None: continue
        c+=1
        if n-86400<t<=n: p+=x
        elif n<t<=n+172800: f+=x
    if not c: return None
    days=[0 if x is None else int(x+.5) for x in (R['daily']['precipitation_sum'] or [])[1:8]]
    o={'r24':p,'r48':f,'days':days,'dr':None}
    try:
        a=F['daily']['river_discharge']; b=[x for x in a[:-7] if x is not None]; g=[x for x in a[-7:] if x is not None]
        if len(b)>30 and g and max(b)>=1: o['dr']=max(g)/max(b)
    except Exception: pass
    return o

def assess(o):
    s=rs=0; w=[]
    if o['r24']>=R24[1] or o['r48']>=R48[1]: s=2; rs=2; w.append('ฝนตกหนักมาก')
    elif o['r24']>=R24[0] or o['r48']>=R48[0]: s=1; rs=1; w.append('มีฝนตกหนัก')
    dm=max([0]+o['days'])
    if dm>=R24[1]:
        s=max(s,2)
        if rs<2: w.append('คาดว่าฝนตกหนักมากภายใน 7 วัน')
        rs=2
    elif dm>=R24[0]:
        s=max(s,1)
        if rs<1: w.append('คาดว่าฝนตกหนักภายใน 7 วัน')
        rs=max(rs,1)
    dr=o['dr']
    if dr is not None:
        if dr>=1:
            s=max(s,2); w.append('ปริมาณน้ำในแม่น้ำ (จำลอง) คาดสูงกว่าช่วง 90 วันที่ผ่านมา')
            if rs>=2: s=3
        elif dr>=.7: s=max(s,1); w.append('ปริมาณน้ำในแม่น้ำ (จำลอง) ใกล้ระดับสูงสุดรอบ 90 วัน')
    return s,' '.join(w)

def main(out='data/hazard.json'):
    rows=int(round((LAT1-LAT0)/STEP))+1; cols=int(round((LON1-LON0)/STEP))+1
    pts=[(round(LAT0+i*STEP,3),round(LON0+j*STEP,3)) for i in range(rows) for j in range(cols)]
    lv=[9]*len(pts); why={}
    for k in range(0,len(pts),50):  # ทีละ 50 จุด พักระหว่างชุด เพื่อไม่ชนโควตาต่อนาที
        ch=pts[k:k+50]
        q='latitude='+','.join(str(a) for a,b in ch)+'&longitude='+','.join(str(b) for a,b in ch)
        R=get(FC+q); F=get(FL+q)
        if R is not None:
            rv=R if isinstance(R,list) else [R]; fv=(F if isinstance(F,list) else [F]) if F else []
            for i in range(len(ch)):
                try: o=calc(rv[i],fv[i] if i<len(fv) else None)
                except Exception: o=None
                if o:
                    s,w=assess(o); lv[k+i]=s
                    if s: why[str(k+i)]=w
        time.sleep(15)
    if lv.count(9)>len(lv)*0.5:
        print('ข้อมูลหายเกินครึ่ง ไม่เขียนทับไฟล์เดิม',file=sys.stderr); sys.exit(1)
    d={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'step':STEP,'lat0':LAT0,'lon0':LON0,'rows':rows,'cols':cols,'lv':''.join(map(str,lv)),'why':why}
    with open(out,'w',encoding='utf-8') as fh: json.dump(d,fh,ensure_ascii=False,separators=(',',':'))
    print('ok',rows,'x',cols,'ข้อมูล',len(lv)-lv.count(9),'/',len(lv))

if __name__=='__main__': main()
