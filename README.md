# General WiFi Password Wordlist

This repository contains a comprehensive WiFi password wordlist, designed for security testing, auditing, and educational purposes.

## Overview

The wordlist `wifi-wordlist.txt` was created by merging specialized wordlists with the well-known `rockyou.txt` dictionary, yielding a highly effective and broad-coverage wordlist for WPA/WPA2/WPA3 cracking.

**Current size**: ~8.5 million passwords | **97 MB**

Key features include:

- **Broad Coverage**: No longer limited to specific regions (e.g., Indonesia). It contains a massive variety of common passwords, dates, patterns, and global terms by incorporating the extensive `rockyou.txt` database.
- **WPA/WPA2/WPA3 Optimized**: 
  - **Length Enforcement**: All passwords in the list have been strictly filtered to have a minimum length of 8 characters and a maximum length of 63 characters, which adheres exactly to the WPA/WPA2/WPA3 standard requirements.
- **Cleaned and Filtered**: Passwords that are too short (< 8 characters) or too long (> 63 characters) have been removed to optimize testing efficiency and save computing time.
- **Date-Only Numeric Filter**: Non-date numeric entries (national ID numbers, phone numbers, PINs, random digit sequences, etc.) are removed — only valid birth dates in 3 worldwide formats (DDMMYYYY, MMDDYYYY, YYYYMMDD) are kept.
- **Leading-Zero Cleanup**: Entries with 4+ leading zeros (e.g., `00001234`, `0000abc`) are removed as unlikely WiFi passwords.
- **Deduplicated & Sorted**: Duplicates removed; numeric-only entries (dates) and digit-prefixed passwords sorted to the top for faster cracking.

## Processing Script

`process_wordlist.py` is a Python tool to manage and analyze the wordlist:

```bash
# Process (dedup + sort + filter) the wordlist
python process_wordlist.py

# Keep only valid birth dates among numeric entries
python process_wordlist.py --dates-only

# Analyze only — no changes
python process_wordlist.py --dry-run

# Show stats on existing output
python process_wordlist.py --stats-only

# Custom file
python process_wordlist.py --input mylist.txt --output cleaned.txt
```

### What it does

1. **Deduplicates** — Removes all duplicate entries
2. **Filters** — Keeps only passwords 8–63 characters (WPA/WPA2/WPA3 standard)
3. **Date validation** (with `--dates-only`) — Removes numeric entries that aren't valid birth dates in any of 3 worldwide formats (DDMMYYYY, MMDDYYYY, YYYYMMDD + 6-digit variants)
4. **Leading-zero cleanup** — Removes entries with 4+ leading zeros (except all-zero strings)
5. **Smart sorts** — Numeric-only (dates) → digit-prefixed → alphabetical
6. **Reports** — Full statistics: composition, length distribution, character analysis, date breakdown

### 3 Date Formats Supported

| Format | Example | Region |
|--------|---------|--------|
| **DDMMYYYY** / DDMMYY | `01011990` / `010190` | Indonesia, Europe, UK, Australia |
| **MMDDYYYY** / MMDDYY | `01011990` / `010190` | United States |
| **YYYYMMDD** / YYMMDD | `19900101` / `900101` | ISO standard, China, Japan, Korea |

## Wordlist References

Additional wordlists suitable for WiFi password cracking (filtered to 8–63 chars):

| Source | Description | Size |
|--------|-------------|------|
| [berzerk0/Probable-Wordlists](https://github.com/berzerk0/Probable-Wordlists) — WPA-Length | Real passwords filtered to 8–40 chars, sorted by probability | 4.27 GB (7z) |
| [kennyn510/wpa2-wordlists](https://github.com/kennyn510/wpa2-wordlists) | Collection with prep script for 8–63 char filtering | Various |
| [WeakPass — weakpass_2_wifi](https://weakpass.com/wordlists/weakpass_2_wifi) | Curated WiFi-focused wordlist | ~1 GB+ |
| [CrackStation](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm) | Massive general-purpose dictionary (pre-filter for WiFi length) | 15 GB |
| [Mysteriza/WiFi-Password-Wordlist](https://github.com/Mysteriza/WiFi-Password-Wordlist) | Indonesia-focused WiFi wordlist | Custom |

> **Recommendation**: For the best additional coverage, download **berzerk0's Real-WPA-Passwords** (torrent available in their repo) — it's already filtered to WPA length and sorted by probability.

## Disclaimer

This wordlist is intended for legal security auditing, penetration testing, and educational purposes only. Usage of this list for attacking targets without prior mutual consent is illegal. The author assumes no liability for any misuse of this content.
