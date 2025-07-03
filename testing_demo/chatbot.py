from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from markdown import markdown
import uvicorn
import nest_asyncio

nest_asyncio.apply()

# Giả sử bạn đã có hàm query() như sau:
# def query(question: str) -> str:
#     return "**Câu hỏi:** " + question + "\n\n**Trả lời:** Đây là câu trả lời mẫu."

from test import query  # Thay bằng module của bạn

app = FastAPI()

# Giao diện HTML với Tailwind CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Hỏi đáp về an toàn giao thông</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-800 min-h-screen">
    <div class="max-w-3xl mx-auto p-6">
        <h1 class="text-3xl font-bold mb-6 text-center">🧠 Hỏi đáp về an toàn giao thông</h1>
        <form method="post" class="mb-8">
            <textarea name="question" rows="5" class="w-full p-4 border border-gray-300 rounded-lg shadow-sm" placeholder="Nhập câu hỏi của bạn..." required>{{ question }}</textarea>
            <button type="submit" class="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                Gửi câu hỏi
            </button>
        </form>

        {% if answer %}
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-xl font-semibold mb-4">💬 Câu trả lời</h2>
            <div class="prose max-w-none">
                {{ answer|safe }}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

from jinja2 import Template

@app.get("/", response_class=HTMLResponse)
async def get_form():
    rendered = Template(HTML_TEMPLATE).render(question="", answer=None)
    return HTMLResponse(content=rendered)

@app.post("/", response_class=HTMLResponse)
async def post_form(question: str = Form(...)):
    raw_markdown = query(question)
    html_answer = markdown(raw_markdown)
    rendered = Template(HTML_TEMPLATE).render(question=question, answer=html_answer)
    return HTMLResponse(content=rendered)

if __name__ == "__main__":
    uvicorn.run("chatbot:app", host="0.0.0.0", port=8000, reload=True)
