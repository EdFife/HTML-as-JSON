"""
html_to_moodle_xml.py
Converts DAS-style HTML quiz template files to valid Moodle XML for question bank import.

Usage:
    python html_to_moodle_xml.py [file1.html file2.html ...]
    python html_to_moodle_xml.py              # converts all *.html files in ./quizzes/

Template format: quiz_template_universal.html (included in this repo)
Pre-check validator: precheck_quiz_html.py (run before converting)

Output: <input_name>_Moodle.xml written alongside each input file.

License: MIT
"""
import re, sys, os, glob
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

# ── CATEGORY PATH ─────────────────────────────────────────────────────────────
SECTION_LEAF = {
    'matching':  'Matching',
    'truefalse': 'TrueFalse',
    'cloze':     'Cloze',
    'essay':     'Essay',
}

def category_path(course, file_type, module, section_type):
    leaf = SECTION_LEAF[section_type]
    if file_type == 'finalexam':
        return f'$course$/{course}/Final Exam/{leaf}'
    return f'$course$/{course}/Question Bank/{module}/{leaf}'

# ── SANITIZE ──────────────────────────────────────────────────────────────────
REPLACEMENTS = {
    '\u201c': '"',  '\u201d': '"',   # smart double quotes
    '\u2018': "'",  '\u2019': "'",   # smart single quotes
    '\u2013': '-',  '\u2014': '-',   # en/em dash
    '\u2026': '...', '\u00a0': ' ',  # ellipsis, non-breaking space
    '\ufeff': '',                     # BOM
}

def clean(text):
    if not text:
        return ''
    for bad, good in REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.encode('ascii', errors='ignore').decode('ascii')

def inner_html(tag):
    return clean(tag.decode_contents().strip()) if tag else ''

def para(text):
    return f'<p>{clean(text.strip())}</p>'

def cdata_text(html):
    html = clean(html).strip()
    return f'<text><![CDATA[{html}]]></text>'

def plain_text(t):
    return f'<text>{escape(clean(t))}</text>'

# ── CLOZE BLANK CONVERSION ────────────────────────────────────────────────────
def blank_to_cloze(m):
    """Convert [BLANK:answer1|answer2] to {1:SHORTANSWER:=answer1~%100%answer2}"""
    alts = [a.strip() for a in m.group(1).split('|') if a.strip()]
    if not alts:
        return '{1:SHORTANSWER:=MISSING}'
    if len(alts) == 1:
        return '{1:SHORTANSWER:=' + alts[0] + '}'
    return '{1:SHORTANSWER:=' + alts[0] + '~' + '~'.join('%100%' + a for a in alts[1:]) + '}'

def convert_blanks(text):
    return re.sub(r'\[BLANK:([^\]]*)\]', blank_to_cloze, text)

# ── QUESTION BUILDERS ─────────────────────────────────────────────────────────
def q_category(cat):
    return (f'  <question type="category">\n'
            f'    <category>{plain_text(cat)}</category>\n'
            f'    <info format="html"><text></text></info>\n'
            f'  </question>\n')

def q_matching(art):
    aid  = art.get('data-id', 'UNKNOWN')
    h3   = art.find('h3')
    name = clean(h3.get_text().strip()) if h3 else aid
    instr = art.find('p', class_='instructions')
    qt    = para(instr.get_text()) if instr else '<p>Match each item to its correct answer.</p>'
    fc = art.find('p', class_='feedback-correct')
    fp = art.find('p', class_='feedback-partial')
    fw = art.find('p', class_='feedback-wrong')
    fc_h = para(fc.get_text()) if fc else '<p>Correct.</p>'
    fp_h = para(fp.get_text()) if fp else '<p>Partially correct. Review and retry.</p>'
    fw_h = para(fw.get_text()) if fw else '<p>Incorrect. Review and retry.</p>'

    subs = ''
    tbl  = art.find('table', class_='pairs')
    if tbl:
        for tr in tbl.find_all('tr'):
            s = tr.find('td', class_='stem')
            a = tr.find('td', class_='answer')
            if s and a:
                subs += (f'    <subquestion format="html">\n'
                         f'      <text>{clean(s.get_text().strip())}</text>\n'
                         f'      <answer><text>{clean(a.get_text().strip())}</text></answer>\n'
                         f'    </subquestion>\n')

    return (f'  <question type="matching">\n'
            f'    <name>{plain_text(name)}</name>\n'
            f'    <questiontext format="html">\n      {cdata_text(qt)}\n    </questiontext>\n'
            f'    <defaultgrade>1.0000000</defaultgrade>\n'
            f'    <penalty>0.3333333</penalty>\n'
            f'    <hidden>0</hidden>\n'
            f'    <shuffleanswers>1</shuffleanswers>\n'
            f'    <correctfeedback format="html">\n      {cdata_text(fc_h)}\n    </correctfeedback>\n'
            f'    <partiallycorrectfeedback format="html">\n      {cdata_text(fp_h)}\n    </partiallycorrectfeedback>\n'
            f'    <incorrectfeedback format="html">\n      {cdata_text(fw_h)}\n    </incorrectfeedback>\n'
            f'{subs}'
            f'  </question>\n')

def q_truefalse(art):
    aid   = art.get('data-id', 'UNKNOWN')
    qtag  = art.find('p', class_='question')
    qt    = para(qtag.get_text()) if qtag else '<p>Missing question text.</p>'
    ca    = art.find('p', class_='correct-answer')
    correct   = ca.get('data-correct', 'true').lower().strip() if ca else 'true'
    incorrect = 'false' if correct == 'true' else 'true'
    fc = art.find('p', class_='feedback-correct')
    fw = art.find('p', class_='feedback-wrong')
    fc_h = para(fc.get_text()) if fc else '<p>Correct.</p>'
    fw_h = para(fw.get_text()) if fw else '<p>Incorrect.</p>'

    def ans(val, frac, fb):
        return (f'    <answer fraction="{frac}" format="plain_text">\n'
                f'      <text>{val}</text>\n'
                f'      <feedback format="html">\n        {cdata_text(fb)}\n      </feedback>\n'
                f'    </answer>\n')

    return (f'  <question type="truefalse">\n'
            f'    <name>{plain_text(aid)}</name>\n'
            f'    <questiontext format="html">\n      {cdata_text(qt)}\n    </questiontext>\n'
            f'    <defaultgrade>1.0000000</defaultgrade>\n'
            f'    <penalty>1.0000000</penalty>\n'
            f'    <hidden>0</hidden>\n'
            f'{ans(correct, "100", fc_h)}'
            f'{ans(incorrect, "0", fw_h)}'
            f'  </question>\n')

def q_cloze(art):
    aid  = art.get('data-id', 'UNKNOWN')
    qtag = art.find('p', class_='question')
    if qtag:
        raw = clean(qtag.get_text(' ', strip=False))
        qt  = '<p>' + convert_blanks(raw).strip() + '</p>'
    else:
        qt  = '<p>Missing question text.</p>'
    return (f'  <question type="cloze">\n'
            f'    <name>{plain_text(aid)}</name>\n'
            f'    <questiontext format="html">\n      {cdata_text(qt)}\n    </questiontext>\n'
            f'    <defaultgrade>1.0000000</defaultgrade>\n'
            f'    <penalty>0.0000000</penalty>\n'
            f'    <hidden>0</hidden>\n'
            f'  </question>\n')

def q_essay(art):
    aid   = art.get('data-id', 'UNKNOWN')
    h3    = art.find('h3')
    name  = clean(h3.get_text().strip()) if h3 else aid
    qdiv  = art.find('div', class_='question')
    rdiv  = art.find('div', class_='rubric')
    qt_h  = inner_html(qdiv) if qdiv else '<p>Missing question text.</p>'
    rb_h  = inner_html(rdiv) if rdiv else ''
    return (f'  <question type="essay">\n'
            f'    <name>{plain_text(name)}</name>\n'
            f'    <questiontext format="html">\n      {cdata_text(qt_h)}\n    </questiontext>\n'
            f'    <defaultgrade>1.0000000</defaultgrade>\n'
            f'    <penalty>0.0000000</penalty>\n'
            f'    <hidden>0</hidden>\n'
            f'    <responseformat>editor</responseformat>\n'
            f'    <responserequired>1</responserequired>\n'
            f'    <responsefieldlines>10</responsefieldlines>\n'
            f'    <attachments>0</attachments>\n'
            f'    <attachmentsrequired>0</attachmentsrequired>\n'
            f'    <graderinfo format="html">\n      {cdata_text(rb_h)}\n    </graderinfo>\n'
            f'    <responsetemplate format="html"><text></text></responsetemplate>\n'
            f'  </question>\n')

BUILDERS = {
    'matching':  q_matching,
    'truefalse': q_truefalse,
    'cloze':     q_cloze,
    'essay':     q_essay,
}

# ── CONVERTER ─────────────────────────────────────────────────────────────────
def convert(html_path, out_path=None):
    """Convert a single HTML quiz template file to Moodle XML.

    Args:
        html_path: Path to the HTML template file.
        out_path:  Output XML path. Defaults to <input>_Moodle.xml.

    Returns:
        Tuple of (output_path, status_string).
    """
    with open(html_path, encoding='utf-8-sig') as f:  # utf-8-sig strips BOM
        raw = f.read()
    soup = BeautifulSoup(raw, 'html.parser')

    def meta(name):
        t = soup.find('meta', attrs={'name': name})
        return t['content'].strip() if t and t.get('content') else ''

    course  = meta('course')       or 'COURSE-ID'
    ftype   = meta('file-type')    or 'module'
    module  = meta('module')       or 'M01'
    deltype = meta('delivery-type') or 'both'
    title   = meta('title')        or ''
    author  = meta('authored-by')  or ''
    date    = meta('date')         or ''

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- Generated by html_to_moodle_xml.py (github.com/ProTect-Athletics/Open_Source_Agent_Personas) -->',
        f'<!-- Course:{course} | Module:{module} | Type:{ftype} | Delivery:{deltype} -->',
        f'<!-- Title:{title} | Author:{author} | Date:{date} -->',
        '<quiz>',
    ]

    total = 0
    for sec in soup.find_all('section', attrs={'data-type': True}):
        dtype   = sec.get('data-type', '')
        include = sec.get('data-include', 'yes').lower()
        if include != 'yes' or dtype not in BUILDERS:
            continue
        arts = sec.find_all('article', attrs={'data-id': True})
        if not arts:
            continue
        cat = category_path(course, ftype, module, dtype)
        lines.append(f'\n  <!-- ── {dtype.upper()} ({len(arts)} questions) ── -->')
        lines.append(q_category(cat))
        for art in arts:
            lines.append(BUILDERS[dtype](art))
            total += 1

    lines.append('</quiz>')

    if out_path is None:
        out_path = os.path.splitext(html_path)[0] + '_Moodle.xml'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    try:
        ET.parse(out_path)
        status = 'VALID XML'
    except Exception as e:
        status = f'INVALID XML: {e}'

    print(f'  {os.path.basename(out_path)}  ({total} questions)  {status}')
    return out_path, status

# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        # Default: all HTML files in ./quizzes/ relative to this script
        quizzes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quizzes')
        paths = sorted(glob.glob(os.path.join(quizzes_dir, '*.html')))

    if not paths:
        print('No HTML quiz files found. Pass file paths as arguments or place files in ./quizzes/')
        sys.exit(1)

    print(f'\nhtml_to_moodle_xml.py — converting {len(paths)} file(s)\n')
    errors = 0
    for p in paths:
        print(f'  Converting: {os.path.basename(p)}')
        _, status = convert(p)
        if 'INVALID' in status:
            errors += 1

    print(f'\nDone. {errors} error(s).')
    sys.exit(1 if errors else 0)
