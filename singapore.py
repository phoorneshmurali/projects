import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Function to load data (optimized with caching)
@st.cache_data(hash_funcs={pd.DataFrame: lambda _: None})
def load_data():
    return pd.read_csv("E:\harvesting\.venv\singapore.csv")

# Load the dataset
df = load_data()

# Label encoding for categorical columns
label_encoders = {}
for col in ['town', 'flat_type', 'street_name']:
    label_encoder = LabelEncoder()
    df[col + '_encoded'] = label_encoder.fit_transform(df[col])
    label_encoders[col] = label_encoder

feature_columns = ['floor_area_sqm', 'remaining_lease', 'town_encoded', 'flat_type_encoded', 'street_name_encoded']

models = {
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Random Forest': RandomForestRegressor(random_state=42),
    'XGBoost': XGBRegressor(n_estimators=100, random_state=42)
}

def predict_resale_price(model, features):
    # Make predictions using the trained model
    predicted_price = model.predict(features)
    return predicted_price[0]

# Main Streamlit app
def main():
    st.title("Singapore Resale Flat Price Prediction")

    # Sidebar with user input
    st.sidebar.header("User Input")

    # Collect user inputs
    floor_area_sqm = st.sidebar.slider("Floor Area (sqm)", min_value=31.0, max_value=280.0, value=120.0)
    remaining_lease = st.sidebar.slider("Remaining Lease (years)", min_value=1, max_value=99, value=50)

    # Display user input
    st.sidebar.subheader("User Input:")
    user_input_summary = pd.DataFrame({
        'floor_area_sqm': [floor_area_sqm],
        'remaining_lease': [remaining_lease]
    })
    st.sidebar.write(user_input_summary)

    # Model selection dropdown
    model_selection = st.sidebar.selectbox("Select Model", list(models.keys()))

    # Choose the selected model
    model = models[model_selection]

    # Encode user input
    user_input_encoded = [floor_area_sqm, remaining_lease]
    for col, encoder in label_encoders.items():
        user_input_encoded.append(encoder.transform([st.sidebar.selectbox(f"{col}:", df[col].unique())])[0])

    # Fit the model
    X = df[feature_columns]
    y = df['resale_price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    # Button to make predictions
    if st.sidebar.button("Predict Resale Price"):
        # Make predictions using the selected model
        features = [user_input_encoded]
        predicted_price = predict_resale_price(model, features)

        # Display the predicted price
        st.success(f"Predicted Resale Price: SGD {predicted_price:,.2f}")

        # Evaluate the model
        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions, squared=False)
        r_squared = r2_score(y_test, predictions)

        # Display evaluation metrics
        st.subheader("Model Evaluation Metrics:")
        st.write(f'Mean Absolute Error (MAE): {mae}')
        st.write(f'Mean Squared Error (MSE): {mse}')
        st.write(f'Root Mean Squared Error (RMSE): {rmse}')
        st.write(f'R-squared: {r_squared}')

# Run the Streamlit app
if __name__ == "__main__":
    main()
    