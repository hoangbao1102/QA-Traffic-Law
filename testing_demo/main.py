from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markdown import markdown
import os
from datetime import datetime
from pathlib import Path
import shutil
from test import query, local_query, caption 
import nest_asyncio
from ultralytics import YOLO
import cv2
import numpy as np
import json
from pathlib import Path
from pydantic import BaseModel

with open('testing_demo/data/traffic_sign_info.json', 'r', encoding='utf-8') as f:
    TRAFFIC_SIGN_DESCRIPTIONS = json.load(f)

nest_asyncio.apply()

traffic_model = YOLO("testing_demo/checkpoints/best_l.pt")

app = FastAPI()
app.mount("/static", StaticFiles(directory="testing_demo/static"), name="static")
templates = Jinja2Templates(directory="testing_demo/templates")

# Configure upload folder
UPLOAD_FOLDER = Path("testing_demo/static/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Store chat history
messages = []

class Query(BaseModel):
    query: str

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "messages": messages})

@app.post("/", response_class=HTMLResponse)
async def handle_chat(
    request: Request,
    message: str = Form(default=None),
    image: UploadFile = File(default=None)
):
    # Handle user input (text, image, or both)
    user_message = {"sender": "User", "type": "combined", "text": None, "image": None, "timestamp": datetime.now().strftime("%H:%M:%S")}
    
    sign_text = ""
    image_caption_text = ""
    # Process text if provided
    query_input = ""
    if message:
        user_message["text"] = message
        query_input += message
        
    # Process image if provided
    if image and allowed_file(image.filename):
        
        filename = image.filename
        file_path = UPLOAD_FOLDER / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        img = cv2.imread(str(file_path))
        results = traffic_model.predict(img)
        # Process YOLO results
        sign_detections = []
        for r in results:
            r.save(filename="static/predictions/results.jpg")  # Save the image with detections
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                cls = box.cls[0]
                name = traffic_model.names[int(cls)]
                
                if conf > 0.5:  # Confidence threshold
                    # Get description from JSON if available
                    description = TRAFFIC_SIGN_DESCRIPTIONS.get(name, "Không có mô tả")
                    sign_detections.append(f"Biển {name}: {description} (độ tin cậy: {conf:.2f})")
        
        user_message["image"] = f"uploads/{filename}"
        # Get image caption
        image_caption = caption(str(file_path), sign_detections)
        image_caption_text = f"### Mô tả hình ảnh:\n{image_caption}\n\n"
        query_input += f"\nMô tả của ảnh đầu vào: {image_caption}" if query_input else f"Đây là mô tả của ảnh đầu vào, hãy phân tích và xử lý: {image_caption}"

    # Add user message to chat history if there's input
    if user_message["text"] or user_message["image"]:
        messages.append(user_message)

    # Call query() if there's input to process
    if query_input:
        raw_markdown = query(query_input)
        combined_markdown = f"{image_caption_text}### Phân tích và hồi đáp:\n{raw_markdown}"
        html_answer = markdown(combined_markdown)
        messages.append({
            "sender": "Chatbot",
            "type": "text",
            "content": html_answer,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    return templates.TemplateResponse("chat.html", {"request": request, "messages": messages})

@app.post("/clear", response_class=HTMLResponse)
async def clear_chat(request: Request):
    messages.clear()
    return templates.TemplateResponse("chat.html", {"request": request, "messages": messages})

@app.post("/clear_caption")
async def clear_caption():
    # Clear the caption from session or state management
    return RedirectResponse(url="/", status_code=303)

@app.post("/caption")
async def process_caption(image: UploadFile = File(...)):
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{image.filename}"
    path = f"static/uploads/{filename}"
    os.makedirs("static/uploads", exist_ok=True)
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    img = cv2.imread(str(path))
    results = traffic_model.predict(img,save=True,project="testing_demo/static/predictions")
    # Process YOLO results
    sign_detections = []
    for r in results:
        path = r.save_dir + "\\" + r.path
        static_index = path.find("static")
        if static_index != -1:
            static_path = path[static_index:]  # Lấy từ "static" trở đi
        else:
            static_path = path
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            conf = box.conf[0]
            cls = box.cls[0]
            name = traffic_model.names[int(cls)]
            
            if conf > 0.5:  # Confidence threshold
                # Get description from JSON if available
                description = TRAFFIC_SIGN_DESCRIPTIONS.get(name, "Không có mô tả về biển báo")
                sign_detections.append(f"Biển {name}: {description} (độ tin cậy: {conf:.2f})")
    
    # Get image caption
    image_caption = caption(str(path), sign_detections)
    # caption = "Đây là mô tả mẫu cho hình ảnh được tải lên."
    
    return {"caption": image_caption, "image_path": static_path}

@app.post("/query")
async def process_query(query: Query):
    # TODO: Implement your query processing logic here
    response = f"Đây là câu trả lời mẫu cho câu hỏi: {query.query}"
    
    return {"response": response}

@app.post("/chat")
async def chat(
    request: Request,
    message: str = Form(...),
    context: str = Form(None),
    action: str = Form(...),
    mode: str = Form(...)
):
    try:
        if action != "chat":
            return {"error": "Invalid action"}

        full_query = (
            f"Dựa vào ngữ cảnh sau đây: '{context}', "
            f"hãy trả lời câu hỏi: '{message}'"
        ) if context else message

        # Choose query function based on mode
        if mode == "local":
            print("Using local mode")
            raw_markdown = local_query(full_query)
        else:  # global mode
            print("Using global mode")
            raw_markdown = query(full_query)
        
        if not raw_markdown:
            return {
                "response": "Xin lỗi, tôi không thể tìm thấy câu trả lời phù hợp."
            }
        html_answer = markdown(raw_markdown)
        return {
            "response": html_answer,
            "context_used": bool(context),
            "mode_used": mode
        }

    except Exception as e:
        return {
            "error": f"Có lỗi xảy ra khi xử lý câu hỏi của bạn: {str(e)}"
        }

@app.get("/graph", response_class=HTMLResponse)
async def show_graph():
    # Đảm bảo file graph_visualization.html đã được tạo từ graphml_test.py
    return FileResponse("graph_visualization.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)