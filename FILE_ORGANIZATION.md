# 📁 VTHacks26 File Organization for Partners

## ✅ **ESSENTIAL FILES (Partner Must Have)**

### **Core Backend:**
- `simple_backend.py` ⭐ - Main working backend server
- `requirements.txt` ⭐ - Dependencies
- `docker-compose.yml` ⭐ - Database setup

### **Documentation:**
- `PARTNER_COMMANDS.md` ⭐ - Exact setup commands
- `FINAL_HANDOFF.md` ⭐ - Complete summary

### **Verification:**
- `partner_verify.py` ⭐ - Quick verification script
- `test_backend_clean.py` ⭐ - Comprehensive tests

---

## 🔧 **HELPFUL SETUP FILES (Recommended to Keep)**

### **Automated Setup:**
- `setup_aerospike_backend.py` 📦 - Automated dependency installation
- `setup_aerospike_namespace.py` 📦 - Database namespace setup
- `start_backend.py` 📦 - Enhanced startup script

### **Alternative Backend:**
- `run_backend.py` 📦 - Alternative startup method
- `backend_server.py` 📦 - Production version (more complex)

### **Troubleshooting:**
- `diagnose_backend.py` 🔧 - System diagnostics

---

## 📚 **DOCUMENTATION (Optional)**

### **Detailed Guides:**
- `PARTNER_SETUP.md` 📖 - Detailed setup guide
- `DEPLOYMENT_GUIDE.md` 📖 - Complete deployment info
- `TRANSFER_GUIDE.md` 📖 - File transfer instructions
- `STARTUP_NOTES.md` 📖 - Startup method notes

---

## 🗑️ **FILES TO REMOVE (Development/Testing Only)**

### **Log Files:**
- `*.log` - Development logs
- `backend.log`, `backend_new.log`, etc.

### **Development Testing:**
- `test_aerospike_direct.py` - Direct Aerospike testing
- `test_aerospike_integration.py` - Integration testing
- `test_backend.py` - Old test file
- `simple_test.py` - Development test
- `final_verification.py` - Development verification

### **Legacy/Duplicate Files:**
- `AEROSPIKE_READY.md` - Development notes
- `BACKEND_README.md` - Superseded by PARTNER_COMMANDS.md
- `PROJECT_STATUS.txt` - Development tracking
- `TROUBLESHOOTING.md` - Superseded by other docs
- `PARTNER_SETUP_GUIDE.md` - Duplicate

### **Development Scripts:**
- `curl_examples.sh` - Development testing
- `manage.sh` - Development management
- `test_risk_api.py` - Specific API testing
- `gemini_stock_api.py` - Alternative implementation

### **Original Components:**
- `financial_risk_analyzer.py` - Original script (superseded by backend)
- `sentiment_analyzer.py` - Component (integrated into backend)
- `test_sentiment.py` - Component test

---

## 🎯 **RECOMMENDED CLEANUP**

Keep the setup files! Remove only:

```bash
# Remove log files
rm -f *.log

# Remove development test files
rm -f test_aerospike_direct.py test_aerospike_integration.py
rm -f test_backend.py simple_test.py final_verification.py
rm -f test_risk_api.py test_sentiment.py

# Remove duplicate documentation
rm -f AEROSPIKE_READY.md BACKEND_README.md PROJECT_STATUS.txt
rm -f TROUBLESHOOTING.md PARTNER_SETUP_GUIDE.md

# Remove development scripts
rm -f curl_examples.sh manage.sh gemini_stock_api.py

# Remove directories not needed
rm -rf __pycache__ backend/ src/ stock-dashboard/ venv/
```

---

## ✅ **What Partner Gets After Cleanup:**

### **Core Files:**
- Working backend + dependencies + database setup
- Clear setup instructions
- Verification tools

### **Helper Files:**
- Automated setup scripts
- Alternative startup methods  
- Troubleshooting tools

### **Documentation:**
- Complete guides for different experience levels
- Startup method explanations

**This gives your partner everything they need while removing development clutter!**