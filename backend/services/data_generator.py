import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
from faker import Faker


class DataGenerator:
    def __init__(self, seed: int = None):
        self.fake = Faker(['en_US'])  # English and Hindi locales
        if seed:
            Faker.seed(seed)
            random.seed(seed)
    
    def generate_for_topic(self, topic: str, num_records: int, custom_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Generate fake data based on topic"""
        if topic == "users":
            return self._generate_users(num_records)
        elif topic == "products":
            return self._generate_products(num_records)
        elif topic == "orders":
            return self._generate_orders(num_records)
        elif topic == "employees":
            return self._generate_employees(num_records)
        elif topic == "financial":
            return self._generate_financial(num_records)
        elif topic == "healthcare":
            return self._generate_healthcare(num_records)
        elif topic == "education":
            return self._generate_education(num_records)
        elif topic == "real_estate":
            return self._generate_real_estate(num_records)
        elif topic == "social_media":
            return self._generate_social_media(num_records)
        elif topic == "iot_sensors":
            return self._generate_iot_sensors(num_records)
        elif topic == "logistics":
            return self._generate_logistics(num_records)
        elif topic == "banking":
            return self._generate_banking(num_records)
        else:
            # Custom topic generation
            return self._generate_custom(num_records, custom_fields or [])
    
    def _generate_users(self, num_records: int) -> List[Dict[str, Any]]:
        return [
            {
                "id": i + 1,
                "name": self.fake.name(),
                "email": self.fake.email(),
                "age": random.randint(18, 80),
                "address": self.fake.address().replace('\n', ', '),
                "phone": self.fake.phone_number(),
                "job": self.fake.job(),
                "company": self.fake.company(),
                "created_at": self.fake.date_time_between(start_date='-2y', end_date='now').isoformat()
            }
            for i in range(num_records)
        ]
    
    def _generate_products(self, num_records: int) -> List[Dict[str, Any]]:
        categories = [
                        "Electronics", "Clothing", "Books", "Home", "Sports", "Beauty", "Automotive", "Toys", "Grocery",
                        "Furniture", "Jewelry", "Shoes", "Pet Supplies", "Music", "Video Games", "Health", "Office Supplies",
                        "Garden", "Baby Products", "Tools & Hardware", "Watches", "Stationery", "Mobile Accessories", 
                        "Luggage & Travel", "Crafts & Sewing", "Kitchen Appliances", "Smart Home Devices", "Cleaning Supplies",
                        "Lighting", "Fitness Equipment"
                    ]
        return [
            {
                "id": i + 1,
                "name": self.fake.catch_phrase(),
                "price": round(random.uniform(10, 1000), 2),
                "category": random.choice(categories),
                "description": self.fake.text(max_nb_chars=200),
                "sku": self.fake.uuid4()[:8].upper(),
                "stock": random.randint(0, 500),
                "rating": round(random.uniform(1, 5), 1)
            }
            for i in range(num_records)
        ]
    
    def _generate_orders(self, num_records: int) -> List[Dict[str, Any]]:
        statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        return [
            {
                "order_id": f"ORD-{str(uuid.uuid4())[:8].upper()}",
                "customer_name": self.fake.name(),
                "customer_email": self.fake.email(),
                "product_name": self.fake.catch_phrase(),
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(10, 500), 2),
                "total_price": lambda: round(random.uniform(10, 5000), 2),
                "order_date": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "status": random.choice(statuses)
            }
            for i in range(num_records)
        ]
    
    def _generate_employees(self, num_records: int) -> List[Dict[str, Any]]:
        departments = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales", "Legal"]
        return [
            {
                "employee_id": f"EMP{str(i+1).zfill(4)}",
                "name": self.fake.name(),
                "email": self.fake.email(),
                "department": random.choice(departments),
                "salary": random.randint(30000, 150000),
                "hire_date": self.fake.date_between(start_date='-10y', end_date='now').isoformat(),
                "manager": self.fake.name(),
                "phone": self.fake.phone_number()
            }
            for i in range(num_records)
        ]
    
    def _generate_financial(self, num_records: int) -> List[Dict[str, Any]]:
        transaction_types = ["Credit", "Debit", "Transfer", "Payment", "Refund"]
        currencies = ["USD", "EUR", "GBP", "INR", "JPY"]
        return [
            {
                "transaction_id": str(uuid.uuid4()),
                "amount": round(random.uniform(-5000, 5000), 2),
                "currency": random.choice(currencies),
                "transaction_date": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "transaction_type": random.choice(transaction_types),
                "account_number": self.fake.bban(),
                "description": self.fake.sentence()
            }
            for i in range(num_records)
        ]
    
    def _generate_healthcare(self, num_records: int) -> List[Dict[str, Any]]:
        diagnoses = ["Hypertension", "Diabetes", "Asthma", "Migraine", "Arthritis", "Flu", "COVID-19"]
        return [
            {
                "patient_id": f"PAT{str(i+1).zfill(6)}",
                "name": self.fake.name(),
                "age": random.randint(1, 100),
                "gender": random.choice(["Male", "Female", "Other"]),
                "diagnosis": random.choice(diagnoses),
                "doctor": f"Dr. {self.fake.name()}",
                "visit_date": self.fake.date_between(start_date='-2y', end_date='now').isoformat(),
                "medication": self.fake.word().capitalize(),
                "cost": round(random.uniform(50, 2000), 2)
            }
            for i in range(num_records)
        ]
    
    def _generate_education(self, num_records: int) -> List[Dict[str, Any]]:
        courses = ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "History", "English"]
        grades = ["A+", "A", "B+", "B", "C+", "C", "D", "F"]
        return [
            {
                "student_id": f"STU{str(i+1).zfill(5)}",
                "name": self.fake.name(),
                "course": random.choice(courses),
                "grade": random.choice(grades),
                "semester": random.randint(1, 8),
                "gpa": round(random.uniform(2.0, 4.0), 2),
                "credits": random.randint(3, 6),
                "enrollment_date": self.fake.date_between(start_date='-4y', end_date='now').isoformat()
            }
            for i in range(num_records)
        ]
    
    def _generate_real_estate(self, num_records: int) -> List[Dict[str, Any]]:
        property_types = ["Apartment", "House", "Condo", "Townhouse", "Villa", "Studio"]
        return [
            {
                "property_id": f"PROP{str(i+1).zfill(6)}",
                "address": self.fake.address().replace('\n', ', '),
                "price": random.randint(100000, 2000000),
                "bedrooms": random.randint(1, 6),
                "bathrooms": random.randint(1, 4),
                "area_sqft": random.randint(500, 5000),
                "property_type": random.choice(property_types),
                "listing_date": self.fake.date_between(start_date='-1y', end_date='now').isoformat(),
                "agent": self.fake.name()
            }
            for i in range(num_records)
        ]
    
    def _generate_social_media(self, num_records: int) -> List[Dict[str, Any]]:
        platforms = ["Facebook", "Twitter", "Instagram", "LinkedIn", "TikTok", "YouTube"]
        return [
            {
                "post_id": str(uuid.uuid4()),
                "username": self.fake.user_name(),
                "post_content": self.fake.text(max_nb_chars=280),
                "likes": random.randint(0, 10000),
                "shares": random.randint(0, 1000),
                "comments": random.randint(0, 500),
                "timestamp": self.fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                "platform": random.choice(platforms),
                "hashtags": [f"#{self.fake.word()}" for _ in range(random.randint(0, 5))]
            }
            for i in range(num_records)
        ]
    
    def _generate_iot_sensors(self, num_records: int) -> List[Dict[str, Any]]:
        sensor_types = ["Temperature", "Humidity", "Pressure", "Motion", "Light", "Sound"]
        return [
            {
                "sensor_id": f"SENSOR{str(i+1).zfill(4)}",
                "sensor_type": random.choice(sensor_types),
                "temperature": round(random.uniform(-10, 50), 2),
                "humidity": round(random.uniform(20, 80), 2),
                "pressure": round(random.uniform(980, 1020), 2),
                "timestamp": self.fake.date_time_between(start_date='-7d', end_date='now').isoformat(),
                "location": f"{self.fake.latitude()}, {self.fake.longitude()}",
                "battery_level": random.randint(10, 100)
            }
            for i in range(num_records)
        ]
    
    def _generate_logistics(self, num_records: int) -> List[Dict[str, Any]]:
        statuses = ["In Transit", "Delivered", "Pending", "Out for Delivery", "Delayed"]
        return [
            {
                "tracking_id": f"TRK{str(uuid.uuid4())[:10].upper()}",
                "origin": self.fake.city(),
                "destination": self.fake.city(),
                "weight_kg": round(random.uniform(0.1, 50), 2),
                "status": random.choice(statuses),
                "estimated_delivery": self.fake.date_between(start_date='now', end_date='+30d').isoformat(),
                "carrier": self.fake.company(),
                "cost": round(random.uniform(10, 500), 2)
            }
            for i in range(num_records)
        ]
    
    def _generate_banking(self, num_records: int) -> List[Dict[str, Any]]:
        transaction_types = ["Deposit", "Withdrawal", "Transfer", "Payment", "Interest"]
        return [
            {
                "account_number": self.fake.bban(),
                "transaction_id": str(uuid.uuid4()),
                "transaction_type": random.choice(transaction_types),
                "amount": round(random.uniform(-10000, 10000), 2),
                "balance": round(random.uniform(0, 100000), 2),
                "branch": self.fake.city(),
                "timestamp": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "description": self.fake.sentence()
            }
            for i in range(num_records)
        ]
    
    def _generate_custom(self, num_records: int, custom_fields: List[str]) -> List[Dict[str, Any]]:
        """Generate custom data based on field names"""
        data = []
        for i in range(num_records):
            record = {"id": i + 1}
            for field in custom_fields:
                field_lower = field.lower()
                if "name" in field_lower:
                    record[field] = self.fake.name()
                elif "email" in field_lower:
                    record[field] = self.fake.email()
                elif "phone" in field_lower:
                    record[field] = self.fake.phone_number()
                elif "address" in field_lower:
                    record[field] = self.fake.address().replace('\n', ', ')
                elif "date" in field_lower:
                    record[field] = self.fake.date().isoformat()
                elif "price" in field_lower or "amount" in field_lower:
                    record[field] = round(random.uniform(10, 1000), 2)
                elif "age" in field_lower:
                    record[field] = random.randint(18, 80)
                elif "description" in field_lower:
                    record[field] = self.fake.text(max_nb_chars=200)
                elif "status" in field_lower:
                    record[field] = random.choice(["Active", "Inactive", "Pending", "Completed"])
                elif "category" in field_lower:
                    record[field] = self.fake.word().capitalize()
                else:
                    # Generic field generation
                    record[field] = self.fake.word()
            data.append(record)
        return data