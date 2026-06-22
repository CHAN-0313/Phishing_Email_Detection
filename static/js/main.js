document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const subjectEl = document.getElementById('subject');
  const senderEl = document.getElementById('sender');
  const contentEl = document.getElementById('content');
  const resultBox = document.getElementById('resultBox');
  const confidenceEl = document.getElementById('confidence');
  const riskEl = document.getElementById('risk');
  const reasonsList = document.getElementById('reasonsList');
  const featuresTable = document.querySelector('#featuresTable tbody');
  const datasetFile = document.getElementById('datasetFile');
  const uploadDatasetBtn = document.getElementById('uploadDatasetBtn');
  const retrainBtn = document.getElementById('retrainBtn');
  const emailFileInput = document.getElementById('emailFileInput');
  const exportReport = document.getElementById('exportReport');

  let currentPrediction = null;
  let currentFeatures = null;

  const confusionChartEl = document.getElementById('confusionChart');
  const rocChartEl = document.getElementById('rocChart');
  const featureChartEl = document.getElementById('featureChart');
  let confusionChart;
  let rocChart;
  let featureChart;

  analyzeBtn.addEventListener('click', async () => {
    await analyzeEmail();
  });

  emailFileInput?.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    contentEl.value = text;
  });

  uploadDatasetBtn?.addEventListener('click', async () => {
    if (!datasetFile.files.length) {
      alert('Please choose a CSV dataset file first.');
      return;
    }
    const file = datasetFile.files[0];
    const form = new FormData();
    form.append('file', file);
    uploadDatasetBtn.disabled = true;
    try {
      const response = await fetch('/upload_dataset', { method: 'POST', body: form });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      alert('Dataset uploaded successfully. Use retrain to update the model.');
    } catch (err) {
      console.error(err);
      alert(err.message || 'Dataset upload failed');
    } finally {
      uploadDatasetBtn.disabled = false;
    }
  });

  retrainBtn?.addEventListener('click', async () => {
    retrainBtn.disabled = true;
    try {
      const payload = { dataset_path: 'dataset/emails.csv' };
      const response = await fetch('/retrain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      updateMetrics(data.metrics);
      alert('Model retrained successfully.');
    } catch (err) {
      console.error(err);
      alert(err.message || 'Retrain failed');
    } finally {
      retrainBtn.disabled = false;
    }
  });

  exportReport?.addEventListener('click', () => {
    if (!currentPrediction) {
      alert('Run an analysis first to generate a report.');
      return;
    }
    fetch('/download_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: subjectEl.value,
        sender: senderEl.value,
        prediction: currentPrediction,
        confidence: confidenceEl.textContent,
        reasons: Array.from(reasonsList.querySelectorAll('li')).map((li) => li.textContent),
        features: currentFeatures || {},
      }),
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'phishing_report.pdf';
        document.body.appendChild(link);
        link.click();
        link.remove();
      })
      .catch((err) => {
        console.error(err);
        alert('Failed to download report');
      });
  });

  async function analyzeEmail() {
    const payload = {
      subject: subjectEl.value,
      sender: senderEl.value,
      content: contentEl.value,
    };
    analyzeBtn.disabled = true;
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      currentPrediction = data.prediction;
      currentFeatures = data.features;
      renderResult(data);
      await loadScans();
    } catch (err) {
      console.error(err);
      alert(err.message || 'Analysis failed');
    } finally {
      analyzeBtn.disabled = false;
    }
  }

  function renderResult(data) {
    resultBox.classList.remove('d-none');
    if (data.prediction === 'Phishing') {
      resultBox.className = 'alert alert-danger';
      resultBox.textContent = '🚨 PHISHING EMAIL DETECTED';
      riskEl.textContent = 'HIGH';
    } else {
      resultBox.className = 'alert alert-success';
      resultBox.textContent = '✅ SAFE EMAIL';
      riskEl.textContent = 'LOW';
    }
    confidenceEl.textContent = data.confidence;
    reasonsList.innerHTML = '';
    (data.reasons || []).forEach((reason) => {
      const li = document.createElement('li');
      li.textContent = reason;
      reasonsList.appendChild(li);
    });
    featuresTable.innerHTML = '';
    const feats = data.features || {};
    for (const key of Object.keys(feats)) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${key}</td><td>${feats[key]}</td>`;
      featuresTable.appendChild(tr);
    }
  }

  async function loadMetrics() {
    try {
      const res = await fetch('/metrics');
      const data = await res.json();
      updateMetrics(data);
    } catch (err) {
      console.error(err);
    }
  }

  function updateMetrics(data) {
    if (!data) return;
    document.getElementById('modelAccuracy').textContent = `${((data.accuracy || 0) * 100).toFixed(1)}%`;
    document.getElementById('precisionText').textContent = `${((data.precision || 0) * 100).toFixed(1)}%`;
    document.getElementById('recallText').textContent = `${((data.recall || 0) * 100).toFixed(1)}%`;
    document.getElementById('f1Text').textContent = `${((data.f1 || 0) * 100).toFixed(1)}%`;
    renderConfusionChart(data.confusion_matrix || [[0, 0], [0, 0]]);
    renderRocChart(data.roc_auc || 0);
    renderFeatureChart(data.top_features || []);
  }

  function renderConfusionChart(matrix) {
    const values = matrix.flat();
    const labels = ['True Negative', 'False Positive', 'False Negative', 'True Positive'];
    const background = [
      'rgba(59, 130, 246, 0.9)',
      'rgba(248, 113, 113, 0.9)',
      'rgba(251, 191, 36, 0.9)',
      'rgba(34, 197, 94, 0.9)',
    ];
    if (confusionChart) confusionChart.destroy();
    confusionChart = new Chart(confusionChartEl, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ label: 'Samples', data: values, backgroundColor: background }],
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function renderRocChart(value) {
    if (rocChart) rocChart.destroy();
    rocChart = new Chart(rocChartEl, {
      type: 'line',
      data: {
        labels: ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'],
        datasets: [
          {
            label: `ROC AUC ${((value || 0) * 100).toFixed(1)}%`,
            data: [0, 0.3, 0.6, 0.8, 0.95, 1],
            borderColor: 'rgba(59, 130, 246, 0.9)',
            backgroundColor: 'rgba(59, 130, 246, 0.18)',
            fill: true,
            tension: 0.35,
          },
          {
            label: 'Random Classifier',
            data: [0, 0.2, 0.4, 0.6, 0.8, 1],
            borderColor: 'rgba(148, 163, 184, 0.5)',
            borderDash: [6, 6],
            fill: false,
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
      },
    });
  }

  function renderFeatureChart(features) {
    const labels = features.map((item) => item.feature);
    const values = features.map((item) => item.importance * 100);
    if (featureChart) featureChart.destroy();
    featureChart = new Chart(featureChartEl, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Importance',
            data: values,
            backgroundColor: 'rgba(56, 189, 248, 0.8)',
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        scales: { x: { beginAtZero: true } },
      },
    });
  }

  async function loadScans() {
    try {
      const res = await fetch('/scans');
      const rows = await res.json();
      const tbody = document.querySelector('#scanTable tbody');
      tbody.innerHTML = '';
      rows.slice(-10).reverse().forEach((row) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${row.timestamp}</td>
          <td>${row.subject}</td>
          <td>${row.sender}</td>
          <td>${row.result}</td>
          <td>${(parseFloat(row.confidence) * 100).toFixed(1)}%</td>
        `;
        tbody.appendChild(tr);
      });
      document.getElementById('emailsScanned').textContent = rows.length;
      const phishingCount = rows.filter((r) => r.result === 'Phishing').length;
      document.getElementById('phishingDetected').textContent = phishingCount;
      document.getElementById('safeEmails').textContent = rows.length - phishingCount;
    } catch (err) {
      console.error(err);
    }
  }

  loadMetrics();
  loadScans();
});
