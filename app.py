"""
Chinese Phishing Detection Model - Flask Application
Supports both REST API and Interactive Web Dashboard
"""

import os
import pickle
import math
import re
import socket
import requests
import warnings
import unicodedata
import json
import logging
from urllib.parse import urlparse, unquote
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ══════════════════════════════════════════════════════════════════
# MODEL LOADING
# ══════════════════════════════════════════════════════════════════

def load_models():
    """Load pickled model and feature names"""
    try:
        # Try to load from current directory (production)
        if os.path.exists('chinese_english_rf_model_v2.pkl'):
            with open('chinese_english_rf_model_v2.pkl', 'rb') as f:
                model = pickle.load(f)
            with open('chinese_english_feature_names_v2.pkl', 'rb') as f:
                feature_names = pickle.load(f)
        else:
            raise FileNotFoundError("Model files not found!")
        
        logger.info("✅ Models loaded successfully")
        return model, feature_names
    except Exception as e:
        logger.error(f"❌ Error loading models: {str(e)}")
        return None, None

# Load models at startup
MODEL, FEATURE_NAMES = load_models()

# ══════════════════════════════════════════════════════════════════
# PHISHING KEYWORDS & CONFIGS
# ══════════════════════════════════════════════════════════════════

ALL_PHISH_KEYWORDS = [
    # Simplified Chinese
    '登录','登陆','验证','账户','账号','安全','银行',
    '支付','密码','充值','提现','中奖','免费','活动',
    '优惠','抢购','领取','点击','立即','微信','支付宝',
    # Traditional Chinese
    '登錄','驗證','帳戶','帳號','銀行','密碼','充值',
    '提現','中獎','免費','優惠','搶購','領取','點擊','微信','支付寶',
    # English
    'login','verify','confirm','account','secure','banking',
    'update','signin','password','pay','urgent','verify',
]

CHINESE_TLDS = {
    '.cn','.中国','.中國','.com.cn','.net.cn','.org.cn',
    '.gov.cn','.edu.cn','.公司','.网络','.網絡',
    '.中文网','.商城','.商标','.我爱你','.sys',
}

# ══════════════════════════════════════════════════════════════════
# FEATURE EXTRACTION
# ══════════════════════════════════════════════════════════════════

def normalize_url(url):
    """Normalize URL by handling encoding and special characters"""
    url = url.lstrip('\ufeff').replace('\u200b','').replace('\u3000',' ')
    url = unicodedata.normalize('NFKC', url)
    try:
        url = unquote(url, encoding='utf-8')
    except Exception:
        pass
    return url.strip()


def get_prediction(url):
    """Extract features and generate prediction"""
    if MODEL is None or FEATURE_NAMES is None:
        return {
            'error': 'Model not loaded',
            'prediction': None
        }
    
    features = {}
    url = normalize_url(url)

    if not url.startswith('http'):
        url = 'http://' + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # ── Lexical features
    features['url_length'] = len(url)
    try:
        features['url_entropy'] = (
            sum(-(url.count(c)/len(url)) * math.log2(url.count(c)/len(url))
                for c in set(url)) if len(url) > 0 else 0
        )
    except:
        features['url_entropy'] = 0
    
    features['count_dots'] = url.count('.')
    features['count_hyphens'] = url.count('-')
    features['count_at'] = url.count('@')

    # ── Encoding / IDN features
    features['is_punycode'] = 1 if 'xn--' in domain else 0
    features['has_non_ascii'] = 1 if not all(ord(c) < 128 for c in url) else 0
    features['is_ip_address'] = (
        1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}(:\d+)?$', domain) else 0
    )

    # ── Chinese + English keyword check
    features['has_suspicious_keyword'] = (
        1 if any(kw in url for kw in ALL_PHISH_KEYWORDS) else 0
    )

    # ── DNS probe
    try:
        clean = domain.split('/')[0].replace('www.','')
        try:
            clean.encode('ascii')
        except UnicodeEncodeError:
            clean = clean.encode('idna').decode('ascii')
        socket.gethostbyname(clean)
        features['domain_age_days'] = 500
        features['has_dns_record'] = 1
    except Exception:
        features['domain_age_days'] = 5
        features['has_dns_record'] = 0

    # ── Content probe
    features['has_iframe'] = 0
    features['right_click_disabled'] = 0
    features['submits_to_email'] = 0
    try:
        r = requests.get(url, timeout=5,
                         headers={'User-Agent': 'Mozilla/5.0'},
                         verify=False)
        soup = BeautifulSoup(r.content, 'html.parser')
        features['has_iframe'] = 1 if soup.find_all('iframe') else 0
        if 'contextmenu' in r.text.lower() and 'return false' in r.text.lower():
            features['right_click_disabled'] = 1
        forms = soup.find_all('form', action=True)
        if any('mailto:' in (f.get('action') or '') for f in forms):
            features['submits_to_email'] = 1
    except Exception:
        pass

    # ── Structure features
    features['path_depth'] = len([p for p in parsed.path.split('/') if p])
    features['param_count'] = url.count('=')

    # Chinese SLD-aware subdomain count
    host_parts = domain.split('.')
    if (len(host_parts) >= 3
            and host_parts[-2] in ('com','net','org','gov','edu')):
        features['subdomain_count'] = max(0, len(host_parts) - 3)
    else:
        features['subdomain_count'] = max(0, len(host_parts) - 2)

    features['is_https'] = 1 if url.startswith('https') else 0

    # ── Composite scores
    legit_pts = 0
    if features['domain_age_days'] > 365:
        legit_pts += 40
    elif features['domain_age_days'] > 100:
        legit_pts += 20
    if features['has_dns_record']:
        legit_pts += 30
    if features['is_https']:
        legit_pts += 20
    if any(domain.endswith(t) for t in ['.gov.cn','.edu.cn','.org.cn']):
        legit_pts = min(100, legit_pts + 10)
    features['domain_legit_score'] = min(100, legit_pts)

    susp_pts = 0
    if features['has_suspicious_keyword']:
        susp_pts += 30
    if features['is_ip_address']:
        susp_pts += 25
    if features['count_at'] > 0:
        susp_pts += 20
    if features['count_hyphens'] > 3:
        susp_pts += 15
    if features['is_punycode']:
        susp_pts += 5
    if features['subdomain_count'] > 3:
        susp_pts += 5
    features['suspicion_score'] = min(100, susp_pts)
    features['very_long_url'] = 1 if features['url_length'] > 100 else 0

    # ── Predict
    try:
        X = pd.DataFrame([features])[FEATURE_NAMES]
        prediction = MODEL.predict(X)[0]
        proba = MODEL.predict_proba(X)[0]
        classes = list(MODEL.classes_)

        return {
            'prediction': prediction,
            'phish_prob': round(proba[classes.index('phishing')] * 100, 2),
            'legit_prob': round(proba[classes.index('legitimate')] * 100, 2),
            'features': features,
            'url': url,
            'error': None
        }
    except Exception as e:
        return {
            'error': f'Prediction error: {str(e)}',
            'prediction': None
        }


def build_feature_flags(features, url=''):
    """Generate human-readable feature flags"""
    red, green = [], []
    domain = urlparse(url).netloc.lower() if url else ''

    # Red flags
    if features['has_suspicious_keyword']:
        red.append('⚠ Suspicious keyword detected')
    if features['is_ip_address']:
        red.append('⚠ Domain is an IP address')
    if features['has_dns_record'] == 0:
        red.append('⚠ No DNS record found')
    if features['count_hyphens'] > 3:
        red.append('⚠ Too many hyphens')
    if features['very_long_url']:
        red.append('⚠ URL is very long (>100 chars)')
    if features['subdomain_count'] > 2:
        red.append('⚠ Many subdomains')
    if features['has_iframe']:
        red.append('⚠ Hidden iframes detected')
    if features['is_punycode']:
        red.append('⚠ Punycode domain (IDN)')
    if features['count_at'] > 0:
        red.append('⚠ @ symbol in URL')
    if features['suspicion_score'] > 60:
        red.append(f'⚠ High suspicion score: {features["suspicion_score"]}')

    # Green flags
    if features['is_https']:
        green.append('✔ Uses HTTPS encryption')
    if features['has_dns_record']:
        green.append('✔ Valid DNS record')
    if features['domain_age_days'] > 100:
        green.append('✔ Domain appears established')
    if not features['has_suspicious_keyword']:
        green.append('✔ No suspicious keywords')
    if features['domain_legit_score'] > 70:
        green.append(f'✔ High legitimacy score: {features["domain_legit_score"]}')
    if any(domain.endswith(t) for t in ['.gov.cn','.edu.cn','.org.cn']):
        green.append('✔ Government or Education TLD')

    return {'red_flags': red, 'green_flags': green}

# ══════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve main dashboard"""
    try:
        with open('multilingual_phishing_detection_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <html>
            <head><title>Chinese Phishing Detector</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>🛡️ Chinese Phishing Detection Dashboard</h1>
                <p>Dashboard HTML file not found. Use the API endpoint instead.</p>
                <pre>POST /api/scan
Content-Type: application/json
{"url": "https://example.com"}</pre>
            </body>
        </html>
        '''


@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint for phishing detection"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'error': 'Missing URL parameter',
                'example': {'url': 'https://example.com'}
            }), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        result = get_prediction(url)
        
        if result.get('error'):
            return jsonify(result), 400
        
        # Add feature flags
        flags = build_feature_flags(result['features'], url=result['url'])
        result['feature_flags'] = flags
        
        # Clean up features for JSON serialization
        result['features'] = {k: v for k, v in result['features'].items() 
                            if isinstance(v, (int, float, str, bool))}
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in /api/scan: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model_status = 'loaded' if MODEL is not None else 'not_loaded'
    return jsonify({
        'status': 'healthy',
        'model': model_status,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/batch', methods=['POST'])
def batch_scan():
    """Batch scan endpoint for multiple URLs"""
    try:
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({
                'error': 'Missing urls parameter',
                'example': {'urls': ['https://example.com', 'https://test.cn']}
            }), 400
        
        urls = data['urls']
        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({'error': 'urls must be a non-empty list'}), 400
        
        if len(urls) > 50:
            return jsonify({'error': 'Maximum 50 URLs per request'}), 400
        
        results = []
        for url in urls:
            result = get_prediction(url.strip())
            if not result.get('error'):
                flags = build_feature_flags(result['features'], url=result['url'])
                result['feature_flags'] = flags
                result['features'] = {k: v for k, v in result['features'].items() 
                                    if isinstance(v, (int, float, str, bool))}
            results.append(result)
        
        return jsonify({'results': results, 'total': len(results)}), 200
    
    except Exception as e:
        logger.error(f"Error in /api/batch: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        'title': 'Chinese Phishing Detection API',
        'version': '2.0',
        'endpoints': {
            'GET /': 'Serve interactive dashboard',
            'GET /api/health': 'Health check',
            'POST /api/scan': 'Scan single URL',
            'POST /api/batch': 'Scan multiple URLs (max 50)',
            'GET /api/docs': 'This documentation'
        },
        'examples': {
            'single_scan': {
                'endpoint': 'POST /api/scan',
                'request': {'url': 'https://www.baidu.com'},
                'response': {
                    'prediction': 'legitimate',
                    'phish_prob': 2.5,
                    'legit_prob': 97.5,
                    'features': {},
                    'feature_flags': {}
                }
            },
            'batch_scan': {
                'endpoint': 'POST /api/batch',
                'request': {'urls': ['https://example.com', 'https://test.cn']},
                'response': {'results': [], 'total': 2}
            }
        }
    }
    return jsonify(docs), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'Use GET /api/docs for API documentation',
        'available_endpoints': [
            'GET /',
            'GET /api/health',
            'GET /api/docs',
            'POST /api/scan',
            'POST /api/batch'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Model loaded: {MODEL is not None}")
    logger.info(f"Feature names loaded: {FEATURE_NAMES is not None}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
