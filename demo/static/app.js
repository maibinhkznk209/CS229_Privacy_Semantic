// ==================== NAVIGATION ====================
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Update active button
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update active section
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(btn.dataset.section).classList.add('active');
    });
});

// ==================== API CALLS ====================
const API_BASE = '';

async function fetchAPI(endpoint) {
    try {
        const res = await fetch(`${API_BASE}/api${endpoint}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('API Error:', err);
        return null;
    }
}

// ==================== LOAD DATA ====================
async function loadSummary() {
    const data = await fetchAPI('/summary');
    if (data) {
        document.getElementById('stat-paragraph').textContent = data.paragraph_length.toLocaleString();
        document.getElementById('stat-annotations').textContent = data.annotations_count;
        document.getElementById('stat-accuracy').textContent = (data.mfs_accuracy * 100).toFixed(2) + '%';
        document.getElementById('stat-kb').textContent = data.kb_facts;
        document.getElementById('stat-augment').textContent = data.kb_augmented_facts;
    }
}

async function loadParagraph() {
    const data = await fetchAPI('/paragraph');
    if (data && data.paragraph) {
        document.getElementById('paragraph-box').textContent = data.paragraph;
    }
}

async function loadWSDResults() {
    const data = await fetchAPI('/wsd/results');
    if (data) {
        const tbody = document.getElementById('wsd-table-body');
        const mfs = data.mfs.evaluation;
        const bert = data.bert.evaluation;

        tbody.innerHTML = `
            <tr>
                <td><strong>MFS Baseline</strong></td>
                <td><span style="color: var(--success)">${(mfs.accuracy * 100).toFixed(2)}%</span></td>
                <td>${mfs.correct}/${mfs.total}</td>
                <td>WordNet First Synset (Zero-shot)</td>
            </tr>
            <tr>
                <td><strong>BERT + SVM</strong></td>
                <td><span style="color: var(--secondary)">${bert.accuracy ? (bert.accuracy * 100).toFixed(2) + '%' : 'Chưa chạy'}</span></td>
                <td>${bert.correct || '-'}/${bert.total || '-'}</td>
                <td>SemCor Training + SVM Classifier</td>
            </tr>
        `;
    }
}

async function loadAnnotations() {
    const data = await fetchAPI('/annotations');
    if (data && data.annotations) {
        const tbody = document.getElementById('annotations-body');
        tbody.innerHTML = data.annotations.map(ann => `
            <tr>
                <td><strong>${ann.lemma}</strong></td>
                <td><code>${ann.pos}</code></td>
                <td><code>${ann.synset}</code></td>
                <td>${ann.fol_predicate || ann.lemma}</td>
            </tr>
        `).join('');
    }
}

async function loadKB() {
    const data = await fetchAPI('/kb');
    if (data) {
        document.getElementById('kb-facts').textContent = data.kb.join('\n');
        document.getElementById('fol-content').innerHTML = data.fol.replace(/\n/g, '<br>');
    }
}

async function loadQueries() {
    const data = await fetchAPI('/queries');
    if (data && data.queries) {
        const list = document.getElementById('queries-list');
        list.innerHTML = data.queries.map(q => `
            <div class="query-card" onclick="runPresetQuery('${q.prolog}')">
                <span class="query-id">${q.id}</span>
                <div class="query-text">${q.question}</div>
                <div class="query-prolog">${q.prolog}</div>
            </div>
        `).join('');
    }
}

async function loadAugmentation() {
    const data = await fetchAPI('/augmentation');
    if (data) {
        document.getElementById('aug-synonyms').textContent = data.total_synonyms;
        document.getElementById('aug-isa').textContent = data.total_is_a;
        document.getElementById('synonyms-list').textContent = data.synonyms.join('\n');
        document.getElementById('isa-list').textContent = data.is_a.join('\n');
    }
}

// ==================== WORD LOOKUP ====================
async function lookupWord() {
    const word = document.getElementById('wsd-word').value.trim();
    const pos = document.getElementById('wsd-pos').value;
    const result = document.getElementById('wsd-result');

    if (!word) {
        result.innerHTML = '<p style="color: var(--text-muted)">Vui lòng nhập từ cần tra cứu</p>';
        return;
    }

    result.innerHTML = '<p>Đang tra cứu...</p>';

    const data = await fetch(`${API_BASE}/api/wsd/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word, pos })
    }).then(r => r.json()).catch(() => null);

    if (!data || data.senses.length === 0) {
        result.innerHTML = `<p style="color: var(--danger)">Không tìm thấy nghĩa cho từ "${word}"</p>`;
        return;
    }

    result.innerHTML = `
        <p style="margin-bottom: 1rem">
            <strong>${data.total_senses}</strong> nghĩa được tìm thấy cho <strong>"${word}"</strong> (${pos})
        </p>
        ${data.senses.map((s, i) => `
            <div class="sense-item ${i === 0 ? 'mfs' : ''}">
                <div class="sense-name">
                    ${i === 0 ? '✓ MFS: ' : ''}${s.name}
                </div>
                <div class="sense-def">${s.definition}</div>
                ${s.examples.length ? `<div class="sense-examples">"${s.examples[0]}"</div>` : ''}
            </div>
        `).join('')}
    `;
}

// ==================== QUERY EXECUTION ====================
async function executeQuery() {
    const query = document.getElementById('query-text').value.trim();
    const result = document.getElementById('query-result');

    if (!query) {
        result.innerHTML = '<p style="color: var(--text-muted)">Vui lòng nhập truy vấn</p>';
        return;
    }

    result.innerHTML = '<p>Đang truy vấn...</p>';

    const data = await fetch(`${API_BASE}/api/query/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    }).then(r => r.json()).catch(() => null);

    if (!data || data.count === 0) {
        result.innerHTML = `<p style="color: var(--accent)">Không tìm thấy kết quả cho "${query}"</p>`;
        return;
    }

    result.innerHTML = `
        <p style="margin-bottom: 1rem">Tìm thấy <strong>${data.count}</strong> kết quả:</p>
        ${data.results.map(r => `<div class="query-item">${r}</div>`).join('')}
    `;
}

function runPresetQuery(prolog) {
    // Extract key terms from prolog query
    const match = prolog.match(/(\w+)\(/);
    if (match) {
        document.getElementById('query-text').value = match[1];
        executeQuery();
    }
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    loadSummary();
    loadParagraph();
    loadWSDResults();
    loadAnnotations();
    loadKB();
    loadQueries();
    loadAugmentation();
});

// Enter key support
document.getElementById('wsd-word').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') lookupWord();
});

document.getElementById('query-text').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeQuery();
});
