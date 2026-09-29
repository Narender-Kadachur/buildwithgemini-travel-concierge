import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# IMPORTANT: Hardcoded Project ID and Bucket Name strings to ensure stability on Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-c99d4be278a4"
GCS_BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-02-c99d4be278a4"


def generate_destination_image(prompt: str, tool_context: ToolContext) -> str:
    """Generate a photo or landmark image for a travel destination using Gemini, save it as an artifact, and upload to public GCS bucket.

    Args:
        prompt: Detailed description of the travel destination image to generate (e.g., 'A vibrant sunset over Mt. Fuji in Japan').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        The public HTTPS URL of the generated image hosted on Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break
        if image_bytes:
            break

    if not image_bytes:
        return "Error: Failed to generate image from the model."

    ext = "png" if "png" in mime_type else "jpg"
    filename = f"gen_{uuid.uuid4().hex[:8]}.{ext}"

    # 1. Save artifact with tool_context for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes to public GCS bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    # Return the public HTTPS URL
    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
    return public_url
