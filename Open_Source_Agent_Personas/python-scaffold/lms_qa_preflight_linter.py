import os
import sys
import glob
import re
from bs4 import BeautifulSoup
from datetime import datetime

class PreflightLinter:
    def __init__(self, package_dir):
        self.package_dir = package_dir
        self.errors = []
        self.warnings = []
        self.lessons_dir = os.path.join(package_dir, "lessons")
        self.images_dir = os.path.join(package_dir, "images")
        self.handouts_dir = os.path.join(package_dir, "handouts")
        self.h5p_dir = os.path.join(package_dir, "h5p_activities")
        self.quizzes_dir = os.path.join(package_dir, "quizzes")
        self.banks_dir = os.path.join(self.quizzes_dir, "moodle_banks")
        self.course_state_data = "> No `COURSE_STATE.md` found in the package root. Team 1 context is missing."
        self.youtube_count = 0

    def extract_course_state(self):
        # Attempt to pull team context
        context_text = "> No `COURSE_STATE.md` found in the package root. Team 1 context is missing."
        
        # Look for standard COURSE_STATE.md or any file ending in QA_Report.md
        context_files = ["COURSE_STATE.md"]
        qa_reports = [f for f in os.listdir(self.package_dir) if f.endswith("QA_Report.md") and f != "QA_REPORT.md"]
        context_files.extend(qa_reports)
        
        for context_file in context_files:
            state_path = os.path.join(self.package_dir, context_file)
            if os.path.exists(state_path):
                try:
                    with open(state_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Grab a short preview
                        lines = content.split('\n')[:15]
                        context_text = '\n'.join(lines)
                except Exception as e:
                    context_text = f"> Failed to read {context_file}: {e}"
        self.course_state_data = context_text

    def run_all_checks(self):
        print(f"=== 🔍 LMS Pre-Flight QA Linter ===")
        print(f"Validating payload: {self.package_dir}\n")

        self.extract_course_state()
        self.check_metadata_and_structure()
        self.check_scorm_packages()
        self.check_legacy_quiz_formats()
        self.check_universal_media_and_links()

        self.generate_qa_report()
        self.report_results()
        
        return len(self.errors) == 0

    def check_metadata_and_structure(self):
        print("[*] Sweeping Metadata & Structural Integrity...")
        if not os.path.exists(self.lessons_dir):
            self.errors.append(f"FATAL: Missing 'lessons' directory **[Target Area: Rebuild standard folder structure in package root]**")
            return
            
        html_files = glob.glob(os.path.join(self.lessons_dir, "*.html"))
        if not html_files:
            self.errors.append("FATAL: No HTML files found **[Target Area: /lessons/ directory is empty]**")
            return

        for filepath in html_files:
            filename = os.path.basename(filepath)
            
            if '_Template' in filename:
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # 1. Style Tags
            styles = soup.find_all('style')
            if not styles:
                self.warnings.append(f"[{filename}] No `<style>` tags found. **[Target Area: Inject internal CSS `<style>` block within the document `<head>` or `<body>`]**")

            # 2. Metadata block
            metadata = soup.find('div', id='module-metadata')
            if not metadata:
                self.warnings.append(f"[{filename}] Missing `#module-metadata` block. **[Target Area: Embed `<div id=\"module-metadata\">` near the top of the `<body>`]**")
                continue

            # 3. Attributes
            required_attrs = ['data-course', 'data-module']
            for attr in required_attrs:
                if not metadata.get(attr):
                    self.errors.append(f"[{filename}] Missing required metadata attribute: `{attr}` **[Target Area: Add `{attr}=\"value\"` into `<div id=\"module-metadata\">`]**")
                    
            # 4. State Targets
            state_target = metadata.find('target', type='state')
            if not state_target:
                self.errors.append(f"[{filename}] Missing State Targeting metadata. **[Target Area: Inject `<target type=\"state\">[STATE]</target>` inside module-metadata]**")

            # 5. Course Logo Enforcement
            course_logo = metadata.find('div', attrs={'data-field': 'course-logo'})
            if not course_logo:
                self.warnings.append(f"[{filename}] Missing `course-logo` block in metadata. **[Target Area: Inject `<div data-field=\"course-logo\"><img src=\"...ST.jpg\"></div>` inside module-metadata]**")

    def check_scorm_packages(self):
        print("[*] Sweeping SCORM Asset Integrity...")
        zips = glob.glob(os.path.join(self.package_dir, "**", "*.zip"), recursive=True)
        if not zips:
            self.warnings.append(f"No SCORM `.zip` files found anywhere in the payload. **[Target Area: Team 1 export failure to zip block]**")
        
    def check_legacy_quiz_formats(self):
        print("[*] Sweeping Legacy Moodle/Aiken Integrity...")
        if not os.path.exists(self.banks_dir):
            self.warnings.append(f"No 'moodle_banks' directory found. Legacy quiz fallbacks absent. **[Target Area: create /quizzes/moodle_banks/ folder]**")
            return
            
        files = os.listdir(self.banks_dir)
        if not [f for f in files if f.endswith('.xml')]:
            self.warnings.append(f"Missing Moodle XML fallback formats **[Target Area: Team 1 must export Moodle XML to /quizzes/moodle_banks/*.xml]**")
        if not [f for f in files if f.endswith('.txt')]:
            self.warnings.append(f"Missing Aiken TXT fallback formats **[Target Area: Team 1 must export Aiken TXT to /quizzes/moodle_banks/*.txt]**")

    def check_universal_media_and_links(self):
        print("[*] Sweeping HTML Workspaces for Universal Assets & YouTube Parity...")
        
        all_html_files = glob.glob(os.path.join(self.package_dir, "**", "*.html"), recursive=True)
        all_html_files = [f for f in all_html_files if "RAW_BACKUP" not in f]

        referenced_assets = set()
        
        # 1. Compile physical assets that currently exist on the drive
        actual_assets = []
        
        # Images
        if os.path.exists(self.images_dir):
            actual_assets.extend([f for f in os.listdir(self.images_dir) if os.path.isfile(os.path.join(self.images_dir, f))])
            
        # Specific structural HTML sub-folders (Handouts & H5P)
        if os.path.exists(self.handouts_dir):
            actual_assets.extend([f for f in os.listdir(self.handouts_dir) if f.endswith('.html')])
        if os.path.exists(self.h5p_dir):
            actual_assets.extend([f for f in os.listdir(self.h5p_dir) if f.endswith('.html')])
            
        # Audio & Video Files located ANYWHERE
        media_files = []
        for ext in ['.mp4', '.wav', '.mp3']:
            media_files.extend(glob.glob(os.path.join(self.package_dir, "**", f"*{ext}"), recursive=True))
        actual_assets.extend([os.path.basename(m) for m in media_files])

        # 2. Parse all referenced HTML code
        for filepath in all_html_files:
            filename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')

            # Native YouTube Tag Extractor
            self.youtube_count += content.count("youtube.com") + content.count("youtu.be")

            for img in soup.find_all('img'):
                src = img.get('src')
                alt = img.get('alt')
                img_id = img.get('id')
                
                # Accessibility Validation: Enforce descriptive alt tags
                # We explicitly ignore the lightbox-img placeholder since it is dynamically injected via JS
                if img_id != 'lightbox-img' and (alt is None or alt.strip() == ""):
                    # Warn rather than fatal error to prevent build halting on purely stylistic elements, 
                    # but flag it aggressively in the QA report.
                    self.warnings.append(f"[{filename}] ACCESSIBILITY FAILURE: `<img src=\"{src if src else 'unknown'}\">` is missing an `alt` tag. **[Target Area: Add descriptive `alt=\"...\"`]**")

                if not src: continue
                if "http" not in src and "data:" not in src and "//" not in src:
                    referenced_assets.add(os.path.basename(src))
                    target_path = os.path.normpath(os.path.join(os.path.dirname(filepath), src))
                    if not os.path.exists(target_path):
                        self.warnings.append(f"[{filename}] BROKEN IMAGE RESOURCE: `{src}` **[Target Area: Ignored during build. Pending LMS external injection.]**")

            html_refs = re.findall(r'[\w\-.]+\.html', content, re.IGNORECASE)
            for h in html_refs: referenced_assets.add(h)
            
            media_refs = re.findall(r'[\w\-.]+\.(?:png|jpg|jpeg|gif|svg|webp|mp4|wav|mp3)', content, re.IGNORECASE)
            for m in media_refs: referenced_assets.add(m)

            for a in soup.find_all('a'):
                href = a.get('href')
                if not href or href.startswith('http') or href.startswith('mailto:') or href.startswith('#'):
                    continue
                referenced_assets.add(os.path.basename(href))
                target_path = os.path.normpath(os.path.join(os.path.dirname(filepath), href))
                if not os.path.exists(target_path):
                    self.warnings.append(f"[{filename}] BROKEN HYPERLINK: `{href}` **[Target Area: Ignored during build. Pending LMS external injection.]**")

        # 3. Universal Orphan Check against referenced assets
        for asset in actual_assets:
            if asset not in referenced_assets:
                self.errors.append(f"ORPHANED ASSET: `{asset}` is present on drive but never natively referenced in HTML code. **[Target Area: Unused bloat is strictly prohibited. Mount via `<a href>` or `<img src>`, or physically delete the file]**")
                
        if self.youtube_count == 0:
            self.warnings.append("ZERO YOUTUBE ANCHORS DETECTED natively in the HTML code. **[Target Area: Ensure Team 1 natively installed `youtube.com` / `youtu.be` iframes replacing `.mp4` video elements]**")

    def generate_qa_report(self):
        report_path = os.path.join(self.package_dir, "QA_REPORT.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            f"# Example System Quality Assurance Report",
            f"**Generated:** {timestamp}",
            f"**Target Payload:** `{self.package_dir}`",
            f"---",
            f"## Asset Architecture Statistics",
            f"- 🎥 **Native YouTube Integrations Discovered:** `{self.youtube_count}` embed logic anchors.",
            f"---",
            f"## Team 1 Intent Context (Extracted from COURSE_STATE.md)\n",
            self.course_state_data,
            f"\n---",
            f"## 🚨 Fatal Deployment Errors ({len(self.errors)})",
            f"> *Fatal errors must be resolved in the template or code before Moodle compilation is permitted.*\n"
        ]
        
        if self.errors:
            for e in self.errors:
                report_lines.append(f"- {e}")
        else:
            report_lines.append("> ✅ No fatal deployment errors found. HTML infrastructure is fundamentally cohesive.")
            
        report_lines.append(f"\n## ⚠️ Warnings & Template Optimizations ({len(self.warnings)})")
        report_lines.append("> *Warnings indicate structural drift, legacy compliance failures, or dummy URLs awaiting LMS injection.*")
        if self.warnings:
            for w in self.warnings:
                report_lines.append(f"- {w}")
        else:
            report_lines.append("> ✅ No warnings detected.")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))

    def report_results(self):
        print("\n=======================================")
        if self.errors:
            print(f"❌ QA STATUS: {len(self.errors)} FATAL ERROR(S) FOUND! See QA_REPORT.md for diagnostics.")
            for e in self.errors:
                print(f"  -> {e.split('**[')[0].strip()}")
        else:
            print("✅ QA STATUS: CSS, DOM, & Link architecture is CLEAN.")

        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for w in self.warnings[:5]:
                print(f"  -> {w.split('**[')[0].strip()}")
            if len(self.warnings) > 5:
                print(f"  -> ... and {len(self.warnings)-5} more. Review QA_REPORT.md!")
        print("=======================================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dept_qa_preflight_linter.py <package_path>")
        sys.exit(1)
        
    target = sys.argv[1]
    linter = PreflightLinter(target)
    success = linter.run_all_checks()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

