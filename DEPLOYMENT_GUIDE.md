# 🚀 Railway Deployment Guide - Chinese Phishing Detection API

## 📋 Pre-Deployment Checklist

### Required Files in Your GitHub Repository:
```
your-repo/
├── app.py                                      # Main Flask application
├── requirements.txt                            # Python dependencies
├── Procfile                                    # Railway process configuration
├── runtime.txt                                 # Python version
├── chinese_english_rf_model_v2.pkl           # ML model (219 KB)
├── chinese_english_feature_names_v2.pkl      # Feature names (340 B)
├── multilingual_phishing_detection_dashboard.html  # UI dashboard
├── .env.example                               # Environment template
└── .gitignore                                 # Git ignore file
```

## 🔧 Step 1: Prepare Your GitHub Repository

### 1a. Create `.gitignore` (if not exists):
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/
.env
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### 1b. Upload All Files to GitHub:
```bash
cd your-local-directory
git init
git add .
git commit -m "Initial commit: Chinese phishing detector for Railway"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 1c. Verify on GitHub:
- Visit: `https://github.com/YOUR_USERNAME/YOUR_REPO`
- Confirm all files are present ✅

---

## 🚄 Step 2: Connect Railway to GitHub

### 2a. Create Railway Account:
1. Go to https://railway.app
2. Click "Start Free" 
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your GitHub account

### 2b. Create New Project:
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Search for your repository: `YOUR_REPO`
4. Click "Deploy Now"

### 2c. Configure Build Settings:
Railway should auto-detect:
- **Build Command**: (leave empty - auto-detected)
- **Start Command**: `gunicorn --workers 4 --timeout 120 --bind 0.0.0.0:$PORT app:app`

---

## ⚙️ Step 3: Configure Environment Variables

### 3a. In Railway Dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add the following variables:

```
FLASK_ENV=production
PORT=8000
```

### 3b. Alternative: Use `.env` in Railway:
1. Click "Settings"
2. Look for "Raw editor" 
3. Copy-paste the .env variables

---

## 🔍 Step 4: Deploy & Monitor

### 4a. Start Deployment:
1. Railway auto-detects changes to main branch
2. Or click "Deploy" button manually
3. Watch build logs:
   - "Building..." → Installing dependencies
   - "Deploying..." → Starting app
   - "Active" → Successfully deployed ✅

### 4b. Check Deployment Status:
1. Go to "Deployments" tab
2. Look for green checkmark ✅
3. If red ❌, click to see error logs

### 4c. Get Your Live URL:
1. Click "Settings" tab
2. Look for "Service URL" or "Domain"
3. Format: `https://your-app-random.up.railway.app`

---

## ✅ Step 5: Test Your Deployment

### 5a. Test Dashboard (Web UI):
```
Visit: https://your-app-random.up.railway.app
```
- You should see the Chinese phishing detection dashboard
- Try scanning a URL

### 5b. Test Health Endpoint:
```bash
curl https://your-app-random.up.railway.app/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model": "loaded",
  "timestamp": "2024-05-07T10:30:00.000000"
}
```

### 5c. Test Single URL Scan:
```bash
curl -X POST https://your-app-random.up.railway.app/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.baidu.com"}'
```

**Expected response:**
```json
{
  "prediction": "legitimate",
  "phish_prob": 2.5,
  "legit_prob": 97.5,
  "url": "https://www.baidu.com",
  "features": {...},
  "feature_flags": {...},
  "error": null
}
```

### 5d. Test API Documentation:
```
Visit: https://your-app-random.up.railway.app/api/docs
```

---

## 🐛 Step 6: Troubleshooting Common Errors

### ❌ Error: "Module not found" or "No module named 'sklearn'"
**Solution:**
1. Check `requirements.txt` includes all packages
2. Run locally: `pip install -r requirements.txt`
3. Commit and push changes
4. Re-deploy in Railway

### ❌ Error: "Model files not found"
**Solution:**
1. Verify pickle files are in repo root:
   - `chinese_english_rf_model_v2.pkl`
   - `chinese_english_feature_names_v2.pkl`
2. Check file names exactly match (case-sensitive)
3. Run git status to confirm files are tracked:
   ```bash
   git status
   ```
4. If not tracked, add:
   ```bash
   git add *.pkl
   git commit -m "Add pickle model files"
   git push
   ```

### ❌ Error: "Port already in use"
**Solution:**
Railway manages ports automatically. Check if `PORT` environment variable is set correctly.

### ❌ Error: "502 Bad Gateway"
**Solutions:**
1. Check deploy logs: Click "Deployments" → View logs
2. Ensure model loads: Check for "✅ Models loaded successfully"
3. Increase worker timeout in Procfile if timeout errors:
   ```
   web: gunicorn --workers 2 --timeout 240 --bind 0.0.0.0:$PORT app:app
   ```

### ❌ Error: "Endpoint not found" (404)
**Solution:**
- Correct URL format: `https://your-app.up.railway.app/api/scan`
- Use POST, not GET for `/api/scan`
- Include Content-Type header: `application/json`

---

## 📊 Step 7: Monitor Performance

### View Logs:
1. Go to Railway dashboard
2. Click "View logs"
3. Look for:
   - `✅ Models loaded successfully` (good)
   - `❌ Error loading models` (bad - fix immediately)

### Check Resource Usage:
1. Click "Metrics" tab
2. Monitor:
   - Memory usage
   - CPU usage
   - Request count

### Common Issues & Solutions:

| Issue | Cause | Fix |
|-------|-------|-----|
| Memory spike | Large batch requests | Limit batch to 50 URLs max |
| High CPU | Model inference | Normal - reduce workers if sustained |
| Slow response | Network timeout | Increase `--timeout` in Procfile |

---

## 🔄 Step 8: Update Your App

### To Update Code:
```bash
# Make changes locally
# Test locally: python app.py

# Commit and push
git add .
git commit -m "Update: improved error handling"
git push origin main

# Railway auto-deploys within 1-2 minutes ✅
```

### To Update Model Files:
```bash
# Replace old pickle files with new ones
cp new_model.pkl chinese_english_rf_model_v2.pkl
cp new_features.pkl chinese_english_feature_names_v2.pkl

# Commit and push
git add *.pkl
git commit -m "Update: new model v3"
git push origin main
```

---

## 🎯 Step 9: API Integration Examples

### Python:
```python
import requests

url = "https://your-app.up.railway.app/api/scan"
data = {"url": "https://example.com"}
response = requests.post(url, json=data)
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Phishing probability: {result['phish_prob']}%")
```

### JavaScript/Node.js:
```javascript
const url = "https://your-app.up.railway.app/api/scan";
const data = { url: "https://example.com" };

fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data)
})
.then(r => r.json())
.then(result => {
  console.log(`Prediction: ${result.prediction}`);
  console.log(`Phishing %: ${result.phish_prob}`);
});
```

### cURL:
```bash
curl -X POST https://your-app.up.railway.app/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

---

## 💾 Step 10: Backup & Maintenance

### Backup Your Code:
```bash
# Create backup branch
git branch backup-$(date +%Y%m%d)
git push origin backup-*
```

### Monitor Deployment History:
1. Railway Dashboard → Deployments
2. Keep last 5-10 deployments
3. Old deployments auto-cleaned after 30 days

---

## 🚨 Critical Checklist Before Going Live

- [ ] All files committed to GitHub (including .pkl files)
- [ ] `requirements.txt` has all dependencies
- [ ] `Procfile` specifies correct start command
- [ ] `runtime.txt` specifies Python 3.11+
- [ ] Environment variables set in Railway
- [ ] `/api/health` endpoint returns 200 OK
- [ ] `/api/scan` accepts POST requests
- [ ] Dashboard loads at root URL `/`
- [ ] Model files are present and loading
- [ ] Error logs are empty or minimal
- [ ] Performance is acceptable (<2s per request)

---

## 📞 Support & Resources

### Common Errors Reference:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Railway Docs](https://docs.railway.app/)
- [Scikit-learn Serialization](https://scikit-learn.org/stable/modules/model_persistence.html)

### If Still Having Issues:

1. **Check Railway logs** (most helpful):
   ```
   Dashboard → Deployments → [Your Deployment] → View Logs
   ```

2. **Run locally to test**:
   ```bash
   pip install -r requirements.txt
   python app.py
   # Visit: http://localhost:5000
   ```

3. **Verify file names and paths**:
   ```bash
   ls -la *.pkl
   # Must show:
   # chinese_english_rf_model_v2.pkl (219K)
   # chinese_english_feature_names_v2.pkl (340B)
   ```

4. **Check git status**:
   ```bash
   git status
   git log --oneline (last 5 commits)
   ```

---

## 🎉 Success! Your App is Live

Once deployed successfully:
- Share URL: `https://your-app.up.railway.app`
- Users can scan URLs via web interface
- Developers can use `/api/scan` endpoint
- Batch processing available at `/api/batch`

**Congratulations! Your Chinese phishing detector is live! 🚀**

---

*Last Updated: May 2024*
*For latest Railway documentation, visit: https://docs.railway.app/*
