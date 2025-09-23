from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageChops, ImageEnhance
import io

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Simple analysis: Error Level Analysis (ELA)
        temp_path = "temp.jpg"
        ela_path = "ela.jpg"
        image.save(temp_path, "JPEG", quality=90)
        ela_img = Image.open(temp_path)
        diff = ImageChops.difference(image, ela_img)
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])

        manipulated = max_diff > 20  # simple threshold
        report = {
            "manipulated": manipulated,
            "ela_score": max_diff,
            "details": "High error level suggests manipulation" if manipulated else "No clear manipulation detected"
        }
        return JSONResponse(content=report)

    except Exception as e:
        return JSONResponse(content={"error": str(e)})
