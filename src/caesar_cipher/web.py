"""
web.py

Flask web visualizer for live frequency analysis and cracking (Challenge 8)

Exposes a small Flask application with an index page (a textarea plus a
Chart.js bar chart) and two JSON endpoints: /analyze returns the letter
frequency distribution for posted text, and /crack returns all 26 Caesar
candidates ranked by chi-squared score. Both reuse the existing analysis
code so the web view and the CLI stay in agreement. Flask is an optional
dependency; the serve command imports this module lazily.

Key exports:
  create_app() - Build and return the configured Flask application

Connects to:
  analyzer.py - FrequencyAnalyzer for frequencies and ranking
  cipher.py - CaesarCipher.crack for candidate generation
  constants.py - Language, UPPERCASE_LETTERS
  main.py - serve command calls create_app()
"""

from typing import Any

from flask import Flask, Response, jsonify, request

from caesar_cipher.analyzer import FrequencyAnalyzer
from caesar_cipher.cipher import CaesarCipher
from caesar_cipher.constants import UPPERCASE_LETTERS, Language

_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Caesar Cipher Frequency Visualizer</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 900px;
           background: #0f1117; color: #e6e6e6; }
    textarea { width: 100%; height: 120px; font-family: monospace; font-size: 1rem;
               background: #1b1e27; color: #e6e6e6; border: 1px solid #333;
               border-radius: 6px; padding: .5rem; }
    button { background: #3b82f6; color: white; border: none; padding: .5rem 1rem;
             border-radius: 6px; cursor: pointer; margin-top: .5rem; }
    #meta { color: #9aa0aa; font-size: .9rem; margin: .5rem 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    td, th { border-bottom: 1px solid #2a2e39; padding: .35rem .5rem; text-align: left; }
    .best { color: #34d399; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Caesar Cipher Frequency Visualizer</h1>
  <textarea id="text" placeholder="Type or paste ciphertext..."></textarea>
  <div id="meta">Characters: 0 | Letters: 0</div>
  <button id="crackBtn">Crack it</button>
  <canvas id="chart" height="120"></canvas>
  <div id="candidates"></div>
  <script>
    const textEl = document.getElementById('text');
    const metaEl = document.getElementById('meta');
    const ctx = document.getElementById('chart').getContext('2d');
    let chart = new Chart(ctx, {
      type: 'bar',
      data: { labels: [], datasets: [{ label: 'Frequency %', data: [],
              backgroundColor: '#3b82f6' }] },
      options: { animation: false, scales: { y: { beginAtZero: true } } }
    });
    async function analyze() {
      metaEl.textContent = 'Characters: ' + textEl.value.length;
      const resp = await fetch('/analyze', { method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textEl.value }) });
      const data = await resp.json();
      chart.data.labels = data.labels;
      chart.data.datasets[0].data = data.frequencies;
      chart.update();
      metaEl.textContent = 'Characters: ' + textEl.value.length +
        ' | Letters: ' + data.count;
    }
    async function crack() {
      const resp = await fetch('/crack', { method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textEl.value }) });
      const data = await resp.json();
      let rows = '<table><tr><th>#</th><th>Shift</th><th>Score</th><th>Text</th></tr>';
      data.candidates.forEach((c, i) => {
        const cls = i === 0 ? ' class="best"' : '';
        const score = c.score === null ? '-' : c.score;
        rows += `<tr${cls}><td>${i + 1}</td><td>${c.shift}</td>` +
                `<td>${score}</td><td>${c.text.slice(0, 80)}</td></tr>`;
      });
      document.getElementById('candidates').innerHTML = rows + '</table>';
    }
    textEl.addEventListener('keyup', analyze);
    document.getElementById('crackBtn').addEventListener('click', crack);
    analyze();
  </script>
</body>
</html>
"""


def _select_language(name: str) -> Language:
    """
    Resolve a language name to a Language, defaulting to English when unknown
    """
    try:
        return Language(name.lower())
    except ValueError:
        return Language.ENGLISH


def create_app() -> Flask:
    """
    Build and return the configured Flask application
    """
    app = Flask(__name__)

    @app.get("/")
    def index() -> Response:
        return Response(_INDEX_HTML, mimetype = "text/html")

    @app.post("/analyze")
    def analyze() -> Response:
        payload: dict[str, Any] = request.get_json(silent = True) or {}
        text = str(payload.get("text", ""))
        analyzer = FrequencyAnalyzer(_select_language(str(payload.get("language", "english"))))
        frequencies = analyzer.letter_frequencies(text)
        count = sum(analyzer.letter_counts(text).values())
        return jsonify({
            "labels": list(UPPERCASE_LETTERS),
            "frequencies": [frequencies[letter] for letter in UPPERCASE_LETTERS],
            "count": count,
        })

    @app.post("/crack")
    def crack() -> Response:
        payload: dict[str, Any] = request.get_json(silent = True) or {}
        text = str(payload.get("text", ""))
        analyzer = FrequencyAnalyzer(_select_language(str(payload.get("language", "english"))))
        ranked = analyzer.rank_candidates(CaesarCipher.crack(text))
        candidates = [
            {
                "shift": shift,
                "text": candidate_text,
                "score": None if score == float("inf") else round(score, 2),
            }
            for shift, candidate_text, score in ranked
        ]
        return jsonify({"candidates": candidates})

    return app
