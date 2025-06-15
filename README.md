# Mock Data Generator

A powerful web application to generate realistic fake data in multiple formats for testing and development purposes.

## 🚀 Features

- **12 Predefined Topics**: Users, Products, Orders, Employees, Financial, Healthcare, Education, Real Estate, Social Media, IoT Sensors, Logistics, Banking
- **Custom Topic Support**: Define your own fields and generate custom data
- **15 Output Formats**: JSON, XML, CSV, YAML, TOML, INI, Avro, Parquet, ORC, Protobuf, MsgPack, HDF5, Feather, BSON, TSV
- **Up to 1000 Records**: Generate large datasets for testing
- **Download & Copy**: Easy data export options
- **Reproducible Data**: Use seeds for consistent data generation
- **Real-time Preview**: See your data before downloading

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Data Generation**: Faker library
- **Data Processing**: Pandas
- **Format Support**: Multiple specialized libraries

## 📁 Project Structure

```
mock-data-generator/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── data_generator.py    # Data generation logic
│   │   └── format_converter.py  # Format conversion
│   └── utils/
│       └── constants.py     # Constants and configurations
├── frontend/
│   └── streamlit_app.py     # Streamlit frontend
├── requirements.txt         # Python dependencies
├── run.py                   # Application runner
└── README.md
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mock-data-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 📋 Available Topics

1. **Users** - Personal information, contact details
2. **Products** - E-commerce product data
3. **Orders** - Transaction and order data
4. **Employees** - HR and employee records
5. **Financial** - Banking and transaction data
6. **Healthcare** - Patient and medical records
7. **Education** - Student and course data
8. **Real Estate** - Property listings
9. **Social Media** - Posts and interactions
10. **IoT Sensors** - Sensor readings and data
11. **Logistics** - Shipping and delivery data
12. **Banking** - Account and transaction data

## 🎛️ API Endpoints

- `GET /` - Health check
- `GET /topics` - Get available topics
- `GET /formats` - Get supported formats
- `POST /generate` - Generate mock data
- `POST /download` - Download generated data

## 🔧 Usage Examples

### Generate User Data (JSON)
```python
import requests

payload = {
    "topic": "users",
    "format": "JSON",
    "num_records": 100,
    "seed": 42
}

response = requests.post("http://localhost:8000/generate", json=payload)
data = response.json()
```

### Custom Topic Generation
```python
payload = {
    "topic": "custom",
    "format": "CSV",
    "num_records": 50,
    "custom_fields": ["product_name", "price", "category", "in_stock"]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Faker](https://faker.readthedocs.io/) - For realistic fake data generation
- [FastAPI](https://fastapi.tiangolo.com/) - For the robust API framework
- [Streamlit](https://streamlit.io/) - For the intuitive frontend interface

## 💡 Future Enhancements

- [ ] Database export options (SQL, MongoDB)
- [ ] API key authentication
- [ ] Data relationship modeling
- [ ] Batch processing for large datasets
- [ ] Custom data templates
- [ ] Data validation rules
- [ ] Export scheduling
- [ ] More language localizations

---

**Happy Data Generation! 🎲**
