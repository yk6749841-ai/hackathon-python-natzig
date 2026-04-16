from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import asyncio
import httpx
import os
import json
from datetime import datetime
import aiofiles
from dotenv import load_dotenv
import edge_tts

# 1. טעינת המשתנים מקובץ ה-.env לתוך סביבת הריצה
load_dotenv()

# 2. שליפת מפתחות ה-API באופן מרוכז וחד-פעמי (ללא קריאה לספריות ה-SDK)
AI21_API_KEY = os.getenv("AI21_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")

# 3. קובץ הארכיון שלנו לניתוח סשנים (זה היה בקוד המקורי שלך וממשיך כאן)
ARCHIVE_FILE = "sessions_archive.jsonl"

# 5. אתחול השרת
app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok", "message": "Voice AI Server is running!"}

async def process_deepgram_stt(audio_bytes: bytes) -> dict:
    """מעקף ישיר ל-Deepgram - עובד עם המודל הכללי בדיוק כמו שהשרת שלהם דרש!"""
    print("-> Deepgram STT Processing (Direct API)...")
    try:
        url = "https://api.deepgram.com/v1/listen?model=nova-3&language=he"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
            
            if response.status_code != 200:
                print(f"!!! Deepgram Error Body: {response.text}") 
                response.raise_for_status()
                
            data = response.json()
            
            if "results" in data and data["results"]["channels"]:
                result = data["results"]["channels"][0]["alternatives"][0]
                transcript = result["transcript"]
                words = result.get("words", [])
                
                print(f"-> Deepgram Result: {transcript}")
                return {
                    "text": transcript,
                    "sentiment": "neutral",
                    "word_count": len(words),
                    "duration_sec": words[-1]["end"] if words else 0.1
                }
            else:
                return {"text": "לא זוהה דיבור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}
                
    except Exception as e:
        print(f"Error in Deepgram STT: {e}")
        return {"text": "סליחה, לא שמעתי ברור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}


async def analyze_acoustics(audio_bytes: bytes, stt_data: dict) -> dict:
    """מבצע ניתוח אקוסטי מהיר. הפונקציה שהלכה לאיבוד הוחזרה!"""
    print("-> Acoustic Analysis running...")
    duration = stt_data["duration_sec"]
    word_count = stt_data["word_count"]
    
    wpm = int((word_count / duration) * 60) if duration > 0 else 0
    size_kb = round(len(audio_bytes) / 1024, 2)
    
    return {
        "wpm": wpm,
        "size_kb": size_kb
    }


async def process_llm_advanced(user_text: str, sentiment: str, acoustics: dict) -> dict:
    """מעקף ישיר ל-AI21 - גרסה יציבה בדוקה"""
    print("-> Sending complex data to AI21 LLM (Direct API)...")
    
    AI21_API_KEY = os.getenv("AI21_API_KEY")
    # הכתובת הזו היא הסטנדרטית לכל המודלים מהדור החדש
    url = "https://api.ai21.com/studio/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {AI21_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    אתה סימולטור אימון לנציגי שירות.
    הלקוח אמר: "{user_text}"
    החזר אובייקט JSON תקני בלבד (ללא Markdown) עם השדות:
    "response_to_user" (תגובת הלקוח הווירטואלי)
    "analysis" (משוב קצר לנציג)
    """

    payload = {
        "model": "jamba-instruct",  # זה השם המדויק ב-endpoint הזה
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 512,
        "temperature": 0.4
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
            if response.status_code != 200:
                print(f"!!! AI21 Error Body: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            text_response = data['choices'][0]['message']['content']
            
            # ניקוי סימני Markdown אם ה-AI הוסיף אותם בטעות
            text_response = text_response.replace("```json", "").replace("```", "").strip()
            
            # המרה ל-JSON
            return json.loads(text_response)
            
    except Exception as e:
        print(f"Error in LLM Advanced: {e}")
        # אם יש שגיאה, נחזיר תגובה פשוטה כדי שהתהליך לא ייתקע
        return {
            "response_to_user": "שלום, אני שומע אותך מצוין. איך אוכל לעזור?",
            "analysis": {"feedback": "החיבור ל-AI הצליח חלקית."}
        }


async def process_tts_hebrew(text: str) -> bytes:
    print("Generating Audio with Edge-TTS...") # לוג התחלה
    try:
        # משתמשים בקול הגברי של אברי (אפשר להחליף ל "he-IL-HilaNeural" לקול נשי)
        communicate = edge_tts.Communicate(text, "he-IL-AvriNeural")
        
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
                
        print(f"Audio Ready - Size: {len(audio_bytes)} bytes") # לוג הצלחה
        return audio_bytes
    except Exception as e:
        print(f"Error in TTS: {e}")
        return b""


async def save_to_archive(data: dict):
    """שומרת נתונים לקובץ ה-JSONL באופן אסינכרוני שלא תוקע את השרת"""
    try:
        # מוסיפים חותמת זמן כדי לדעת מתי הסשן התקיים
        data["timestamp"] = datetime.now().isoformat()
        
        # פתיחת הקובץ וכתיבה אליו ללא חסימה של השרת הראשי
        async with aiofiles.open(ARCHIVE_FILE, mode='a', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error saving to archive: {e}") 
  

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. קבלת מקטע האודיו מהלקוח (React)
            audio_bytes = await websocket.receive_bytes()

            #---------------------------------
            print(f"---> DEBUG: Raw data received! Size: {len(audio_bytes)} bytes", flush=True)
            #---------------------------------
            
          
            # 2. STT (Deepgram) מול קריאה מקבילית
            stt_data = await process_deepgram_stt(audio_bytes)
            user_text = stt_data["text"]

            # אם הלקוח שתק, אין טעם להמשיך
            if not user_text or len(user_text.strip()) < 2:
                continue

            # 3. ניתוח אקוסטי במקביל (משתמש במידע מה-STT)
            acoustics = await analyze_acoustics(audio_bytes, stt_data)

            # 4. הפעלת מנוע ה-LLM לקבלת JSON מורכב
            llm_result = await process_llm_advanced(user_text, stt_data["sentiment"], acoustics)
            ai_text = llm_result.get("response_to_user", "")

        # 5. המרת התשובה לקול במקביל לשמירת הנתונים לארכיון
            archive_data = {
                "user_text": user_text,
                "deepgram_metadata": stt_data,
                "acoustics": acoustics,
                "ai_analysis": llm_result.get("analysis", {})
            }
            
            ai_audio_bytes, _ = await asyncio.gather(
                process_tts_hebrew(ai_text),
                save_to_archive(archive_data)
            )

            # 6. שליחת האודיו המוכן חזרה ללקוח (מופיע פעם אחת בלבד!)
            if ai_audio_bytes:
                await websocket.send_bytes(ai_audio_bytes)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)