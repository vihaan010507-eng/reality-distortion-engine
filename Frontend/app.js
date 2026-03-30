// frontend/app.js

const API_URL = 'http://localhost:5000';

// Update character count live
document.getElementById('news-input').addEventListener('input', function () {
  const count = this.value.length;
  document.getElementById('char-count').textContent = `${count} character${count !== 1 ? 's' : ''}`;
});

async function analyzeText() {
  const input = document.getElementById('news-input');
  const text = input.value.trim();

  // Basic client-side validation
  if (text.length < 15) {
    showError('Please enter at least one complete sentence.');
    return;
  }

  // UI state: show loading
  setLoading(true);
  hideAll();

  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || 'Server error. Please try again.');
      return;
    }

    displayResult(data);

  } catch (err) {
    showError('Could not reach the server. Make sure Flask is running on port 5000.');
    console.error(err);
  } finally {
    setLoading(false);
  }
}

function displayResult(data) {
  const section = document.getElementById('result-section');
  const banner  = document.getElementById('verdict-banner');
  const label   = document.getElementById('verdict-label');
  const conf    = document.getElementById('verdict-confidence');

  // Set label and banner color
  const labelMap = { Fake: 'fake', Real: 'real', Misleading: 'misleading' };
  banner.className = `verdict-banner ${labelMap[data.label] || 'fake'}`;
  label.textContent = data.label.toUpperCase();
  conf.textContent  = `${data.confidence}% confidence`;

  // Animate score bars (use setTimeout so the element is visible first)
  section.classList.remove('hidden');
  setTimeout(() => {
    animateBar('ml-bar',   'ml-pct',   data.ml_score);
    animateBar('rule-bar', 'rule-pct', data.rule_score);
  }, 50);

  // Flags
  const flagsSection = document.getElementById('flags-section');
  const flagsList    = document.getElementById('flags-list');
  flagsList.innerHTML = '';

  if (data.rule_flags && data.rule_flags.length > 0) {
    flagsSection.classList.remove('hidden');
    data.rule_flags.forEach(flag => {
      const li = document.createElement('li');
      li.textContent = flag;
      flagsList.appendChild(li);
    });
  }

  // Explanation
  document.getElementById('explanation-text').textContent = data.explanation;
}

function animateBar(barId, pctId, value) {
  document.getElementById(barId).style.width = `${value}%`;
  document.getElementById(pctId).textContent  = `${value}%`;
}

function showError(message) {
  const section = document.getElementById('error-section');
  document.getElementById('error-text').textContent = message;
  section.classList.remove('hidden');
}

function resetForm() {
  document.getElementById('news-input').value = '';
  document.getElementById('char-count').textContent = '0 characters';
  hideAll();
}

function hideAll() {
  ['result-section', 'error-section', 'loading'].forEach(id => {
    document.getElementById(id).classList.add('hidden');
  });
}

function setLoading(show) {
  const btn  = document.getElementById('analyze-btn');
  const load = document.getElementById('loading');
  btn.disabled = show;
  show ? load.classList.remove('hidden') : load.classList.add('hidden');
}