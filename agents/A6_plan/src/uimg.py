# Чтение плана 1 этажа, нарисованного архитектором (скриншот Revit от 17.11): цветные помещения → оси здания.
from PIL import Image
import numpy as np, cv2, math
IMG = '/tmp/claude-0/-home-user-ENU/bb2fce9f-64bd-51be-9b3b-d67c281d68e1/images/12.png'
S = 8.214
def to_uv(x, y):
    px = x * 0.8208 - y * 0.5710
    py = x * 0.5710 + y * 0.8208
    return ((px + 89.5) / S, 0.1 + (py - 399.5) / S)
COLS = {'серый (холл)': [(240, 240, 236), (243, 243, 240)], 'розово-сиреневый': [(250, 230, 249), (251, 235, 250)], 'бирюзовый': [(230, 250, 250)],
        'сиреневый': [(241, 230, 250)], 'голубой': [(230, 234, 250)], 'салатовый': [(244, 250, 230)], 'лососевый': [(243, 193, 172), (240, 177, 151)],
        'лавандовый': [(236, 230, 250)], 'персиковый': [(250, 242, 230)], 'жёлтый': [(243, 238, 194)]}
def regions(minpx=300):
    im = np.array(Image.open(IMG).convert('RGB')).astype(int)
    out = []
    for nm, lst in COLS.items():
        m = np.zeros(im.shape[:2], bool)
        for c in lst:
            m |= np.abs(im - np.array(c)).sum(2) < 5
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            if st[i, 4] < minpx: continue
            cs, _ = cv2.findContours((lab == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            c = max(cs, key=cv2.contourArea)
            ap = cv2.approxPolyDP(c, 2.5, True)[:, 0, :]
            uv = [to_uv(x, y) for x, y in ap]
            out.append(dict(c=nm, a=st[i, 4] / S ** 2, uv=uv, cen=to_uv(*cen[i])))
    return out
if __name__ == '__main__':
    for r in sorted(regions(), key=lambda r: r['cen'][0]):
        print(f"{r['c']:18s} {r['a']:6.0f} м²  центр ({r['cen'][0]:5.1f},{r['cen'][1]:5.1f})  " + ' '.join(f"({x:.1f},{y:.1f})" for x, y in r['uv']))
