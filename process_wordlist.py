#!/usr/bin/env python3
"""
WiFi Password Wordlist Processor
=================================
Deduplicates, sorts, filters (8-63 chars), and analyzes a WiFi password wordlist.

Usage:
    python process_wordlist.py                          # Process wifi-wordlist.txt
    python process_wordlist.py --input <file>           # Process custom file
    python process_wordlist.py --dry-run                # Analyze only, no output
    python process_wordlist.py --stats-only             # Show stats on existing output
    python process_wordlist.py --dates-only             # Keep only valid birth dates among numeric entries
"""

import os
import sys
import argparse
import time
import calendar
from pathlib import Path
from collections import Counter


# ─── Configuration ───────────────────────────────────────────────────────────
MIN_LENGTH = 8
MAX_LENGTH = 63
DEFAULT_INPUT = "wifi-wordlist.txt"
DEFAULT_OUTPUT = "wifi-wordlist.txt"


# ─── Date Validation ─────────────────────────────────────────────────────────
# 3 worldwide date formats for birth dates:
#   Format 1: DDMMYYYY / DDMMYY  (Day-Month-Year) — Indonesia, Europe, UK, etc.
#   Format 2: MMDDYYYY / MMDDYY  (Month-Day-Year) — United States
#   Format 3: YYYYMMDD / YYMMDD  (Year-Month-Day) — ISO, China, Japan, Korea

YEAR_4D_MIN = 1920
YEAR_4D_MAX = 2020
YEAR_2D_MIN = 20   # 1920
YEAR_2D_MAX = 20   # 2020 → 20


def _valid_ymd(year: int, month: int, day: int) -> bool:
    """Check if year/month/day form a valid calendar date."""
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False
    try:
        return day <= calendar.monthrange(year, month)[1]
    except ValueError:
        return False


def _valid_year_4d(year: int) -> bool:
    return YEAR_4D_MIN <= year <= YEAR_4D_MAX


def _valid_year_2d(year: int) -> bool:
    # 00-20 → 2000-2020, 21-99 → 1921-1999
    if 0 <= year <= YEAR_2D_MAX:
        return True
    if 21 <= year <= 99:
        return True
    return False


def is_valid_date(s: str) -> bool:
    """
    Check if a numeric string is a valid birth date in any of the 3 formats.
    Supports 6-digit (DDMMYY, MMDDYY, YYMMDD) and 8-digit (DDMMYYYY, MMDDYYYY, YYYYMMDD).
    """
    if not s.isdigit():
        return False

    length = len(s)

    # ── 8-digit dates ──
    if length == 8:
        # Format 1: DDMMYYYY
        d, m, y = int(s[0:2]), int(s[2:4]), int(s[4:8])
        if _valid_year_4d(y) and _valid_ymd(y, m, d):
            return True

        # Format 2: MMDDYYYY
        m, d, y = int(s[0:2]), int(s[2:4]), int(s[4:8])
        if _valid_year_4d(y) and _valid_ymd(y, m, d):
            return True

        # Format 3: YYYYMMDD
        y, m, d = int(s[0:4]), int(s[4:6]), int(s[6:8])
        if _valid_year_4d(y) and _valid_ymd(y, m, d):
            return True

    # ── 6-digit dates ──
    elif length == 6:
        # Format 1: DDMMYY
        d, m, y = int(s[0:2]), int(s[2:4]), int(s[4:6])
        year = 2000 + y if 0 <= y <= YEAR_2D_MAX else 1900 + y
        if _valid_ymd(year, m, d):
            return True

        # Format 2: MMDDYY
        m, d, y = int(s[0:2]), int(s[2:4]), int(s[4:6])
        year = 2000 + y if 0 <= y <= YEAR_2D_MAX else 1900 + y
        if _valid_ymd(year, m, d):
            return True

        # Format 3: YYMMDD
        y, m, d = int(s[0:2]), int(s[2:4]), int(s[4:6])
        year = 2000 + y if 0 <= y <= YEAR_2D_MAX else 1900 + y
        if _valid_ymd(year, m, d):
            return True

    return False


# ─── Helpers ─────────────────────────────────────────────────────────────────

def sizeof_fmt(num: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.2f} {unit}"
        num /= 1024
    return f"{num:.2f} TB"


def sort_key(password: str) -> tuple:
    """
    Custom sort key:
    1. Numeric-only strings (dates, PINs) → sorted numerically, at top
    2. Strings starting with digit → next group, sorted numerically then alpha
    3. Everything else → alphabetical (case-insensitive)
    """
    if password.isdigit() and all("0" <= c <= "9" for c in password):
        return (0, int(password), "")
    elif password and password[0].isdigit():
        # Extract leading digits for numeric sort, rest for alpha sort
        i = 0
        while i < len(password) and password[i].isdigit():
            i += 1
        leading = password[:i]
        if all("0" <= c <= "9" for c in leading):
            return (1, int(leading), password[i:].lower())
        else:
            return (2, 0, password.lower())
    else:
        return (2, 0, password.lower())


def analyze_wordlist(filepath: str) -> dict:
    """
    Stream-analyze a wordlist file and return statistics.
    Memory-efficient: reads line by line.
    """
    stats = {
        "total": 0,
        "valid": 0,
        "too_short": 0,
        "too_long": 0,
        "min_len": 999,
        "max_len": 0,
        "unique_chars": set(),
        "digit_only": 0,
        "valid_dates": 0,
        "non_date_digits": 0,
        "alpha_only": 0,
        "alphanumeric": 0,
        "has_special": 0,
        "lowercase_only": 0,
        "uppercase_only": 0,
        "mixed_case": 0,
        "length_distribution": Counter(),
        "duplicates": 0,
        "seen": set(),
    }

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pwd = line.rstrip("\n\r")
            if not pwd:
                continue

            stats["total"] += 1
            length = len(pwd)

            # Length checks
            if length < MIN_LENGTH:
                stats["too_short"] += 1
            elif length > MAX_LENGTH:
                stats["too_long"] += 1
            else:
                stats["valid"] += 1

            # Track min/max
            if length < stats["min_len"]:
                stats["min_len"] = length
            if length > stats["max_len"]:
                stats["max_len"] = length

            # Length distribution (only for valid range)
            if MIN_LENGTH <= length <= MAX_LENGTH:
                stats["length_distribution"][length] += 1

            # Character composition
            has_digit = any(c.isdigit() for c in pwd)
            has_alpha = any(c.isalpha() for c in pwd)
            has_special = any(not c.isalnum() for c in pwd)

            if has_digit and not has_alpha and not has_special:
                stats["digit_only"] += 1
                if is_valid_date(pwd):
                    stats["valid_dates"] += 1
                else:
                    stats["non_date_digits"] += 1
            elif has_alpha and not has_digit and not has_special:
                stats["alpha_only"] += 1
                if pwd.islower():
                    stats["lowercase_only"] += 1
                elif pwd.isupper():
                    stats["uppercase_only"] += 1
                else:
                    stats["mixed_case"] += 1
            elif has_alpha and has_digit and not has_special:
                stats["alphanumeric"] += 1
            if has_special:
                stats["has_special"] += 1

            # Unique characters across wordlist (sample first 100k)
            if stats["total"] <= 100_000:
                stats["unique_chars"].update(pwd)

            # Duplicate detection (sample first 500k for speed)
            if stats["total"] <= 500_000:
                if pwd in stats["seen"]:
                    stats["duplicates"] += 1
                stats["seen"].add(pwd)

    return stats


def print_stats(stats: dict, label: str = "Wordlist Statistics"):
    """Print formatted statistics."""
    total = stats["total"]
    valid = stats["valid"]
    too_short = stats["too_short"]
    too_long = stats["too_long"]

    print("=" * 60)
    print(f"  {label}")
    print("=" * 60)
    print(f"  Total entries          : {total:>12,}")
    print(f"  ─────────────────────────────────────────")
    print(f"  Valid (8-63 chars)     : {valid:>12,}  ({valid / total * 100:5.1f}%)" if total else "")
    print(f"  Too short (<8)         : {too_short:>12,}  ({too_short / total * 100:5.1f}%)" if total else "")
    print(f"  Too long (>63)         : {too_long:>12,}  ({too_long / total * 100:5.1f}%)" if total else "")
    print()

    if stats["min_len"] != 999:
        print(f"  Shortest password      : {stats['min_len']:>12} chars")
        print(f"  Longest password       : {stats['max_len']:>12} chars")
    print()

    # Composition
    print(f"  ── Composition ──")
    print(f"  Digits only            : {stats['digit_only']:>12,}")
    if stats["valid_dates"] > 0 or stats["non_date_digits"] > 0:
        print(f"    ├─ Valid dates       : {stats['valid_dates']:>12,}")
        print(f"    └─ Non-date numbers  : {stats['non_date_digits']:>12,}")
    print(f"  Alpha only             : {stats['alpha_only']:>12,}")
    print(f"    ├─ Lowercase only    : {stats['lowercase_only']:>12,}")
    print(f"    ├─ Uppercase only    : {stats['uppercase_only']:>12,}")
    print(f"    └─ Mixed case        : {stats['mixed_case']:>12,}")
    print(f"  Alphanumeric           : {stats['alphanumeric']:>12,}")
    print(f"  Contains special chars : {stats['has_special']:>12,}")
    print()

    # Length distribution (top 10)
    if stats["length_distribution"]:
        print(f"  ── Length Distribution (Top 10) ──")
        for length, count in stats["length_distribution"].most_common(10):
            pct = count / valid * 100 if valid else 0
            bar = "█" * int(pct / 2) + "▌" * (pct % 2 > 0)
            print(f"    {length:>2} chars : {count:>10,} ({pct:5.1f}%)  {bar}")
        print()

    # Duplicate info
    if stats["duplicates"] > 0:
        print(f"  Duplicates (sample)    : {stats['duplicates']:>12,}")
    print(f"  Unique chars sampled   : {len(stats['unique_chars']):>12}")
    print("=" * 60)


def process_wordlist(input_path: str, output_path: str, dry_run: bool = False, dates_only: bool = False):
    """
    Main processing pipeline:
    1. Filter by length (8-63 chars)
    2. Optionally filter numeric non-date entries (--dates-only)
    3. Deduplicate
    4. Sort (dates/numbers first, then alphabetical)
    """
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)

    file_size = input_file.stat().st_size
    print(f"📂 Input : {input_file.name} ({sizeof_fmt(file_size)})")
    print(f"🔧 Mode  : {'DRY RUN (no output)' if dry_run else 'Full processing'}"
          f"{' | Dates-only filter ON' if dates_only else ''}")
    print()

    # ── Phase 1: Read, filter, dedup ──
    print("⏳ Phase 1/3: Reading, filtering, and deduplicating...")
    start = time.time()

    seen = set()
    unique_valid = []
    total_read = 0
    filtered_short = 0
    filtered_long = 0
    filtered_non_date = 0
    filtered_leading_zeros = 0
    duplicates = 0

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pwd = line.rstrip("\n\r")
            if not pwd:
                continue
            total_read += 1

            length = len(pwd)
            if length < MIN_LENGTH:
                filtered_short += 1
                continue
            if length > MAX_LENGTH:
                filtered_long += 1
                continue

# ── Leading-zero filter ──
            # Remove entries with 4+ leading zeros (e.g., 00001234, 0000abc)
            # but keep all-zero entries (e.g., 00000000)
            is_all_zeros = all(c == "0" for c in pwd)
            if not is_all_zeros:
                leading_zeros = 0
                for c in pwd:
                    if c == "0":
                        leading_zeros += 1
                    else:
                        break
                if leading_zeros >= 4:
                    filtered_leading_zeros += 1
                    continue

            # ── Dates-only filter ──
            # Remove numeric strings that aren't valid dates
            # (all-zero entries are exempt — they pass through)
            if dates_only and pwd.isdigit() and not is_valid_date(pwd) and not is_all_zeros:
                filtered_non_date += 1
                continue

            if pwd in seen:
                duplicates += 1
                continue
            seen.add(pwd)
            unique_valid.append(pwd)

    phase1_time = time.time() - start
    print(f"   ✅ Read {total_read:,} lines")
    print(f"   ✅ Filtered: {filtered_short:,} too short, {filtered_long:,} too long"
          f"{f', {filtered_non_date:,} non-date numbers' if dates_only else ''}"
          f"{f', {filtered_leading_zeros:,} leading-zero numbers' if filtered_leading_zeros else ''}")
    print(f"   ✅ Removed {duplicates:,} duplicates")
    print(f"   ✅ Unique valid entries: {len(unique_valid):,}")
    print(f"   ⏱  {phase1_time:.2f}s")
    print()

    if dry_run:
        print("🔍 DRY RUN — No output file written.")
        return unique_valid

    # ── Phase 2: Sort ──
    print("⏳ Phase 2/3: Sorting (dates/numbers first, then alphabetical)...")
    start = time.time()

    unique_valid.sort(key=sort_key)

    phase2_time = time.time() - start
    print(f"   ✅ Sorting complete")
    print(f"   ⏱  {phase2_time:.2f}s")
    print()

    # ── Phase 3: Write output ──
    print("⏳ Phase 3/3: Writing output...")
    start = time.time()

    with open(output_path, "w", encoding="utf-8") as f:
        for pwd in unique_valid:
            f.write(pwd + "\n")

    phase3_time = time.time() - start
    out_size = Path(output_path).stat().st_size
    print(f"   ✅ Output written: {output_path} ({sizeof_fmt(out_size)})")
    print(f"   ⏱  {phase3_time:.2f}s")
    print()

    total_time = phase1_time + phase2_time + phase3_time
    print(f"🎯 Done! Total time: {total_time:.2f}s")
    print(f"   {len(unique_valid):,} passwords written to {output_path}")

    return unique_valid


def main():
    global MIN_LENGTH, MAX_LENGTH
    parser = argparse.ArgumentParser(
        description="WiFi Password Wordlist Processor — Dedup, Sort, Filter & Analyze",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_wordlist.py                          # Process default file
  python process_wordlist.py --input mylist.txt       # Custom input file
  python process_wordlist.py --dry-run                # Analyze only
  python process_wordlist.py --stats-only             # Stats on existing output
  python process_wordlist.py --dates-only             # Keep only valid birth dates among numeric entries
        """,
    )
    parser.add_argument(
        "--input", "-i",
        default=DEFAULT_INPUT,
        help=f"Input wordlist file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Output wordlist file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Analyze only — do not write output file",
    )
    parser.add_argument(
        "--stats-only", "-s",
        action="store_true",
        help="Show statistics on existing output file without processing",
    )
    parser.add_argument(
        "--dates-only", "-d",
        action="store_true",
        help="Remove numeric entries that aren't valid birth dates (keeps DDMMYYYY, MMDDYYYY, YYYYMMDD and 6-digit variants)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=MIN_LENGTH,
        help=f"Minimum password length (default: {MIN_LENGTH})",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=MAX_LENGTH,
        help=f"Maximum password length (default: {MAX_LENGTH})",
    )

    args = parser.parse_args()

    # Update globals from CLI args
    MIN_LENGTH = args.min_length
    MAX_LENGTH = args.max_length

    # ── Stats-only mode ──
    if args.stats_only:
        if not Path(args.output).exists():
            print(f"❌ Error: Output file not found: {args.output}")
            sys.exit(1)
        stats = analyze_wordlist(args.output)
        print_stats(stats, f"Analysis: {args.output}")
        return

    # ── Process ──
    result = process_wordlist(args.input, args.output, args.dry_run, args.dates_only)

    # ── Final statistics ──
    print()
    print("📊 Final Statistics:")
    print_stats(analyze_wordlist(args.output if not args.dry_run else args.input))


if __name__ == "__main__":
    main()