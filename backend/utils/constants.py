SUPPORTED_FORMATS = [
    "JSON", "CSV", "TSV", "YAML","XML", "Parquet"
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
    }
}

# Custom topic template for user-defined topics
# CUSTOM_TOPIC_TEMPLATE = {
#     "description": "User-defined custom data",
#     "fields": ["id", "name", "value", "category", "date", "status", "description"]
# }
