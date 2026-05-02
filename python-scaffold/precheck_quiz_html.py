"""
Pre-check validator for HTML quiz files authored using quiz_template_universal.html
Validates structure, counts, encoding, and syntax before converter build.
"""
from bs4 import BeautifulSoup
import re
import sys
import os

def check(path):
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    soup = BeautifulSoup(raw, 'html.parser')
    fname = os.path.basename(path)

    errors   = []
    warnings = []
    ok       = []

    # ── METADATA ──────────────────────────────────────────────────────────────
    def meta(name):
        tag = soup.find('meta', attrs={'name': name})
        return tag['content'].strip() if tag and tag.get('content') else ''

    required_meta = ['course', 'file-type', 'module', 'title', 'delivery-type',
                     'authored-by', 'date']
    for field in required_meta:
        val = meta(field)
        if not val:
            errors.append(f'META missing or empty: {field}')
        else:
            ok.append(f'META {field} = "{val}"')

    file_type     = meta('file-type')
    module        = meta('module')
    delivery_type = meta('delivery-type')

    if file_type not in ('module', 'finalexam'):
        errors.append(f'META file-type must be "module" or "finalexam", got "{file_type}"')

    if file_type == 'module' and not re.match(r'^M\d{2}$', module):
        warnings.append(f'META module "{module}" — expected format M01..M12')

    if file_type == 'finalexam' and module != 'FINAL':
        warnings.append(f'META module should be "FINAL" for finalexam files, got "{module}"')

    if delivery_type not in ('sync', 'async', 'both'):
        errors.append(f'META delivery-type must be sync|async|both, got "{delivery_type}"')

    # ── SECTIONS ──────────────────────────────────────────────────────────────
    valid_types = {'matching', 'truefalse', 'cloze', 'essay'}
    sections = soup.find_all('section', attrs={'data-type': True})
    found_types = {s['data-type'] for s in sections}

    for t in valid_types:
        if t not in found_types:
            warnings.append(f'SECTION missing entirely: {t} (expected but not found)')

    # ── PER-SECTION COUNTS & CHECKS ───────────────────────────────────────────
    counts = {}
    for sec in sections:
        dtype   = sec.get('data-type', '?')
        include = sec.get('data-include', '').lower()

        if dtype not in valid_types:
            errors.append(f'SECTION unknown data-type="{dtype}"')
            continue

        if include not in ('yes', 'no'):
            errors.append(f'SECTION [{dtype}] data-include must be "yes" or "no", got "{include}"')

        articles = sec.find_all('article', attrs={'data-id': True})
        counts[dtype] = len(articles)

        if include == 'no':
            ok.append(f'SECTION [{dtype}] excluded (data-include=no)')
            continue

        ok.append(f'SECTION [{dtype}] included — {len(articles)} question(s)')

        # ── MATCHING ──
        if dtype == 'matching':
            min_sets = 5 if delivery_type in ('async', 'both') else 3
            if len(articles) < min_sets:
                errors.append(f'MATCHING: {len(articles)} sets found, minimum {min_sets} required for delivery-type="{delivery_type}"')
            for art in articles:
                pairs = art.find_all('tr')
                stems   = art.find_all('td', class_='stem')
                answers = art.find_all('td', class_='answer')
                if len(stems) < 4:
                    warnings.append(f'MATCHING [{art.get("data-id","?")}]: only {len(stems)} pairs — recommend 4+')
                if len(stems) != len(answers):
                    errors.append(f'MATCHING [{art.get("data-id","?")}]: {len(stems)} stems vs {len(answers)} answers — mismatch')

        # ── TRUE/FALSE ──
        elif dtype == 'truefalse':
            if len(articles) < 8:
                errors.append(f'TRUEFALSE: {len(articles)} questions, minimum 8 required')
            for art in articles:
                aid = art.get('data-id', '?')
                ca  = art.find('p', class_='correct-answer')
                if not ca:
                    errors.append(f'TF [{aid}]: missing <p class="correct-answer">')
                    continue
                dc = ca.get('data-correct', '')
                if dc not in ('true', 'false'):
                    errors.append(f'TF [{aid}]: data-correct="{dc}" — must be exactly "true" or "false" (lowercase)')

        # ── CLOZE ──
        elif dtype == 'cloze':
            if len(articles) < 6:
                errors.append(f'CLOZE: {len(articles)} questions, minimum 6 required')
            for art in articles:
                aid  = art.get('data-id', '?')
                qtag = art.find('p', class_='question')
                if not qtag:
                    errors.append(f'CLOZE [{aid}]: missing <p class="question">')
                    continue
                text = qtag.get_text()
                blanks = re.findall(r'\[BLANK:([^\]]*)\]', text)
                empty  = re.findall(r'\[BLANK:\]', text)
                if not blanks:
                    errors.append(f'CLOZE [{aid}]: no [BLANK:answer] markers found in question text')
                if empty:
                    errors.append(f'CLOZE [{aid}]: {len(empty)} [BLANK:] with no answer value')

        # ── ESSAY ──
        elif dtype == 'essay':
            if len(articles) < 4:
                errors.append(f'ESSAY: {len(articles)} questions, minimum 4 required')
            for art in articles:
                aid = art.get('data-id', '?')
                if not art.find('div', class_='question'):
                    errors.append(f'ESSAY [{aid}]: missing <div class="question">')
                rubric = art.find('div', class_='rubric')
                if not rubric:
                    errors.append(f'ESSAY [{aid}]: missing <div class="rubric">')
                else:
                    headers = [th.get_text().strip() for th in rubric.find_all('th')]
                    required_headers = {'Criterion', 'Full', 'Partial', 'None'}
                    missing_h = required_headers - set(headers)
                    if missing_h:
                        errors.append(f'ESSAY [{aid}] rubric missing columns: {missing_h}')

    # ── DATA-ID UNIQUENESS ────────────────────────────────────────────────────
    all_ids = [a['data-id'] for a in soup.find_all('article', attrs={'data-id': True})]
    seen = set()
    for aid in all_ids:
        if aid in seen:
            errors.append(f'DUPLICATE data-id: "{aid}"')
        seen.add(aid)
    if len(seen) == len(all_ids):
        ok.append(f'data-id uniqueness: {len(all_ids)} unique IDs — all OK')

    # ── ENCODING: SMART QUOTES / MOJIBAKE / SPECIAL CHARS ────────────────────
    smart_q = len(re.findall('[\u201c\u201d\u2018\u2019]', raw))
    smart_d = len(re.findall('[\u2013\u2014]', raw))
    moji    = len(re.findall('\u00e2\u20ac', raw))
    bare_e  = sum(raw.count(e) for e in ['&ndash;', '&mdash;', '&deg;', '&nbsp;'])
    non_asc = len(re.findall(r'[^\x00-\x7F]', raw))

    if smart_q:  errors.append(f'ENCODING: {smart_q} smart quote(s) — use straight " and \'')
    else:        ok.append('ENCODING: no smart quotes')
    if smart_d:  errors.append(f'ENCODING: {smart_d} smart dash(es) — use hyphen -')
    else:        ok.append('ENCODING: no smart dashes')
    if moji:     errors.append(f'ENCODING: {moji} mojibake sequence(s)')
    else:        ok.append('ENCODING: no mojibake')
    if bare_e:   warnings.append(f'ENCODING: {bare_e} bare HTML entity/entities — will be stripped in XML')
    if non_asc > 0:
        non_asc_chars = set(re.findall(r'[^\x00-\x7F]', raw))
        # Ignore chars already caught above
        remaining = non_asc_chars - set('\u201c\u201d\u2018\u2019\u2013\u2014')
        if remaining:
            warnings.append(f'ENCODING: {len(remaining)} other non-ASCII char(s): {sorted(remaining)[:10]}')

    # ── PRINT REPORT ──────────────────────────────────────────────────────────
    print(f'\n{"="*60}')
    print(f'  PRE-CHECK: {fname}')
    print(f'{"="*60}')

    if errors:
        print(f'\n  ERRORS ({len(errors)}) — must fix before converter run:')
        for e in errors:
            print(f'    ✗  {e}')

    if warnings:
        print(f'\n  WARNINGS ({len(warnings)}) — review:')
        for w in warnings:
            print(f'    ⚠  {w}')

    print(f'\n  OK ({len(ok)}):')
    for o in ok:
        print(f'    ✓  {o}')

    verdict = 'PASS — READY FOR CONVERTER' if not errors else 'FAIL — ERRORS MUST BE FIXED'
    print(f'\n  VERDICT: {verdict}')
    print(f'{"="*60}\n')
    return len(errors)

if __name__ == '__main__':
    paths = sys.argv[1:] if len(sys.argv) > 1 else [
        r'C:\Users\Ed\Documents\Antigravity_projects\Protect-learning\Course_2_Delivery_Package\quizzes\C2_M01_Quiz.html'
    ]
    total_errors = 0
    for p in paths:
        total_errors += check(p)
    sys.exit(1 if total_errors else 0)
