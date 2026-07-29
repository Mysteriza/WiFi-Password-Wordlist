# General WiFi Password Wordlist

This repository contains a comprehensive WiFi password wordlist, designed for security testing, auditing, and educational purposes.

## Overview

The wordlist `wifi-wordlist.txt` was created by merging specialized wordlists with the well-known `rockyou.txt` dictionary, yielding a highly effective and broad-coverage wordlist for WPA/WPA2/WPA3 cracking.

**Current size**: ~8.5 million passwords

![](https://img.shields.io/github/repo-size/Mysteriza/WiFi-Password-Wordlist)

Key features include:

- **Broad Coverage**: No longer limited to specific regions (e.g., Indonesia). It contains a massive variety of common passwords, dates, patterns, and global terms by incorporating the extensive `rockyou.txt` database.
- **WPA/WPA2/WPA3 Optimized**: 
  - **Length Enforcement**: All passwords in the list have been strictly filtered to have a minimum length of 8 characters and a maximum length of 63 characters, which adheres exactly to the WPA/WPA2/WPA3 standard requirements.
- **Cleaned and Filtered**: Passwords that are too short (< 8 characters) or too long (> 63 characters) have been removed to optimize testing efficiency and save computing time.
- **Deduplicated & Sorted**: Duplicates removed; numeric-only entries and digit-prefixed passwords sorted to the top for faster cracking.

## Processing Script

`process_wordlist.py` is a Python tool to manage and analyze the wordlist:

```bash
# Process (dedup + sort + filter) the wordlist
python process_wordlist.py

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
3. **Smart sorts** — Numeric-only → digit-prefixed → alphabetical
4. **Reports** — Full statistics: composition, length distribution, character analysis

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
