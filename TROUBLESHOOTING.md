# 🔧 Railway Deployment Troubleshooting Guide

## Quick Diagnosis

### Your app status on Railway:
- 🟢 **Green/Active** = App is running correctly
- 🟠 **Yellow** = App is starting or redeploying
- 🔴 **Red** = App has crashed or failed to start

**Solution**: Click on the app card → "View Logs" to see error messages

---

## Common Errors & Fixes

### 1. ❌ "ModuleNotFoundError: No module named 'sklearn'"

**Cause**: Dependency not listed in `requirements.txt`

**Fix**:
```bash
# Add to requirements.txt:
scikit-learn==1.3.2

# Then:
git add requirements.txt
git commit -m "Fix: add scikit-learn dependency"
git push origin main

# Railway will re-deploy automatically
```

**Verify locally**:
```bash
pip install -r requirements.txt
python app.py
```

---

### 2. ❌ "FileNotFoundError: Model files not found"

**Cause**: Pickle files are not in the repository or not uploaded to Railway

**Fix**:

```bash
# Check files exist locally
ls -la *.pkl

# If missing, copy correct files
cp path/to/chinese_english_rf_model_v2.pkl .
cp path/to/chinese_english_feature_names_v2.pkl .

# Add to git (IMPORTANT!)
git add *.pkl
git status  # Verify files show as "new file"

git commit -m "Add: ML model pickle files"
git push origin main

# Wait 1-2 minutes for re-deploy
```

**Check Railway logs**:
1. Dashboard → Your app
2. Click "View Logs"
3. Look for: "✅ Models loaded successfully"
4. If not present, file path is wrong

---

### 3. ❌ "Build failed: requirements not found"

**Cause**: `requirements.txt` is missing or not in root directory

**Fix**:
```bash
# Verify file exists in root:
ls -la requirements.txt

# If missing, create from template:
cat > requirements.txt << EOF
Flask==3.0.0
Werkzeug==3.0.1
pandas==2.0.3
scikit-learn==1.3.2
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
gunicorn==21.2.0
EOF

# Add and push
git add requirements.txt
git commit -m "Add: Python requirements"
git push origin main
```

---

### 4. ❌ "Procfile not found"

**Cause**: Missing or incorrectly named Procfile

**Fix**:
```bash
# Create Procfile (exactly this name, no .txt)
cat > Procfile << EOF
web: gunicorn --workers 4 --timeout 120 --bind 0.0.0.0:\$PORT app:app
EOF

# Verify case-sensitive name
ls -la Procfile  # Should show as "Procfile", not "Procfile.txt"

# Add and push
git add Procfile
git commit -m "Add: Railway Procfile"
git push origin main
```

---

### 5. ❌ "502 Bad Gateway"

**Cause**: App crashes after starting (gunicorn fails to run `app:app`)

**Fix**:

**Step 1**: Test locally
```bash
pip install -r requirements.txt
python app.py
# Visit http://localhost:5000
# If error here, fix before deploying
```

**Step 2**: Check Railway logs
```
Dashboard → Deployments → [Latest] → View Logs
Look for: "Failed to find application: app:app"
```

**Step 3**: Verify `app.py` structure
```python
# Must have this at bottom:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

**Step 4**: Check Procfile syntax
```bash
# Should be:
web: gunicorn --workers 4 --timeout 120 --bind 0.0.0.0:$PORT app:app
# NOT:
web: gunicorn app.py
web: python app.py
```

---

### 6. ❌ "H18 - Request Timeout (30s)"

**Cause**: Model inference takes >30 seconds

**Fix**:

**Option A**: Increase timeout in Procfile
```bash
# Edit Procfile:
web: gunicorn --workers 2 --timeout 240 --bind 0.0.0.0:$PORT app:app
#                                  ^^^
#                         Increased from 120 to 240

git add Procfile
git commit -m "Increase: gunicorn timeout to 240s"
git push origin main
```

**Option B**: Reduce workers (use less memory)
```bash
web: gunicorn --workers 2 --timeout 120 --bind 0.0.0.0:$PORT app:app
#                     ^
#                Changed from 4 to 2
```

---

### 7. ❌ "No such file or directory: 'multilingual_phishing_detection_dashboard.html'"

**Cause**: Dashboard HTML file not in repository

**Fix**:
```bash
# Verify file exists
ls -la *.html

# If missing, copy it:
cp /path/to/multilingual_phishing_detection_dashboard.html .

# Add to git
git add multilingual_phishing_detection_dashboard.html
git commit -m "Add: phishing detection dashboard"
git push origin main
```

**Test locally**:
```bash
python app.py
# Visit http://localhost:5000
# Should see dashboard UI
```

---

### 8. ❌ "AttributeError: 'NoneType' object"

**Cause**: Model failed to load, but app continues

**Fix**:
1. Check `app.py` loads models at startup:
```python
MODEL, FEATURE_NAMES = load_models()  # This line at top level
```

2. Check Railway logs for model loading error
3. Verify pickle files are not corrupted:
```bash
python -c "import pickle; pickle.load(open('chinese_english_rf_model_v2.pkl', 'rb'))"
# Should not error
```

---

### 9. ❌ "OSError: Model expects 21 features, got 20"

**Cause**: Feature names don't match model

**Fix**:
1. Verify both pickle files are compatible
2. Run locally to test:
```bash
python -c "
import pickle
with open('chinese_english_rf_model_v2.pkl', 'rb') as f:
    model = pickle.load(f)
with open('chinese_english_feature_names_v2.pkl', 'rb') as f:
    features = pickle.load(f)
print(f'Model expects {model.n_features_in_} features')
print(f'Feature names has {len(features)} features')
"
```

3. If mismatch, regenerate both files together

---

### 10. ❌ "App stuck in redeployment loop"

**Cause**: Deployment script crashes immediately

**Fix**:
```bash
# Stop deployment
# Click "Settings" → "Stop Deploy"

# Check recent commits
git log --oneline -5

# Revert to last working version
git revert HEAD
git push origin main

# Or revert specific file
git checkout HEAD~1 app.py
git commit -m "Revert: broken app.py"
git push origin main
```

---

## Step-by-Step Diagnostics

If error message is unclear, follow this:

### Step 1: Check Railway Logs
```
Dashboard → Your Project → Deployments → [Latest] → View Logs
```
**What to look for:**
- ❌ Red text = error
- ⚠️ Yellow = warning
- ✅ Green = success

### Step 2: Test Locally
```bash
# Clone from your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO
cd YOUR_REPO

# Install deps
pip install -r requirements.txt

# Try running
python app.py

# Test in browser
open http://localhost:5000
```

If local test fails, the error is in your code, not Railway.

### Step 3: Verify Git Status
```bash
# Ensure all files are tracked
git status

# Should show no "Untracked files" except __pycache__, .env
git log --oneline -3  # Check recent commits

# Ensure files are on GitHub
git remote -v
git branch -vv
```

### Step 4: Check File Sizes
```bash
# Model file should be ~219 KB
ls -lh *.pkl

# If 0 bytes, file is corrupted - recopy
# If >1MB, something is wrong
```

### Step 5: Verify Environment
On Railway dashboard, check Variables:
```
FLASK_ENV=production  ✅
PORT=8000 (auto-set)   ✅
```

---

## Quick Emergency Fix

If your app crashes on Railway and you need it back ASAP:

```bash
# 1. Revert to last known good state
git revert HEAD --no-edit
git push origin main

# 2. Or reset to specific commit
git reset --hard COMMIT_HASH
git push origin main -f

# 3. Railway will re-deploy automatically

# 4. Check status
# Dashboard should show green checkmark within 2 minutes
```

---

## Getting Help

### Before asking for help, gather this info:
1. **Railway deployment logs** (copy full error)
2. **Your git log** (`git log --oneline -5`)
3. **Local test result** (does `python app.py` work locally?)
4. **File listing** (`ls -lah *.pkl`)
5. **Requirements check** (`pip install -r requirements.txt`)

### Useful Links:
- [Railway Docs - Troubleshooting](https://docs.railway.app/)
- [Flask Error Handling](https://flask.palletsprojects.com/en/latest/errorhandling/)
- [Common Buildpack Errors](https://docs.railway.app/troubleshooting/)

---

## Prevention Checklist

Before pushing to GitHub:
- [ ] Test locally: `python app.py` works without errors
- [ ] All required files exist: `*.pkl`, `*.html`, `requirements.txt`, `Procfile`
- [ ] File sizes correct: `*.pkl` not 0 bytes
- [ ] Git status clean: no uncommitted changes
- [ ] `git push` successful: check on GitHub.com
- [ ] No typos in filenames (case-sensitive!)

---

**Need more help?**
1. Check Railway logs first (99% of issues shown there)
2. Test locally to isolate the problem
3. Verify all required files are on GitHub
4. Check file permissions and sizes
5. Try the revert emergency fix

**You've got this! 💪**
