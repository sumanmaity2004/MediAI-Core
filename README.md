# 🫀 CardioScan AI

### Advanced Heart Attack Risk Prediction System using AI + IoT

---

## 🚀 Overview

**CardioScan AI** is an intelligent healthcare system that predicts **cardiac risk levels** using machine learning and real-time biosensor data.

It integrates:

* 🧠 AI-based prediction model
* 📊 Streamlit interactive dashboard
* 📡 ESP32 + MAX30100 sensor (Heart Rate & SpO₂)

This system helps in **early detection of heart-related risks** and supports preventive healthcare.

---

## 🎯 Features

* ✅ Real-time Heart Rate & SpO₂ monitoring
* ✅ AI-based cardiac risk prediction (Low / Medium / High)
* ✅ Beautiful futuristic Streamlit UI
* ✅ Manual input fallback (for cloud deployment)
* ✅ Probability distribution visualization
* ✅ BMI calculation & patient profiling

---

## 🛠️ Tech Stack

* **Frontend/UI**: Streamlit
* **Backend**: Python
* **Machine Learning**: Scikit-learn
* **Data Handling**: Pandas, NumPy
* **Hardware**: ESP32 + MAX30100 Sensor
* **Communication**: Serial + HTTP (requests)

---

## 📁 Project Structure

```
CardioScan-AI/
│
├── app.py                # Streamlit web app
├── main.py               # CLI-based prediction
├── sensor_reader.py      # ESP32 sensor integration
├── model.pkl             # Trained ML model
├── encoders.pkl          # Label encoders
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git](https://github.com/sumanmaity2004/MediAI-Core
cd MediAI-Core
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Streamlit app

```bash
streamlit run app.py
```

---

## 🌐 Deployment

This project can be deployed using **Streamlit Community Cloud**.

⚠️ Note:

* Hardware sensor (ESP32) will **not work on cloud platforms**
* Use **manual input mode** for online deployment

---

## 📡 Sensor Integration

* Uses **MAX30100 sensor** with ESP32
* Reads:

  * ❤️ Heart Rate
  * 🩸 Oxygen Saturation (SpO₂)

📌 If sensor is not connected:

* System automatically switches to manual input mode

---

## 🧠 Machine Learning Model

* Model: Classification model (Scikit-learn)

* Inputs:

  * Heart Rate
  * SpO₂
  * Age
  * Gender
  * Weight & Height
  * BMI (derived)

* Output:

  * Risk Category: **Low / Medium / High**
  * Probability scores for each class

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.
It is **not a medical diagnostic tool** and should not replace professional medical advice.

---

## 👨‍💻 Author

**Srinjan Ghosh**

* AI Enthusiast | Developer | Founder of VECTORIX

---

## 🌟 Future Improvements

* 🌐 Cloud-based sensor integration (ESP32 → API)
* 📱 Mobile app integration
* 📊 Advanced analytics dashboard
* 🧬 More medical parameters for higher accuracy

---

## ⭐ Support

If you like this project:
👉 Star the repo
👉 Share with others
👉 Contribute improvements

---

**Made with ❤️ using AI + IoT**
