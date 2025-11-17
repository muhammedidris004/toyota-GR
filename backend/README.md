# Backend API Documentation

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Access API docs**: http://localhost:8000/docs

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /api/status` - API status and data loading state

### Data Loading
- `POST /api/data/load-sample?num_drivers=5&num_laps=50` - Load sample data
- `POST /api/data/upload` - Upload CSV file with racing data
- `GET /api/data/info` - Get information about loaded data

### Feature Engineering
- `GET /api/features/tire-wear/{driver_id}?current_lap=25` - Tire Wear Index
- `GET /api/features/consistency/{driver_id}?window=10` - Driver Consistency Score
- `GET /api/features/traffic/{driver_id}?current_lap=25` - Traffic Loss Factor
- `GET /api/features/track-evolution?window=20` - Track Evolution Rate
- `GET /api/features/pace-delta/{driver_id}?window=10` - Pace Delta Trend

### Strategy Predictions
- `GET /api/strategy/{driver_id}?current_lap=25&total_laps=50&include_undercut=true` - Complete strategy
- `GET /api/strategy/pit-window/{driver_id}?current_lap=25&total_laps=50` - Pit window recommendation
- `GET /api/strategy/undercut/{driver_id}/{target_driver_id}?current_lap=25&total_laps=50` - Undercut simulation
- `GET /api/strategy/pace-projection/{driver_id}?current_lap=25&projection_laps=10` - Pace projection

## Example Usage

### 1. Load Sample Data
```bash
curl -X POST "http://localhost:8000/api/data/load-sample?num_drivers=5&num_laps=50"
```

### 2. Get Strategy for Driver
```bash
curl "http://localhost:8000/api/strategy/DRIVER_01?current_lap=25&total_laps=50"
```

### 3. Get Tire Wear Index
```bash
curl "http://localhost:8000/api/features/tire-wear/DRIVER_01?current_lap=25"
```

## Data Format

### CSV Upload Format

Required columns:
- `lap_number` - Lap number
- `driver_id` - Driver identifier
- `lap_time` - Lap time in seconds

Optional columns:
- `tire_compound` - Soft, Medium, Hard
- `tire_age` - Number of laps on current tires
- `position` - Race position
- `sector_1_time`, `sector_2_time`, `sector_3_time` - Sector times
- `fuel_load` - Fuel load in kg
- `track_temperature`, `air_temperature` - Temperature data

## Module Structure

- `main.py` - FastAPI application and routes
- `models.py` - Pydantic data models
- `data_loader.py` - Data loading utilities
- `feature_engineering.py` - Feature calculation engine
- `ml_models.py` - Strategy prediction models

