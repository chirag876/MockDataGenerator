import random
import uuid
from typing import Any, Dict, List
from faker import Faker

class DataGenerator:
    def __init__(self, seed: int = None):
        self.fake = Faker(['en_US'])  # English and Hindi locales
        if seed:
            Faker.seed(seed)
            random.seed(seed)
    
    def generate_for_topic(self, topic: str, num_records: int, custom_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Generate fake data based on topic"""
        if topic == "Citizen":
            return self._generate_citizen(num_records)
        elif topic == "Products":
            return self._generate_products(num_records)
        elif topic == "Orders":
            return self._generate_orders(num_records)
        elif topic == "Employee":
            return self._generate_employees(num_records)
        elif topic == "Finance":
            return self._generate_financial(num_records)
        elif topic == "Healthcare":
            return self._generate_healthcare(num_records)
        elif topic == "Education":
            return self._generate_education(num_records)
        elif topic == "Real_Estate":
            return self._generate_real_estate(num_records)
        elif topic == "Social_Media":
            return self._generate_social_media(num_records)
        elif topic == "Iot_Sensors":
            return self._generate_iot_sensors(num_records)
        elif topic == "Logistics":
            return self._generate_logistics(num_records)
        elif topic == "Banking":
            return self._generate_banking(num_records)
        else:
            # Custom topic generation
            return self._generate_custom(num_records, custom_fields or [])
    
    def _generate_citizen(self, num_records: int) -> List[Dict[str, Any]]:
        # field_data = self._load_field_data(assets_File_path)
        marital_statuses = ["Single", "Married", "Divorced", "Widowed"]
        genders = ["Male", "Female", "Other"]
        religions = ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Buddhist", "Other"]
        nationalities = ["Indian", "American", "British", "Canadian", "Australian", "Other"]
        disablitystatus = ["None", "Visually Impaired", "Hearing Impaired", "Physically Disabled", "Mentally Challenged"]
        bloodgroups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        emaildomains = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com", "live.com", "icloud.com", "protonmail.com", "zoho.com", "mail.com", "aol.com", "yandex.com", "tutanota.com", "fastmail.com", "gmx.com", "hushmail.com"]
       
        return [
            {
                "citizen id": f"CIT{str(i+1).zfill(2)}",
                "name": (name := self.fake.name()),
                "email": f"{name.lower().replace(' ', '.').replace(',', '').replace("'", '')}@{random.choice(emaildomains)}",
                "age": random.randint(18, 100),
                "gender": random.choice(genders),
                "marital status": random.choice(marital_statuses),
                "religion": random.choice(religions),
                "disability status": random.choice(disablitystatus),
                "blood group": random.choice(bloodgroups),
                "nationality": random.choice(nationalities),
                "address": self.fake.address().replace('\n', ', '),
                "phone number": self.fake.phone_number(),
                "occupation": self.fake.job(),
                "employer": self.fake.company(),
                "aadhaar number": f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
                "pan number": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000, 9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                "voter id": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(1000000, 9999999)}",
                "date of birth": self.fake.date_of_birth(minimum_age=18, maximum_age=100).isoformat(),
            }
            for i in range(num_records)
        ]
    
    def _generate_products(self, num_records: int) -> List[Dict[str, Any]]:
        categories = [
            "Electronics", "Clothing", "Books", "Home", "Sports", "Beauty", "Automotive", 
            "Toys", "Grocery", "Furniture", "Jewelry", "Shoes", "Pet Supplies", "Music", 
            "Video Games", "Health", "Office Supplies", "Garden", "Baby Products", 
            "Tools & Hardware", "Watches", "Stationery", "Mobile Accessories", 
            "Luggage & Travel", "Crafts & Sewing", "Kitchen Appliances", 
            "Smart Home Devices", "Cleaning Supplies", "Lighting", "Fitness Equipment"
        ]
        brands_by_category = {
            "Electronics": ["Samsung", "Apple", "OnePlus", "Xiaomi", "Sony"],
            "Clothing": ["Raymond", "Allen Solly", "FabIndia", "Levi's", "Zara"],
            "Books": ["Penguin", "Scholastic", "Arihant", "Oxford", "Pearson"],
            "Home": ["IKEA", "Godrej Interio", "Pepperfry", "Urban Ladder", "Nilkamal"],
            "Grocery": ["Amul", "Patanjali", "Haldiram's", "Bikanervala", "Nestle"],
            "Kitchen Appliances": ["Prestige", "Philips", "Bajaj", "Havells", "Morphy Richards"],
            "default": ["Generic", "Local", "BrandX", "BrandY", "BrandZ"]
        }
        materials = ["Plastic", "Metal", "Wood", "Fabric", "Glass", "Leather", "Ceramic"]
        availability_status = ["In Stock", "Out of Stock", "Pre-Order", "Limited Stock"]
        
        def generate_product_name(category: str) -> str:
            if category == "Electronics":
                return f"{random.choice(brands_by_category[category])} {random.choice(['Smartphone', 'TV', 'Laptop', 'Tablet', 'Headphones'])} {random.choice(['Pro', 'Plus', 'Ultra', 'Lite', ''])}"
            elif category == "Clothing":
                return f"{random.choice(brands_by_category[category])} {random.choice(['T-Shirt', 'Kurta', 'Jeans', 'Saree', 'Jacket'])} {random.choice(['Casual', 'Formal', 'Traditional', ''])}"
            elif category == "Grocery":
                return f"{random.choice(brands_by_category[category])} {random.choice(['Butter', 'Paneer', 'Spices', 'Rice', 'Lentils'])} {random.randint(100, 1000)}g"
            elif category == "Kitchen Appliances":
                return f"{random.choice(brands_by_category[category])} {random.choice(['Mixer Grinder', 'Microwave', 'Toaster', 'Electric Kettle', 'Induction Cooktop'])}"
            else:
                return f"{random.choice(brands_by_category.get(category, brands_by_category['default']))} {self.fake.word().capitalize()} {random.choice(['Pro', 'Classic', 'Premium', ''])}"

        return [
                (
                    lambda: (
                        lambda category, price_inr, discount_percentage, stock_quantity: {
                            "product id": f"PROD{str(i+1).zfill(2)}",
                            "name": generate_product_name(category=category),
                            "category": category,
                            "brand": random.choice(brands_by_category.get(category, brands_by_category['default'])),
                            "price inr": price_inr,
                            "discount percentage": discount_percentage,
                            "final price inr": round(price_inr * (1 - discount_percentage / 100), 2),
                            "sku": f"SKU-{str(uuid.uuid4())[:8].upper()}",
                            "stock quantity": stock_quantity,
                            "availability": "Out of Stock" if stock_quantity == 0 else random.choice(availability_status),
                            "description": self.fake.text(max_nb_chars=100),
                            "weight kg": round(random.uniform(0.1, 50), 2),
                            "dimensions cm": f"{random.randint(5, 200)}x{random.randint(5, 200)}x{random.randint(5, 200)}",
                            "material": random.choice(materials) if random.random() > 0.2 else "Plastic",
                            "warranty months": random.randint(6, 36) if random.random() > 0.5 else "No Warranty on this product",
                            "rating": round(random.uniform(1, 5), 1),
                            "reviews count": random.randint(0, 500),
                            "made in": random.choice(["India", "China", "USA", "Germany", "Japan"])
                        }
                    )
                    (
                        category := random.choice(categories),
                        price_inr := round(random.uniform(100, 100000), 2),
                        discount_percentage := random.randint(0, 50) if random.random() > 0.3 else 0,
                        stock_quantity := random.randint(0, 1000)
                    )
                )()
                for i in range(num_records)
            ]

    def _generate_orders(self, num_records: int) -> List[Dict[str, Any]]:
        statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        emaildomains = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com", "live.com", "icloud.com", "protonmail.com", "zoho.com", "mail.com", "aol.com", "yandex.com", "tutanota.com", "fastmail.com", "gmx.com", "hushmail.com"]
        payment_methods = ["Credit Card", "Debit Card", "PayPal", "Net Banking", "Cash on Delivery", "UPI", "Wallet"]
        orderchannels = ["Online", "In-Store", "Mobile App", "Phone Order", "Email Order"]
        return [
            {
                "order id": f"ORD-{str(uuid.uuid4())[:8].upper()}",
                "customer name": (name := self.fake.name()),
                "customer email": f"{name.lower().replace(' ', '.').replace(',', '').replace("'", '')}@{random.choice(emaildomains)}",
                "customer phone": self.fake.phone_number(),
                "shipping address": self.fake.address().replace('\n', ', '),
                "payment method": random.choice(payment_methods),
                "order Channel": random.choice(orderchannels),
                "product name": self.fake.catch_phrase(),
                "quantity": random.randint(1, 1000),
                "unit price": round(random.uniform(10, 500), 2),
                "total price": round(random.uniform(10, 5000), 2),
                "order date": self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                "delivery date": self.fake.date_time_between(start_date='now', end_date='+30d').isoformat(),
                "status": random.choice(statuses)
            }
            for i in range(num_records)
        ]
    
    def _generate_employees(self, num_records: int) -> List[Dict[str, Any]]:
        departments = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales", "Legal"]
        employment_types = ["Full-time", "Part-time", "Contractor", "Intern"]
        statuses = ["Active", "Resigned", "On Leave"]
        genders = ["Male", "Female", "Other"]
        performance_ratings = ["Excellent", "Good", "Average", "Below Average", "Poor"]
        emaildomains = [
            "gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com", 
            "live.com", "icloud.com", "protonmail.com", "zoho.com", "mail.com", 
            "aol.com", "yandex.com", "tutanota.com", "fastmail.com", "gmx.com", "hushmail.com"
        ]
        bloodgroups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

        return [
            {
                "employee_id": f"EMP{str(i+1).zfill(2)}",
                "employee_name": (name := self.fake.name()),
                "gender": random.choice(genders),
                "date_of_birth": self.fake.date_of_birth(minimum_age=22, maximum_age=60).isoformat(),
                "email": f"{name.lower().replace(' ', '.').replace(',', '').replace("'", '')}@{random.choice(emaildomains)}",
                "phone": self.fake.phone_number(),
                "department": random.choice(departments),
                "Projects Handled": random.randint(0, 20),
                "employment_type": random.choice(employment_types),
                "employee status": random.choice(statuses),
                "hire date": self.fake.date_between(start_date='-10y', end_date='now').isoformat(),
                "Experience (years)": random.randint(0, 20),
                "salary": random.randint(30000, 150000),
                "performance_rating": random.choice(performance_ratings),
                "manager": (mgr_name := self.fake.name()),
                "manager_email": f"{mgr_name.lower().replace(' ', '.').replace(',', '').replace("'", '')}@{random.choice(emaildomains)}",
                "location": self.fake.city(),
                "blood_group": random.choice(bloodgroups),
                "emergency_contact": f"{self.fake.name()} - {self.fake.phone_number()}",
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
        emaildomains = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com", "live.com", "icloud.com", "protonmail.com", "zoho.com", "mail.com", "aol.com", "yandex.com", "tutanota.com", "fastmail.com", "gmx.com", "hushmail.com"]
        for i in range(num_records):
            record = {"id": i + 1}
            for field in custom_fields:
                field_lower = field.lower()
                if "name" in field_lower:
                    record[field] = (name := self.fake.name())
                elif "email" in field_lower:
                    record[field] = f"{name.lower().replace(' ', '.').replace(',', '').replace("'", '')}@{random.choice(emaildomains)}"
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