from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageChops
import io, os

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Save and reload with lower quality
        temp_path = "temp.jpg"
        image.save(temp_path, "JPEG", quality=90)
        compressed = Image.open(temp_path)

        # Difference
        diff = ImageChops.difference(image, compressed)
        extrema = diff.getextrema()

        # extrema = [(minR, maxR), (minG, maxG), (minB, maxB)]
        max_diff = max([channel[1] for channel in extrema])

        manipulated = max_diff > 20
        report = {
            "manipulated": manipulated,
            "ela_score": int(max_diff),
            "details": "High error level suggests manipulation"
            if manipulated
            else "No clear manipulation detected",
        }

        # cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return JSONResponse(content=report)

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
