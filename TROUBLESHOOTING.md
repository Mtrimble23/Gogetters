# 🔧 Simple Backend Troubleshooting Guide

## 🚨 **If simple_backend.py is not working, try these solutions:**

### **Option 1: Use the Enhanced Startup Script** ⭐ **RECOMMENDED**
```bash
python3 start_backend.py
```
This script checks everything and gives detailed error messages.

### **Option 2: Manual Step-by-Step**

1. **Check you're in the right directory:**
   ```bash
   ls -la simple_backend.py
   # Should show the file exists
   ```

2. **Install missing dependencies:**
   ```bash
   pip3 install --break-system-packages fastapi uvicorn aerospike
   ```

3. **Make sure Aerospike is running:**
   ```bash
   docker-compose up -d
   docker ps | grep aerospike
   ```

4. **Kill any existing backend processes:**
   ```bash
   pkill -f simple_backend.py
   ```

5. **Start the backend:**
   ```bash
   python3 simple_backend.py
   ```

### **Option 3: Run Diagnostics First**
```bash
python3 diagnose_backend.py
```
This will tell you exactly what's wrong.

---

## 🎯 **Common Issues and Solutions:**

### **Issue 1: "ModuleNotFoundError: No module named 'fastapi'"**
**Solution:**
```bash
pip3 install --break-system-packages fastapi uvicorn
```

### **Issue 2: "ModuleNotFoundError: No module named 'aerospike'"**
**Solution:**
```bash
pip3 install --break-system-packages aerospike
```

### **Issue 3: "Address already in use" or "Port 8000 busy"**
**Solution:**
```bash
pkill -f simple_backend.py
# Then try starting again
python3 simple_backend.py
```

### **Issue 4: "Connection refused" to Aerospike**
**Solution:**
```bash
# Start Aerospike
docker-compose up -d

# Check it's running
docker ps | grep aerospike
```

### **Issue 5: "Permission denied"**
**Solution:**
```bash
chmod +x simple_backend.py
python3 simple_backend.py
```

### **Issue 6: Backend starts but immediately stops**
**Solution:**
This usually means there's an import error. Use the enhanced startup script:
```bash
python3 start_backend.py
```

---

## ✅ **How to Verify It's Working:**

Once the backend starts, you should see:
```
🚀 Starting Aerospike Test Backend...
📊 API will be available at: http://localhost:8000
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test it with:**
```bash
# In another terminal:
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"Aerospike Test Backend"}

curl http://localhost:8000/risk-level/AAPL
# Should return risk analysis for AAPL
```

---

## 🆘 **If Nothing Works:**

1. **Try the simple test first:**
   ```bash
   python3 -c "print('Python is working')"
   ```

2. **Check Python version:**
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

3. **Try installing everything again:**
   ```bash
   pip3 install --break-system-packages --upgrade fastapi uvicorn aerospike
   ```

4. **Restart everything:**
   ```bash
   # Kill all Python processes
   pkill -f python3
   
   # Restart Aerospike
   docker-compose down
   docker-compose up -d
   
   # Try the enhanced startup script
   python3 start_backend.py
   ```

---

## 🎉 **Success Indicators:**

You'll know it's working when:
- ✅ No error messages during startup
- ✅ You see "Uvicorn running on http://0.0.0.0:8000"
- ✅ `curl http://localhost:8000/health` returns JSON
- ✅ The server stays running (doesn't immediately exit)

---

## 📞 **Still Having Issues?**

If your partner is still having problems, ask them to run:
```bash
python3 diagnose_backend.py
```

And share the output - this will tell us exactly what's wrong!