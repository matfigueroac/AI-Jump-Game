from pathlib import Path
import re

app = Path('web/app.js')
s = app.read_text()

header = '''  function header() {
    return '<header class="topbar mockup-topbar">' +
      '<button class="icon-btn mockup-help" data-action="info" aria-label="How to play"><span>?</span></button>' +
      '<div class="brand-lockup mockup-brand"><div class="brand-burst" aria-hidden="true"></div><div class="mockup-logo-text" aria-label="Retro Slide Tales"><span class="mockup-retro">RETRO</span><span class="mockup-slide">SLIDE TALES</span></div></div>' +
      '<div class="mockup-score" aria-label="Total stars"><span>★</span><b>' + totalStars() + '</b></div>' +
    '</header>';
  }'''
s, n = re.subn(r"  function header\(\) \{.*?\n  \}", header, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'header replace failed: {n}')

collection = '''function renderCollection() {
  return shell('<section class="screen collection-screen mockup-collection">' +
    '<div class="collection-hero">' +
      '<button class="back collection-back" data-action="home" aria-label="Back">←</button>' +
      '<div class="collection-paper"><h1>COLLECTIONS</h1><p>PICK A THEME.</p></div>' +
      '<div class="collection-callout">COLLECT<br>SOLVE<br>DISCOVER<br><b>NEW WORLDS!</b></div>' +
    '</div>' +
    levelSelector() + '<div class="collection-tabs">' + collectionTabsMarkup() + '</div>' +
    '<div class="collection-summary"><b>' + state.size + '×' + state.size + ' COLLECTION</b><span>' + collectionProgress(state.filter) + '</span></div>' +
    '<div class="cards">' + collectionCardsMarkup() + '</div>' +
  '</section>');
}'''
s, n = re.subn(r"function renderCollection\(\) \{.*?\n\}", collection, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'collection replace failed: {n}')

game = '''  function renderGame() {
    const record = state.records[recordKey(state.current.id, state.size)];
    return shell('<section class="screen game-screen mockup-game">' +
      '<div class="game-head mockup-game-head"><button class="back game-back" data-action="collection">←</button><div class="mini"><span>MOVES</span><b>' + state.moves + '</b></div><div class="mini"><span>TIME</span><b id="time">' + formatTime(state.seconds) + '</b></div><button class="back game-pause" data-action="pause">Ⅱ</button></div>' +
      '<div class="now-playing"><strong>' + state.current.title + '</strong><span>' + state.current.category.toUpperCase() + ' · ' + state.size + '×' + state.size + '</span></div>' +
      '<div class="board-frame"><div class="board" style="--n:' + state.size + '">' + state.board.map(tileMarkup).join('') + '</div>' + gameOverlay() + '</div>' +
      '<div class="controls mockup-controls"><button class="control blue" data-action="shuffle"><b>↝</b><span>SHUFFLE</span></button><button class="control green" data-action="hint"><b>✦</b><span>HINT</span></button><button class="control red" data-action="reset"><b>↻</b><span>RESET</span></button></div>' +
      '<div class="guide-row"><button class="guide-quick" data-action="guide">☰ QUICK GUIDE</button>' + (state.size === 4 ? '<button class="game-help" data-action="help">FULL 4×4 GUIDE</button>' : '') + '</div>' +
      '<div class="progress mockup-progress"><span>' + starMarkup(record?.stars || 0) + '</span><b>' + (record ? 'BEST ' + record.moves + ' MOVES · ' + formatTime(record.seconds) : 'SOLVE & COLLECT ALL PUZZLES!') + '</b></div>' +
    '</section>');
  }'''
s, n = re.subn(r"  function renderGame\(\) \{.*?\n  \}", game, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'game replace failed: {n}')

app.write_text(s)
