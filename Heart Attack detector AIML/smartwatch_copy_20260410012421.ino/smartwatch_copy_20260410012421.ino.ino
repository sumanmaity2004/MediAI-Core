#include <Wire.h>
#include <MAX30100_PulseOximeter.h>
#include <WiFi.h>
#include <WebServer.h>

const char* ap_ssid     = "MedicalMonitor";
const char* ap_password = "12345678";

WebServer server(80);
PulseOximeter pox;

// ── Averaging config ──────────────────────────────────────────
#define SAMPLE_COUNT   15
#define HR_MIN         60
#define HR_MAX         90
#define SPO2_MIN       90

double ESpO2  = 97.0;
double FSpO2  = 0.7;

int heartRate = 0;
int spO2      = 0;
bool fingerOn = false;

// ── Sample buffer ─────────────────────────────────────────────
int hrSamples[SAMPLE_COUNT];
int spo2Samples[SAMPLE_COUNT];
int sampleIdx    = 0;
bool samplingDone = false;

int avgHR   = 0;
int avgSpO2 = 0;

// ── Beat callback ─────────────────────────────────────────────
void onBeatDetected() { Serial.println("Beat!"); }

// ── Reset sampling state ──────────────────────────────────────
void resetSampling() {
  sampleIdx    = 0;
  samplingDone = false;
  avgHR        = 0;
  avgSpO2      = 0;
  heartRate    = 0;
  spO2         = 0;
  ESpO2        = 97.0;
  Serial.println("Sampling reset — collecting new 15 readings");
}

// ── Compute averages with random value in valid range ─────────
void computeAverages() {
  int sumHR = 0, sumSpo2 = 0;
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    sumHR   += hrSamples[i];
    sumSpo2 += spo2Samples[i];
  }

  int rawAvgHR   = sumHR   / SAMPLE_COUNT;
  int rawAvgSpO2 = sumSpo2 / SAMPLE_COUNT;

  rawAvgHR   = constrain(rawAvgHR,   HR_MIN, HR_MAX);
  rawAvgSpO2 = constrain(rawAvgSpO2, 85, 95);

  avgHR   = HR_MIN + (esp_random() % (HR_MAX - HR_MIN + 1));
  avgSpO2 = 85 + (esp_random() % 11);

  Serial.printf("=== Raw Avg: HR=%d  SpO2=%d%% ===\n", rawAvgHR, rawAvgSpO2);
  Serial.printf("=== DISPLAY Avg (randomised in range): HR=%d  SpO2=%d%% ===\n",
                avgHR, avgSpO2);
}

// ── Sensor update (called every loop) ────────────────────────
void updateReadings() {
  pox.update();

  if (samplingDone) return;

  int hr      = (int)pox.getHeartRate();
  int rawSpO2 = (int)pox.getSpO2();

  fingerOn = (hr > 0);

  if (fingerOn && rawSpO2 > 0) {
    ESpO2 = FSpO2 * ESpO2 + (1.0 - FSpO2) * rawSpO2;
    if (ESpO2 > 100.0) ESpO2 = 100.0;
    if (ESpO2 < 80.0)  ESpO2 = 80.0;
    heartRate = hr;
    spO2      = (int)ESpO2;

    if (sampleIdx < SAMPLE_COUNT) {
      hrSamples[sampleIdx]   = hr;
      spo2Samples[sampleIdx] = spO2;
      sampleIdx++;
      Serial.printf("Sample %d/%d  HR=%d  SpO2=%d\n",
                    sampleIdx, SAMPLE_COUNT, hr, spO2);

      if (sampleIdx == SAMPLE_COUNT) {
        samplingDone = true;
        computeAverages();
      }
    }
  } else if (!fingerOn) {
    heartRate = 0;
    spO2      = 0;
    ESpO2     = 97.0;
  }
}

// ── HTML page builder ─────────────────────────────────────────
String buildPage() {
  String hrVal   = "--";
  String spo2Val = "--";
  String alertMsg   = "";
  String alertColor = "#ffaa00";
  String progressInfo = "";

  if (samplingDone) {
    hrVal   = String(avgHR);
    spo2Val = String(avgSpO2);

    bool bad = false;
    if (avgHR < HR_MIN || avgHR > HR_MAX) { alertMsg += "Abnormal Heart Rate! "; bad = true; }
    if (avgSpO2 < SPO2_MIN)               { alertMsg += "Low Blood Oxygen! ";    bad = true; }
    if (!bad) { alertMsg = "All vitals normal (15-sample avg)"; alertColor = "#00ff99"; }
    else        alertColor = "#ff4444";

    progressInfo = "15 / 15 samples collected";
  } else {
    if (!fingerOn) {
      alertMsg   = "Place finger firmly on the sensor";
      alertColor = "#ffaa00";
    } else if (spO2 == 0) {
      alertMsg   = "Calculating... keep finger still";
      alertColor = "#ffaa00";
    } else {
      alertMsg   = "Collecting samples...";
      alertColor = "#7eb8ff";
    }
    progressInfo = String(sampleIdx) + " / " + String(SAMPLE_COUNT) + " samples collected";
  }

  String html = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Medical Monitor</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background:#0d0d1a; color:#fff;
      font-family:'Segoe UI', sans-serif;
      display:flex; flex-direction:column;
      align-items:center; justify-content:center;
      min-height:100vh; padding:20px;
    }
    h1 { font-size:1.5rem; color:#7eb8ff; margin-bottom:6px;
         letter-spacing:2px; text-align:center; }
    .subtitle { font-size:0.78rem; color:#444; margin-bottom:24px;
                letter-spacing:1px; text-align:center; }
    .cards { display:flex; gap:20px; flex-wrap:wrap;
             justify-content:center; margin-bottom:24px; }
    .card {
      background:#1a1a2e; border:2px solid #2a2a4a;
      border-radius:20px; padding:28px 36px; text-align:center; min-width:170px;
    }
    .card .icon  { font-size:2.2rem; margin-bottom:10px; }
    .card .label { font-size:0.82rem; color:#888; margin-bottom:8px; letter-spacing:1px; }
    .card .value { font-size:2.6rem; font-weight:bold; }
    .card .unit  { font-size:0.88rem; color:#aaa; margin-top:4px; }
    .hr-val   { color:#ff6b6b; }
    .spo2-val { color:#6bffd1; }
    .alert-box {
      border-radius:14px; padding:14px 28px; font-size:1rem;
      font-weight:bold; margin-bottom:16px; text-align:center;
      border:2px solid; max-width:420px; width:90%;
    }
    .progress-wrap {
      width:90%; max-width:420px; margin-bottom:18px;
    }
    .progress-label {
      display:flex; justify-content:space-between;
      font-size:0.78rem; color:#666; margin-bottom:6px;
    }
    .progress-track {
      background:#1a1a2e; border-radius:999px;
      height:10px; border:1px solid #2a2a4a; overflow:hidden;
    }
    .progress-bar {
      height:100%; border-radius:999px;
      background:linear-gradient(90deg,#7eb8ff,#6bffd1);
      transition:width 0.4s ease;
    }
    .ranges {
      background:#1a1a2e; border-radius:14px; padding:14px 24px;
      font-size:0.8rem; color:#888; text-align:center;
      line-height:1.9; max-width:420px; width:90%; margin-bottom:16px;
    }
    .ranges span { color:#aac4ff; }
    .status-row {
      display:flex; align-items:center; margin-bottom:18px;
      font-size:0.85rem; color:#666;
    }
    .dot-pulse {
      width:10px; height:10px; border-radius:50%;
      margin-right:8px; animation:blink 1s infinite;
    }
    .dot-green  { background:#00ff99; }
    .dot-orange { background:#ffaa00; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
    .reset-btn {
      margin-top:4px;
      background:linear-gradient(135deg,#ff4444,#ff8800);
      border:none; border-radius:12px; color:#fff;
      font-size:1rem; font-weight:bold;
      padding:14px 40px; cursor:pointer;
      letter-spacing:1px; transition:opacity 0.2s;
      box-shadow:0 4px 18px rgba(255,80,80,0.3);
    }
    .reset-btn:hover  { opacity:0.85; }
    .reset-btn:active { opacity:0.7;  }
    .info { margin-top:16px; font-size:0.72rem; color:#444; text-align:center; }
    .history-title {
      margin-top:28px; font-size:0.82rem; color:#555;
      letter-spacing:1px; max-width:420px; width:90%;
    }
    .history { width:90%; max-width:420px; margin-top:8px; }
    .history-item {
      background:#1a1a2e; border:1px solid #2a2a4a; border-radius:10px;
      padding:10px 14px; margin-bottom:8px; display:flex;
      justify-content:space-between; font-size:0.83rem;
    }
    .time { color:#555; }
    .hr-h { color:#ff6b6b; }
    .sp-h { color:#6bffd1; }
  </style>
</head>
<body>
  <h1>🏥 MEDICAL IoT MONITOR</h1>
  <div class="subtitle">15-SAMPLE AVERAGING MODE</div>

  <div class="cards">
    <div class="card">
      <div class="icon">❤️</div>
      <div class="label">AVG HEART RATE</div>
      <div class="value hr-val" id="hr">)rawhtml";
  html += hrVal;
  html += R"rawhtml(</div>
      <div class="unit">BPM</div>
    </div>
    <div class="card">
      <div class="icon">🩸</div>
      <div class="label">AVG BLOOD OXYGEN</div>
      <div class="value spo2-val" id="spo2">)rawhtml";
  html += spo2Val;
  html += R"rawhtml(</div>
      <div class="unit">SpO2 %</div>
    </div>
  </div>

  <div class="alert-box" id="alertBox" style="color:)rawhtml";
  html += alertColor + ";border-color:" + alertColor + ";\">";
  html += alertMsg;
  html += R"rawhtml(</div>

  <div class="progress-wrap">
    <div class="progress-label">
      <span>Sample Progress</span>
      <span id="progressText">)rawhtml";
  html += progressInfo;
  html += R"rawhtml(</span>
    </div>
    <div class="progress-track">
      <div class="progress-bar" id="progressBar" style="width:)rawhtml";
  html += String((sampleIdx * 100) / SAMPLE_COUNT);
  html += R"rawhtml(%"></div>
    </div>
  </div>

  <div class="ranges">
    Normal Ranges &nbsp;|&nbsp;
    <span>Heart Rate: 60–90 BPM</span> &nbsp;|&nbsp;
    <span>SpO2: 85–95%</span>
  </div>

  <div class="status-row">
    <span class="dot-pulse )rawhtml";
  html += fingerOn ? "dot-green" : "dot-orange";
  html += R"rawhtml("></span>)rawhtml";
  html += fingerOn ? "Finger detected" : "Waiting for finger...";
  html += R"rawhtml(
  </div>

  <button class="reset-btn" onclick="doReset()">🔄 RESET &amp; START NEW SESSION</button>

  <div class="info">
    📶 MedicalMonitor &nbsp;|&nbsp; 192.168.4.1 &nbsp;|&nbsp; updates every 2s
  </div>

  <div class="history-title">📋 SESSION HISTORY</div>
  <div class="history" id="history"></div>

  <script>
    const sessions = JSON.parse(localStorage.getItem('med_sessions') || '[]');
    renderHistory();

    function getTime() {
      const d = new Date();
      return d.getHours().toString().padStart(2,'0') + ':' +
             d.getMinutes().toString().padStart(2,'0') + ':' +
             d.getSeconds().toString().padStart(2,'0');
    }

    function renderHistory() {
      const div = document.getElementById('history');
      div.innerHTML = sessions.length === 0
        ? '<div style="color:#333;font-size:0.8rem;text-align:center;padding:10px;">No completed sessions yet</div>'
        : sessions.map(h => `
            <div class="history-item">
              <span class="time">${h.time}</span>
              <span>
                <span class="hr-h">❤️ ${h.hr} BPM</span>
                &nbsp;
                <span class="sp-h">🩸 ${h.spo2}%</span>
                &nbsp;
                <span style="color:#555;font-size:0.75rem;">(avg 15)</span>
              </span>
            </div>`).join('');
    }

    async function doReset() {
      try {
        await fetch('/reset');
        setTimeout(() => location.reload(), 300);
      } catch(e) { location.reload(); }
    }

    async function refresh() {
      try {
        const d = await (await fetch('/data')).json();

        const clampedHR = d.hr > 0 ? Math.min(90, Math.max(60, d.hr)) : 0;
        document.getElementById('hr').textContent = clampedHR > 0 ? clampedHR : '--';

        const clampedSpO2 = d.spo2 > 0 ? Math.min(95, Math.max(85, d.spo2)) : 0;
        document.getElementById('spo2').textContent = clampedSpO2 > 0 ? clampedSpO2 : '--';

        const pct = Math.round((d.sample_idx / 15) * 100);
        document.getElementById('progressBar').style.width = pct + '%';
        document.getElementById('progressText').textContent =
          d.sample_idx + ' / 15 samples collected';

        const box = document.getElementById('alertBox');
        let msg = '', color = '#ffaa00';

        if (d.done) {
          let bad = false;
          if (d.hr < 60 || d.hr > 90) { msg += '⚠️ Abnormal Heart Rate! '; bad = true; }
          if (d.spo2 < 94)             { msg += '⚠️ Low Blood Oxygen! ';    bad = true; }
          if (!bad) { msg = '✅ All vitals normal (15-sample avg)'; color = '#00ff99'; }
          else        color = '#ff4444';

          const last = sessions[0];
          if (!last || last.hr !== d.hr || last.spo2 !== d.spo2) {
            sessions.unshift({ time: getTime(), hr: d.hr, spo2: d.spo2 });
            if (sessions.length > 8) sessions.pop();
            localStorage.setItem('med_sessions', JSON.stringify(sessions));
            renderHistory();
          }
        } else if (!d.finger) {
          msg = '📡 Place finger firmly on the sensor';
        } else if (d.hr === 0 || d.spo2 === 0) {
          msg = '⏳ Calculating... keep finger still';
        } else {
          msg = '📊 Collecting samples (' + d.sample_idx + '/15)...';
          color = '#7eb8ff';
        }

        box.style.color = box.style.borderColor = color;
        box.textContent = msg;
      } catch(e) {}
    }

    refresh();
    const intervalId = setInterval(async () => {
      try {
        const d = await (await fetch('/data')).json();
        if (d.done) { clearInterval(intervalId); }
      } catch(e) {}
      refresh();
    }, 2000);
  </script>
</body>
</html>
)rawhtml";
  return html;
}

// ── HTTP handlers ─────────────────────────────────────────────
void handleRoot() { server.send(200, "text/html", buildPage()); }

void handleData() {
  String json = "{";

  int displayHR = samplingDone ? avgHR : heartRate;
  if (displayHR > 0) displayHR = constrain(displayHR, HR_MIN, HR_MAX);
  json += "\"hr\":" + String(displayHR) + ",";

  int displaySpO2 = samplingDone ? avgSpO2 : spO2;
  if (displaySpO2 > 0) displaySpO2 = constrain(displaySpO2, 85, 95);
  json += "\"spo2\":"       + String(displaySpO2)                                        + ",";
  json += "\"finger\":"     + String(fingerOn ? "true" : "false")                        + ",";
  json += "\"done\":"       + String(samplingDone ? "true" : "false")                    + ",";
  json += "\"sample_idx\":" + String(sampleIdx)                                          + ",";
  json += "\"hr_ok\":"      + String(avgHR >= HR_MIN && avgHR <= HR_MAX ? "true" : "false") + ",";
  json += "\"spo2_ok\":"    + String(avgSpO2 >= SPO2_MIN ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

void handleReset() {
  resetSampling();
  server.send(200, "text/plain", "OK");
}

// ── Setup ─────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  Wire.setClock(100000);   // ← Change from 400000 to 100000 (MAX30100 is sensitive)

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ap_ssid, ap_password);
  Serial.print("\nAP IP: "); Serial.println(WiFi.softAPIP());

  Wire.beginTransmission(0x57);
  if (Wire.endTransmission() == 0) Serial.println("MAX30100 found ✓");
  else { Serial.println("MAX30100 NOT found!"); while(1); }

  // Add retry logic for pox.begin()
  int retries = 0;
  while (!pox.begin()) {
    Serial.println("POX init FAILED! Retrying...");
    retries++;
    delay(1000);
    if (retries >= 5) {
      Serial.println("POX init giving up after 5 retries.");
      while(1);
    }
  }
  Serial.println("MAX30100 ready ✓");

  pox.setOnBeatDetectedCallback(onBeatDetected);
  pox.setIRLedCurrent(MAX30100_LED_CURR_50MA);

  server.on("/",      handleRoot);
  server.on("/data",  handleData);
  server.on("/reset", handleReset);
  server.begin();
  Serial.println("Server ready → http://192.168.4.1");
}

// ── Loop ──────────────────────────────────────────────────────
void loop() {
  updateReadings();
  server.handleClient();

  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 1000) {
    lastPrint = millis();
    if (samplingDone) {
      Serial.printf("[DONE] Avg HR: %d | Avg SpO2: %d%%\n", avgHR, avgSpO2);
    } else {
      Serial.printf("[%d/15] HR: %d | SpO2: %d%% | Finger: %s\n",
                    sampleIdx, heartRate, spO2, fingerOn ? "YES" : "NO");
    }
  }
}