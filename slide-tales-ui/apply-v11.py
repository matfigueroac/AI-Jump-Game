from pathlib import Path
import re

app = Path('web/app.js')
s = app.read_text()

s = s.replace(
"  const prefsKey = 'slide-tales-prefs-v1';",
"  const prefsKey = 'slide-tales-prefs-v1';\n  const profileKey = 'slide-tales-profile-v11';"
)
s = s.replace(
"  const savedPrefs = loadJson(prefsKey, {});\n  const state = {",
"  const savedPrefs = loadJson(prefsKey, {});\n  const savedProfile = loadJson(profileKey, {});\n  const state = {"
)
s = s.replace(
"    infoReturn: 'home',\n    records: loadJson(recordsKey, {}),",
"    infoReturn: 'home',\n    isDaily: false,\n    lastResult: null,\n    profile: { bonusStars: Number(savedProfile.bonusStars || 0), dailySolved: savedProfile.dailySolved || {} },\n    records: loadJson(recordsKey, {}),"
)

progression = r'''  function recordKey(id, size) { return id + '-' + size + 'x' + size; }
  function resultStars(size, moves) {
    if (size === 3) return moves <= 35 ? 3 : moves <= 55 ? 2 : 1;
    return moves <= 80 ? 3 : moves <= 130 ? 2 : 1;
  }

  function recordStars() {
    return Object.values(state.records).reduce((sum, record) => sum + Number(record.stars || 0), 0);
  }

  function totalStars() {
    return recordStars() + Number(state.profile.bonusStars || 0);
  }

  function playerLevel(total = totalStars()) {
    return 1 + Math.floor(total / 12);
  }

  function levelProgress(total = totalStars()) {
    return { current: total % 12, max: 12, pct: Math.round(((total % 12) / 12) * 100) };
  }

  function saveProfile() {
    localStorage.setItem(profileKey, JSON.stringify(state.profile));
  }

  function dateKey(offset = 0) {
    const d = new Date();
    d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() + offset);
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function dailyNumber() {
    const start = new Date(2026, 0, 1, 12, 0, 0, 0);
    const now = new Date();
    now.setHours(12, 0, 0, 0);
    return Math.max(1, Math.floor((now - start) / 86400000) + 1);
  }

  function dailyDoneToday() {
    return Boolean(state.profile.dailySolved[dateKey(0)]);
  }

  function dailyStreak() {
    let offset = dailyDoneToday() ? 0 : -1;
    let streak = 0;
    while (streak < 365 && state.profile.dailySolved[dateKey(offset)]) {
      streak += 1;
      offset -= 1;
    }
    return streak;
  }

  function weeklyStreakMarkup() {
    const letters = ['S','M','T','W','T','F','S'];
    return Array.from({ length: 7 }, (_, i) => {
      const offset = i - 6;
      const d = new Date();
      d.setDate(d.getDate() + offset);
      const key = dateKey(offset);
      const done = Boolean(state.profile.dailySolved[key]);
      const today = offset === 0;
      return '<span class="week-day ' + (done ? 'done ' : '') + (today ? 'today' : '') + '"><b>' + letters[d.getDay()] + '</b><i>' + (done ? '✓' : '·') + '</i></span>';
    }).join('');
  }

  function collectionStats(collectionId, size = state.size) {
    const list = collectionId === 'all' ? PUZZLES : PUZZLES.filter(p => p.collection === collectionId);
    const records = list.map(p => state.records[recordKey(p.id, size)]).filter(Boolean);
    return {
      solved: records.length,
      total: list.length,
      stars: records.reduce((sum, record) => sum + Number(record.stars || 0), 0),
      maxStars: list.length * 3,
    };
  }

  function targetMarkup(size = state.size) {
    return size === 3 ? '★★★ ≤35 &nbsp; · &nbsp; ★★ ≤55' : '★★★ ≤80 &nbsp; · &nbsp; ★★ ≤130';
  }

  function nextPuzzle() {
    const list = PUZZLES.filter(p => p.collection === state.current.collection);
    const currentIndex = Math.max(0, list.findIndex(p => p.id === state.current.id));
    for (let step = 1; step <= list.length; step += 1) {
      const candidate = list[(currentIndex + step) % list.length];
      if (!state.records[recordKey(candidate.id, state.size)]) return candidate;
    }
    return list[(currentIndex + 1) % list.length] || PUZZLES[0];
  }

  function saveRecord() {
    const key = recordKey(state.current.id, state.size);
    const stars = resultStars(state.size, state.moves);
    const previous = state.records[key];
    const firstEverSolve = !state.records[recordKey(state.current.id, 3)] && !state.records[recordKey(state.current.id, 4)];
    const previousStars = Number(previous?.stars || 0);
    const better = !previous || stars > previous.stars ||
      (stars === previous.stars && state.moves < previous.moves) ||
      (stars === previous.stars && state.moves === previous.moves && state.seconds < previous.seconds);
    if (better) {
      state.records[key] = { moves: state.moves, seconds: state.seconds, stars };
      localStorage.setItem(recordsKey, JSON.stringify(state.records));
    }
    return {
      stars,
      previous,
      improved: better,
      firstSolve: !previous,
      firstEverSolve,
      starGain: Math.max(0, stars - previousStars),
    };
  }'''

s, n = re.subn(r"  function recordKey\(id, size\).*?\n  function formatTime", progression + "\n\n  function formatTime", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'progression replace failed {n}')

home = r'''function renderHome() {
  const featured = dailyPuzzle();
  const level = playerLevel();
  const xp = levelProgress();
  const streak = dailyStreak();
  const dailyDone = dailyDoneToday();
  return shell('<section class="screen home-screen retention-home">' +
    '<div class="hero-lockup"><p class="hero-copy">PICK · SLIDE · SOLVE</p><p class="hero-sub"><span class="daily-dot">●</span> TODAY · ' + featured.title.toUpperCase() + '</p></div>' +
    '<div class="player-strip"><div class="player-level"><b>LV ' + level + '</b><span>' + xp.current + '/12 ★</span></div><div class="xp-track"><i style="--xp:' + xp.pct + '%"></i></div><div class="streak-pill"><b>🔥 ' + streak + '</b><span>STREAK</span></div></div>' +
    '<div class="week-strip">' + weeklyStreakMarkup() + '</div>' +
    levelSelector() +
    '<div class="preview"><img fetchpriority="high" decoding="async" src="' + puzzleSrc(featured.id) + '" alt="' + featured.title + '">' + previewGrid() + '<span class="preview-chip">' + state.size + '×' + state.size + '</span></div>' +
    '<div class="daily-meta"><span>DAILY #' + dailyNumber() + '</span><span>' + (dailyDone ? '✓ COMPLETED' : '+2 ★ REWARD') + '</span></div>' +
    '<button class="action red play sticky-daily ' + (dailyDone ? 'daily-done' : '') + '" data-action="daily">' + (dailyDone ? '↻ REPLAY DAILY' : '▶ PLAY DAILY PICK') + '</button>' +
    '<div class="home-actions">' +
      '<button class="action blue" data-action="collection">▦<span>COLLECTIONS</span></button>' +
      '<button class="action green" data-action="info">?<span>HOW TO PLAY</span></button>' +
    '</div>' +
    '<div class="home-secondary single"><button class="action salmon" data-action="help">★ LEARN THE 4×4</button></div>' +
  '</section>');
}'''
s, n = re.subn(r"function renderHome\(\) \{.*?\n\}", home, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'home replace failed {n}')

s = re.sub(r"  function collectionProgress\(collectionId\) \{.*?\n  \}", r'''  function collectionProgress(collectionId) {
    const stats = collectionStats(collectionId);
    return stats.solved + '/' + stats.total + ' solved · ' + stats.stars + '/' + stats.maxStars + ' ★' + (stats.solved === stats.total && stats.total ? ' · COMPLETE!' : '');
  }''', s, count=1, flags=re.S)

s = s.replace(
"'<div class=\"card-art\"><img loading=\"lazy\" decoding=\"async\" fetchpriority=\"low\" width=\"192\" height=\"192\" src=\"' + thumbSrc(p.id) + '\" alt=\"' + p.title + '\"><span class=\"card-chip\">' + collectionLabel + '</span><span class=\"grid-chip\">' + state.size + '×' + state.size + '</span></div>' +",
"'<div class=\"card-art\"><img loading=\"lazy\" decoding=\"async\" fetchpriority=\"low\" width=\"192\" height=\"192\" src=\"' + thumbSrc(p.id) + '\" alt=\"' + p.title + '\"><span class=\"card-chip\">' + collectionLabel + '</span><span class=\"grid-chip\">' + state.size + '×' + state.size + '</span>' + (record ? '<span class=\"solved-chip\">✓</span>' : '') + '</div>' +"
)
s = s.replace("(record ? record.moves + ' moves' : 'NEW')", "(record ? 'SOLVED · ' + record.moves : 'NEW TALE')")

collection_screen = r'''function renderCollection() {
  const stats = collectionStats(state.filter);
  const pct = stats.total ? Math.round((stats.solved / stats.total) * 100) : 0;
  return shell('<section class="screen collection-screen mockup-collection retention-collection">' +
    '<div class="collection-hero">' +
      '<button class="back collection-back" data-action="home" aria-label="Back">←</button>' +
      '<div class="collection-paper"><h1>COLLECTIONS</h1><p>PICK A THEME.</p></div>' +
      '<div class="collection-callout">COLLECT<br>SOLVE<br>DISCOVER<br><b>NEW WORLDS!</b></div>' +
    '</div>' +
    levelSelector() + '<div class="collection-tabs">' + collectionTabsMarkup() + '</div>' +
    '<div class="collection-summary retention-summary"><b>' + state.size + '×' + state.size + ' COLLECTION</b><span>' + collectionProgress(state.filter) + '</span></div>' +
    '<div class="collection-meter"><i style="--collection:' + pct + '%"></i></div>' +
    (stats.solved === stats.total && stats.total ? '<div class="collection-complete">★ COLLECTION COMPLETE ★</div>' : '') +
    '<div class="cards">' + collectionCardsMarkup() + '</div>' +
  '</section>');
}'''
s, n = re.subn(r"function renderCollection\(\) \{.*?\n\}", collection_screen, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'collection screen replace failed {n}')

s = s.replace(
"    summary.textContent = collectionProgress(state.filter);",
"    summary.textContent = collectionProgress(state.filter);\n    const meter = document.querySelector('.collection-meter i');\n    const stats = collectionStats(state.filter);\n    if (meter) meter.style.setProperty('--collection', (stats.total ? Math.round((stats.solved / stats.total) * 100) : 0) + '%');"
)

win_overlay = r'''    if (state.won) {
      const result = state.lastResult || { stars: resultStars(state.size, state.moves), improved: false, firstEverSolve: false, dailyBonus: 0, levelUp: false, streak: dailyStreak() };
      const next = nextPuzzle();
      const badges = [
        result.firstEverSolve ? '<span class="result-badge new">NEW TALE!</span>' : '',
        result.improved && !result.firstEverSolve ? '<span class="result-badge record">NEW RECORD!</span>' : '',
        result.levelUp ? '<span class="result-badge level">LEVEL UP!</span>' : '',
        result.collectionComplete ? '<span class="result-badge collection">COLLECTION COMPLETE!</span>' : '',
        result.dailyBonus ? '<span class="result-badge daily">DAILY +' + result.dailyBonus + ' ★</span>' : '',
      ].join('');
      const confetti = Array.from({ length: 18 }, (_, i) => '<i style="--i:' + i + '"></i>').join('');
      return '<div class="overlay win-overlay"><div class="confetti" aria-hidden="true">' + confetti + '</div>' +
        '<div class="win-kicker">' + (result.firstEverSolve ? 'NEW TALE!' : 'SOLVED!') + '</div>' +
        '<div class="win-cover"><img src="' + puzzleSrc(state.current.id) + '" alt="' + state.current.title + '"></div>' +
        '<h2>' + state.current.title + '</h2><div class="win-stars">' + starMarkup(result.stars) + '</div>' +
        '<div class="win-stats"><span><b>' + state.moves + '</b>MOVES</span><span><b>' + formatTime(state.seconds) + '</b>TIME</span><span><b>LV ' + playerLevel() + '</b>PLAYER</span></div>' +
        '<div class="result-badges">' + badges + '</div>' +
        (state.isDaily ? '<div class="streak-result">🔥 ' + result.streak + ' DAY STREAK</div>' : '') +
        '<button class="next-tale" data-action="next" data-id="' + next.id + '"><img src="' + thumbSrc(next.id) + '" alt=""><span><small>UP NEXT</small><b>' + next.title + '</b></span><strong>›</strong></button>' +
        '<div class="overlay-actions win-actions"><button class="action red" data-action="next" data-id="' + next.id + '">NEXT PUZZLE</button><button class="action blue" data-action="collection">COLLECTION</button><button class="action cream" data-action="replay">REPLAY</button></div></div>';
    }'''
s, n = re.subn(r"    if \(state\.won\) \{.*?\n    \}", win_overlay, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'win overlay failed {n}')

game = r'''  function renderGame() {
    const record = state.records[recordKey(state.current.id, state.size)];
    return shell('<section class="screen game-screen mockup-game retention-game">' +
      '<div class="game-head mockup-game-head"><button class="back game-back" data-action="collection">←</button><div class="mini"><span>MOVES</span><b>' + state.moves + '</b></div><div class="mini"><span>TIME</span><b id="time">' + formatTime(state.seconds) + '</b></div><button class="back game-pause" data-action="pause">Ⅱ</button></div>' +
      '<div class="now-playing"><strong>' + state.current.title + '</strong><span>' + state.current.category.toUpperCase() + ' · ' + state.size + '×' + state.size + '</span></div>' +
      '<div class="challenge-strip"><span>' + (state.isDaily ? 'DAILY #' + dailyNumber() + ' · +2 ★' : 'STAR TARGET') + '</span><b>' + targetMarkup() + '</b></div>' +
      '<div class="board-frame"><div class="board" style="--n:' + state.size + '">' + state.board.map(tileMarkup).join('') + '</div>' + gameOverlay() + '</div>' +
      '<div class="controls mockup-controls"><button class="control blue" data-action="shuffle"><b>↝</b><span>SHUFFLE</span></button><button class="control green" data-action="hint"><b>✦</b><span>HINT</span></button><button class="control red" data-action="reset"><b>↻</b><span>RESET</span></button></div>' +
      '<div class="guide-row"><button class="guide-quick" data-action="guide">☰ QUICK GUIDE</button>' + (state.size === 4 ? '<button class="game-help" data-action="help">FULL 4×4 GUIDE</button>' : '') + '</div>' +
      '<div class="progress mockup-progress"><span>' + starMarkup(record?.stars || 0) + '</span><b>' + (record ? 'BEST ' + record.moves + ' MOVES · ' + formatTime(record.seconds) : 'BEAT THE TARGET · EARN 3 ★') + '</b></div>' +
    '</section>');
  }'''
s, n = re.subn(r"  function renderGame\(\) \{.*?\n  \}", game, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'game replace failed {n}')

start_round = r'''  function startRound(puzzle, size = state.size, isDaily = false) {
    const board = shuffledBoard(size);
    state.size = size;
    state.current = puzzle;
    state.board = board.slice();
    state.initial = board.slice();
    state.moves = 0;
    state.seconds = 0;
    state.running = false;
    state.paused = false;
    state.hint = false;
    state.guide = false;
    state.won = false;
    state.isDaily = Boolean(isDaily);
    state.lastResult = null;
    state.screen = 'game';
    savePrefs();
    preloadImage(thumbSrc(puzzle.id), 'high');
    render();
    preloadPuzzle(puzzle.id).then(() => {
      if (state.screen === 'game' && state.current.id === puzzle.id) upgradeBoardImage(puzzle.id);
    });
  }'''
s, n = re.subn(r"  function startRound\(puzzle, size = state\.size\) \{.*?\n  \}\n\n  function resetRound", start_round + "\n\n  function resetRound", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'start round replace failed {n}')

s = s.replace(
"    state.won = false;\n    render();\n  }\n\n  function preloadImage",
"    state.won = false;\n    state.lastResult = null;\n    render();\n  }\n\n  function preloadImage"
)

old_solve = '''    if (isSolved(next, size)) {
      state.won = true;
      state.running = false;
      saveRecord();
      haptic(55);
    }'''
new_solve = '''    if (isSolved(next, size)) {
      const beforeTotal = totalStars();
      const beforeLevel = playerLevel(beforeTotal);
      const beforeCollection = collectionStats(state.current.collection, state.size);
      const result = saveRecord();
      let dailyBonus = 0;
      if (state.isDaily && !dailyDoneToday()) {
        state.profile.dailySolved[dateKey(0)] = state.current.id;
        state.profile.bonusStars = Number(state.profile.bonusStars || 0) + 2;
        dailyBonus = 2;
        saveProfile();
      }
      const afterTotal = totalStars();
      const afterCollection = collectionStats(state.current.collection, state.size);
      state.lastResult = {
        ...result,
        dailyBonus,
        streak: dailyStreak(),
        levelUp: playerLevel(afterTotal) > beforeLevel,
        collectionComplete: beforeCollection.solved < beforeCollection.total && afterCollection.solved === afterCollection.total,
      };
      state.won = true;
      state.running = false;
      try { if (navigator.vibrate) navigator.vibrate([25, 35, 55]); else haptic(55); } catch (_) { haptic(55); }
    }'''
if old_solve not in s:
    raise SystemExit('solve block not found')
s = s.replace(old_solve, new_solve, 1)

s = s.replace("    if (action === 'daily') { startRound(dailyPuzzle()); return; }", "    if (action === 'daily') { startRound(dailyPuzzle(), state.size, true); return; }")
s = s.replace("    if (action === 'shuffle') { startRound(state.current); return; }", "    if (action === 'shuffle') { startRound(state.current, state.size, state.isDaily); return; }")
s = s.replace("    if (action === 'replay') { startRound(state.current); return; }", "    if (action === 'replay') { startRound(state.current, state.size, state.isDaily); return; }")
s = s.replace(
"    if (action === 'hint') { showHint(); return; }",
"    if (action === 'next') { const puzzle = PUZZLES.find(p => p.id === element.dataset.id) || nextPuzzle(); state.filter = puzzle.collection; savePrefs(); startRound(puzzle, state.size, false); return; }\n    if (action === 'hint') { showHint(); return; }"
)
s = s.replace("      startRound(puzzle); return;", "      startRound(puzzle, state.size, false); return;", 1)

app.write_text(s)
