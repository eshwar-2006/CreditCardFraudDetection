# Credit Card Fraud Detection Web App

A complete Flask web application for credit card fraud detection using MongoDB, Scikit-learn, Random Forest, Bootstrap, and JavaScript.

## Step 1: Setup the Project

1. Open the project folder in VS Code: `c:\Users\Eshwar\OneDrive\Desktop\CreditCardFraudDetection`
2. Open Terminal in VS Code.
3. Check Python installation:
   ```powershell
   python --version
   ```
4. Create a new virtual environment:
   ```powershell
   python -m venv venv
   ```
5. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate
   ```
6. Install required libraries:
   ```powershell
   pip install -r requirements.txt
   ```

## Step 2: Folder Structure

The project contains the following folders:

- `dataset/` - place `creditcard.csv` here
- `models/` - stores training script and trained model
- `templates/` - HTML pages for Flask
- `static/` - CSS and JavaScript assets
- `database/` - MongoDB helper functions

## Step 3: Download the Kaggle Dataset

1. Download the Kaggle dataset from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
2. Save the file as `creditcard.csv` inside the `dataset` folder.
3. Confirm the file path: `dataset/creditcard.csv`

## Step 4: Train the Model

Run the training script:
```powershell
python models/train_model.py --data dataset/creditcard.csv --output models/model.pkl
```

This builds a Random Forest classifier and saves it to `models/model.pkl`.

## Step 5: Configure MongoDB Environment

Create a `.env` file at the project root with the following variables:

```env
SECRET_KEY=supersecretkey
MONGO_URI=mongodb://localhost:27017/fraud_detection
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin123!
```

If you use MongoDB Atlas, replace `MONGO_URI` with the connection string.

## Step 6: Run the Flask App

Start the app with:
```powershell
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Step 7: Deployment

### Render
1. Push the repository to GitHub.
2. Create a Render web service.
3. Use the `python app.py` start command.
4. Set environment variables in Render: `SECRET_KEY`, `MONGO_URI`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `PORT`.

### Railway
1. Connect your GitHub repository.
2. Choose Python as the deployment language.
3. Set environment variables in Railway.
4. Use the `python app.py` start command.

## Features

- Login and registration
- User and admin dashboards
- MongoDB transaction history
- Real-time fraud prediction
- Random Forest model
- Multithreaded batch processing
- Charts with Chart.js
- Responsive Bootstrap UI
- Dark mode
- Deployment-ready structure

## Notes

- Place the Kaggle dataset in `dataset/creditcard.csv` before training.
- Ensure the `models/model.pkl` file exists before running predictions.
- If you need an admin account, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`.
