# 🚀 Render Deployment Files

This folder contains all files related to deploying FozCaribe v2.0 on Render.com.

## 📁 Files

| File | Description |
|------|-------------|
| `DEPLOY_RENDER.md` | Complete step-by-step deployment guide |
| `prepare_render.py` | Pre-deployment validation script |
| `Procfile` | Process file for Render deployment |
| `build.sh` | Build script for setting up the environment |
| `render.yaml` | Render service configuration |

## 🎯 Quick Start

1. **Prepare for deployment:**
   ```bash
   python prepare_render.py
   ```

2. **Follow the detailed guide:**
   Read `DEPLOY_RENDER.md` for complete instructions

3. **Deploy on Render:**
   - Connect your GitHub repository
   - Use files in this folder for configuration
   - Set environment variables as documented

## 📋 Requirements

- GitHub repository connected to Render
- Google Cloud credentials (as environment variable)
- Python 3.9+ runtime

---

💡 **Tip:** Always run `prepare_render.py` before deploying to validate your setup!
