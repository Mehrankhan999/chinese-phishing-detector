# 🛡️ Chinese Phishing Detection API

An AI-powered REST API for detecting phishing URLs in Chinese and English. Built with Random Forest, deployed on Railway with Flask.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Quick Start (5 minutes)

### Option 1: Deploy to Railway (Recommended)

1. **Fork or clone this repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/chinese-phishing-detector
   cd chinese-phishing-detector
   ```

2. **Push to GitHub**
   ```bash
   git push origin main
   ```

3. **Connect to Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose this repository
   - Railway auto-deploys! ✅

4. **Get your live URL**
   - Check Railway dashboard for your URL
   - Example: `https://your-app-abc123.up.railway.app`

---

### Option 2: Run Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the app**
   ```bash
   python app.py
   ```

3. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 📊 Features

### 🎯 Core Capabilities
- ✅ Detects phishing URLs with **95%+ accuracy**
- ✅ Supports **Chinese & English** URLs
- ✅ Handles **Punycode** and **IDN** domains
- ✅ Analyzes **21 URL features** in real-time
- ✅ Provides **confidence scores** (0-100%)
- ✅ Batch processing (up to 50 URLs)

### 🔧 Technical Features
- **ML Model**: Random Forest (scikit-learn)
- **Features**: Lexical, DNS, content, structural analysis
- **Language Support**: Simplified Chinese, Traditional Chinese, English
- **TLD Support**: `.cn`, `.com.cn`, `.中国`, `.网络`, etc.
- **API Format**: JSON REST with detailed responses
- **Security**: HTTPS validation, DNS verification, iframe detection

---

## 📡 API Documentation

### Base URL
```
https://your-app.up.railway.app
```

### Endpoints

#### 1. Dashboard (Web UI)
```
GET /
```
Interactive web interface for manual URL scanning.

---

#### 2. Single URL Scan
```
POST /api/scan
Content-Type: application/json
```

**Request:**
```json
{
  "url": "https://www.baidu.com"
}
```

**Response:**
```json
{
  "prediction": "legitimate",
  "phish_prob": 2.5,
  "legit_prob": 97.5,
  "url": "https://www.baidu.com",
  "error": null,
  "features": {
    "url_length": 21,
    "is_https": 1,
    "has_dns_record": 1,
    "domain_legit_score": 95,
    "suspicion_score": 5,
    ...
  },
  "feature_flags": {
    "red_flags": [],
    "green_flags": [
      "✔ Uses HTTPS encryption",
      "✔ Valid DNS record",
      "✔ Domain appears established"
    ]
  }
}
```

---

#### 3. Batch URL Scan
```
POST /api/batch
Content-Type: application/json
```

**Request:**
```json
{
  "urls": [
    "https://www.baidu.com",
    "https://example.com",
    "https://test.cn"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "prediction": "legitimate",
      "phish_prob": 2.5,
      ...
    },
    ...
  ],
  "total": 3
}
```

**Limits:**
- Maximum 50 URLs per request
- Timeout: 120 seconds

---

#### 4. Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "loaded",
  "timestamp": "2024-05-07T10:30:00.000000"
}
```

---

#### 5. API Documentation
```
GET /api/docs
```
Returns full API specification with examples.

---

## 🧠 How It Works

### Feature Extraction (21 Features)

**Lexical Features:**
- URL length, entropy, character counts (dots, hyphens, @)

**Encoding Features:**
- Punycode detection, non-ASCII characters, IP addresses

**Domain Features:**
- DNS validity, subdomain count, HTTPS presence
- Domain age, legitimacy score, suspicion score

**Content Features:**
- Hidden iframes, disabled right-click, email submission
- Suspicious keywords in Chinese & English

**Score Calculation:**
- **Legitimacy Score** (0-100): Age, DNS, HTTPS, TLD trust
- **Suspicion Score** (0-100): Keywords, IP, hyphens, punycode

### Prediction Model
- **Algorithm**: Random Forest Classifier
- **Training Data**: Mixed Chinese & English phishing URLs
- **Accuracy**: 95%+ on test set
- **Inference Time**: 100-500ms per URL

---

## 🔐 Security Features

✅ HTTPS validation
✅ DNS record verification
✅ Iframe detection
✅ Form submission analysis
✅ Keyword blacklist (Chinese + English)
✅ IDN/Punycode support
✅ Government/Education TLD detection

---

## 📊 Example Predictions

### ✅ Legitimate Domain
```
URL: https://www.baidu.com
Prediction: legitimate
Phishing Probability: 2.5%
Legitimacy Score: 95/100
Features: HTTPS, Valid DNS, Old domain, No keywords
```

### 🚨 Phishing Domain
```
URL: http://114.114.114.114/login
Prediction: phishing
Phishing Probability: 98.5%
Suspicion Score: 92/100
Red Flags: IP address, HTTP only, No DNS
```

### ⚠️ Suspicious Domain
```
URL: https://verify-account-update-password.xyz
Prediction: phishing
Phishing Probability: 78.3%
Red Flags: Suspicious keywords, Multiple hyphens, New domain
```

---

## 🛠️ Installation & Setup

### Requirements
- Python 3.11+
- 512MB RAM minimum
- 300MB disk space

### Dependencies
```
Flask==3.0.0
pandas==2.0.3
scikit-learn==1.3.2
requests==2.31.0
beautifulsoup4==4.12.2
gunicorn==21.2.0
```

### Install
```bash
git clone https://github.com/YOUR_USERNAME/chinese-phishing-detector
cd chinese-phishing-detector
pip install -r requirements.txt
```

---

## 🧪 Testing

### Local Testing
```bash
# Start app
python app.py

# Test health
curl http://localhost:5000/api/health

# Test single scan
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'

# Test batch
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com","https://test.cn"]}'
```

---

## 🚀 Deployment

### Railway (Recommended)
1. Connect GitHub repo to Railway
2. Auto-configures from `Procfile` and `requirements.txt`
3. One-click deployment
4. Auto-scaling included

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🐛 Troubleshooting

### Model not loading
```
Check that pickle files exist:
- chinese_english_rf_model_v2.pkl (219 KB)
- chinese_english_feature_names_v2.pkl (340 B)
```

### Slow responses
```
Increase workers in Procfile:
web: gunicorn --workers 8 --timeout 120 --bind 0.0.0.0:$PORT app:app
```

### Out of memory
```
Reduce batch size limit in app.py:
if len(urls) > 30:  # Changed from 50
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Model Load Time | 2-5s |
| Single URL Scan | 100-500ms |
| Batch (50 URLs) | 5-25s |
| Memory Usage | 200-300MB |
| Max Concurrent | 100+ users |

---

## 🤝 Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/name`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

### Documentation
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Railway deployment steps
- [API Docs](https://your-app.up.railway.app/api/docs) - Full API reference

### Issues
- Create GitHub issue with error details
- Include Railway deployment logs if applicable

### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Railway Docs](https://docs.railway.app/)
- [scikit-learn Guide](https://scikit-learn.org/)

---

## 🎯 Roadmap

- [ ] Support for more languages (Japanese, Korean, Vietnamese)
- [ ] Real-time model updates
- [ ] Advanced analytics dashboard
- [ ] Browser extension
- [ ] Mobile app integration
- [ ] Custom model training API

---

## ⭐ Show Your Support

If this project helps you, please consider giving it a star! ⭐

---

**Made with ❤️ for cybersecurity**

*Last Updated: May 2024*
