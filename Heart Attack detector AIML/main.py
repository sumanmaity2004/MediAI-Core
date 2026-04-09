import pickle
import pandas as pd
import sklearn
from sensor_reader import read_sensor_data

# Load the trained model
with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

# Load the encoders dictionary
with open('encoders.pkl', 'rb') as file:
    encoders = pickle.load(file)


def get_user_input():
    print("\n--- Reading Heart Rate & SpO2 from sensor ---")
    heart_rate, oxygen_saturation = read_sensor_data()

    if heart_rate is None or oxygen_saturation is None:
        print("⚠️  Sensor read failed. Falling back to manual input.")
        heart_rate        = float(input("Enter Heart Rate: "))
        oxygen_saturation = float(input("Enter Oxygen Saturation: "))
    else:
        print(f"✅ Sensor readings captured → Heart Rate: {heart_rate}, Oxygen Saturation: {oxygen_saturation}")

    print("\n--- Please enter the remaining details manually ---")
    age       = int(input("Enter your Age: "))
    gender    = input("Enter Your Gender (Male/Female): ")
    weight_kg = float(input("Enter Weight (kg): "))
    height_m  = float(input("Enter Height (m): "))

    return {
        'Heart Rate':        heart_rate,
        'Oxygen Saturation': oxygen_saturation,
        'Age':               age,
        'Gender':            gender,
        'Weight (kg)':       weight_kg,
        'Height (m)':        height_m
    }


def preprocess_input(user_input):
    try:
        heart_rate        = user_input['Heart Rate']
        oxygen_saturation = user_input['Oxygen Saturation']
        age               = user_input['Age']
        weight_kg         = user_input['Weight (kg)']
        height_m          = user_input['Height (m)']

        if height_m == 0:
            raise ValueError("Height cannot be zero.")

        derived_bmi    = weight_kg / (height_m * height_m)
        gender_encoded = encoders['Gender'].transform(
            [user_input['Gender'].lower().capitalize()]
        )[0]

        processed_data = pd.DataFrame([
            [heart_rate, oxygen_saturation, age, gender_encoded,
             weight_kg, height_m, derived_bmi]
        ], columns=[
            'Heart Rate', 'Oxygen Saturation', 'Age', 'Gender',
            'Weight (kg)', 'Height (m)', 'Derived_BMI'
        ])

        return processed_data

    except ValueError as e:
        print(f"❌ Error processing input: {e}")
        return None
    except KeyError as e:
        print(f"❌ Missing expected input key: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during preprocessing: {e}")
        return None


def predict_risk():
    user_input = get_user_input()
    processed  = preprocess_input(user_input)

    if processed is None:
        print("❌ Prediction failed due to invalid input.")
        return

    probabilities   = model.predict_proba(processed)[0]
    risk_categories = encoders['Risk Category'].classes_

    print("\n--- Risk Category Prediction Probabilities ---\n")
    for i, prob in enumerate(probabilities):
        print(f"  {risk_categories[i]}: {round(prob * 100, 2)}%")

    predicted_class_index   = model.predict(processed)[0]
    predicted_risk_category = encoders['Risk Category'].inverse_transform(
        [predicted_class_index]
    )[0]
    print(f"\n🏥 Predicted Risk Category: {predicted_risk_category}")


predict_risk()