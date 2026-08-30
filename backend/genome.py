from __future__ import annotations

import json
from pathlib import Path

TECHNOLOGY_MAP_PATH = Path(__file__).with_name('technology_map.json')


def _load_map():
    with TECHNOLOGY_MAP_PATH.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def normalize_category_signals(repositories):
    map_doc = _load_map()
    categories = map_doc.get('categories', {})
    signal_counts = {name: 0 for name in categories}
    tech_names = set()
    for repo in repositories:
        repo_name = str(repo.get('name') or '').lower()
        repo_language = str(repo.get('language') or '').lower()
        languages = [str(item).lower() for item in (repo.get('languages') or [])]
        hits = set()
        for cat, keywords in categories.items():
            for keyword in keywords:
                if keyword in repo_name or keyword in repo_language or keyword in ' '.join(languages):
                    hits.add(cat)
        for cat in hits:
            signal_counts[cat] += 1
        tech_names.update({item.lower() for item in (repo.get('topics') or [])})
        tech_names.update({item.lower() for item in languages})
    return signal_counts, tech_names


def build_technical_genome(repositories):
    signal_counts, _ = normalize_category_signals(repositories)
    total = sum(signal_counts.values()) or 1
    scores = {}
    for category, value in signal_counts.items():
        score = round((value / total) * 100, 2)
        scores[category] = min(100, max(10, score + 35))
    return {
        'Backend': scores.get('Backend', 20),
        'Frontend': scores.get('Frontend', 20),
        'Data': scores.get('Data', 20),
        'Algorithms': scores.get('Algorithms', 20),
        'DevOps': scores.get('DevOps', 20),
    }


def build_behavioral_genome(metrics):
    active_days = max(0, int(metrics.get('active_days') or 0))
    streak = max(0, int(metrics.get('streak_days') or 0))
    repos_touched = max(0, int(metrics.get('repositories_touched') or 0))
    core_ratio = float(metrics.get('core_repo_ratio') or 0.0)

    consistency = max(0, min(100, round((active_days / 30) * 100, 2)))
    exploration = max(0, min(100, round((repos_touched / 8) * 100, 2)))
    focus = max(0, min(100, round(core_ratio * 100, 2)))
    persistence = max(0, min(100, round((streak / 21) * 100, 2)))

    return {
        'Consistency': consistency,
        'Exploration': exploration,
        'Focus': focus,
        'Persistence': persistence,
    }
