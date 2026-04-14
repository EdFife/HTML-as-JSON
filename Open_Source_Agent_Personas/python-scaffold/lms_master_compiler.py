import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime

def run_compiler(target_dir):
    print(f"\n=== 🚀 LMS Master Moodle Compiler ===")
    print(f"Target Package: {target_dir}")
    print("=======================================\n")
    
    if not os.path.exists(target_dir):
        print(f"FATAL ERROR: Package directory not found: {target_dir}")
        return

    # 0. Pre-Flight QA Linting
    print(f"[*] STEP 0: Initiating Pre-Flight QA Validation...")
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    linter_path = os.path.join(tools_dir, "dept_qa_preflight_linter.py")
    linter_result = subprocess.run([sys.executable, linter_path, target_dir])
    
    if linter_result.returncode != 0:
        override = input("\n[!] FATAL QA ERRORS FOUND. Are you absolutely sure you want to deploy a broken payload? (y/N): ")
        if override.strip().lower() != 'y':
            print("Aborting compilation to prevent broken code from hitting Moodle.")
            return
    
    # 1. Zero-Footprint Backup
    parent_dir = os.path.dirname(os.path.abspath(target_dir))
    package_name = os.path.basename(os.path.normpath(target_dir))
    
    print(f"[*] STEP 1: Initializing Zero-Footprint Backup...")
    # Check if a backup folder already exists to prevent hard-drive bloat
    existing_backups = [d for d in os.listdir(parent_dir) if d.startswith(f"{package_name}_RAW_BACKUP") and os.path.isdir(os.path.join(parent_dir, d))]
    
    if existing_backups:
        print(f"    -> Backup already exists ({existing_backups[0]}). Skipping backup creation to prevent workspace bloat.")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(parent_dir, f"{package_name}_RAW_BACKUP_{timestamp}")
        shutil.copytree(target_dir, backup_dir)
        print(f"    -> Safe backup generated: {os.path.basename(backup_dir)}")
    
    tools_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. SCORM Checks
    print(f"\n[*] STEP 2: Executing SCORM Integrity Repairs...")
    manifest_fixer = os.path.join(tools_dir, "dept_scorm_manifest_fixer.py")
    subprocess.run([sys.executable, manifest_fixer, target_dir])
    
    js_patcher = os.path.join(tools_dir, "dept_scorm_js_patcher.py")
    subprocess.run([sys.executable, js_patcher, target_dir])

    # 3. Moodle Sanitizer
    print(f"\n[*] STEP 3: Executing Moodle Sanitizer...")
    sanitizer = os.path.join(tools_dir, "dept_moodle_sanitizer.py")
    subprocess.run([sys.executable, sanitizer, target_dir])

    # 3.5 Objective Layout Patcher
    print(f"\n[*] STEP 3.5: Patching Objective UI Pills to Gold Standard DOM...")
    patcher = os.path.join(tools_dir, "dept_objective_patcher.py")
    subprocess.run([sys.executable, patcher, target_dir])

    # 3.6 Universal Header Sync
    print(f"\n[*] STEP 3.6: Synchronizing Gold Standard Headers across 12+ files...")
    header_sync = os.path.join(tools_dir, "dept_header_sync.py")
    subprocess.run([sys.executable, header_sync, target_dir])

    # 3.7 Cloud Media Abstractor
    print(f"\n[*] STEP 3.7: Abstracting native video frames to YouTube API endpoints...")
    media_patcher = os.path.join(tools_dir, "dept_moodle_media_patcher.py")
    subprocess.run([sys.executable, media_patcher, target_dir])

    # 3.8 Absolute Moodle URL Mapping
    print(f"\n[*] STEP 3.8: Abstracting generic relative paths to live Moodle Server URLs...")
    url_patcher = os.path.join(tools_dir, "dept_moodle_url_injector.py")
    subprocess.run([sys.executable, url_patcher, target_dir])

    # 4. CSS Inlining
    print(f"\n[*] STEP 4: Executing Moodle CSS Inliner...")
    css_inliner = os.path.join(tools_dir, "dept_moodle_css_inliner.py")
    subprocess.run([sys.executable, css_inliner, target_dir])

    # 5. Offline Participant Guides
    print(f"\n[*] STEP 5: Executing Offline Participant Guide Generation...")
    guide_gen = os.path.join(tools_dir, "dept_guide_generator.py")
    subprocess.run([sys.executable, guide_gen, target_dir])

    print(f"\n=======================================")
    print(f"🎯 COMPILATION COMPLETE!")
    print(f"The active package '{package_name}' has been scrubbed and repaired.")
    print(f"Moodle-Ready SCORM files: {os.path.join(target_dir, 'quizzes')}")
    print(f"Moodle-Ready HTML Pages: {os.path.join(target_dir, 'inlined_lessons')}")
    print(f"Offline HTML Participant Guides: {os.path.join(target_dir, 'Participant_Guides')}")
    print(f"=======================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Moodle Delivery Package Compiler")
    parser.add_argument("package_path", nargs="?", help="Path to the Delivery Package root folder")
    args = parser.parse_args()
    
    if args.package_path:
        target = args.package_path
    else:
        target = input("\nEnter the full path to the Delivery Package folder:\n> ").strip().strip('"').strip("'")
            
    if os.path.exists(target):
        run_compiler(target)
    else:
        print(f"ERROR: The package path provided does not exist: {target}")

