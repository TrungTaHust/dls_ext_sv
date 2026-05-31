import json, glob, os, shutil

BASE = 'resources/data'
data_files = sorted(f for f in glob.glob(os.path.join(BASE, '*.json'))
                    if os.path.basename(f)[:-5].isdigit())

total_fixed = 0

for fpath in data_files:
    stem = os.path.basename(fpath)[:-5]
    rows = json.load(open(fpath, encoding='utf-8'))
    changed = 0

    for r in rows:
        fn   = r.get('fname', '').strip()
        ln   = r.get('lname', '').strip()
        name = (fn + ' ' + ln).strip()

        # ── 1. Leading space in fname ─────────────────────────────────────────
        if r.get('fname', '').startswith(' '):
            r['fname'] = r['fname'].strip()
            print(f'[{stem}] Fixed leading space: {name}')
            changed += 1

        # ── 2. club = nation (swap) ───────────────────────────────────────────
        # Thomas Meunier, Hans Vanaken, Sebastiaan Bornauw: club='Belgium' -> club='Brugge' (Club Brugge)
        # Taty Castellanos: club='Argentina' -> club='Lazio'
        if name == 'Thomas Meunier' and r.get('club') == 'Belgium':
            r['club'] = 'Brugge'
            print(f'[{stem}] Fixed club: Thomas Meunier Belgium->Brugge')
            changed += 1
        if name == 'Hans Vanaken' and r.get('club') == 'Belgium':
            r['club'] = 'Brugge'
            print(f'[{stem}] Fixed club: Hans Vanaken Belgium->Brugge')
            changed += 1
        if name == 'Sebastiaan Bornauw' and r.get('club') == 'Belgium':
            r['club'] = 'Wolfsburg'
            print(f'[{stem}] Fixed club: Sebastiaan Bornauw Belgium->Wolfsburg')
            changed += 1
        if name == 'Taty Castellanos' and r.get('club') == 'Argentina':
            r['club'] = 'Lazio'
            print(f'[{stem}] Fixed club: Taty Castellanos Argentina->Lazio')
            changed += 1

        # ── 3. nat = club (Sam Johnstone) ─────────────────────────────────────
        if name == 'Sam Johnstone' and r.get('nat') == 'Wolves':
            r['nat'] = 'England'
            print(f'[{stem}] Fixed nat: Sam Johnstone Wolves->England')
            changed += 1

        # ── 4. sta not int (Joakim Maehle) ───────────────────────────────────
        if name == 'Joakim Maehle' and not isinstance(r.get('sta'), int):
            r['sta'] = 70   # reasonable default for a fullback
            print(f'[{stem}] Fixed sta: Joakim Maehle sta=70')
            changed += 1

        # ── 5. Stat > 100 ─────────────────────────────────────────────────────
        # Niklas Pyyhtia sta=550 -> likely 55
        if name == 'Niklas Pyyhtia' and r.get('sta', 0) > 100:
            r['sta'] = 55
            print(f'[{stem}] Fixed sta: Niklas Pyyhtia 550->55')
            changed += 1
        # Mario Hermoso str=180 -> likely 80; acc=7->70; sta=7->70
        if name == 'Mario Hermoso':
            if r.get('str', 0) > 100:
                r['str'] = 80
                print(f'[{stem}] Fixed str: Mario Hermoso 180->80')
                changed += 1
            if r.get('acc', 0) < 10:
                r['acc'] = 70
                print(f'[{stem}] Fixed acc: Mario Hermoso 7->70')
                changed += 1
            if r.get('sta', 0) < 10:
                r['sta'] = 70
                print(f'[{stem}] Fixed sta: Mario Hermoso 7->70')
                changed += 1
        # Giovane con=169->69; str=6->60
        if fn == '' and ln == 'Giovane':
            if r.get('con', 0) > 100:
                r['con'] = 69
                print(f'[{stem}] Fixed con: Giovane 169->69')
                changed += 1
            if r.get('str', 0) < 10:
                r['str'] = 60
                print(f'[{stem}] Fixed str: Giovane 6->60')
                changed += 1
        # Thierry Small pas=159->59; con=6->60
        if name == 'Thierry Small':
            if r.get('pas', 0) > 100:
                r['pas'] = 59
                print(f'[{stem}] Fixed pas: Thierry Small 159->59')
                changed += 1
            if r.get('con', 0) < 10:
                r['con'] = 60
                print(f'[{stem}] Fixed con: Thierry Small 6->60')
                changed += 1
        # Robinio Risser con=5->50
        if name == 'Robinio Risser' and r.get('con', 0) < 10:
            r['con'] = 50
            print(f'[{stem}] Fixed con: Robinio Risser 5->50')
            changed += 1

        # ── 6. Invalid foot ───────────────────────────────────────────────────
        if name == 'Kenneth Vargas' and r.get('foot') == 'RW':
            r['foot'] = 'R'
            print(f'[{stem}] Fixed foot: Kenneth Vargas RW->R')
            changed += 1

        # ── 7. hgt bất thường ────────────────────────────────────────────────
        if name == 'Stephan Zagadou' and r.get('hgt', 0) < 155:
            r['hgt'] = 196
            print(f'[{stem}] Fixed hgt: Stephan Zagadou 86->196')
            changed += 1

    if changed:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=4)
        print(f'  -> {stem}.json: {changed} fixes saved')
    total_fixed += changed

print(f'\nTotal fixes: {total_fixed}')
