# Render Deployment Guide

## 🚀 Deploy to Render

### Prerequisites
- GitHub account
- Render account (render.com)
- MongoDB Atlas database

### Step 1: Push to GitHub
1. Create a new repository on GitHub
2. Push your code to the repository:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Choose the repository containing your app

### Step 3: Configure the Service
**Basic Settings:**
- **Name**: `barcode-scanner` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `Website` (if your app is in Website folder)

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### Step 4: Environment Variables
Add these environment variables in Render dashboard:

| Key | Value |
|-----|-------|
| `MONGODB_URL` | `mongodb+srv://admin:Admin%40123@cluster0.lgew08w.mongodb.net/Spiro` |
| `DATABASE_NAME` | `Council` |
| `COLLECTION_NAME` | `students` |
| `DEBUG` | `false` |

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Your app will be available at: `https://your-service-name.onrender.com`

## 📱 Mobile Access
Once deployed, you can access your barcode scanner from any device:
- Share the Render URL with your team
- Works on mobile browsers
- Supports camera access on HTTPS

## 🔒 Security Notes
- Your MongoDB credentials are included in environment variables
- Consider creating a dedicated MongoDB user for production
- Enable MongoDB IP whitelist if needed

## 🛠️ Troubleshooting

### Common Issues:
1. **Build Fails**: Check `requirements.txt` format
2. **App Won't Start**: Verify `Procfile` and start command
3. **Database Connection**: Check MongoDB URL and credentials
4. **Camera Not Working**: Ensure HTTPS is enabled (Render provides this automatically)

### Logs:
- Check Render dashboard logs for detailed error messages
- MongoDB connection status is logged on startup

## 📊 Monitoring
- Render provides basic metrics
- Monitor MongoDB Atlas usage
- Check scan logs in your app dashboard

## 🔄 Updates
To update your deployed app:
1. Push changes to your GitHub repository
2. Render will automatically redeploy

## 🌐 Custom Domain (Optional)
- Upgrade to Render Pro plan
- Add your custom domain in settings
- Configure DNS records

## 📞 Support
- Render Docs: https://render.com/docs
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com/
