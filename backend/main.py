import base64
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.models.schemas import DataRequest, DataResponse, TopicInfo
from backend.services.data_generator import DataGenerator
from backend.services.format_converter import FormatConverter
from backend.utils.constants import PREDEFINED_TOPICS, SUPPORTED_FORMATS

app = FastAPI(title="Mock Data Generator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/")
async def root():
    return {"message": "Mock Data Generator API is running!"}


@app.get("/topics", response_model=List[TopicInfo])
async def get_topics():
    """Get all available predefined topics"""
    topics = []
    for name, info in PREDEFINED_TOPICS.items():
        topics.append(TopicInfo(
            name=name,
            description=info["description"],
            fields=info["fields"]
        ))
    return topics


@app.get("/formats")
async def get_formats():
    """Get all supported formats"""
    return {"formats": SUPPORTED_FORMATS}


@app.post("/generate", response_model=DataResponse)
async def generate_data(request: DataRequest):
    """Generate mock data based on request"""
    try:
        # Initialize data generator
        generator = DataGenerator(seed=request.seed)

        # Generate data
        data = generator.generate_for_topic(
            topic=request.topic,
            num_records=request.num_records,
            custom_fields=request.custom_fields
        )

        # Convert to requested format
        content, filename, content_type = FormatConverter.convert_to_format(
            data=data,
            format_type=request.format.value,
            topic=request.topic
        )

        return DataResponse(
            success=True,
            data=content,
            filename=filename,
            content_type=content_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download")
async def download_data(request: DataRequest):
    """Generate and return data as downloadable file"""
    try:
        # Generate data
        generator = DataGenerator(seed=request.seed)
        data = generator.generate_for_topic(
            topic=request.topic,
            num_records=request.num_records,
            custom_fields=request.custom_fields
        )

        # Convert to format
        content, filename, content_type = FormatConverter.convert_to_format(
            data=data,
            format_type=request.format.value,
            topic=request.topic
        )

        # Handle binary formats
        if content_type == "application/octet-stream":
            # Content is base64 encoded for binary formats
            binary_content = base64.b64decode(content)
            return Response(
                content=binary_content,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            return Response(
                content=content,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
