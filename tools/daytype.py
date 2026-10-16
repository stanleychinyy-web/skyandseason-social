"""Day stem/branch for any date, and each Day Master's day-type (Ten God, plain words)."""
import datetime
STEMS=[('Yang','Wood'),('Yin','Wood'),('Yang','Fire'),('Yin','Fire'),('Yang','Earth'),('Yin','Earth'),('Yang','Metal'),('Yin','Metal'),('Yang','Water'),('Yin','Water')]
BRANCH_EL=['Water','Earth','Wood','Wood','Earth','Fire','Fire','Earth','Metal','Metal','Earth','Water']
BRANCH_ANIMAL=['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig']
REF=datetime.date(2026,10,17)  # 甲子 day: stem 0, branch 0 (verified with the site's calendar engine)
PROD={'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
CTRL={'Wood':'Earth','Earth':'Water','Water':'Fire','Fire':'Metal','Metal':'Wood'}
def day(d):
    n=(d-REF).days
    return n%10, n%12
def daytype(dm, ds):
    (pd,ed),(pt,et)=STEMS[dm],STEMS[ds]; same=pd==pt
    if ed==et: return 'Friend' if same else 'Rival'
    if PROD[ed]==et: return 'Joy' if same else 'Speak-up'
    if PROD[et]==ed: return 'Insight' if same else 'Support'
    if CTRL[ed]==et: return 'Opportunity' if same else 'Steady-money'
    if CTRL[et]==ed: return 'Pressure' if same else 'Recognition'
def name(i): return f"{STEMS[i][0]} {STEMS[i][1]}"
