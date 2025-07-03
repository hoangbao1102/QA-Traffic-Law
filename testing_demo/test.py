import os
import logging
import numpy as np
from openai import AsyncOpenAI, AsyncAzureOpenAI, APIConnectionError, RateLimitError

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag.base import BaseKVStorage
from nano_graphrag._utils import compute_args_hash, wrap_embedding_func_with_attrs
from dotenv import load_dotenv
from google import genai
from google.genai import types
import re

WORKING_DIR = "./traffic_law_deepseek_vietnamese"

def chunking_by_special_separators(
    tokens_list: list[list[int]],
    doc_keys,
    tiktoken_model,
    overlap_token_size=128,
    max_token_size=2024
):
    results = []

    for index, tokens in enumerate(tokens_list):
        chunk_order_index=0
        chunk_text = []
        decoded_text = tiktoken_model.decode(tokens)
        special_spec = ["\nChương", "\nĐiều"]
        pattern = r"(?=" + "|".join(map(re.escape, special_spec)) + ")"

        # Tách các đoạn theo chương/điều
        chunks = re.split(pattern, decoded_text)
        if chunks:
            if not chunks[0].startswith(tuple(special_spec)):
                chunk_text.append(chunks[0].strip())
                chunks = chunks[1:]
        for chunk in chunks:
            if chunk.strip():
                chunk_text.append(chunk.strip())

        # Tokenize các chunk sau khi split
        chunk_token_lists = tiktoken_model.encode_batch(chunk_text)

        for i, token_list in enumerate(chunk_token_lists):
            text_chunks = []
            # Nếu đoạn ngắn thì giữ nguyên
            if len(token_list) <= max_token_size:
                text_chunks = [token_list]
            else:
                # Sliding window để chia nhỏ
                text_chunks = []
                start = 0
                while start < len(token_list):
                    end = start + max_token_size
                    text_chunks.append(token_list[start:end])
                    if end >= len(token_list):
                        break
                    start += max_token_size - overlap_token_size  # trượt có overlap

            # Decode các phần nhỏ và thêm vào kết quả
            for j, chunk_tokens in enumerate(text_chunks):
                decoded_chunk = tiktoken_model.decode(chunk_tokens)
                results.append({
                    "tokens": len(chunk_tokens),
                    "content": decoded_chunk.strip(),
                    "chunk_order_index": chunk_order_index,
                    "full_doc_id": doc_keys[index],
                })
                chunk_order_index += 1

    return results

load_dotenv()

from time import time
import docx

logging.basicConfig(level=logging.WARNING)
logging.getLogger("nano-graphrag").setLevel(logging.INFO)

DEEPSEEK_API_KEY = "" #YOUR API KEY HERE
MODEL = "deepseek-chat"
GEMINI_API_KEY = "" #YOUR API KEY HERE

token = os.getenv("API_KEY_EMB")
endpoint = os.getenv("AZURE_ENDPOINT_EMB")
modelName = os.getenv("API_VERSION_EMB")
print(token, endpoint, modelName)

client = AsyncOpenAI(api_key=token)

@wrap_embedding_func_with_attrs(embedding_dim=3072, max_token_size=8192)
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
)
async def openai_embedding(texts: list[str]) -> np.ndarray:
    openai_async_client = client
    response = await openai_async_client.embeddings.create(
        model="text-embedding-3-large", input=texts, encoding_format="float"
    )
    return np.array([dp.embedding for dp in response.data])

# client = genai.Client(api_key=GEMINI_API_KEY)
# client = AsyncOpenAI(api_key=token, base_url=endpoint)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

async def deepseepk_model_if_cache(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    openai_async_client = AsyncOpenAI(
        api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
    )
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Get the cached response if having-------------------
    hashing_kv: BaseKVStorage = kwargs.pop("hashing_kv", None)
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    if hashing_kv is not None:
        args_hash = compute_args_hash(MODEL, messages)
        if_cache_return = await hashing_kv.get_by_id(args_hash)
        if if_cache_return is not None:
            return if_cache_return["return"]
    # -----------------------------------------------------

    response = await openai_async_client.chat.completions.create(
        model=MODEL, messages=messages, **kwargs
    )

    # Cache the response if having-------------------
    if hashing_kv is not None:
        await hashing_kv.upsert(
            {args_hash: {"return": response.choices[0].message.content, "model": MODEL}}
        )
    # -----------------------------------------------------
    return response.choices[0].message.content

# EMBEDDING_MODEL = SentenceTransformer("Alibaba-NLP/gte-Qwen2-7B-instruct", trust_remote_code=True)
# @wrap_embedding_func_with_attrs(
#     embedding_dim=EMBEDDING_MODEL.get_sentence_embedding_dimension(),
#     max_token_size=EMBEDDING_MODEL.max_seq_length,
# )
# async def local_embedding(texts: list[str]) -> np.ndarray:
#     return EMBEDDING_MODEL.encode(texts, normalize_embeddings=True)


# @wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
# async def azure_openai_embedding(texts: list[str]) -> np.ndarray:
#     response = await client.embeddings.create(
#         model=modelName, input=texts, encoding_format="float"
#     )
#     return np.array([dp.embedding for dp in response.data])



# @wrap_embedding_func_with_attrs(embedding_dim=1536, max_token_size=8192)
# async def gemini_embedding(texts: list[str]) -> np.ndarray:
#     response = await client.models.embed_content(
#         model="gemini-embedding-exp-03-07",
#         contents=texts)
#     return np.array([response.embeddings])


def remove_if_exist(file):
    if os.path.exists(file):
        os.remove(file)

rag = GraphRAG(
    working_dir=WORKING_DIR,
    best_model_func=deepseepk_model_if_cache,
    cheap_model_func=deepseepk_model_if_cache,
    # using_azure_openai=True,
    enable_naive_rag=True,
    embedding_func=openai_embedding,
)
def query(text):
    return rag.query(text, param=QueryParam(mode="global"))

# def naive_query(text):
#     return rag.query(text, param=QueryParam(mode="naive"))

def local_query(text):
    return rag.query(text, param=QueryParam(mode="local"))

def caption(image_path, sign_descriptions=None):
    gemini_prompt = """
        Bạn là một chuyên gia trong lĩnh vực giao thông đường bộ.
        Đây là một bức ảnh có thể liên quan đến giao thông đường bộ.
        Hãy trả về mô tả súc tích nhưng đầy đủ về nội dung của bức ảnh này. Càng liên quan đến giao thông đường bộ càng tốt.
        Nếu bạn không thể xác định nội dung của bức ảnh, hãy trả về "Không thể xác định nội dung của bức ảnh này".
        Hãy chỉ trả về nội dung mô tả mà không cần thêm bất kỳ thông tin nào khác. Mô tả khách quan, không đưa ra kết luận hay đánh giá pháp lý. Chỉ mô tả những gì nhìn thấy được trong ảnh.
        Hãy trả về mô tả bằng tiếng Việt. Luôn trả về các biển báo giao thông phát hiện nếu có xuất hiện ở đầu prompt.
        """
    if sign_descriptions:
        gemini_prompt = f"""
        Đây là một detection của những biển báo giao thông có trong hình ảnh đầu vào:
        {sign_descriptions}
        """ + gemini_prompt
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    response = gemini_client.models.generate_content(
    model='gemini-2.5-flash-preview-04-17',
    contents=[
      types.Part.from_bytes(
        data=image_data,
        mime_type='image/jpeg',
      ),
      gemini_prompt
    ]
    )
    return response.text

def insert():
    from time import time

    # with open("./tests/mock_data.txt", encoding="utf-8-sig") as f:
    #     FAKE_TEXT = f.read()

    def getText(filename):
        doc = docx.Document(filename)
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        return '\n'.join(fullText)

    FAKE_TEXT1 = getText("testing_demo/data/36_2024_QH15_444251.docx")
    FAKE_TEXT2 = getText("testing_demo/data/168_2024_ND-CP_619502.docx")

    remove_if_exist(f"{WORKING_DIR}/vdb_entities.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_full_docs.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_text_chunks.json")
    remove_if_exist(f"{WORKING_DIR}/kv_store_community_reports.json")
    remove_if_exist(f"{WORKING_DIR}/graph_chunk_entity_relation.graphml")

    rag = GraphRAG(
        working_dir=WORKING_DIR,
        best_model_func=deepseepk_model_if_cache,
        cheap_model_func=deepseepk_model_if_cache,
        embedding_func=openai_embedding,
        chunk_func=chunking_by_special_separators,
    )
    start = time()
    rag.insert([FAKE_TEXT1, FAKE_TEXT2])
    print("indexing time:", time() - start)
    # rag = GraphRAG(working_dir=WORKING_DIR, enable_llm_cache=True)
    # rag.insert(FAKE_TEXT[half_len:])


if __name__ == "__main__":
    insert()
    # print(query("tín hiệu còi là gì"))
    # print("hi")