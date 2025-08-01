SUPPORTED_FORMATS = [
    "JSON", "CSV", "TSV", "YAML", "XML", "Parquet"
]

PREDEFINED_TOPICS = {
    "Citizen": {
        "description": "Citizen profiles with personal information",
        "fields": ["name", "email", "age", "address", "phone", "job", "company"]
    },
    "Products": {
        "description": "E-commerce product data",
        "fields": ["name", "price", "category", "description", "sku", "stock", "rating"]
    },
    "Orders": {
        "description": "Order and transaction data",
        "fields": ["order_id", "customer", "product", "quantity", "price", "date", "status"]
    },
    "Employee": {
        "description": "Employee records",
        "fields": ["name", "employee_id", "department", "salary", "hire_date", "email"]
    },

    "Healthcare": {
        "description": "Patient and medical records",
        "fields": ["patient_id", "name", "age", "diagnosis", "doctor", "date", "medication"]
    },
    "Education": {
        "description": "Student and course data",
        "fields": ["student_id", "name", "course", "grade", "semester", "gpa", "credits"]
    },
    "Real_Estate": {
        "description": "Property listings",
        "fields": ["property_id", "address", "price", "bedrooms", "bathrooms", "area", "type"]
    },
    "Social_Media": {
        "description": "Social media posts and interactions",
        "fields": ["user", "post_content", "likes", "shares", "comments", "timestamp", "platform"]
    },
    "Iot_Sensors": {
        "description": "IoT sensor readings",
        "fields": ["sensor_id", "temperature", "humidity", "pressure", "timestamp", "location"]
    },
    "Logistics": {
        "description": "Shipping and delivery data",
        "fields": ["tracking_id", "origin", "destination", "weight", "status", "estimated_delivery"]
    },
    "Banking": {
        "description": "Banking transactions",
        "fields": ["account_number", "transaction_type", "amount", "balance", "branch", "timestamp"]
    },
    "Pilot_Log_Book": {
        "description": "Pilot flight log book data",
        "fields": [
            "flight id", "pilot name", "pilot license number", "pilot role", "aircraft type",
            "departure airport", "arrival airport", "flight date", "departure time",
            "arrival time", "flight time hours", "flight number", "passenger count",
            "crew count", "flight type", "weather conditions", "fuel consumption",
            "night flight", "remarks"
        ]
    },
    "Weather": {
        "description": "Weather data for various locations",
        "fields": [
            "record_id",
            "location",
            "observation_time",
            "temperature_c",
            "weather_condition",
            "humidity_percent",
            "pressure_mb",
            "wind_speed_kmh",
            "wind_direction",
            "precipitation_mm",
            "is_night",
            "visibility_km",
            "cloud_cover_percent",
            "dew_point_c"
        ]
    }
}

# Custom topic template for user-defined topics
# CUSTOM_TOPIC_TEMPLATE = {
#     "description": "User-defined custom data",
#     "fields": ["id", "name", "value", "category", "date", "status", "description"]
# }
