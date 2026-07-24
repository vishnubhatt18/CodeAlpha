/* ── Element refs ── */
const sourceText   = document.getElementById('sourceText');
const targetText   = document.getElementById('targetText');
const sourceLang   = document.getElementById('sourceLang');
const targetLang   = document.getElementById('targetLang');
const translateBtn = document.getElementById('translateBtn');
const btnText      = document.getElementById('btnText');
const spinner      = document.getElementById('spinner');
const clearBtn     = document.getElementById('clearBtn');
const copyBtn      = document.getElementById('copyBtn');
const swapBtn      = document.getElementById('swapBtn');
const charCount    = document.getElementById('charCount');
const errorBanner  = document.getElementById('errorBanner');
const errorMsg     = document.getElementById('errorMsg');
const detectedBadge= document.getElementById('detectedBadge');
const sourceTtsBtn = document.getElementById('sourceTtsBtn');
const targetTtsBtn = document.getElementById('targetTtsBtn');
const chips        = document.querySelectorAll('.chip');

let currentTranslation = '';
let ttsUtterance       = null;

/* ── Character counter ── */
sourceText.addEventListener('input', () => {
  const len = sourceText.value.length;
  charCount.textContent = `${len} / 5000`;
  charCount.classList.toggle('warn', len > 4500);
});

/* ── Auto-translate on Ctrl+Enter ── */
sourceText.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    doTranslate();
  }
});

/* ── Translate button ── */
translateBtn.addEventListener('click', doTranslate);

async function doTranslate() {
  const text = sourceText.value.trim();
  if (!text) { showError('Please enter some text to translate.'); return; }

  setLoading(true);
  hideError();

  try {
    const res = await fetch('/translate', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        text,
        source: sourceLang.value,
        target: targetLang.value,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Translation failed');

    currentTranslation = data.translated;
    renderTranslation(data.translated);

    /* Detected language badge */
    if (data.detected_name && sourceLang.value === 'auto') {
      detectedBadge.textContent = `Detected: ${data.detected_name}`;
      detectedBadge.style.display = 'inline-block';
    } else {
      detectedBadge.style.display = 'none';
    }

    copyBtn.disabled      = false;
    targetTtsBtn.disabled = false;

  } catch (err) {
    showError(err.message);
    currentTranslation = '';
    copyBtn.disabled      = true;
    targetTtsBtn.disabled = true;
  } finally {
    setLoading(false);
  }
}

function renderTranslation(text) {
  targetText.classList.remove('loading');
  targetText.textContent = text;
}

/* ── Loading state ── */
function setLoading(active) {
  translateBtn.disabled = active;
  btnText.textContent   = active ? 'Translating…' : 'Translate';
  spinner.classList.toggle('active', active);
  if (active) {
    targetText.classList.add('loading');
    targetText.textContent = '';
  }
}

/* ── Error handling ── */
function showError(msg) {
  errorMsg.textContent    = msg;
  errorBanner.style.display = 'flex';
}
function hideError() {
  errorBanner.style.display = 'none';
}

/* ── Clear ── */
clearBtn.addEventListener('click', () => {
  sourceText.value          = '';
  charCount.textContent     = '0 / 5000';
  charCount.classList.remove('warn');
  currentTranslation        = '';
  targetText.innerHTML      = '<span class="placeholder-output">Translation will appear here…</span>';
  detectedBadge.style.display = 'none';
  copyBtn.disabled          = true;
  targetTtsBtn.disabled     = true;
  hideError();
  stopTts();
  sourceText.focus();
});

/* ── Copy ── */
copyBtn.addEventListener('click', async () => {
  if (!currentTranslation) return;
  try {
    await navigator.clipboard.writeText(currentTranslation);
    copyBtn.classList.add('copied');
    copyBtn.querySelector('svg').style.stroke = 'var(--success)';
    setTimeout(() => {
      copyBtn.classList.remove('copied');
      copyBtn.querySelector('svg').style.stroke = '';
    }, 2000);
  } catch {
    /* Fallback for older browsers */
    const ta = document.createElement('textarea');
    ta.value = currentTranslation;
    ta.style.position = 'fixed';
    ta.style.opacity  = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
});

/* ── Swap languages ── */
swapBtn.addEventListener('click', () => {
  const srcVal = sourceLang.value;
  const tgtVal = targetLang.value;

  /* Don't swap if source is "auto" */
  if (srcVal === 'auto') {
    sourceLang.value = tgtVal;
    targetLang.value = 'en';
  } else {
    sourceLang.value = tgtVal;
    targetLang.value = srcVal;
  }

  /* Swap text content too if there's a translation */
  if (currentTranslation) {
    sourceText.value   = currentTranslation;
    charCount.textContent = `${currentTranslation.length} / 5000`;
    currentTranslation = '';
    targetText.innerHTML = '<span class="placeholder-output">Translation will appear here…</span>';
    detectedBadge.style.display = 'none';
    copyBtn.disabled      = true;
    targetTtsBtn.disabled = true;
  }

  stopTts();
});

/* ── Text-to-Speech ── */
function stopTts() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}

function speak(text, langCode) {
  if (!window.speechSynthesis) {
    showError('Text-to-speech is not supported in your browser.');
    return;
  }
  stopTts();
  if (!text.trim()) return;

  ttsUtterance = new SpeechSynthesisUtterance(text);
  ttsUtterance.lang = langCode === 'auto' ? 'en' : langCode;
  ttsUtterance.rate = 0.95;
  window.speechSynthesis.speak(ttsUtterance);
}

sourceTtsBtn.addEventListener('click', () => {
  speak(sourceText.value, sourceLang.value);
});

targetTtsBtn.addEventListener('click', () => {
  speak(currentTranslation, targetLang.value);
});

/* ── Quick language chips ── */
chips.forEach(chip => {
  chip.addEventListener('click', () => {
    const lang = chip.dataset.lang;
    targetLang.value = lang;

    /* Highlight active chip */
    chips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');

    /* Auto-translate if there's already text */
    if (sourceText.value.trim()) doTranslate();
  });
});

/* Sync chip highlight with select change */
targetLang.addEventListener('change', () => {
  const val = targetLang.value;
  chips.forEach(c => {
    c.classList.toggle('active', c.dataset.lang === val);
  });
});

/* Set initial chip state */
(function initChips() {
  const val = targetLang.value;
  chips.forEach(c => {
    if (c.dataset.lang === val) c.classList.add('active');
  });
})();
