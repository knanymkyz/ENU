# Сверка плана архитектора (Revit, PDF от 18.11) с программой табл. 26 Пособия и решениями по проекту.
# Площади экспликации — полезные (площади помещений из Revit), сравниваются с нормой напрямую.
import json, os, html
HERE = os.path.dirname(os.path.abspath(__file__))
R = {r['no']: r for r in json.load(open(os.path.join(HERE, 'rooms_1811.json')))}


def A(*ns):
    return sum(R[n]['a'] for n in ns)


def fm(x, d=0):
    return f"{x:,.{d}f}".replace(',', ' ').replace('.', ',')


def ids(ns):
    return ', '.join(ns)


# ---------- программа: (строка, норма м², помещения, примечание)
STORE = {'138': 2.5, '246': 1.5, '248': 1.5, '311': 1.5, '313': 1.5, '310': 2.5}
CAP = sum(R[n]['a'] / r for n, r in STORE.items())          # тыс. ед.
OPEN = ['203', '224', '225', '316', '330']
CAPO = A(*OPEN) / 5
U = ['114', '204', '205', '206', '216', '226']
G = ['115', '117', '118']
S = ['318', '319', '327', '328', '329', '340', '341', '342']
AV = ['227', '228', '309']
SP = ['105', '131', '132', '133', '134']
ROWS = [
    ('Абонемент', 678, ['140', '215', '139'], 'читатели 1,8 м² × 360 + сотрудники 5 м² × 6; 139 — площадь сотрудников у хранилища'),
    ('Аванзал', 450, ['116', '201'], 'читатели 1,5 м² × 270 + сотрудники 5 м² × 9; в прежней программе этой строки не было'),
    ('Каталоги и СБО', 503, ['141', '142', '214', '217', '317', '331'], 'по электронной оценке нужно 290–330 м²; выставка 142 — часть СБО (п. 3.108)'),
    ('Учебные читальные залы', 1728, U, '2,4 м² × 720 мест'),
    ('Помещения групповых занятий', 792, G, '2,2 м² × 360 мест'),
    ('Научные читальные залы', 2700, S, '3,0 м² × 900 мест'),
    ('АВ-залы, крупноформатные, редкие книги', 900, AV, '5,0 м² × 180 мест; зала крупноформатных изданий нет'),
    ('Открытый фонд, 360 тыс.', 1800, OPEN, '5 м² на 1 000 ед.'),
    ('Закрытое хранение, 1,44 млн', 2160, list(STORE), 'по вместимости: 1 этаж и редкие — 2,5 м², 2–3 этажи мобильные — 1,5 м² на 1 000'),
    ('Сотрудники хранения', 52, ['135'], ''),
    ('Комплектование и обработка', 78, ['130'], ''),
    ('Служебный каталог', 112.5, [], 'электронный — ваше решение 17.11'),
    ('Лаборатории', 360, ['136'], 'решение 17.11: современный состав 160–200 м²; гигиена книг — в 131'),
    ('Служебно-производственные', 540, SP, '3 м² на 10 тыс. ед.: дирекция, экспедиция, служебный вход, рекреация'),
]


def net(nm, ns):
    if nm.startswith('Закрытое'):
        return CAP * 1.5        # в пересчёте на мобильные стеллажи, как в программе
    return A(*ns)


def cls(p):
    return 'ok' if p >= 95 else ('mid' if p >= 70 else 'low')


TN = TP = TC = 0
prow = []
for nm, norm, ns, note in ROWS:
    n = net(nm, ns); p = 100 * n / norm
    TN += norm; TP += n; TC += min(n, norm)
    over = ' over' if p > 120 else ''
    prow.append(f'<tr><td>{nm}</td><td class="n">{fm(norm, 1 if norm % 1 else 0)}</td><td class="n">{fm(n)}</td>'
                f'<td class="n"><span class="pill {cls(p)}{over}">{p:.0f} %</span></td><td class="rm">{ids(ns) or "—"}</td><td class="note">{note}</td></tr>')
PROG = 100 * TC / TN
prow.append(f'<tr class="tot"><td>Итого по программе</td><td class="n">{fm(TN, 1)}</td><td class="n">{fm(TP)}</td><td class="n"><b>{PROG:.0f} %</b></td><td></td><td class="note">превышения не засчитываются: в счёт идёт {fm(TC)} м²</td></tr>')

# ---------- места
SU, SG, SS, SA = A(*U) / 2.4, A(*G) / 2.2, A(*S) / 3.0, A(*AV) / 5.0
SEATS = int(SU) + int(SS) + int(SA)
seat = [('Учебные залы', int(SU), 720), ('Научные залы', int(SS), 900), ('АВ-залы и зал редких книг', int(SA), 180)]
srow = ''.join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n"><span class="pill {cls(100*b/c)}">{100*b/c:.0f} %</span></td></tr>' for a, b, c in seat)
srow += f'<tr class="tot"><td>Читательские места</td><td class="n">{SEATS}</td><td class="n">1 800</td><td class="n"><b>{100*SEATS/1800:.0f} %</b></td></tr>'
srow += f'<tr><td>Групповые (сверх 1 800)</td><td class="n">{int(SG)}</td><td class="n">360</td><td class="n"><span class="pill {cls(100*SG/360)}">{100*SG/360:.0f} %</span></td></tr>'

# ---------- хранение
strow = ''.join(f'<tr><td>{n}</td><td>{html.escape(R[n]["n"])}</td><td class="n">{R[n]["f"]}</td><td class="n">{fm(R[n]["a"], 2)}</td><td class="n">{fm(r, 1)}</td><td class="n">{fm(R[n]["a"]/r)}</td></tr>' for n, r in STORE.items())
strow += f'<tr class="tot"><td></td><td>Закрытое хранение</td><td></td><td class="n">{fm(A(*STORE), 2)}</td><td></td><td class="n">{fm(CAP)}</td></tr>'
strow += f'<tr><td></td><td>Открытый фонд ({ids(OPEN)})</td><td class="n">2, 3</td><td class="n">{fm(A(*OPEN), 2)}</td><td class="n">5</td><td class="n">{fm(CAPO)}</td></tr>'
strow += f'<tr class="tot"><td></td><td>Весь фонд</td><td></td><td></td><td></td><td class="n">{fm(CAP + CAPO)} из 1 800</td></tr>'
ALL25 = A(*STORE) / 2.5

# ---------- вне программы
VC = A('101', '102', '103', '146')
xrow = [
    ('Лекционный зал на 150 мест', '143', A('143'), 'около 213 (зал 180 + аппаратная 33)', f'+{fm(A("143") - 213)} м²'),
    ('Вестибюль, тамбур, КПП и гардероб', '101–103, 146', VC, '270–360 при равномерном потоке, 450–630 при массовом (1 800 чел.)', f'+{fm(VC - 630)}…+{fm(VC - 270)} м²'),
    ('Гардероб на 1 860 мест, 15 рядов', '146', A('146'), 'за барьером 144–180 м²', 'площади хватает; шаг рядов проверить'),
    ('Буфет и кофе-пойнт', '147, 144', A('147', '144'), 'около 1,8 м² на место', f'≈ {int(A("147") / 2.5)} мест с раздачей'),
    ('Коридоры 2 этажа', '202', A('202'), '—', f'{100*A("202")/4686.87:.0f} % этажа'),
    ('Коридоры 3 этажа', '315', A('315'), '—', f'{100*A("315")/4459.96:.0f} % этажа'),
]
xr = ''.join(f'<tr><td>{a}</td><td class="rm">{b}</td><td class="n">{fm(c)}</td><td class="note">{d}</td><td class="note">{e}</td></tr>' for a, b, c, d, e in xrow)

t = open(os.path.join(HERE, 'tpl.html')).read()
for k, v in dict(PROW=''.join(prow), SROW=srow, STROW=strow, XROW=xr, PROG=f'{PROG:.0f}', SEATS=str(SEATS), FUND=fm((CAP + CAPO) / 1000, 2),
                 CLOSED=fm(CAP / 1000, 2), ALL25=fm(ALL25), SPA=fm(A(*SP)), SPP=f'{100*A(*SP)/540:.0f}', SG=str(int(SG)),
                 OPENK=fm(CAPO), AVAN=fm(A('116', '201')), VC=fm(VC), C2=fm(A('202')), C3=fm(A('315'))).items():
    t = t.replace('%%' + k + '%%', v)
open(os.path.join(HERE, 'SVERKA_1811.html'), 'w').write(t)
print('prog', round(PROG, 1), 'seats', SEATS, 'groups', int(SG), 'fund', round(CAP + CAPO), 'closed', round(CAP), 'sp', round(A(*SP), 1), 'size', len(t))
