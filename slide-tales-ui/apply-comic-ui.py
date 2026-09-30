from pathlib import Path
import re

app = Path('web/app.js')
s = app.read_text()

header = r'''  function header() {
    return '<header class="topbar comic-topbar">' +
      '<button class="icon-btn comic-help" data-action="info" aria-label="How to play"><span>?</span></button>' +
      '<div class="brand-lockup">' +
        '<img class="brand-logo" src="./assets/ui/retro-slide-tales-logo.webp" alt="Retro Slide Tales" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'grid\'">' +
        '<div class="brand-fallback" aria-hidden="true"><span class="retro-word">RETRO</span><span class="slide-word">SLIDE TALES</span></div>' +
      '</div>' +
      '<div class="star-badge comic-score" aria-label="Total stars"><span class="score-star">★</span><b>' + totalStars() + '</b></div>' +
    '</header>';
  }'''

s, n = re.subn(r"  function header\(\) \{.*?\n\}", header, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'header replacement failed: {n}')

s = s.replace('<strong>3 x 3</strong>', '<strong>3 × 3</strong>')
s = s.replace('<strong>4 x 4</strong>', '<strong>4 × 4</strong>')
app.write_text(s)

sw = Path('web/sw.js')
if sw.exists():
    x = sw.read_text()
    x = re.sub(r"const SHELL_CACHE='[^']+';", "const SHELL_CACHE='slide-tales-shell-v7';", x, count=1)
    if "./assets/ui/retro-slide-tales-logo.webp" not in x:
        x = x.replace(
            "const SHELL=['./','./index.html','./styles.css','./app.js'];",
            "const SHELL=['./','./index.html','./styles.css','./app.js','./assets/ui/retro-slide-tales-logo.webp'];"
        )
    sw.write_text(x)
