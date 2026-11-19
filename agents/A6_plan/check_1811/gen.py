# Сверка плана архитектора с программой табл. 26 Пособия и решениями по проекту.
# Основа — DWG 1–3 этажей (19.11): площадь по заливке помещения, номер по марке, назначение по цвету легенды.
# Для сравнения — экспликация PDF от 18.11 (площади помещений из Revit, полезные).
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
P = {r['no']: r for r in json.load(open(os.path.join(HERE, 'rooms_1811.json')))}
DW = json.load(open(os.path.join(HERE, 'rooms_dwg_1911.json')))
W = {r['no']: dict(a=r['a'] or 0.0, cat=r['cat'], f=int(f)) for f in DW for r in DW[f]['rooms'] if r['no'].isdigit()}
NEW = {'250': 'Учебная зона (новая)', '251': 'Коридор (новый)', '252': 'Учебная зона (новая)', '343': 'Научная зона (новая)', '344': 'Научная зона (новая)'}


def name(n):
    return P[n]['n'] if n in P else NEW.get(n, W[n]['cat'])


def A(ns, src=W):
    return sum((src[n]['a'] if n in src else 0) for n in ns)


def fm(x, d=0):
    return f"{x:,.{d}f}".replace(',', ' ').replace('.', ',').replace('-', '−')


def floors(ns):
    fl = sorted({(W[n]['f'] if n in W else P[n]['f']) for n in ns})
    return ', '.join(map(str, fl)) if fl else '—'


STORE = {'138': 2.5, '246': 1.5, '248': 1.5, '311': 1.5, '313': 1.5, '310': 2.5}
CAP = sum(W[n]['a'] / r for n, r in STORE.items())
CAPP = sum(P[n]['a'] / r for n, r in STORE.items())
OPEN = ['203', '224', '225', '316', '330']
U_P = ['114', '204', '205', '206', '216', '226']; U = U_P + ['250', '252']
S_P = ['318', '319', '327', '328', '329', '340', '341', '342']; S = ['318', '327', '328', '329', '340', '341', '342', '343', '344']
G = ['115', '117', '118']; AV = ['227', '228', '309']; SP = ['105', '131', '132', '133', '134']
CAT = ['141', '142', '214', '217', '317', '331']
# строка, норма, помещения PDF, помещения DWG, где не хватает и что делать
ROWS = [
    ('Научные читальные залы', 2700, S_P, S, '3,0 м² × 900 мест', 'только 3 этаж; резерв — коридор 315 и открытый фонд 3 этажа с запасом проходов'),
    ('Учебные читальные залы', 1728, U_P, U, '2,4 м² × 720 мест', '1 и 2 этажи; резерв — вестибюль 1 этажа и коридоры 2 этажа'),
    ('АВ-залы, крупноформатные, редкие книги', 900, AV, AV, '5,0 м² × 180 мест', 'нет зала крупноформатных изданий; АВ-залы только на 2 этаже'),
    ('Помещения групповых занятий', 792, G, G, '2,2 м² × 360 мест', 'только 3 комнаты на 1 этаже; на 2 и 3 этажах групповых нет'),
    ('Служебно-производственные', 540, SP, SP, '3 м² на 10 тыс. ед.', 'нет санузлов и душевых персонала, комнаты приёма пищи, кабинетов заведующих, склада'),
    ('Каталоги и СБО', 503, CAT, CAT, 'шкафы + сотрудники + СБО', 'по электронной оценке нужно 290–330 м² — этого хватает'),
    ('Открытый фонд, 360 тыс.', 1800, OPEN, OPEN, '5 м² на 1 000 ед.', '2 и 3 этажи; вмещает около 318 тыс. из 360'),
    ('Абонемент', 678, ['140', '215', '139'], ['140', '215', '139'], '1,8 м² × 360 + 5 м² × 6 сотрудников', 'абонемент 2 этажа 215 далеко от хранилища'),
    ('Лаборатории', 360, ['136'], ['136'], '2 м² на 10 тыс. ед.', 'решение 17.11 — 160–200 м²: хватает'),
    ('Аванзал', 450, ['116', '201'], ['116', '201'], '1,5 м² × 270 + 5 м² × 9', 'норма «до 15 %» — верхний предел, недобор не нарушение'),
    ('Комплектование и обработка', 78, ['130'], ['130'], '6 м² на сотрудника', '1 этаж'),
    ('Сотрудники хранения', 52, ['135'], ['135'], '4 м² на сотрудника', '1 этаж'),
    ('Закрытое хранение, 1,44 млн', 2160, list(STORE), list(STORE), 'по вместимости', '1–3 этажи; вмещает 1,41 млн при мобильных стеллажах на 2–3 этажах'),
    ('Служебный каталог', 112.5, [], [], '—', 'электронный — ваше решение 17.11'),
]
OKROWS = {'Каталоги и СБО', 'Лаборатории', 'Аванзал', 'Служебный каталог'}   # недобор по решению или по смыслу нормы


def val(nm, ns, src):
    if nm.startswith('Закрытое'):
        return (CAP if src is W else CAPP) * 1.5
    return A(ns, src)


def cls(p):
    return 'ok' if p >= 95 else ('mid' if p >= 70 else 'low')


TN = TC = TCP = 0
prow = []; short = []
for nm, norm, pp, dd, how, where in ROWS:
    a, b = val(nm, pp, P), val(nm, dd, W)
    p = 100 * b / norm
    TN += norm; TC += min(b, norm); TCP += min(a, norm)
    tag = cls(p) + (' over' if p > 120 else '')
    d = b - a
    prow.append(f'<tr><td>{nm}<div class="note">{how}</div></td><td class="n">{fm(norm, 1 if norm % 1 else 0)}</td><td class="n muted">{fm(a)}</td><td class="n">{fm(b)}</td>'
                f'<td class="n {"up" if d > 5 else ("dn" if d < -5 else "")}">{("+" if d > 0.5 else "") + fm(d) if abs(d) >= 0.5 else "—"}</td>'
                f'<td class="n"><span class="pill {tag}">{p:.0f} %</span></td><td class="rm">{", ".join(dd) or "—"}</td></tr>')
    if b < norm * 0.95 and not nm.startswith('Закрытое'):
        short.append((nm, norm - b, norm, b, dd, where, nm in OKROWS))
PROG = 100 * TC / TN; PROGP = 100 * TCP / TN
prow.append(f'<tr class="tot"><td>Программа в целом</td><td class="n">{fm(TN, 1)}</td><td class="n muted">{PROGP:.0f} %</td><td class="n">{PROG:.0f} %</td><td></td><td></td><td class="note">превышения не засчитываются</td></tr>')

# ---------- чего не хватает: по убыванию нехватки
SEATN = {'Научные читальные залы': 3.0, 'Учебные читальные залы': 2.4, 'АВ-залы, крупноформатные, редкие книги': 5.0, 'Помещения групповых занятий': 2.2}
srt = sorted([s for s in short if not s[6]], key=lambda s: -s[1]) + sorted([s for s in short if s[6]], key=lambda s: -s[1])
shrow = []
for nm, dm, norm, b, dd, where, okk in srt:
    seats = f'{int(dm / SEATN[nm])} мест' if nm in SEATN else ''
    tag = '<span class="tag ok">по решению</span>' if okk else ('<span class="tag low">мало</span>' if b / norm < .7 else '<span class="tag mid">частично</span>')
    shrow.append(f'<tr><td>{tag}</td><td>{nm}</td><td class="n"><b>{fm(dm)}</b></td><td class="n">{seats}</td><td class="n">{floors(dd)}</td><td class="note">{where}</td></tr>')
STOT = sum(s[1] for s in short if not s[6])

# ---------- места
SU, SS, SA, SG = A(U) / 2.4, A(S) / 3.0, A(AV) / 5.0, A(G) / 2.2
SUP, SSP, SAP = A(U_P, P) / 2.4, A(S_P, P) / 3.0, A(AV, P) / 5.0
SEATS = int(SU) + int(SS) + int(SA); SEATSP = int(SUP) + int(SSP) + int(SAP)
seat = [('Учебные', int(SUP), int(SU), 720), ('Научные', int(SSP), int(SS), 900), ('АВ-залы и редкие книги', int(SAP), int(SA), 180)]
srow = ''.join(f'<tr><td>{a}</td><td class="n muted">{p}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n">{c - b}</td><td class="n"><span class="pill {cls(100*b/c)}">{100*b/c:.0f} %</span></td></tr>' for a, p, b, c in seat)
srow += f'<tr class="tot"><td>Читательские места</td><td class="n muted">{SEATSP}</td><td class="n">{fm(SEATS)}</td><td class="n">1 800</td><td class="n">{1800 - SEATS}</td><td class="n">{100*SEATS/1800:.0f} %</td></tr>'
srow += f'<tr><td>Групповые (сверх 1 800)</td><td class="n muted">{int(A(G, P) / 2.2)}</td><td class="n">{int(SG)}</td><td class="n">360</td><td class="n">{360 - int(SG)}</td><td class="n"><span class="pill {cls(100*SG/360)}">{100*SG/360:.0f} %</span></td></tr>'

# ---------- фонд
strow = ''.join(f'<tr><td>{n}</td><td>{html.escape(name(n))}</td><td class="n">{W[n]["f"]}</td><td class="n">{fm(W[n]["a"], 1)}</td><td class="n">{fm(r, 1)}</td><td class="n">{fm(W[n]["a"]/r)}</td></tr>' for n, r in STORE.items())
CAPO = A(OPEN) / 5
strow += f'<tr class="tot"><td></td><td>Закрытое хранение</td><td></td><td class="n">{fm(A(list(STORE)), 1)}</td><td></td><td class="n">{fm(CAP)} из 1 440</td></tr>'
strow += f'<tr><td></td><td>Открытый фонд ({", ".join(OPEN)})</td><td class="n">2, 3</td><td class="n">{fm(A(OPEN), 1)}</td><td class="n">5</td><td class="n">{fm(CAPO)} из 360</td></tr>'
strow += f'<tr class="tot"><td></td><td>Весь фонд</td><td></td><td></td><td></td><td class="n">{fm(CAP + CAPO)} из 1 800</td></tr>'

# ---------- резервы и вне программы
VC = A(['101', '102', '103', '146'])
C2, C3 = A(['202', '251']), A(['315'])
xrow = [
    ('Вестибюль, тамбур, КПП и гардероб', '101–103, 146', VC, '270–360 при равномерном потоке, 450–630 при массовом', f'больше нормы на {fm(VC - 630)}–{fm(VC - 270)} м²'),
    ('Лекционный зал на 150 мест', '143', A(['143']), 'около 213 (зал 180 + аппаратная 33)', f'больше на {fm(A(["143"]) - 213)} м²'),
    ('Коридоры 2 этажа', '202, 251', C2, '—', f'{100*C2/4686.87:.0f} % этажа (было 968 м²)'),
    ('Коридоры 3 этажа', '315', C3, '—', f'{100*C3/4459.96:.0f} % этажа (было 925 м²)'),
    ('Гардероб на 1 860 мест, 15 рядов', '146', A(['146']), 'за барьером 144–180 м²', 'площади хватает, шаг рядов проверить'),
    ('Буфет и кофе-пойнт', '147, 144', A(['147', '144']), '—', 'для читателей и гостей'),
]
xr = ''.join(f'<tr><td>{a}</td><td class="rm">{b}</td><td class="n">{fm(c)}</td><td class="note">{d}</td><td class="note">{e}</td></tr>' for a, b, c, d, e in xrow)

# ---------- что изменилось против PDF 18.11
chg = []
for n in sorted(set(W) | set(P)):
    a = P[n]['a'] if n in P else None
    b = W[n]['a'] if n in W else None
    nm = name(n)
    if any(k in nm for k in ('С/У', 'С/у', 'Шахта', 'Лестничн', 'ПУИ', 'Шлюз', 'Тамбур')) or n in ('253', '254'):
        continue
    if a is None or b is None or abs(a - b) > 3:
        chg.append(f'<tr><td class="rm">{n}</td><td>{html.escape(nm)}</td><td class="n muted">{fm(a, 1) if a is not None else "—"}</td><td class="n">{fm(b, 1) if b else "убрано"}</td>'
                   f'<td class="n">{("+" if (b or 0) > (a or 0) else "") + fm((b or 0) - (a or 0))}</td></tr>')

t = open(os.path.join(HERE, 'tpl.html')).read()
for k, v in dict(PROW=''.join(prow), SHROW=''.join(shrow), SROW=srow, STROW=strow, XROW=xr, CHG=''.join(chg), PROG=f'{PROG:.0f}', PROGP=f'{PROGP:.0f}',
                 SEATS=fm(SEATS), SEATSP=fm(SEATSP), SEATSD=fm(1800 - SEATS), SG=str(int(SG)), FUND=fm((CAP + CAPO) / 1000, 2), CLOSED=fm(CAP / 1000, 2),
                 OPENK=fm(CAPO), SPA=fm(A(SP)), STOT=fm(STOT), VC=fm(VC), C2=fm(C2), C3=fm(C3), ALL25=fm(A(list(STORE)) / 2.5)).items():
    t = t.replace('%%' + k + '%%', v)
assert '%%' not in t, t[t.index('%%'):t.index('%%') + 30]
open(os.path.join(HERE, 'SVERKA_1811.html'), 'w').write(t)
print('prog', round(PROG, 1), round(PROGP, 1), 'seats', SEATS, SEATSP, 'groups', int(SG), 'short', round(STOT), 'fund', round(CAP + CAPO), 'size', len(t))
