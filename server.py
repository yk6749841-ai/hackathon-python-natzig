# # from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# # import uvicorn
# # import asyncio
# # import httpx
# # import os
# # import json
# # from datetime import datetime
# # import aiofiles
# # from dotenv import load_dotenv
# # import edge_tts

# # # 1. טעינת המשתנים מקובץ ה-.env לתוך סביבת הריצה
# # load_dotenv()

# # # 2. שליפת מפתחות ה-API באופן מרוכז וחד-פעמי (ללא קריאה לספריות ה-SDK)
# # AI21_API_KEY = os.getenv("AI21_API_KEY")
# # DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")

# # # 3. קובץ הארכיון שלנו לניתוח סשנים (זה היה בקוד המקורי שלך וממשיך כאן)
# # ARCHIVE_FILE = "sessions_archive.jsonl"

# # # 5. אתחול השרת
# # app = FastAPI()


# # @app.get("/")
# # async def root():
# #     return {"status": "ok", "message": "Voice AI Server is running!"}

# # async def process_deepgram_stt(audio_bytes: bytes) -> dict:
# #     """מעקף ישיר ל-Deepgram - עובד עם המודל הכללי בדיוק כמו שהשרת שלהם דרש!"""
# #     print("-> Deepgram STT Processing (Direct API)...")
# #     try:
# #         url = "https://api.deepgram.com/v1/listen?model=nova-3&language=he"
# #         headers = {
# #             "Authorization": f"Token {DEEPGRAM_API_KEY}",
# #             "Content-Type": "audio/webm"
# #         }
        
# #         async with httpx.AsyncClient() as client:
# #             response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
            
# #             if response.status_code != 200:
# #                 print(f"!!! Deepgram Error Body: {response.text}") 
# #                 response.raise_for_status()
                
# #             data = response.json()
            
# #             if "results" in data and data["results"]["channels"]:
# #                 result = data["results"]["channels"][0]["alternatives"][0]
# #                 transcript = result["transcript"]
# #                 words = result.get("words", [])
                
# #                 print(f"-> Deepgram Result: {transcript}")
# #                 return {
# #                     "text": transcript,
# #                     "sentiment": "neutral",
# #                     "word_count": len(words),
# #                     "duration_sec": words[-1]["end"] if words else 0.1
# #                 }
# #             else:
# #                 return {"text": "לא זוהה דיבור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}
                
# #     except Exception as e:
# #         print(f"Error in Deepgram STT: {e}")
# #         return {"text": "סליחה, לא שמעתי ברור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}


# # async def analyze_acoustics(audio_bytes: bytes, stt_data: dict) -> dict:
# #     """מבצע ניתוח אקוסטי מהיר. הפונקציה שהלכה לאיבוד הוחזרה!"""
# #     print("-> Acoustic Analysis running...")
# #     duration = stt_data["duration_sec"]
# #     word_count = stt_data["word_count"]
    
# #     wpm = int((word_count / duration) * 60) if duration > 0 else 0
# #     size_kb = round(len(audio_bytes) / 1024, 2)
    
# #     return {
# #         "wpm": wpm,
# #         "size_kb": size_kb
# #     }


# # async def process_llm_advanced(user_text: str, sentiment: str, acoustics: dict) -> dict:
# #     """מעקף ישיר ל-AI21 - גרסה יציבה בדוקה"""
# #     print("-> Sending complex data to AI21 LLM (Direct API)...")
    
# #     AI21_API_KEY = os.getenv("AI21_API_KEY")
# #     # הכתובת הזו היא הסטנדרטית לכל המודלים מהדור החדש
# #     url = "https://api.ai21.com/studio/v1/chat/completions"
    
# #     headers = {
# #         "Authorization": f"Bearer {AI21_API_KEY}",
# #         "Content-Type": "application/json"
# #     }
    
# #     prompt = f"""
# #     אתה סימולטור אימון לנציגי שירות.
# #     הלקוח אמר: "{user_text}"
# #     החזר אובייקט JSON תקני בלבד (ללא Markdown) עם השדות:
# #     "response_to_user" (תגובת הלקוח הווירטואלי)
# #     "analysis" (משוב קצר לנציג)
# #     """

# #     payload = {
# #         "model": "jamba-instruct",  # זה השם המדויק ב-endpoint הזה
# #         "messages": [
# #             {
# #                 "role": "user",
# #                 "content": prompt
# #             }
# #         ],
# #         "max_tokens": 512,
# #         "temperature": 0.4
# #     }
    
# #     try:
# #         async with httpx.AsyncClient() as client:
# #             response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
# #             if response.status_code != 200:
# #                 print(f"!!! AI21 Error Body: {response.text}")
# #                 response.raise_for_status()
                
# #             data = response.json()
# #             text_response = data['choices'][0]['message']['content']
            
# #             # ניקוי סימני Markdown אם ה-AI הוסיף אותם בטעות
# #             text_response = text_response.replace("```json", "").replace("```", "").strip()
            
# #             # המרה ל-JSON
# #             return json.loads(text_response)
            
# #     except Exception as e:
# #         print(f"Error in LLM Advanced: {e}")
# #         # אם יש שגיאה, נחזיר תגובה פשוטה כדי שהתהליך לא ייתקע
# #         return {
# #             "response_to_user": "שלום, אני שומע אותך מצוין. איך אוכל לעזור?",
# #             "analysis": {"feedback": "החיבור ל-AI הצליח חלקית."}
# #         }


# # async def process_tts_hebrew(text: str) -> bytes:
# #     print("Generating Audio with Edge-TTS...") # לוג התחלה
# #     try:
# #         # משתמשים בקול הגברי של אברי (אפשר להחליף ל "he-IL-HilaNeural" לקול נשי)
# #         communicate = edge_tts.Communicate(text, "he-IL-AvriNeural")
        
# #         audio_bytes = b""
# #         async for chunk in communicate.stream():
# #             if chunk["type"] == "audio":
# #                 audio_bytes += chunk["data"]
                
# #         print(f"Audio Ready - Size: {len(audio_bytes)} bytes") # לוג הצלחה
# #         return audio_bytes
# #     except Exception as e:
# #         print(f"Error in TTS: {e}")
# #         return b""


# # async def save_to_archive(data: dict):
# #     """שומרת נתונים לקובץ ה-JSONL באופן אסינכרוני שלא תוקע את השרת"""
# #     try:
# #         # מוסיפים חותמת זמן כדי לדעת מתי הסשן התקיים
# #         data["timestamp"] = datetime.now().isoformat()
        
# #         # פתיחת הקובץ וכתיבה אליו ללא חסימה של השרת הראשי
# #         async with aiofiles.open(ARCHIVE_FILE, mode='a', encoding='utf-8') as f:
# #             await f.write(json.dumps(data, ensure_ascii=False) + "\n")
# #     except Exception as e:
# #         print(f"Error saving to archive: {e}") 
  

# # @app.websocket("/ws/voice")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     try:
# #         while True:
# #             # 1. קבלת מקטע האודיו מהלקוח (React)
# #             audio_bytes = await websocket.receive_bytes()

# #             #---------------------------------
# #             print(f"---> DEBUG: Raw data received! Size: {len(audio_bytes)} bytes", flush=True)
# #             #---------------------------------
            
          
# #             # 2. STT (Deepgram) מול קריאה מקבילית
# #             stt_data = await process_deepgram_stt(audio_bytes)
# #             user_text = stt_data["text"]

# #             # אם הלקוח שתק, אין טעם להמשיך
# #             if not user_text or len(user_text.strip()) < 2:
# #                 continue

# #             # 3. ניתוח אקוסטי במקביל (משתמש במידע מה-STT)
# #             acoustics = await analyze_acoustics(audio_bytes, stt_data)

# #             # 4. הפעלת מנוע ה-LLM לקבלת JSON מורכב
# #             llm_result = await process_llm_advanced(user_text, stt_data["sentiment"], acoustics)
# #             ai_text = llm_result.get("response_to_user", "")

# #         # 5. המרת התשובה לקול במקביל לשמירת הנתונים לארכיון
# #             archive_data = {
# #                 "user_text": user_text,
# #                 "deepgram_metadata": stt_data,
# #                 "acoustics": acoustics,
# #                 "ai_analysis": llm_result.get("analysis", {})
# #             }
            
# #             ai_audio_bytes, _ = await asyncio.gather(
# #                 process_tts_hebrew(ai_text),
# #                 save_to_archive(archive_data)
# #             )

# #             # 6. שליחת האודיו המוכן חזרה ללקוח (מופיע פעם אחת בלבד!)
# #             if ai_audio_bytes:
# #                 await websocket.send_bytes(ai_audio_bytes)
            
# #     except WebSocketDisconnect:
# #         print("Client disconnected")
# #     except Exception as e:
# #         print(f"Error: {e}")

# # if __name__ == "__main__":
# #     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)





# import os
# import json
# import itertools
# import asyncio
# import httpx
# import aiofiles
# import edge_tts
# import requests
# from google import genai
# from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from dotenv import load_dotenv
# from typing import List, Optional
# from datetime import datetime

# #הוספה
# from google.genai import types
# #סיום

# load_dotenv()

# # --- 1. הגדרות תשתית ונטפרי ---
# JAVA_SERVER_URL = os.getenv("JAVA_SERVER_URL", "").rstrip('/')
# cert_path = r'C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt'
# if os.path.exists(cert_path):
#     os.environ['SSL_CERT_FILE'] = cert_path
#     os.environ['REQUESTS_CA_BUNDLE'] = cert_path
#     print("✅ NetFree Certificate loaded")

# # --- 2. טעינת חוקים גנריים ---
# try:
#     from prompts import GENERIC_RULES as GENERAL_PROMPT
# except ImportError:
#     GENERAL_PROMPT = "חוקי סימולציה כלליים חסרים."

# # --- 3. ניהול מפתחות API (Gemini Tier 1) ---
# api_keys = ["AIzaSyCMCx14A7r-jHtc7XjyBArU1jdcamUyNqM"]

# if not api_keys or api_keys[0] == "YOUR_NEW_KEY_HERE":
#     api_keys = [os.getenv("AI_STUDIO_API_KEY")]

# key_cycle = itertools.cycle(api_keys)
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")

# app = FastAPI()
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# current_scenario_prompt = ""
# port = int(os.environ.get("PORT", 8001))


# # --- 4. מודלים של נתונים ---
# class ChatRequest(BaseModel):
#     deepgram_data: dict
#     history: List[dict] = []
#     system_prompt: Optional[str] = None
#     voice_analysis_metrics: Optional[dict] = None

# # --- 5. פונקציות עזר לעיבוד קול ---
# async def process_deepgram_stt(audio_bytes: bytes) -> str:
#     try:
#         url = "https://api.deepgram.com/v1/listen?model=nova-3&language=he"
#         headers = {
#             "Authorization": f"Token {DEEPGRAM_API_KEY}",
#             "Content-Type": "audio/webm"
#         }
#         verify_cert = cert_path if os.path.exists(cert_path) else True
#         async with httpx.AsyncClient(verify=verify_cert) as client:
#             response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
#             data = response.json()
#             return data["results"]["channels"][0]["alternatives"][0]["transcript"]
#     except Exception as e:
#         print(f"❌ שגיאה בתמלול: {e}")
#         return ""

# async def process_tts_hebrew(text: str) -> bytes:
#     try:
#         communicate = edge_tts.Communicate(text, "he-IL-AvriNeural")
#         audio_bytes = b""
#         async for chunk in communicate.stream():
#             if chunk["type"] == "audio":
#                 audio_bytes += chunk["data"]
#         return audio_bytes
#     except Exception as e:
#         print(f"❌ שגיאה ביצירת קול: {e}")
#         return b""

# # --- 6. נקודת קצה לשיחה קולית (WebSocket) ---
# @app.websocket("/ws/voice/{assignment_id}")
# async def websocket_endpoint(websocket: WebSocket, assignment_id: str):
#     # הסרנו את ה-accept הכפול שגרם לקריסה
#     print(f"🚀 חיבור קולי נפתח עבור משימה מספר: {assignment_id}")
#     await websocket.accept()
    
#     global current_scenario_prompt
#     session_history = []

#     try:
#         while True:
#             message = await websocket.receive()

#             if "bytes" in message:
#                 audio_bytes = message["bytes"]

#                 user_text = await process_deepgram_stt(audio_bytes)
#                 if not user_text or len(user_text.strip()) < 2:
#                     continue
#                 print(f"🗣️ נציג: {user_text}")

#                 await websocket.send_text(json.dumps({"user_text": user_text}))
                
#                 active_prompt = current_scenario_prompt or GENERAL_PROMPT
#                 client = genai.Client(api_key=next(key_cycle))

#                 gemini_history = []
#                 for msg in session_history:
#                     role = "user" if msg["role"] == "user" else "model"
#                     gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

#                 full_response = ""
#                 sentence_buffer = ""

#                 # שינינו ל-gemini-2.0-flash כדי לוודא תאימות (2.5 לא קיים רשמית)
#                 stream = client.models.generate_content_stream(
#                     model="gemini-2.0-flash",
#                     config={
#                         "system_instruction": active_prompt,
#                         "temperature": 0.7
#                     },
#                     contents=gemini_history + [{"role": "user", "parts": [{"text": user_text}]}]
#                 )

#                 print("🤖 לקוח (Gemini) מתחיל לייצר תשובה...")

#                 for chunk in stream:
#                     chunk_text = chunk.text
#                     full_response += chunk_text
#                     sentence_buffer += chunk_text

#                     if any(punc in chunk_text for punc in [".", "?", "!", "\n"]):
#                         clean_sentence = sentence_buffer.strip()
#                         if clean_sentence and len(clean_sentence) > 2:
#                             if "JSON:" not in clean_sentence and "{" not in clean_sentence:
#                                 tts_text = clean_sentence.replace("[END_CALL]", "")
#                                 if tts_text.strip():
#                                     audio_chunk = await process_tts_hebrew(tts_text)
#                                     if audio_chunk:
#                                         await websocket.send_bytes(audio_chunk)
                            
#                             await websocket.send_text(json.dumps({"text": clean_sentence.replace("[END_CALL]", "")}))
#                             sentence_buffer = ""

#                 # שליחת שארית הטקסט אם קיימת
#                 if sentence_buffer.strip():
#                     await websocket.send_text(json.dumps({"text": sentence_buffer.strip().replace("[END_CALL]", "")}))

#                 await websocket.send_text(json.dumps({"status": "end_of_turn"}))

#                 session_history.append({"role": "user", "content": user_text})
#                 session_history.append({"role": "assistant", "content": full_response})

#                 print(f"✅ סיום סבב שיחה.")

#     except WebSocketDisconnect:
#         print(f"❌ החיבור למשימה {assignment_id} נסגר")
#     except Exception as e:
#         print(f"⚠️ שגיאה ב-WebSocket: {str(e)}")

# # --- 8. נקודת קצה לאתחול ---
# @app.post("/initialize-simulation")
# async def initialize_simulation(request: Request):
#     global current_scenario_prompt
#     try:
#         local_data = await request.json()
#         print(f"📦 קיבלתי נתונים מהריאקט עבור: {local_data.get('customerName', 'לא ידוע')}")

#         c_name = local_data.get("customerName", "הלקוח")
#         c_reason = local_data.get("reason", "סיבת הפנייה לא הוגדרה")
#         c_mood = local_data.get("initialMood", "ניטרלי")

#         meta_prompt = f"""
#         # הוראה קריטית למודל ה-AI:
#         אתה שחקן בסימולציה מקצועית. שמך הוא {c_name}.
#         תפקידך הבלעדי: לקוח שפנה לשירות בגלל: "{c_reason}".
#         מצבך הרגשי ההתחלתי: {c_mood}.
#         # חוקי הברזל של הדמות:
#         1. איסור היפוך תפקידים: אתה לעולם לא הנציג. 
#         2. תגובה למדדי קול: בסוגריים מרובעים תקבל נתוני קול.
#         3. בלי "דיבור בוט": אל תגיד "אני לא יכול להמשיך". 
#         4. סיום שיחה: כאשר הבעיה נפתרה או שהשיחה הגיעה לסיומה הטבעי, חובה עליך להוסיף בסוף התגובה שלך את המילה: [END_CALL]
#         {GENERAL_PROMPT}
#         {json.dumps(local_data, ensure_ascii=False, indent=2)}
#         החזר אך ורק את מסמך ההנחיות הסופי (System Prompt).
#         """

#         client = genai.Client(api_key=next(key_cycle))
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=meta_prompt,
#             config={"temperature": 0.3}
#         )

#         current_scenario_prompt = response.text.strip()
#         print(f"🎯 תסריט ה-System Prompt נבנה בהצלחה!")

#         if JAVA_SERVER_URL:
#             payload_to_java = {
#                 "name": c_name,
#                 "systemPrompt": current_scenario_prompt,
#                 "difficulty": local_data.get("difficulty", "Medium"),
#                 "category": local_data.get("category", "General"),
#                 "rawData": json.dumps(local_data, ensure_ascii=False)
#             }
#             if "id" in local_data:
#                 payload_to_java["id"] = local_data["id"]

#             try:
#                 requests.post(f"{JAVA_SERVER_URL}/api/manager/add-scenario", json=payload_to_java, timeout=5)
#                 print("💾 התרחיש נשמר ב-Java!")
#             except Exception as j_err:
#                 print(f"⚠️ שגיאה בשמירה ל-Java: {j_err}")

#         return {"status": "success", "final_prompt": current_scenario_prompt}

#     except Exception as e:
#         print(f"❌ שגיאה קריטית באתחול פייתון: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# # --- 9. נקודת קצה לצ'אט ---
# @app.post("/chat")
# async def chat_with_agent(request: ChatRequest):
#     global current_scenario_prompt
#     try:
#         agent_text = request.deepgram_data["results"]["channels"][0]["alternatives"][0]["transcript"]
#         active_prompt = request.system_prompt or current_scenario_prompt or GENERAL_PROMPT
#         chat_history = []
#         for msg in request.history:
#             role = "user" if msg["role"] == "user" else "model"
#             chat_history.append({"role": role, "parts": [{"text": msg["content"]}]})

#         client = genai.Client(api_key=next(key_cycle))
#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             config={"system_instruction": active_prompt, "temperature": 0.7},
#             contents=chat_history + [{"role": "user", "parts": [{"text": agent_text}]}]
#         )
#         return {"reply": response.text}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     # הרצת השרת בצורה תקינה
#     uvicorn.run(app, host="0.0.0.0", port=port)



import os
import json
import itertools
import asyncio
import httpx
import aiofiles
import edge_tts
import requests
from google import genai
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
from google.genai import types

load_dotenv()

# --- 1. הגדרות תשתית ונטפרי (לא יפריע ב-Render) ---
JAVA_SERVER_URL = os.getenv("JAVA_SERVER_URL", "").rstrip('/')
cert_path = r'C:\ProgramData\NetFree\CA\netfree-ca-bundle-curl.crt'
if os.path.exists(cert_path):
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    print("✅ NetFree Certificate loaded")

# --- 2. טעינת חוקים גנריים ---
try:
    from prompts import GENERIC_RULES as GENERAL_PROMPT
except ImportError:
    GENERAL_PROMPT = "חוקי סימולציה כלליים חסרים."

# --- 3. ניהול מפתחות API ---
api_keys = ["AIzaSyCMCx14A7r-jHtc7XjyBArU1jdcamUyNqM"]
if not api_keys or api_keys[0] == "YOUR_NEW_KEY_HERE":
    api_keys = [os.getenv("AI_STUDIO_API_KEY")]

key_cycle = itertools.cycle(api_keys)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

current_scenario_prompt = ""
port = int(os.environ.get("PORT", 8000))

class ChatRequest(BaseModel):
    deepgram_data: dict
    history: List[dict] = []
    system_prompt: Optional[str] = None
    voice_analysis_metrics: Optional[dict] = None

# 👇 הוספתי את הנתיב הזה כדי שנוכל לבדוק אם השרת חי! 👇
@app.get("/")
async def root():
    return {"status": "success", "message": "✅ Server is LIVE and ready for WebSockets on Render!"}

# --- פונקציות עזר לעיבוד קול ---
async def process_deepgram_stt(audio_bytes: bytes) -> str:
    try:
        url = "https://api.deepgram.com/v1/listen?model=nova-3&language=he"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }
        verify_cert = cert_path if os.path.exists(cert_path) else True
        async with httpx.AsyncClient(verify=verify_cert) as client:
            response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
            data = response.json()
            return data["results"]["channels"][0]["alternatives"][0]["transcript"]
    except Exception as e:
        print(f"❌ Error STT: {e}")
        return ""

async def process_tts_hebrew(text: str) -> bytes:
    try:
        communicate = edge_tts.Communicate(text, "he-IL-AvriNeural")
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes
    except Exception as e:
        print(f"❌ Error TTS: {e}")
        return b""

# --- נקודת קצה לשיחה קולית (WebSocket) ---
@app.websocket("/ws/voice/{assignment_id}")
async def websocket_endpoint(websocket: WebSocket, assignment_id: str):
    print(f"🚀 חיבור קולי נפתח עבור משימה: {assignment_id}")
    await websocket.accept()
    
    global current_scenario_prompt
    session_history = []

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                audio_bytes = message["bytes"]
                user_text = await process_deepgram_stt(audio_bytes)
                
                if not user_text or len(user_text.strip()) < 2:
                    continue
                
                print(f"🗣️ נציג: {user_text}")
                await websocket.send_text(json.dumps({"user_text": user_text}))
                
                active_prompt = current_scenario_prompt or GENERAL_PROMPT
                client = genai.Client(api_key=next(key_cycle))

                gemini_history = []
                for msg in session_history:
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

                full_response = ""
                sentence_buffer = ""

                stream = client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    config={"system_instruction": active_prompt, "temperature": 0.7},
                    contents=gemini_history + [{"role": "user", "parts": [{"text": user_text}]}]
                )

                for chunk in stream:
                    chunk_text = chunk.text
                    full_response += chunk_text
                    sentence_buffer += chunk_text

                    if any(punc in chunk_text for punc in [".", "?", "!", "\n"]):
                        clean_sentence = sentence_buffer.strip()
                        if clean_sentence and len(clean_sentence) > 2:
                            if "JSON:" not in clean_sentence and "{" not in clean_sentence:
                                tts_text = clean_sentence.replace("[END_CALL]", "")
                                if tts_text.strip():
                                    audio_chunk = await process_tts_hebrew(tts_text)
                                    if audio_chunk:
                                        await websocket.send_bytes(audio_chunk)
                            
                            await websocket.send_text(json.dumps({"text": clean_sentence.replace("[END_CALL]", "")}))
                            sentence_buffer = ""

                if sentence_buffer.strip():
                    await websocket.send_text(json.dumps({"text": sentence_buffer.strip().replace("[END_CALL]", "")}))

                await websocket.send_text(json.dumps({"status": "end_of_turn"}))
                session_history.append({"role": "user", "content": user_text})
                session_history.append({"role": "assistant", "content": full_response})

    except WebSocketDisconnect:
        print(f"❌ החיבור למשימה {assignment_id} נסגר")
    except Exception as e:
        print(f"⚠️ שגיאה ב-WebSocket: {str(e)}")

@app.post("/initialize-simulation")
async def initialize_simulation(request: Request):
    global current_scenario_prompt
    try:
        local_data = await request.json()
        c_name = local_data.get("customerName", "הלקוח")
        c_reason = local_data.get("reason", "סיבת הפנייה לא הוגדרה")
        c_mood = local_data.get("initialMood", "ניטרלי")

        meta_prompt = f"""
        אתה שחקן בסימולציה. שמך הוא {c_name}. פנית בגלל: "{c_reason}".
        מצבך הרגשי: {c_mood}. חוק: אל תשבור דמות לעולם. כאשר הבעיה נפתרה, כתוב: [END_CALL].
        {GENERAL_PROMPT}
        החזר אך ורק את מסמך ההנחיות הסופי.
        """

        client = genai.Client(api_key=next(key_cycle))
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=meta_prompt, config={"temperature": 0.3}
        )
        current_scenario_prompt = response.text.strip()

        if JAVA_SERVER_URL:
            try:
                payload = {
                    "name": c_name, "systemPrompt": current_scenario_prompt,
                    "difficulty": local_data.get("difficulty", "Medium"),
                    "category": local_data.get("category", "General"),
                    "rawData": json.dumps(local_data, ensure_ascii=False)
                }
                if "id" in local_data: payload["id"] = local_data["id"]
                requests.post(f"{JAVA_SERVER_URL}/api/manager/add-scenario", json=payload, timeout=5)
            except: pass

        return {"status": "success", "final_prompt": current_scenario_prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
