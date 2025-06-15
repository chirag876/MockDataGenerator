SUPPORTED_FORMATS = [
    "JSON", "XML", "CSV", "YAML", "TOML", "INI", 
    "Avro", "Parquet", "ORC", "Protobuf", "MsgPack", 
    "HDF5", "Feather", "BSON", "TSV"
]

PREDEFINED_TOPICS = {
    "users": {
        "description": "User profiles with personal information",
        "fields": ["name", "email", "age", "address", "phone", "job", "company"]
    },
    "products": {
        "description": "E-commerce product data",
        "fields": ["name", "price", "category", "description", "sku", "stock", "rating"]
    },
    "orders": {
        "description": "Order and transaction data",
        "fields": ["order_id", "customer", "product", "quantity", "price", "date", "status"]
    },
    "employees": {
        "description": "Employee records",
        "fields": ["name", "employee_id", "department", "salary", "hire_date", "email"]
    },
    "financial": {
        "description": "Financial transactions",
        "fields": ["transaction_id", "amount", "currency", "date", "type", "account"]
    },
    "healthcare": {
        "description": "Patient and medical records",
        "fields": ["patient_id", "name", "age", "diagnosis", "doctor", "date", "medication"]
    },
    "education": {
        "description": "Student and course data",
        "fields": ["student_id", "name", "course", "grade", "semester", "gpa", "credits"]
    },
    "real_estate": {
        "description": "Property listings",
        "fields": ["property_id", "address", "price", "bedrooms", "bathrooms", "area", "type"]
    },
    "social_media": {
        "description": "Social media posts and interactions",
        "fields": ["user", "post_content", "likes", "shares", "comments", "timestamp", "platform"]
    },
    "iot_sensors": {
        "description": "IoT sensor readings",
        "fields": ["sensor_id", "temperature", "humidity", "pressure", "timestamp", "location"]
    },
    "logistics": {
        "description": "Shipping and delivery data",
        "fields": ["tracking_id", "origin", "destination", "weight", "status", "estimated_delivery"]
    },
    "banking": {
        "description": "Banking transactions",
        "fields": ["account_number", "transaction_type", "amount", "balance", "branch", "timestamp"]
    }
}

# Custom topic template for user-defined topics
CUSTOM_TOPIC_TEMPLATE = {
    "description": "User-defined custom data",
    "fields": ["id", "name", "value", "category", "date", "status", "description"]
}
