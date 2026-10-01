from pathlib import Path
import re

app = Path('web/app.js')
s = app.read_text()

old_profile = "    profile: { bonusStars: Number(savedProfile.bonusStars || 0), dailySolved: savedProfile.dailySolved || {} },"
new_profile = "    profileReturn: 'home',\n    profile: { bonusStars: Number(savedProfile.bonusStars || 0), dailySolved: savedProfile.dailySolved || {}, dayStats: savedProfile.dayStats || {}, questClaims: savedProfile.questClaims || {}, soundEnabled: savedProfile.soundEnabled !== false, lastPlayed: savedProfile.lastPlayed || null },"
if old_profile not in s:
    raise SystemExit('v11 profile state not found')
s = s.replace(old_profile, new_profile, 1)

helpers = r'''
  function todayStats() {
    const key = dateKey(0);
    if (!state.profile.dayStats[key]) state.profile.dayStats[key] = { solves: 0, threeStars: 0 };
    return state.profile.dayStats[key];
  }

  function uniqueSolvedCount() {
    return PUZZLES.filter(p => state.records[recordKey(p.id, 3)] || state.records[recordKey(p.id, 4)]).length;
  }

  function threeStarRecordCount() {
    return Object.values(state.records).filter(record => Number(record.stars || 0) >= 3).length;
  }

  function completedCollectionsCount() {
    return COLLECTIONS.filter(c => c.id !== 'all').filter(c => {
      const list = PUZZLES.filter(p => p.collection === c.id);
      return list.length && list.every(p => state.records[recordKey(p.id, 3)] || state.records[recordKey(p.id, 4)]);
    }).length;
  }

  function continuePuzzle() {
    const solved = p => Boolean(state.records[recordKey(p.id, state.size)]);
    const lastIndex = Math.max(-1, PUZZLES.findIndex(p => p.id === state.profile.lastPlayed));
    for (let step = 1; step <= PUZZLES.length; step += 1) {
      const candidate = PUZZLES[(lastIndex + step + PUZZLES.length) % PUZZLES.length];
      if (!solved(candidate)) return candidate;
    }
    return PUZZLES[(lastIndex + 1 + PUZZLES.length) % PUZZLES.length] || PUZZLES[0];
  }

  function questState() {
    const stats = todayStats();
    return [
      { id: 'daily', label: 'DAILY PICK', reward: 2, done: dailyDoneToday() },
      { id: 'solve2', label: 'SOLVE 2', reward: 1, done: stats.solves >= 2, progress: Math.min(stats.solves, 2) + '/2' },
      { id: 'three', label: 'EARN 3★', reward: 1, done: stats.threeStars >= 1 },
    ];
  }

  function questMarkup() {
    return questState().map(q => '<span class="quest-chip ' + (q.done ? 'done' : '') + '"><i>' + (q.done ? '✓' : '○') + '</i><b>' + q.label + '</b><small>' + (q.progress || ('+' + q.reward + '★')) + '</small></span>').join('');
  }

  function evaluateQuestRewards() {
    const key = dateKey(0);
    const claims = state.profile.questClaims[key] || {};
    const stats = todayStats();
    let reward = 0;
    if (stats.solves >= 2 && !claims.solve2) { claims.solve2 = true; reward += 1; }
    if (stats.threeStars >= 1 && !claims.three) { claims.three = true; reward += 1; }
    state.profile.questClaims[key] = claims;
    if (reward) state.profile.bonusStars = Number(state.profile.bonusStars || 0) + reward;
    return reward;
  }

  function achievements() {
    const solved = uniqueSolvedCount();
    const stars = totalStars();
    const streak = dailyStreak();
    const complete = completedCollectionsCount();
    const perfect = threeStarRecordCount();
    return [
      { icon: '★', name: 'FIRST TALE', text: 'Solve your first puzzle', done: solved >= 1 },
      { icon: '10', name: 'STORY HUNTER', text: 'Solve 10 different tales', done: solved >= 10 },
      { icon: '30', name: 'STAR COLLECTOR', text: 'Collect 30 stars', done: stars >= 30 },
      { icon: '🔥', name: 'DAILY HERO', text: 'Reach a 7 day streak', done: streak >= 7 },
      { icon: '✓', name: 'WORLD COMPLETE', text: 'Finish a full collection', done: complete >= 1 },
      { icon: '3★', name: 'MASTER SLIDER', text: 'Earn ten 3-star records', done: perfect >= 10 },
    ];
  }

  function achievementMarkup() {
    return achievements().map(a => '<article class="achievement ' + (a.done ? 'unlocked' : 'locked') + '"><span>' + a.icon + '</span><div><b>' + a.name + '</b><small>' + a.text + '</small></div><i>' + (a.done ? '✓' : 'LOCKED') + '</i></article>').join('');
  }

  let audioContext = null;
  function uiSound(kind = 'tap') {
    if (!state.profile.soundEnabled) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    try {
      audioContext = audioContext || new Ctx();
      if (audioContext.state === 'suspended') audioContext.resume();
      const now = audioContext.currentTime;
      const gain = audioContext.createGain();
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(kind === 'win' ? 0.045 : 0.022, now + 0.008);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + (kind === 'win' ? 0.32 : 0.10));
      gain.connect(audioContext.destination);
      const notes = kind === 'win' ? [523.25, 659.25, 783.99] : [kind === 'error' ? 165 : kind === 'slide' ? 330 : 440];
      notes.forEach((freq, idx) => {
        const osc = audioContext.createOscillator();
        osc.type = kind === 'error' ? 'square' : 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.065);
        osc.connect(gain);
        osc.start(now + idx * 0.065);
        osc.stop(now + idx * 0.065 + (kind === 'win' ? 0.16 : 0.085));
      });
    } catch (_) {}
  }
'''
anchor = "  function weeklyStreakMarkup() {"
if anchor not in s:
    raise SystemExit('weekly streak anchor missing')
s = s.replace(anchor, helpers + "\n" + anchor, 1)

old_header = """  function header() {
    return '<header class="topbar mockup-topbar">' +
      '<button class="icon-btn mockup-help" data-action="info" aria-label="How to play"><span>?</span></button>' +
      '<div class="brand-lockup mockup-brand"><div class="brand-burst" aria-hidden="true"></div><div class="mockup-logo-text" aria-label="Retro Slide Tales"><span class="mockup-retro">RETRO</span><span class="mockup-slide">SLIDE TALES</span></div></div>' +
      '<div class="mockup-score" aria-label="Total stars"><span>★</span><b>' + totalStars() + '</b></div>' +
    '</header>';
  }"""
new_header = """  function header() {
    return '<header class="topbar mockup-topbar">' +
      '<button class="icon-btn mockup-help" data-action="info" aria-label="How to play"><span>?</span></button>' +
      '<div class="brand-lockup mockup-brand"><div class="brand-burst" aria-hidden="true"></div><div class="mockup-logo-text" aria-label="Retro Slide Tales"><span class="mockup-retro">RETRO</span><span class="mockup-slide">SLIDE TALES</span></div></div>' +
      '<button class="mockup-score profile-trigger" data-action="profile" aria-label="Open player profile"><span>★</span><b>' + totalStars() + '</b></button>' +
    '</header>';
  }"""
if old_header not in s:
    raise SystemExit('v11 header not found')
s = s.replace(old_header, new_header, 1)

home = r'''function renderHome() {
  const featured = dailyPuzzle();
  const level = playerLevel();
  const xp = levelProgress();
  const streak = dailyStreak();
  const dailyDone = dailyDoneToday();
  const cont = continuePuzzle();
  const quests = questState();
  const questDone = quests.filter(q => q.done).length;
  return shell('<section class="screen home-screen retention-home v12-home">' +
    '<div class="hero-lockup"><p class="hero-copy">PICK · SLIDE · SOLVE</p><p class="hero-sub"><span class="daily-dot">●</span> TODAY · ' + featured.title.toUpperCase() + '</p></div>' +
    '<div class="player-strip"><button class="player-level" data-action="profile"><b>LV ' + level + '</b><span>' + xp.current + '/12 ★</span></button><div class="xp-track"><i style="--xp:' + xp.pct + '%"></i></div><div class="streak-pill"><b>🔥 ' + streak + '</b><span>STREAK</span></div></div>' +
    '<div class="week-strip">' + weeklyStreakMarkup() + '</div>' +
    '<div class="quest-panel"><div class="quest-title"><b>TODAY\\'S GOALS</b><span>' + questDone + '/3</span></div><div class="quest-row">' + questMarkup() + '</div></div>' +
    levelSelector() +
    '<div class="preview"><img fetchpriority="high" decoding="async" src="' + puzzleSrc(featured.id) + '" alt="' + featured.title + '">' + previewGrid() + '<span class="preview-chip">' + state.size + '×' + state.size + '</span></div>' +
    '<div class="daily-meta"><span>DAILY #' + dailyNumber() + '</span><span>' + (dailyDone ? '✓ COMPLETED' : '+2 ★ REWARD') + '</span></div>' +
    '<button class="action red play sticky-daily ' + (dailyDone ? 'daily-done' : '') + '" data-action="daily">' + (dailyDone ? '↻ REPLAY DAILY' : '▶ PLAY DAILY PICK') + '</button>' +
    '<button class="continue-tale" data-action="continue" data-id="' + cont.id + '"><img src="' + thumbSrc(cont.id) + '" alt=""><span><small>CONTINUE JOURNEY</small><b>' + cont.title + '</b><em>' + cont.category.toUpperCase() + ' · ' + state.size + '×' + state.size + '</em></span><strong>›</strong></button>' +
    '<div class="home-actions">' +
      '<button class="action blue" data-action="collection">▦<span>COLLECTIONS</span></button>' +
      '<button class="action green" data-action="info">?<span>HOW TO PLAY</span></button>' +
    '</div>' +
    '<div class="home-secondary single"><button class="action salmon" data-action="help">★ LEARN THE 4×4</button></div>' +
  '</section>');
}'''
s, n = re.subn(r"function renderHome\(\) \{.*?\n\}", home, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'v12 home replace failed {n}')

profile_render = r'''
  function renderProfile() {
    const solved = uniqueSolvedCount();
    const total = totalStars();
    const streak = dailyStreak();
    const complete = completedCollectionsCount();
    const xp = levelProgress();
    const quests = questState();
    return shell('<section class="screen profile-screen">' +
      '<div class="profile-hero"><button class="back" data-action="back-profile">←</button><div><small>PLAYER CARD</small><h1>SLIDE HERO</h1><p>Level ' + playerLevel(total) + ' · ' + total + ' stars</p></div><button class="sound-toggle ' + (state.profile.soundEnabled ? 'on' : 'off') + '" data-action="toggle-sound"><b>' + (state.profile.soundEnabled ? '♪' : '×') + '</b><span>SOUND</span></button></div>' +
      '<div class="profile-level"><div><b>LV ' + playerLevel(total) + '</b><span>' + xp.current + '/12 ★ TO NEXT</span></div><div class="xp-track big"><i style="--xp:' + xp.pct + '%"></i></div></div>' +
      '<div class="profile-stats"><article><b>' + solved + '</b><span>TALES</span></article><article><b>' + total + '</b><span>STARS</span></article><article><b>🔥 ' + streak + '</b><span>STREAK</span></article><article><b>' + complete + '</b><span>WORLDS</span></article></div>' +
      '<div class="profile-section"><div class="section-title"><b>TODAY\\'S GOALS</b><span>' + quests.filter(q => q.done).length + '/3</span></div><div class="quest-row profile-quests">' + questMarkup() + '</div></div>' +
      '<div class="profile-section"><div class="section-title"><b>BADGES</b><span>' + achievements().filter(a => a.done).length + '/6</span></div><div class="achievements">' + achievementMarkup() + '</div></div>' +
      '<button class="action red profile-play" data-action="continue" data-id="' + continuePuzzle().id + '">▶ CONTINUE JOURNEY</button>' +
    '</section>');
  }
'''
render_anchor = "  function render() {"
if render_anchor not in s:
    raise SystemExit('render anchor missing')
s = s.replace(render_anchor, profile_render + "\n" + render_anchor, 1)

old_render = """  function render() {
  if (state.screen === 'home') app.innerHTML = renderHome();
  else if (state.screen === 'collection') app.innerHTML = renderCollection();
  else if (state.screen === 'game') app.innerHTML = renderGame();
  else if (state.screen === 'help') app.innerHTML = renderHelp();
  else app.innerHTML = renderInfo();
}"""
new_render = """  function render() {
  if (state.screen === 'home') app.innerHTML = renderHome();
  else if (state.screen === 'collection') app.innerHTML = renderCollection();
  else if (state.screen === 'game') app.innerHTML = renderGame();
  else if (state.screen === 'help') app.innerHTML = renderHelp();
  else if (state.screen === 'profile') app.innerHTML = renderProfile();
  else app.innerHTML = renderInfo();
}"""
if old_render not in s:
    raise SystemExit('render function exact block missing')
s = s.replace(old_render, new_render, 1)

s = s.replace(
"    state.lastResult = null;\n    state.screen = 'game';\n    savePrefs();",
"    state.lastResult = null;\n    state.screen = 'game';\n    state.profile.lastPlayed = puzzle.id;\n    saveProfile();\n    savePrefs();",
1
)

old_after_record = """      const afterTotal = totalStars();
      const afterCollection = collectionStats(state.current.collection, state.size);
      state.lastResult = {
        ...result,
        dailyBonus,
        streak: dailyStreak(),
        levelUp: playerLevel(afterTotal) > beforeLevel,
        collectionComplete: beforeCollection.solved < beforeCollection.total && afterCollection.solved === afterCollection.total,
      };"""
new_after_record = """      const statsToday = todayStats();
      statsToday.solves = Number(statsToday.solves || 0) + 1;
      if (result.stars >= 3) statsToday.threeStars = Number(statsToday.threeStars || 0) + 1;
      const questBonus = evaluateQuestRewards();
      saveProfile();
      const afterTotal = totalStars();
      const afterCollection = collectionStats(state.current.collection, state.size);
      state.lastResult = {
        ...result,
        dailyBonus,
        questBonus,
        streak: dailyStreak(),
        levelUp: playerLevel(afterTotal) > beforeLevel,
        collectionComplete: beforeCollection.solved < beforeCollection.total && afterCollection.solved === afterCollection.total,
      };"""
if old_after_record not in s:
    raise SystemExit('solve result block missing')
s = s.replace(old_after_record, new_after_record, 1)

s = s.replace(
"        result.dailyBonus ? '<span class=\"result-badge daily\">DAILY +' + result.dailyBonus + ' ★</span>' : '',",
"        result.dailyBonus ? '<span class=\"result-badge daily\">DAILY +' + result.dailyBonus + ' ★</span>' : '',\n        result.questBonus ? '<span class=\"result-badge quest\">GOALS +' + result.questBonus + ' ★</span>' : '',",
1
)

s = s.replace(
"    haptic(24);\n  }\n\n  function refreshGameBoard",
"    haptic(24);\n    uiSound('error');\n  }\n\n  function refreshGameBoard",
1
)
s = s.replace(
"    haptic(Math.min(20, 6 + moved * 3));\n\n    if (isSolved(next, size)) {",
"    haptic(Math.min(20, 6 + moved * 3));\n    uiSound('slide');\n\n    if (isSolved(next, size)) {",
1
)
s = s.replace(
"      try { if (navigator.vibrate) navigator.vibrate([25, 35, 55]); else haptic(55); } catch (_) { haptic(55); }\n    }",
"      try { if (navigator.vibrate) navigator.vibrate([25, 35, 55]); else haptic(55); } catch (_) { haptic(55); }\n      uiSound('win');\n    }",
1
)

handle_anchor = """    if (action === 'collection') {
      state.screen = 'collection'; state.paused = false; state.hint = false; state.guide = false; render(); return;
    }"""
handle_extra = handle_anchor + """
    if (action === 'profile') {
      state.profileReturn = state.screen === 'profile' ? 'home' : state.screen;
      state.screen = 'profile'; state.running = false; render(); return;
    }
    if (action === 'back-profile') {
      state.screen = state.profileReturn || 'home'; render(); return;
    }
    if (action === 'toggle-sound') {
      state.profile.soundEnabled = !state.profile.soundEnabled; saveProfile();
      if (state.profile.soundEnabled) uiSound('tap');
      render(); return;
    }
    if (action === 'continue') {
      const puzzle = PUZZLES.find(p => p.id === element.dataset.id) || continuePuzzle();
      state.filter = puzzle.collection; savePrefs(); startRound(puzzle, state.size, false); return;
    }"""
if handle_anchor not in s:
    raise SystemExit('handle collection anchor missing')
s = s.replace(handle_anchor, handle_extra, 1)

old_click = """  document.addEventListener('click', event => {
    const target = event.target.closest('[data-action]');
    if (target) handle(target.dataset.action, target);
  });"""
new_click = """  document.addEventListener('click', event => {
    const target = event.target.closest('[data-action]');
    if (!target) return;
    if (target.dataset.action !== 'tile' && target.dataset.action !== 'toggle-sound') uiSound('tap');
    handle(target.dataset.action, target);
  });"""
if old_click not in s:
    raise SystemExit('click router missing')
s = s.replace(old_click, new_click, 1)

app.write_text(s)
