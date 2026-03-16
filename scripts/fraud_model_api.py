import pickle
import pandas as pd
import os

# Load the model globally so it's only loaded once when the model is deployed
MODEL_PATH = "models/fraud_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Run training script first.")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

def predict(args):
    """
    Standard CML predict function.
    Args:
        args (dict): Dictionary of input features. Expects:
                     {"amount": float, "age": int, "credit_limit": float, "tx_hour": int}
    Returns:
        dict: Prediction results including probability and classification.
    """
    # Convert input dict to DataFrame for Scikit-Learn
    input_df = pd.DataFrame([args])
    
    # Ensure correct column order
    input_df = input_df[['amount', 'age', 'credit_limit', 'tx_hour']]
    
    # Run Prediction
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1] # Probability of being Fraud (class 1)
    
    status = "FLAGGED" if prediction == 1 else "AUTHORIZED"
    
    return {
        "prediction": int(prediction),
        "fraud_probability": float(probability),
        "status": status,
        "explanation": f"Fraud probability is {probability:.2%}. Transaction is {status}."
    }

# --- Example Test Call (Optional for local testing) ---
# if __name__ == "__main__":
#     test_input = {"amount": 25000.0, "age": 45, "credit_limit": 5000.0, "tx_hour": 14}
#     print(predict(test_input))
