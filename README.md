# GR Race Strategist AI 🏁

**Real-time pit-window, tire-wear, pace-projection, and undercut/overcut prediction system for Toyota GR "Hack the Track" Devpost Hackathon**

## 🚀 Quick Start

### One Command to Run Everything

```bash
./start.sh
```

Or using npm:

```bash
npm start
```

This will:
- ✅ Start the backend server on http://localhost:8000
- ✅ Start the frontend server on http://localhost:3000
- ✅ Open your browser automatically
- ✅ Show status of both servers

**Press Ctrl+C to stop both servers**

---

## 📋 Manual Setup (First Time)

### Prerequisites

1. **Data-GR folder is REQUIRED**: Place the TRD hackathon datasets in a `Data-GR/` folder inside the `backend/` folder
2. **Python 3.10+** installed
3. **Node.js 18+** installed

### Installation

If you haven't set up the project yet:

```bash
npm run install
```

This installs:
- Python dependencies (backend)
- Node.js dependencies (frontend)

**Note**: The application will NOT work without the `Data-GR/` folder containing the TRD hackathon datasets.

---

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Next.js 14+ (TypeScript + Tailwind CSS)
- **ML/Analytics**: Python (pandas, scikit-learn, numpy)
- **Real-time**: WebSockets for live race data

## ⚠️ IMPORTANT: Data Requirements

**This application ONLY uses REAL-TIME TRD hackathon data.**
- ❌ **NO mock data**
- ❌ **NO sample data**
- ❌ **NO AI-generated data**
- ✅ **ONLY real TRD hackathon datasets from Data-GR folder**

**The `Data-GR/` folder is REQUIRED** for the application to work. It must be placed in the `backend/` folder.

## 📁 Project Structure

```
toyota-GR/
├── backend/          # FastAPI backend
│   ├── Data-GR/     # ⚠️ REQUIRED: TRD hackathon datasets (real-time data only)
│   ├── main.py      # FastAPI app entry point
│   └── ...          # Other backend files
├── frontend/         # Next.js frontend
├── notebooks/        # Jupyter notebooks for data exploration & ML
├── docs/            # Documentation and Devpost materials
├── start.sh         # Start script (run both servers)
└── README.md        # This file
```

## 🎯 Features

### 1. Race Engineer Console
Real-time dashboard with live race metrics and strategy recommendations.
- **Interactive Charts**: Tire wear progression and pace projection graphs
- **Pit Window Recommendations**: Optimal timing with urgency levels
- **Undercut Opportunities**: Strategic overtaking analysis

### 2. Driver Comparison
Compare multiple drivers' performance, tire wear, and pace projections.
- **Side-by-Side Analysis**: Compare up to 5 drivers simultaneously
- **Visual Charts**: Bar charts for TWI, Consistency, and Traffic Loss
- **Performance Metrics**: Detailed breakdown of each driver's performance

### 3. Strategy Replay
Review and analyze past race strategies with visualizations.
- **Timeline View**: See how strategy evolved throughout the race
- **Pit Window History**: Review pit stop recommendations at each lap
- **Pace Analysis**: Track pace projections over time

## 📊 Supported Tracks

- COTA (Circuit of the Americas)
- Sonoma (Sonoma Raceway)
- barber (Barber Motorsports Park)
- indianapolis (Indianapolis Motor Speedway)
- road-america (Road America)
- sebring (Sebring International Raceway)
- virginia-international-raceway (VIR)

## 🎨 Design System

**Toyota GR Colors**:
- **Black**: `#000000`
- **GR Red**: `#E60012`
- **Asphalt Grey**: `#2C2C2C`
- **Neon Accent**: `#00FF88`

## 📝 API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏆 Hackathon Submission

Built for **Toyota GR "Hack the Track" Devpost Hackathon**

## 📝 License

MIT License

## 👥 Contributors

Built with ❤️ for the racing community

---

## 🛠️ Troubleshooting

### Port Already in Use?
```bash
# Kill processes on ports 3000 and 8000
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Backend Not Starting?
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Not Starting?
```bash
cd frontend
npm install
npm run dev
```

### Check Logs
- Backend logs: `backend.log`
- Frontend logs: `frontend.log`
