
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn
# import asyncio
# import io
# import os
# from dotenv import load_dotenv
# import edge_tts

# # 1. מייבאים את הספרייה של ג'מיני במקום זו של OpenAI
# import google.generativeai as genai

# # טעינת המשתנים מקובץ ה-.env לתוך סביבת הריצה
# load_dotenv()

# # 2. מגדירים את מפתח ה-API של גוגל
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # 3. כאן בדיוק מגדירים את המודל!
# model = genai.GenerativeModel('gemini-3-flash-preview')

# app = FastAPI()


#-----------------------------------------------------------הוספה
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import asyncio
import httpx
import io
import os
import json
import time
from datetime import datetime
import aiofiles
from dotenv import load_dotenv
import edge_tts
import google.generativeai as genai
from deepgram import AsyncDeepgramClient

# 1. טעינת המשתנים מקובץ ה-.env לתוך סביבת הריצה - חובה לפני שקוראים למפתחות!
load_dotenv()

# 2. הגדרת מודל Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')
# model = genai.GenerativeModel('gemini-3-flash-preview') 

# 3. הגדרת Deepgram
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")
deepgram = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)

# 4. קובץ הארכיון שלנו לניתוח סשנים
ARCHIVE_FILE = "sessions_archive.jsonl"

# 5. אתחול השרת
app = FastAPI()
#------------------------------------------------------------סיום


@app.get("/")
async def root():
    return {"status": "ok", "message": "Voice AI Server is running!"}

# async def process_stt_hebrew(audio_bytes: bytes) -> str:
#     print("STT Processing with Gemini...") # לוג התחלה
#     try:
#         # שולחים את האודיו ל-Gemini יחד עם הנחיה לתמלל
#         response = await model.generate_content_async([
#             {"mime_type": "audio/webm", "data": audio_bytes},
#             "תמלל את ההקלטה הבאה לעברית במדויק. החזר רק את הטקסט המתומלל ללא שום תוספות."
#         ])
#         print(f"STT Result: {response.text}") # לוג תוצאה
#         return response.text
#     except Exception as e:
#         print(f"Error during STT: {e}")
#         return "סליחה, לא הצלחתי להבין את ההקלטה."

# async def process_llm(text: str) -> str:
#     print("Sending to LLM...") # לוג התחלה
#     try:
#         # אנו מצרפים את הוראות המערכת לבקשה של המשתמש
#         prompt = f"הוראות מערכת: אתה נציג שירות לקוחות קולי. ענה בקצרה, לעניין ובעברית בלבד.\n\nדברי הלקוח: {text}"
        
#         response = await model.generate_content_async(prompt)
#         answer = response.text
        
#         print(f"AI Response: {answer}") # לוג תוצאה
#         return answer
#     except Exception as e:
#         print(f"Error in LLM: {e}")
#         return "הייתה שגיאה בעיבוד התשובה."


#----------------------------------------------------------------
# async def process_deepgram_stt(audio_bytes: bytes) -> dict:
#     """שולח אודיו ל-Deepgram (מעודכן לגרסה החדשה!)"""
#     print("-> Deepgram STT & Sentiment Processing...")
#     try:
#         # בגרסה החדשה פשוט מעבירים את ההגדרות ישירות
#         response = await deepgram.listen.v1.media.transcribe_file(
#             request=audio_bytes,
#             model="nova-2",
#             language="he",
#             smart_format=True,
#             analyze_sentiment=True
#         )
        
#         # חילוץ הנתונים (התשובה חוזרת כאובייקטים, לא כמילון)
#         result = response.results.channels[0].alternatives[0]
#         transcript = result.transcript
#         words = result.words
        
#         # חילוץ סנטימנט אם קיים
#         sentiment = "neutral"
#         if response.results.sentiments and response.results.sentiments.segments:
#             sentiment = response.results.sentiments.segments[0].sentiment

#         print(f"-> Deepgram Result: {transcript} | Sentiment: {sentiment}")
#         return {
#             "text": transcript,
#             "sentiment": sentiment,
#             "word_count": len(words) if words else 0,
#             "duration_sec": words[-1].end if words else 0.1
#         }
#     except Exception as e:
#         print(f"Error in Deepgram STT: {e}")
#         return {"text": "סליחה, לא שמעתי ברור.", "sentiment": "unknown", "word_count": 0, "duration_sec": 1}
# async def process_deepgram_stt(audio_bytes: bytes) -> dict:
#     """שולח אודיו ל-Deepgram בצורה ישירה (ללא סנטימנט שלא נתמך בעברית)"""
#     print("-> Deepgram STT Processing (Direct API)...")
#     try:

#         url = "https://api.deepgram.com/v1/listen?language=he&punctuate=true"
#         headers = {
#             "Authorization": f"Token {DEEPGRAM_API_KEY}",
#             "Content-Type": "audio/webm"
#         }
        
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
#             response.raise_for_status()
#             data = response.json()
            
#             result = data["results"]["channels"][0]["alternatives"][0]
#             transcript = result["transcript"]
#             words = result.get("words", [])

#             print(f"-> Deepgram Result: {transcript}")
#             return {
#                 "text": transcript,
#                 "sentiment": "neutral", # מכניסים ערך קבוע כי דיפגרם לא תומך בעברית לזה
#                 "word_count": len(words),
#                 "duration_sec": words[-1]["end"] if words else 0.1
#             }
#     except Exception as e:
#         print(f"Error in Deepgram STT: {e}")
#         return {"text": "סליחה, לא שמעתי ברור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}

# async def analyze_acoustics(audio_bytes: bytes, stt_data: dict) -> dict:
#     """מבצע ניתוח אקוסטי מהיר. במקום ספריות כבדות, נשתמש בנתוני ה-STT"""
#     print("-> Acoustic Analysis running...")
#     duration = stt_data["duration_sec"]
#     word_count = stt_data["word_count"]
    
#     wpm = int((word_count / duration) * 60) if duration > 0 else 0
#     size_kb = round(len(audio_bytes) / 1024, 2)
    
#     return {
#         "wpm": wpm,
#         "size_kb": size_kb
#     }

# async def process_llm_advanced(user_text: str, sentiment: str, acoustics: dict) -> dict:
#     """המוח: Gemini מקבל את הכל ומחזיר JSON עם התגובה והאנליזה"""
#     print("-> Sending complex data to Gemini LLM...")
#     try:
#         # אנו מבקשים מ-Gemini להחזיר רק JSON טהור כדי שנוכל לחלץ ממנו נתונים
#         prompt = f"""
#         אתה סימולטור חכם לאימון נציגי שירות לקוחות.
#         דברי הלקוח (המתאמן): "{user_text}"
#         סנטימנט קולי שזוהה: {sentiment}
#         קצב דיבור של הלקוח: {acoustics['wpm']} מילים בדקה.

#         נתח את תגובת הלקוח, והחזר אובייקט JSON תקני בלבד (ללא Markdown) במבנה הבא:
#         {{
#             "response_to_user": "תגובת הלקוח הווירטואלי (קצרה, בעברית)",
#             "analysis": {{
#                 "empathy_score": <ציון מ-1 עד 10>,
#                 "respect_score": <ציון מ-1 עד 10>,
#                 "feedback": "הערה קצרה למתאמן על טון הדיבור והאמפתיה שלו"
#             }}
#         }}
#         """
#         response = await model.generate_content_async(prompt)
#         text_response = response.text.replace("```json", "").replace("```", "").strip()
#         data = json.loads(text_response)
        
#         print(f"-> AI Response text: {data.get('response_to_user')}")
#         return data
#     except Exception as e:
#         print(f"Error in LLM Advanced: {e}")
#         # מבנה גיבוי למקרה של שגיאה
#         return {"response_to_user": "הייתה שגיאת עיבוד בשרת.", "analysis": {}}

# async def save_to_archive(session_data: dict):
#     """שומר את הניתוח לקובץ JSONL מקומי שבו כל שורה היא אובייקט חוקי"""
#     session_data["timestamp"] = datetime.now().isoformat()
#     try:
#         async with aiofiles.open(ARCHIVE_FILE, mode='a', encoding='utf-8') as f:
#             await f.write(json.dumps(session_data, ensure_ascii=False) + "\n")
#         print("-> Analytics saved to Archive.")
#     except Exception as e:
#         print(f"Failed to save archive: {e}")
# #------------------------------------------------------------------------------------


async def process_deepgram_stt(audio_bytes: bytes) -> dict:
    """מעקף ישיר ל-Deepgram - יציב וחסין תקלות"""
    print("-> Deepgram STT Processing (Direct API)...")
    try:
        # חזרנו ל-nova-2 שתומך בעברית, ללא תוספות מיותרות שיכשילו את הבקשה
        url = "https://api.deepgram.com/v1/listen?model=nova-2&language=he"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
            
            # אם יש שגיאה 400, עכשיו נראה בדיוק מה הסיבה האמיתית!
            if response.status_code != 200:
                print(f"!!! Deepgram Error Body: {response.text}") 
                response.raise_for_status()
                
            data = response.json()
            
            # בדיקה בטוחה שהתקבל טקסט
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

# שולפים את המפתח של ג'מיני באופן בטוח
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def process_llm_advanced(user_text: str, sentiment: str, acoustics: dict) -> dict:
    """מעקף ישיר ל-Gemini - עוקף את כל באגי ה-404 של הספרייה המיושנת"""
    print("-> Sending complex data to Gemini LLM (Direct API)...")
    
    # פנייה ישירה לכתובת ה-API של 1.5-flash ללא תלות בשום ספרייה!
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    אתה סימולטור חכם לאימון נציגי שירות לקוחות.
    דברי הלקוח (המתאמן): "{user_text}"
    סנטימנט קולי שזוהה: {sentiment}
    קצב דיבור של הלקוח: {acoustics['wpm']} מילים בדקה.

    נתח את תגובת הלקוח, והחזר אובייקט JSON תקני בלבד (ללא Markdown) במבנה הבא:
    {{
        "response_to_user": "תגובת הלקוח הווירטואלי (קצרה, בעברית)",
        "analysis": {{
            "empathy_score": 8,
            "respect_score": 9,
            "feedback": "הערה קצרה למתאמן על טון הדיבור והאמפתיה שלו"
        }}
    }}
    """
    
    # בניית המבנה שגוגל דורשת
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
            if response.status_code != 200:
                print(f"!!! Gemini Error Body: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            text_response = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # ניקוי במקרה שג'מיני עוטף את ה-JSON בסימני Markdown
            text_response = text_response.replace("```json", "").replace("```", "").strip()
            
            result_json = json.loads(text_response)
            print(f"-> AI Response text: {result_json.get('response_to_user')}")
            return result_json
            
    except Exception as e:
        print(f"Error in LLM Advanced: {e}")
        return {"response_to_user": "הייתה שגיאת עיבוד בשרת.", "analysis": {}}


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
            
            # # 2. המרה לטקסט (STT)
            # user_text = await process_stt_hebrew(audio_bytes)
            
            # # 3. עיבוד שפה טבעית ויצירת תגובה (LLM)
            # ai_response_text = await process_llm(user_text)

            # # 4. המרה חזרה לקול (TTS)
            # ai_audio_bytes = await process_tts_hebrew(ai_response_text)  
                     
            #------------------------------------------------------------------
            # --- צינור העיבוד החדש (The Pipeline) ---
            
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

            # 6. שליחת האודיו המוכן חזרה ללקוח
            if ai_audio_bytes:
                await websocket.send_bytes(ai_audio_bytes)
            #--------------------------------------------------------------------------

            # 5. שליחת האודיו המוכן חזרה ללקוח
            await websocket.send_bytes(ai_audio_bytes)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)