# 🎮 King's Valley Game - Free Deployment Guide

Deploy your King's Valley multiplayer game for **FREE** using modern cloud platforms!

## 🌟 Deployment Options

### Option 1: Vercel + MongoDB Atlas (Recommended)
- **Frontend**: Free on Vercel
- **Backend**: Free serverless functions on Vercel  
- **Database**: Free MongoDB Atlas (512MB)
- **Custom URL**: Free .vercel.app subdomain

### Option 2: Railway + MongoDB Atlas
- **Full-stack**: Free tier on Railway
- **Database**: Free MongoDB Atlas
- **Custom URL**: Free .railway.app subdomain

## 🚀 Quick Start with Vercel (5 minutes)

### Step 1: Setup MongoDB Atlas (Free)
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create free account
3. Create new cluster (free M0 tier)
4. Create database user
5. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### Step 2: Deploy Frontend to Vercel
1. Go to [Vercel](https://vercel.com)
2. Connect your GitHub account
3. Import your repository
4. Set environment variables:
   - `REACT_APP_BACKEND_URL` = `https://your-app.vercel.app`
5. Deploy!

### Step 3: Deploy Backend to Vercel
1. In same Vercel project, add backend
2. Set environment variables:
   - `MONGO_URL` = your MongoDB Atlas connection string
   - `DB_NAME` = `kings_valley`
3. Deploy backend as serverless functions

## 📁 File Structure for Deployment
```
kings-valley-game/
├── frontend/          # React app
├── api/              # Backend serverless functions  
├── vercel.json       # Vercel configuration
└── package.json      # Root package.json
```

## 🔧 Environment Variables

### Frontend (.env)
```
REACT_APP_BACKEND_URL=https://your-app.vercel.app
```

### Backend (.env)
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=kings_valley
```

## 🎯 Result
- **Free hosting** for your multiplayer game
- **Public URL** to share with kids and families
- **Automatic scaling** - handles traffic spikes
- **SSL included** - secure HTTPS connection

## 📞 Support
Having issues? The deployment should take about 5-10 minutes total!