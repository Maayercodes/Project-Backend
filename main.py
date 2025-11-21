from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from model_client import call_vision_model_sync
from PIL import Image
import io
from prompts import build_instruction

app = FastAPI(title="Gemini Image Describer")

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Describe single image
@app.post("/describe")
async def describe(
    file: UploadFile,
    description_type: str = Form("Describe in Detail"),
    tone: str = Form("Friendly"),
    length: str = Form("Medium"),
):
    try:
        contents = await file.read()
        # Verify image
        try:
            Image.open(io.BytesIO(contents))
        except:
            return JSONResponse({"error": "Uploaded file is not a valid image."}, status_code=400)
        
        # Build prompt dynamically from provided options (no fixed instruction)
        opts = {
            "description_type": description_type,
            "tone": tone,
            "output_length": length,
            # keep defaults for detail_level, style_prompt, return_format
        }
        prompt = build_instruction(opts, require_json=False)
        
        # Call Gemini
        description = call_vision_model_sync(contents, prompt)
        return {"description": description}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Allow running directly with dynamic port from env (useful locally and on PaaS)
if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
