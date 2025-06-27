# Railway Deployment Guide (Recommended)

## Step-by-Step Instructions

1. **Go to railway.app** and create a free account
2. **Click "New Project"**
3. **Choose "Deploy from GitHub repo"** 
4. **Connect your GitHub account** (if you haven't already)
5. **Upload your code to GitHub** or use "Empty Project" and upload files
6. **Railway will automatically detect Python** and install dependencies
7. **Add environment variable**: 
   - Key: `PORT` 
   - Value: `8000`
8. **Railway automatically runs**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Why Railway Works Best:
- Native Python/Streamlit support
- Automatic dependency installation
- Built-in port handling
- Free tier available
- Deploys in 2-3 minutes

## Your app will be live at: `your-app-name.up.railway.app`