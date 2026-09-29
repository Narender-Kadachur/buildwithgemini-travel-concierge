import base64
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# IMPORTANT: Hardcoded Project ID and Bucket Name strings to ensure stability on Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-c99d4be278a4"
GCS_BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-02-c99d4be278a4"


def generate_destination_video(prompt: str, tool_context: ToolContext) -> str:
    """Generate a short video clip for a travel destination, landmark, or venue using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video as an artifact for the Playground's Artifacts panel and uploads the video bytes to a public Cloud Storage bucket.

    Args:
        prompt: Description of the short travel video clip to generate (e.g., 'A 3-second scenic video of the Eiffel Tower at sunset').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        The public HTTPS URL of the generated video hosted on Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    video_bytes = None
    mime_type = "video/mp4"

    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        # 1. Check output_video attribute
        if hasattr(interaction, "output_video") and interaction.output_video:
            ov = interaction.output_video
            if hasattr(ov, "data") and ov.data:
                video_bytes = (
                    base64.b64decode(ov.data)
                    if isinstance(ov.data, str)
                    else ov.data
                )
                if hasattr(ov, "mime_type") and ov.mime_type:
                    mime_type = ov.mime_type

        # 2. Check steps attribute if not found
        if not video_bytes and hasattr(interaction, "steps") and interaction.steps:
            for step in interaction.steps:
                if hasattr(step, "content") and step.content:
                    for item in step.content:
                        if getattr(item, "type", None) == "video" or hasattr(
                            item, "data"
                        ):
                            raw = getattr(item, "data", None)
                            if raw:
                                video_bytes = (
                                    base64.b64decode(raw)
                                    if isinstance(raw, str)
                                    else raw
                                )
                                if hasattr(item, "mime_type") and item.mime_type:
                                    mime_type = item.mime_type
                                break
                if video_bytes:
                    break

        # 3. Check outputs attribute if not found
        if (
            not video_bytes
            and hasattr(interaction, "outputs")
            and interaction.outputs
        ):
            for out in interaction.outputs:
                if hasattr(out, "data") and out.data:
                    raw = out.data
                    video_bytes = (
                        base64.b64decode(raw) if isinstance(raw, str) else raw
                    )
                    if hasattr(out, "mime_type") and out.mime_type:
                        mime_type = out.mime_type
                    break

    except Exception as e:
        return f"Error generating video with gemini-omni-flash-preview: {e}"

    if not video_bytes:
        return "Error: Failed to extract video bytes from gemini-omni-flash-preview model output."

    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

    # (1) Save video artifact with tool_context for Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # (2) Upload same video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    # Return public HTTPS URL
    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
    return public_url
