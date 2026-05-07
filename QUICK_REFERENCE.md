# 📋 Quick Reference Card - Railway Deployment Commands

## 🎯 Pre-Deployment (Local)

```bash
# 1. Clone or create repo
git clone https://github.com/YOUR_USERNAME/chinese-phishing-detector
cd chinese-phishing-detector

# 2. Copy all required files here:
# - app.py
# - requirements.txt
# - Procfile
# - runtime.txt
# - *.pkl files
# - *.html files

# 3. Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
venv/
.env
.DS_Store
EOF

# 4. Test locally
pip install -r requirements.txt
python app.py
# Visit: http://localhost:5000

# 5. If all works, commit
git add .
git commit -m "Initial commit: Chinese phishing detector"
git branch -M main
```

---

## 🚀 First Deployment

```bash
# 1. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main

# 2. Go to Railway.app
# 3. Create new project
# 4. Connect GitHub repo
# 5. Set environment variables:
#    FLASK_ENV=production
# 6. Click Deploy

# Wait 2-3 minutes...

# 7. Get your URL from Railway dashboard
# https://your-app-xxx.up.railway.app
```

---

## ✅ Test Deployment

```bash
# Health check
curl https://your-app-xxx.up.railway.app/api/health

# Single URL test
curl -X POST https://your-app-xxx.up.railway.app/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.baidu.com"}'

# Batch test
curl -X POST https://your-app-xxx.up.railway.app/api/batch \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com","https://test.cn"]}'

# View docs
open https://your-app-xxx.up.railway.app/api/docs
```

---

## 📝 Make Updates

```bash
# 1. Make changes locally
# 2. Test: python app.py
# 3. Commit & push:
git add .
git commit -m "Update: [what changed]"
git push origin main

# Railway auto-deploys within 2 minutes ✅
```

---

## 📊 View Logs

```bash
# Railway Dashboard:
1. Click your project
2. Click "View Logs"
3. Look for errors (red text)
4. Search for "Models loaded successfully" (should be green)
```

---

## 🔍 Debug Issues

```bash
# View git log
git log --oneline -10

# Verify files
ls -lah *.pkl
ls -lah *.html
ls -lah app.py
ls -lah requirements.txt
ls -lah Procfile

# Check if tracked by git
git status
git ls-files | grep -E "\.pkl|\.html"

# Revert to previous version (if broken)
git revert HEAD --no-edit
git push origin main
```

---

## 🛠️ Common Fixes

### Model not loading
```bash
# Verify files exist
ls -lah chinese_english_rf_model_v2.pkl
ls -lah chinese_english_feature_names_v2.pkl

# If 0 bytes, recopy:
cp /source/path/chinese_english_rf_model_v2.pkl .

# Add and push
git add *.pkl
git commit -m "Fix: recopy model files"
git push origin main
```

### Module not found
```bash
# Add to requirements.txt
echo "scikit-learn==1.3.2" >> requirements.txt

# Test locally
pip install -r requirements.txt

# Push
git add requirements.txt
git commit -m "Fix: add missing dependency"
git push origin main
```

### Timeout errors
```bash
# Edit Procfile - increase timeout
sed -i 's/--timeout 120/--timeout 240/g' Procfile

# Or reduce workers
sed -i 's/--workers 4/--workers 2/g' Procfile

# Push
git add Procfile
git commit -m "Fix: adjust gunicorn settings"
git push origin main
```

---

## 📋 File Checklist

Before deploying, ensure you have:

```bash
✅ app.py (Flask application)
✅ requirements.txt (dependencies)
✅ Procfile (Railway config)
✅ runtime.txt (Python 3.11.7)
✅ chinese_english_rf_model_v2.pkl (~219 KB)
✅ chinese_english_feature_names_v2.pkl (~340 B)
✅ multilingual_phishing_detection_dashboard.html (~45 KB)
✅ .gitignore (ignore pycache, venv)
✅ README.md (documentation)
```

Verify all files:
```bash
ls -lah app.py requirements.txt Procfile runtime.txt *.pkl *.html
```

---

## 🚨 Emergency Commands

### Stop deployment
```bash
# In Railway Dashboard:
1. Click Settings
2. Find "Stop Current Deploy"
3. Click it
```

### Revert to previous version
```bash
git log --oneline
# Find good commit hash (e.g., abc1234)
git reset --hard abc1234
git push origin main -f

# Railway will re-deploy to old version
```

### Force redeploy same version
```bash
# Make empty commit
git commit --allow-empty -m "Force redeploy"
git push origin main

# Or edit Procfile and push
echo "" >> Procfile
git add Procfile
git commit -m "Trigger redeploy"
git push origin main
```

---

## 🔗 Important URLs

| Item | URL |
|------|-----|
| Railway Dashboard | https://railway.app |
| Your Project | https://railway.app/project/PROJECT_ID |
| Logs | Click "View Logs" in dashboard |
| API Health | https://your-app.up.railway.app/api/health |
| API Docs | https://your-app.up.railway.app/api/docs |
| Web Dashboard | https://your-app.up.railway.app |

---

## 📞 Debugging Flow

```
Problem?
    ↓
1. Check Railway logs (most helpful)
2. Test locally: python app.py
3. Check git status: git status
4. Verify files: ls -lah *.pkl
5. Check git log: git log --oneline -5
6. Try revert if needed
```

---

## ⏱️ Timeline

| Step | Time | What to Expect |
|------|------|-----------------|
| Push to GitHub | 0-1s | Instant |
| Railway detects | 1-10s | Notification |
| Building | 30-60s | "Building..." status |
| Deploying | 30-60s | "Deploying..." status |
| Live | 60-120s | Green checkmark ✅ |

---

## 💾 Backup & Recovery

```bash
# Create backup branch before major changes
git branch backup-$(date +%Y%m%d)
git push origin backup-*

# Switch to backup if needed
git checkout backup-20240507
git push origin main -f

# Clean up old backups
git branch -d backup-*
git push origin --delete backup-*
```

---

## 🎓 Learning Resources

- [Flask Official Docs](https://flask.palletsprojects.com/)
- [Railway Documentation](https://docs.railway.app/)
- [Git Cheat Sheet](https://github.github.com/training-kit/downloads/github-git-cheat-sheet.pdf)
- [scikit-learn Model Persistence](https://scikit-learn.org/stable/modules/model_persistence.html)

---

## ✨ Success Indicators

✅ You're good if you see:
- Railway dashboard shows green checkmark
- `/api/health` returns `{"status": "healthy", "model": "loaded"}`
- Dashboard loads at root URL
- `/api/scan` accepts POST requests
- Model prediction completes in <2 seconds
- Logs show "✅ Models loaded successfully"

---

**Print this card & keep it handy during deployment! 📋**

*Last updated: May 2024*
