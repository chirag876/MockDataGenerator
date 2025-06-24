const API_BASE_URL = 'http://localhost:8000';
let generatedData = null;
let currentConfig = {};

// Initialize the theme toggle button
// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        themeIcon.textContent = '☀️';
    } else {
        html.setAttribute('data-theme', 'light');
        themeIcon.textContent = '🌙';
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = html.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        html.setAttribute('data-theme', 'light');
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'dark');
    }
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    
    // Add click listener to theme toggle button
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
});

async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        return response.status === 200;
    } catch {
        return false;
    }
}

function formatXML(xml) {
    // Remove leading/trailing whitespace
    xml = xml.trim();
    // Add line breaks and indentation
    let formatted = "";
    const reg = /(>)(<)(\/*)/g;
    xml = xml.replace(reg, "$1\n$2$3");
    let pad = 0;
    xml.split("\n").forEach((node) => {
        let indent = 0;
        if (node.match(/^<\/\w/)) {
            // Closing tag
            if (pad !== 0) pad -= 1;
        } else if (node.match(/^<\w([^>]*[^/])?>.*$/)) {
            // Opening tag
            indent = 1;
        } else {
            indent = 0;
        }
        formatted += "  ".repeat(pad) + node + "\n";
        pad += indent;
    });
    return formatted.trim();
}

async function loadTopics() {
    try {
        const response = await fetch(`${API_BASE_URL}/topics`);
        if (response.ok) return await response.json();
        return [];
    } catch {
        return [];
    }
}

async function loadFormats() {
    try {
        const response = await fetch(`${API_BASE_URL}/formats`);
        if (response.ok) return (await response.json()).formats;
        return ['JSON', 'CSV', 'XML', 'YAML'];
    } catch {
        return ['JSON', 'CSV', 'XML', 'YAML'];
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => errorDiv.style.display = 'none', 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    setTimeout(() => successDiv.style.display = 'none', 5000);
}

async function generateData(topic, format, numRecords, customFields, seed) {
    const payload = {
        topic,
        format,
        num_records: numRecords,
        custom_fields: customFields,
        seed
    };
    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) return await response.json();
        showError(`Error: ${await response.text()}`);
        return null;
    } catch (e) {
        showError(`Connection error: ${e.message}`);
        return null;
    }
}

async function downloadData(topic, format, numRecords, customFields, seed) {
    const payload = {
        topic,
        format,
        num_records: numRecords,
        custom_fields: customFields,
        seed
    };
    try {
        const response = await fetch(`${API_BASE_URL}/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            const blob = await response.blob();
            const disposition = response.headers.get('Content-Disposition');
            const filename = disposition ? disposition.split('filename=')[1]?.replace(/"/g, '') || `data.${format.toLowerCase()}` : `data.${format.toLowerCase()}`;
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            showError(`Download error: ${await response.text()}`);
        }
    } catch (e) {
        showError(`Download error: ${e.message}`);
    }
}

function formatData(data, format) {
    if (format === 'JSON') {
        try {
            return JSON.stringify(JSON.parse(data), null, 2);
        } catch {
            return data;
        }
    } else if (format === 'XML') {
        try {
            return formatXML(data);
        } catch {
            return data;
        }
    } else if (format === 'YAML') {
        return data.replace(/^(-+)/gm, (match) => match.replace(/-/g, '  '));
    }
    return data;
}

function parseCSV(csv) {
    const result = Papa.parse(csv, {
        header: true,
        skipEmptyLines: true,
        trim: true,
        dynamicTyping: false
    });
    if (result.errors.length) {
        console.warn('CSV parsing errors:', result.errors);
        return { headers: [], rows: [] };
    }
    const headers = result.meta.fields || [];
    const rows = result.data.map(obj => headers.map(h => obj[h] || ''));
    return { headers, rows };
}



async function init() {
    initTheme();
    if (!(await checkApiHealth())) {
        showError('Backend API is not running! Start with: cd mock-data-generator && python main.py');
        return;
    }

    const topics = await loadTopics();
    const formats = await loadFormats();

    const topicSelect = document.getElementById('topic-select');
    topicSelect.innerHTML = topics.map(t => `<option value="${t.name}">${t.name.replace(/_/g, ' ')}</option>`).join('') + '<option value="custom">Custom Topic</option>';

    const formatSelect = document.getElementById('format-select');
    formatSelect.innerHTML = formats.map(f => `<option value="${f}">${f}</option>`).join('');

    const numRecordsInput = document.getElementById('num-records');
    const numRecordsValue = document.getElementById('num-records-value');
    numRecordsInput.oninput = () => {
        numRecordsValue.textContent = numRecordsInput.value;
    };

    // Topic select change logic
    topicSelect.onchange = () => {
        const topic = topicSelect.value;
        const topicInfo = topics.find(t => t.name === topic);
        const descDiv = document.getElementById('topic-description');
        descDiv.innerHTML = '';
        if (topic === 'custom') {
            document.getElementById('custom-fields').style.display = 'block';
        } else {
            document.getElementById('custom-fields').style.display = 'none';
            if (topicInfo) {
                descDiv.innerHTML = `
                    <p><strong>Description:</strong> ${topicInfo.description}</p>
                    <details>
                        <summary>Available Fields</summary>
                        <ul>${topicInfo.fields.map(f => `<li>${f}</li>`).join('')}</ul>
                    </details>
                `;
            }
        }
    };

    // Ensure description is shown for the first time
    topicSelect.onchange();

    document.getElementById('use-seed').onchange = (e) => {
        // Optional: may want to visually indicate if seed is used
    };

    document.getElementById('generate-btn').onclick = async () => {
        const topic = topicSelect.value;
        const format = formatSelect.value;
        const numRecords = parseInt(numRecordsInput.value);
        const customFields = topic === 'custom' ? document.getElementById('custom-fields-input').value.split('\n').filter(f => f.trim()) : null;
        const seed = document.getElementById('use-seed').checked ? parseInt(document.getElementById('seed-input').value) : null;

        currentConfig = { topic, format, numRecords, customFields, seed };

        const form = document.getElementById('metric-form');
        form.classList.add('loading');

        const result = await generateData(topic, format, numRecords, customFields, seed);

        if (result && result.success) {
            generatedData = result;
            showSuccess('✅ Data generated successfully!');
            renderPreview(result, format);
        } else {
            showError('❌ Failed to generate data');
        }

        form.classList.remove('loading');
    };

    document.getElementById('show-raw-btn').onclick = () => {
        const raw = document.getElementById('raw-data');
        raw.style.display = raw.style.display === 'none' ? 'block' : 'none';
    };

    document.getElementById('copy-btn').onclick = () => {
        if (generatedData) {
            navigator.clipboard.writeText(generatedData.data).then(() => {
                showSuccess('✅ Data copied to clipboard!');
            }).catch(() => {
                showError('❌ Failed to copy data');
            });
        } else {
            showError('❌ No data to copy');
        }
    };

    document.getElementById('download-btn').onclick = () => {
        downloadData(currentConfig.topic, currentConfig.format, currentConfig.numRecords, currentConfig.customFields, currentConfig.seed);
    };

    function renderPreview(data, format) {
        const preview = document.getElementById('preview');
        preview.style.display = 'block';
        const rawDataElement = document.getElementById('raw-data');
        rawDataElement.textContent = formatData(data.data, format);

        const tableContainer = document.getElementById('table-container');
        tableContainer.innerHTML = '';
        if (format === 'XML') {
        // Always show as preformatted text (raw XML)
        document.getElementById('table-container').innerHTML = '';
        rawDataElement.style.display = 'block';
        rawDataElement.textContent = formatData(data.data, format); // use pretty formatter if needed
        } else if (format === 'CSV') {
            const { headers, rows } = parseCSV(data.data);
            if (headers.length > 0) {
                const table = document.createElement('table');
                table.innerHTML = `
                    <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
                    ${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}
                `;
                tableContainer.appendChild(table);
            } else {
                tableContainer.innerHTML = `<pre>${formatData(data.data, format)}</pre>`;
            }
        } else {
            tableContainer.innerHTML = `<pre>${formatData(data.data, format)}</pre>`;
        }
    }
}


init();