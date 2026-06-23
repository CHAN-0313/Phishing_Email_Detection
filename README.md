# 🛡️ Phishing Email Detection System

A Machine Learning-based web application that detects phishing emails and helps users identify malicious messages before they become victims of cyber attacks. The system analyzes email content using Natural Language Processing (NLP) techniques and predicts whether an email is **Phishing** or **Legitimate** through a modern cybersecurity dashboard.

---

## 📌 Overview

Phishing attacks are among the most common cybersecurity threats used to steal sensitive information such as usernames, passwords, banking credentials, and personal data. This project provides an intelligent solution that leverages Machine Learning to classify suspicious emails and improve email security.

---

## ✨ Features

- 🔐 Detect phishing emails using Machine Learning
- 📧 Analyze email content in real-time
- 🧠 NLP-based text preprocessing and feature extraction
- 📊 Probability score and prediction results
- 🎨 Modern cybersecurity dashboard UI
- 📈 Interactive charts and analytics
- ⚡ Fast and lightweight Flask backend
- 🛡️ User-friendly interface inspired by SOC (Security Operations Center) tools

---

## 🏗️ Project Architecture

```
User Input
     ↓
Email Text Processing
     ↓
Text Cleaning & Preprocessing
     ↓
TF-IDF Feature Extraction
     ↓
Machine Learning Model
     ↓
Prediction Engine
     ↓
Result Dashboard
```

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Chart.js

### Backend
- Python
- Flask

### Machine Learning
- Scikit-learn
- Pandas
- NumPy
- Joblib

### NLP
- TF-IDF Vectorizer
- Text Preprocessing

---

## 📂 Project Structure

```
Phishing_Email_Detection/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── result.html
│
├── model/
│   ├── phishing_model.pkl
│   └── vectorizer.pkl
│
├── dataset/
│
├── app.py
├── requirements.txt
├── train_model.py
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CHAN-0313/Phishing_Email_Detection.git

cd Phishing_Email_Detection
```

### 2. Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

```bash
python app.py
```

---

### 5. Open Browser

```
http://127.0.0.1:5000
```

---

## 🔄 Working Process

1. User enters email content.
2. Input text is cleaned and preprocessed.
3. TF-IDF converts text into numerical vectors.
4. Trained Machine Learning model analyzes the features.
5. System predicts whether the email is:
   - ✅ Legitimate
   - ⚠️ Phishing
6. Result is displayed on the cybersecurity dashboard.

---

## 📊 Machine Learning Workflow

```
Dataset
   ↓
Data Cleaning
   ↓
Text Preprocessing
   ↓
TF-IDF Vectorization
   ↓
Train/Test Split
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Model Deployment with Flask
```

---

## 🚀 Future Enhancements

- Email header analysis
- URL reputation checking
- Deep Learning models (LSTM/BERT)
- Real-time email scanning
- API integration
- Multi-class threat detection
- Threat intelligence dashboard

---

## 📸 Dashboard Preview

- Home Page
- Email Analyzer
- Detection Result Page
- Analytics Dashboard
- Threat Statistics

---

## 🎯 Expected Outcome

The Phishing Email Detection System provides an effective solution for identifying malicious emails using Machine Learning and NLP techniques. It enhances email security by detecting phishing attempts in real time and helps users avoid credential theft and social engineering attacks.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

## ⭐ Support

If you found this project useful, please give it a ⭐ on GitHub.

---

## 👨‍💻 Author

**CHAN-0313**

GitHub: https://github.com/CHAN-0313
