# Deployment Guide for AI-LTH

## Architecture Overview
- **Frontend**: React + Vite (Static Site)
- **Backend**: Flask API (Python Server)

These need to be deployed **separately** because:
- Frontend → Netlify (static hosting)
- Backend → Render/Railway/PythonAnywhere (Python hosting)

---

## 🚀 Step 1: Deploy Backend (Choose One Platform)

### **Option A: Deploy on Render.com (Recommended - FREE)**

1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `junaidaslam2006/AI-LTH`
4. Configure the service:
   - **Name**: `ai-lth-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables:
   - `OPENROUTER_VISION_API_KEY` = your vision key
   - `OPENROUTER_TEXT_API_KEY` = your text key
   - `PYTHON_VERSION` = `3.11.0`
6. Click **"Create Web Service"**
7. Wait for deployment (5-10 minutes)
8. **Copy your backend URL** (e.g., `https://ai-lth-backend.onrender.com`)

**Important**: Add `gunicorn` to requirements.txt:
```bash
cd backend
echo "gunicorn==21.2.0" >> requirements.txt
```

---

### **Option B: Deploy on Railway.app (FREE)**

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select `junaidaslam2006/AI-LTH`
4. Add these settings:
   - **Root Directory**: `/backend`
   - **Start Command**: `gunicorn app:app`
5. Add environment variables (same as above)
6. Deploy and copy your URL

---

### **Option C: PythonAnywhere (FREE - Easiest)**

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a Bash console
3. Clone your repo:
   ```bash
   git clone https://github.com/junaidaslam2006/AI-LTH.git
   cd AI-LTH/backend
   pip install -r requirements.txt
   ```
4. Set up a web app pointing to `app.py`
5. Add environment variables in the web app settings
6. Your URL will be: `https://yourusername.pythonanywhere.com`

---

## 🎨 Step 2: Deploy Frontend on Netlify

### **Method 1: Via Netlify Dashboard (Easiest)**

1. Go to [netlify.com](https://www.netlify.com) and sign in
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to GitHub and select `junaidaslam2006/AI-LTH`
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
5. **IMPORTANT**: Add environment variable:
   - Go to **Site settings** → **Environment variables**
   - Add: `VITE_API_URL` = `https://your-backend-url.onrender.com/api`
     (Use the URL from Step 1 + `/api`)
6. Click **"Deploy site"**
7. Wait for build to complete

### **Method 2: Via Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from root directory
cd c:\Users\kk\Desktop\HACKATHON
netlify deploy --prod

# Follow prompts and set:
# - Build command: npm run build
# - Publish directory: frontend/dist
```

Then add environment variable via dashboard (same as Method 1).

---

## ✅ Step 3: Test Your Deployment

1. Open your Netlify site URL (e.g., `https://ai-lth.netlify.app`)
2. Test the following:
   - ✅ Upload an image of medicine packaging
   - ✅ Ask a question about a medicine
   - ✅ Check if OCR and explanations work

---

## 🐛 Troubleshooting

### **Frontend shows blank page:**
- Check browser console for errors (F12)
- Verify `VITE_API_URL` environment variable is set correctly
- Make sure it ends with `/api` (e.g., `https://backend.com/api`)

### **API calls failing (CORS errors):**
Add CORS headers to backend `app.py` (already done in your code):
```python
from flask_cors import CORS
CORS(app)
```

### **Backend not starting:**
- Check Render/Railway logs for errors
- Verify all environment variables are set
- Make sure `gunicorn` is in `requirements.txt`

### **Build fails on Netlify:**
- Check build logs in Netlify dashboard
- Ensure `package.json` has correct scripts
- Verify Node version is 18+ (set in `netlify.toml`)

---

## 📝 Important Notes

1. **Free Tier Limitations:**
   - Render: Backend sleeps after 15 min of inactivity (first request takes ~30s to wake up)
   - Netlify: 300 build minutes/month, 100GB bandwidth
   - Railway: $5 free credit/month

2. **Environment Variables:**
   - Frontend: `VITE_API_URL` (must start with `VITE_`)
   - Backend: `OPENROUTER_VISION_API_KEY`, `OPENROUTER_TEXT_API_KEY`

3. **Data Files:**
   - Your CSV/PDF files in `backend/data/` will be included in deployment
   - They're gitignored but you can upload them manually to hosting platform

---

## 🔄 Future Updates

When you push code changes:
1. **Backend**: Render/Railway auto-deploys from GitHub
2. **Frontend**: Netlify auto-deploys from GitHub
3. Both will rebuild automatically on push to `main` branch

---

## 🆘 Still Not Working?

Share these details:
1. Netlify build logs (Settings → Deploys → [Latest deploy] → Deploy log)
2. Render/Railway backend logs
3. Browser console errors (F12 → Console tab)
4. Exact error message you're seeing
