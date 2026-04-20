# Tailwind CSS Production Setup

## Current Status
The home page is currently using Tailwind CSS via CDN, which shows a warning in production.

## Production Setup Instructions

### Option 1: Install Tailwind CSS as a PostCSS Plugin

1. **Install dependencies:**
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   ```

2. **Initialize Tailwind CSS:**
   ```bash
   npx tailwindcss init -p
   ```

3. **Configure `tailwind.config.js`:**
   ```javascript
   /** @type {import('tailwindcss').Config} */
   module.exports = {
     content: [
       "./home/templates/**/*.html",
       "./templates/**/*.html",
       "./static/**/*.js"
     ],
     darkMode: 'class',
     theme: {
       extend: {
         colors: {
           'accent': '#ef4444',
           'accent-dark': '#dc2626',
           'eclick-600': '#dc2626',
           'eclick-700': '#b91c1c',
         }
       }
     },
     plugins: [],
   }
   ```

4. **Create `static/css/input.css`:**
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

5. **Build CSS:**
   ```bash
   npx tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --minify
   ```

6. **Replace CDN in HTML:**
   Replace:
   ```html
   <script src="https://cdn.tailwindcss.com"></script>
   ```
   With:
   ```html
   <link rel="stylesheet" href="/static/css/tailwind.css">
   ```

### Option 2: Use Django Management Command

1. **Create management command:**
   ```bash
   python manage.py build_tailwind
   ```

2. **Add to `package.json`:**
   ```json
   {
     "scripts": {
       "build-css": "tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --minify",
       "watch-css": "tailwindcss -i ./static/css/input.css -o ./static/css/tailwind.css --watch"
     }
   }
   ```

### Option 3: Keep CDN (Quick Fix)
If you want to keep using the CDN for now, the warning can be ignored as it doesn't affect functionality.

## Benefits of Production Setup
- ✅ No console warnings
- ✅ Better performance (smaller file size)
- ✅ Offline capability
- ✅ Better caching
- ✅ Custom configuration

## Current Performance
- LCP: ~520ms (Good)
- FID: ~0.8ms (Excellent)
- The page is performing well even with CDN
