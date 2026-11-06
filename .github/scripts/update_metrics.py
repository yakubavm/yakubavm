#!/usr/bin/env python3
"""Build self-hosted profile metrics from GitHub's public repository API and GraphQL.

Only standard-library modules are used. No third-party image endpoints, tracking,
user-provided access tokens, or private-repository scraping.

In GitHub Actions GITHUB_TOKEN has access to this data. Pass --placeholder locally
when creating or inspecting the profile before the first Actions run.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

USERNAME = 'yakubavm'
OUTPUT = Path(__file__).resolve().parents[2] / 'assets' / 'metrics.svg'
API = 'https://api.github.com'
BG, FG, MUTED = '#0d1117', '#e9f1ff', '#94a3b8'
CYAN, PURPLE, GREEN = '#67e8f9', '#c084fc', '#50e3a4'
LEVEL = ['#1c2532', '#3c3367', '#6553b4', '#9970e3', '#d29bff']


def api_json(path: str, token: str, method: str = 'GET', body: dict | None = None):
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'yakubavm-profile-metrics',
        'X-GitHub-Api-Version': '2022-11-28',
        'Authorization': f'Bearer {token}',
    }
    data = json.dumps(body).encode('utf-8') if body is not None else None
    url = path if path.startswith('https:') else API + path
    req = Request(url, data=data, method=method, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(req, timeout=28) as resp:
                return json.load(resp)
        except (HTTPError, URLError, TimeoutError) as ex:
            if attempt == 2:
                raise RuntimeError(f'GitHub API request failed: {path}: {ex}') from ex
            time.sleep(1 + attempt * 2)
    raise AssertionError('unreachable')


def fetch() -> dict:
    token = os.environ.get('GITHUB_TOKEN', '').strip()
    if not token:
        raise RuntimeError('GITHUB_TOKEN is required for live sync. Use --placeholder locally.')

    repos = []
    for page in range(1, 20):
        chunk = api_json(f'/users/{USERNAME}/repos?per_page=100&page={page}&type=owner', token)
        if not isinstance(chunk, list):
            raise RuntimeError(f'Unexpected API response for repositories: {chunk!r}')
        repos.extend(chunk)
        if len(chunk) < 100:
            break
    else:
        raise RuntimeError('Repository pagination limit reached; increase if necessary.')

    # Public original projects; skip the special profile repository itself.
    projects = [r for r in repos if not r.get('fork', False) and r.get('name', '').lower() != USERNAME.lower()]
    stars = sum(int(r.get('stargazers_count', 0)) for r in projects)
    lang_bytes = Counter()
    for repo in projects:
        # Github REST's language endpoint reports *bytes of code*, not expertise.
        languages = api_json(f"/repos/{USERNAME}/{repo['name']}/languages", token)
        if not isinstance(languages, dict):
            raise RuntimeError(f"Unexpected languages response for {repo['name']}")
        lang_bytes.update({k: int(v) for k, v in languages.items()})

    query = '''query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }'''
    reply = api_json('/graphql', token, method='POST', body={
        'query': query,
        'variables': {'login': USERNAME},
    })
    if reply.get('errors'):
        raise RuntimeError(f"GitHub GraphQL error: {reply['errors']!r}")
    try:
        calendar = reply['data']['user']['contributionsCollection']['contributionCalendar']
        days = [day for week in calendar['weeks'] for day in week['contributionDays']]
    except (TypeError, KeyError) as ex:
        raise RuntimeError(f'Unexpected GitHub GraphQL calendar response: {reply!r}') from ex
    return {
        'projects': len(projects),
        'stars': stars,
        'contributions': int(calendar['totalContributions']),
        'days': days,
        'languages': lang_bytes,
        'pending': False,
    }


def rect(x, y, w, h, *, fill='#111925', stroke='#344057', rad=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rad}" fill="{fill}" stroke="{stroke}"/>'


def tx(x, y, value, *, size=20, color=FG, bold=False, mono=False, anchor=None):
    font = 'Consolas,DejaVu Sans Mono,monospace' if mono else 'Segoe UI,Inter,Arial,sans-serif'
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-family="{font}" font-weight="{700 if bold else 400}" '
            + (f'text-anchor="{anchor}" ' if anchor else '')
            + f'>{escape(str(value))}</text>')


def level(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    return 4


def render(data: dict) -> str:
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="473" viewBox="0 0 1160 473" '
        'role="img" aria-label="Automatically updated GitHub public activity statistics">',
        '<defs><linearGradient id="line" x1="0" y1="0" x2="1" y2="0">'
        '<stop stop-color="#c084fc"/><stop offset=".55" stop-color="#7287fa"/>'
        '<stop offset="1" stop-color="#67e8f9"/></linearGradient></defs>',
        rect(1, 1, 1158, 471, fill=BG, stroke='#283244', rad=18),
        '<rect x="28" y="22" width="7" height="24" rx="3" fill="url(#line)"/>',
        tx(52, 42, 'GITHUB / PUBLIC SIGNAL', size=20, color=CYAN, bold=True, mono=True),
        tx(1122, 42, 'LIVE DATA  //  github.com/yakubavm', size=16, color=MUTED, mono=True, anchor='end'),
    ]
    names = ['PUBLIC PROJECTS', 'STARS RECEIVED', 'LAST 12M CONTRIBUTIONS']
    nums = [data['projects'], data['stars'], data['contributions']]
    for i, (name, value) in enumerate(zip(names, nums)):
        x = 22 + i * 378
        pieces += [rect(x, 65, 362, 109, fill='#141b29', stroke='#354159', rad=13),
                   tx(x + 19, 95, name, size=16, color=MUTED, bold=True, mono=True),
                   tx(x + 19, 150, value, size=50, color=(PURPLE, CYAN, GREEN)[i], bold=True)]
    pieces += [tx(30, 217, 'CONTRIBUTION MAP', size=19, color=FG, bold=True, mono=True),
               tx(794, 217, 'LANGUAGE MIX', size=19, color=FG, bold=True, mono=True),
               '<line x1="764" y1="199" x2="764" y2="432" stroke="#303b50"/>',
               rect(23, 229, 731, 208, fill='#111925', stroke='#303b50', rad=11),
               rect(778, 229, 356, 208, fill='#111925', stroke='#303b50', rad=11)]

    day_lookup = {item['date']: int(item['contributionCount']) for item in data['days']}
    all_dates = sorted(day_lookup)
    # GitHub's calendar starts on Sunday. Group each 7-day week in chronological order.
    first_month_marks = []
    if all_dates:
        date_objs = [date.fromisoformat(x) for x in all_dates]
        weekday_offset = (date_objs[0].weekday() + 1) % 7
        if weekday_offset != 0:
            # The GraphQL calendar normally supplies complete Sun-Sat weeks; if it
            # doesn't, preserve alignment without inventing activity.
            all_dates = [None] * weekday_offset + all_dates
    else:
        all_dates = [None] * (53 * 7)
    cols = min(53, (len(all_dates) + 6) // 7)
    if len(all_dates) > 53 * 7:
        all_dates = all_dates[-53 * 7:]
        cols = 53
    dx = 13.05
    for col in range(cols):
        for row in range(7):
            index = col * 7 + row
            d = all_dates[index] if index < len(all_dates) else None
            count = day_lookup.get(d, 0) if d else 0
            color = LEVEL[level(count)]
            x = 45 + col * dx
            y = 267 + row * 17.9
            pieces.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="9.5" height="9.5" rx="2" fill="{color}"/>')
            if d and d[8:10] == '01' and row < 4:
                m = date.fromisoformat(d).strftime('%b')
                first_month_marks.append((x, m))
    for x, month in first_month_marks:
        # labels are placed only when enough space remains within the heatmap
        if x < 680:
            pieces.append(tx(round(x, 1), 255, month, size=12, color=MUTED, mono=True))
    pieces += [tx(45, 420, 'Sun  →  Sat    ·    Dots represent calendar days', size=14, color=MUTED)]

    langs = Counter(data['languages'])
    total = sum(langs.values())
    if total:
        main = langs.most_common(4)
        other = total - sum(value for _, value in main)
        if other:
            main.append(('Other', other))
        colors = [PURPLE, CYAN, '#8098fa', GREEN, '#8696aa']
        for i, (name, byte_count) in enumerate(main[:5]):
            y = 263 + i * 33
            pct = byte_count / total * 100
            pieces += [tx(797, y, name, size=17, color=FG),
                       tx(1113, y, f'{pct:.1f}%', size=16, color=MUTED, anchor='end'),
                       rect(798, y + 7, 313, 6, fill='#283142', stroke='#283142', rad=3),
                       rect(798, y + 7, round(313 * byte_count / total, 2), 6,
                            fill=colors[i], stroke=colors[i], rad=3)]
    else:
        pieces += [tx(797, 283, 'No public language data yet', size=17, color=MUTED),
                   tx(797, 317, 'This section refreshes automatically.', size=15, color=MUTED)]
    pieces += [tx(797, 422, 'Code bytes in public original repos', size=14, color=MUTED),
               tx(35, 459, ('Waiting for the first GitHub Actions sync' if data['pending']
                            else 'Generated from public GitHub data · no third-party stat servers'),
                  size=13, color=MUTED),
               '</svg>']
    return '\n'.join(pieces) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--placeholder', action='store_true')
    args = parser.parse_args()
    if args.placeholder:
        data = {'projects': '—', 'stars': '—', 'contributions': '—',
                'days': [], 'languages': {}, 'pending': True}
    else:
        data = fetch()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result = render(data)
    # Don't touch the file if no visible metrics have changed.
    if OUTPUT.exists() and OUTPUT.read_text(encoding='utf-8') == result:
        print('Metrics are unchanged')
        return
    OUTPUT.write_text(result, encoding='utf-8')
    print(f'Updated {OUTPUT} ({len(result)} bytes)')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Metrics build failed: {exc}', file=sys.stderr)
        sys.exit(1)
