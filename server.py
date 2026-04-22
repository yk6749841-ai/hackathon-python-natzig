# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# import uvicorn
# import asyncio
# import httpx
# import os
# import json
# from datetime import datetime
# import aiofiles
# from dotenv import load_dotenv
# import edge_tts

# # 1. טעינת המשתנים מקובץ ה-.env לתוך סביבת הריצה
# load_dotenv()

# # 2. שליפת מפתחות ה-API באופן מרוכז וחד-פעמי (ללא קריאה לספריות ה-SDK)
# AI21_API_KEY = os.getenv("AI21_API_KEY")
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_KEY")

# # 3. קובץ הארכיון שלנו לניתוח סשנים (זה היה בקוד המקורי שלך וממשיך כאן)
# ARCHIVE_FILE = "sessions_archive.jsonl"

# # 5. אתחול השרת
# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"status": "ok", "message": "Voice AI Server is running!"}

# async def process_deepgram_stt(audio_bytes: bytes) -> dict:
#     """מעקף ישיר ל-Deepgram - עובד עם המודל הכללי בדיוק כמו שהשרת שלהם דרש!"""
#     print("-> Deepgram STT Processing (Direct API)...")
#     try:
#         url = "https://api.deepgram.com/v1/listen?model=nova-3&language=he"
#         headers = {
#             "Authorization": f"Token {DEEPGRAM_API_KEY}",
#             "Content-Type": "audio/webm"
#         }
        
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, headers=headers, content=audio_bytes, timeout=15.0)
            
#             if response.status_code != 200:
#                 print(f"!!! Deepgram Error Body: {response.text}") 
#                 response.raise_for_status()
                
#             data = response.json()
            
#             if "results" in data and data["results"]["channels"]:
#                 result = data["results"]["channels"][0]["alternatives"][0]
#                 transcript = result["transcript"]
#                 words = result.get("words", [])
                
#                 print(f"-> Deepgram Result: {transcript}")
#                 return {
#                     "text": transcript,
#                     "sentiment": "neutral",
#                     "word_count": len(words),
#                     "duration_sec": words[-1]["end"] if words else 0.1
#                 }
#             else:
#                 return {"text": "לא זוהה דיבור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}
                
#     except Exception as e:
#         print(f"Error in Deepgram STT: {e}")
#         return {"text": "סליחה, לא שמעתי ברור.", "sentiment": "neutral", "word_count": 0, "duration_sec": 1}


# async def analyze_acoustics(audio_bytes: bytes, stt_data: dict) -> dict:
#     """מבצע ניתוח אקוסטי מהיר. הפונקציה שהלכה לאיבוד הוחזרה!"""
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
#     """מעקף ישיר ל-AI21 - גרסה יציבה בדוקה"""
#     print("-> Sending complex data to AI21 LLM (Direct API)...")
    
#     AI21_API_KEY = os.getenv("AI21_API_KEY")
#     # הכתובת הזו היא הסטנדרטית לכל המודלים מהדור החדש
#     url = "https://api.ai21.com/studio/v1/chat/completions"
    
#     headers = {
#         "Authorization": f"Bearer {AI21_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     prompt = f"""
#     אתה סימולטור אימון לנציגי שירות.
#     הלקוח אמר: "{user_text}"
#     החזר אובייקט JSON תקני בלבד (ללא Markdown) עם השדות:
#     "response_to_user" (תגובת הלקוח הווירטואלי)
#     "analysis" (משוב קצר לנציג)
#     """

#     payload = {
#         "model": "jamba-instruct",  # זה השם המדויק ב-endpoint הזה
#         "messages": [
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         "max_tokens": 512,
#         "temperature": 0.4
#     }
    
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
#             if response.status_code != 200:
#                 print(f"!!! AI21 Error Body: {response.text}")
#                 response.raise_for_status()
                
#             data = response.json()
#             text_response = data['choices'][0]['message']['content']
            
#             # ניקוי סימני Markdown אם ה-AI הוסיף אותם בטעות
#             text_response = text_response.replace("```json", "").replace("```", "").strip()
            
#             # המרה ל-JSON
#             return json.loads(text_response)
            
#     except Exception as e:
#         print(f"Error in LLM Advanced: {e}")
#         # אם יש שגיאה, נחזיר תגובה פשוטה כדי שהתהליך לא ייתקע
#         return {
#             "response_to_user": "שלום, אני שומע אותך מצוין. איך אוכל לעזור?",
#             "analysis": {"feedback": "החיבור ל-AI הצליח חלקית."}
#         }


# async def process_tts_hebrew(text: str) -> bytes:
#     print("Generating Audio with Edge-TTS...") # לוג התחלה
#     try:
#         # משתמשים בקול הגברי של אברי (אפשר להחליף ל "he-IL-HilaNeural" לקול נשי)
#         communicate = edge_tts.Communicate(text, "he-IL-AvriNeural")
        
#         audio_bytes = b""
#         async for chunk in communicate.stream():
#             if chunk["type"] == "audio":
#                 audio_bytes += chunk["data"]
                
#         print(f"Audio Ready - Size: {len(audio_bytes)} bytes") # לוג הצלחה
#         return audio_bytes
#     except Exception as e:
#         print(f"Error in TTS: {e}")
#         return b""


# async def save_to_archive(data: dict):
#     """שומרת נתונים לקובץ ה-JSONL באופן אסינכרוני שלא תוקע את השרת"""
#     try:
#         # מוסיפים חותמת זמן כדי לדעת מתי הסשן התקיים
#         data["timestamp"] = datetime.now().isoformat()
        
#         # פתיחת הקובץ וכתיבה אליו ללא חסימה של השרת הראשי
#         async with aiofiles.open(ARCHIVE_FILE, mode='a', encoding='utf-8') as f:
#             await f.write(json.dumps(data, ensure_ascii=False) + "\n")
#     except Exception as e:
#         print(f"Error saving to archive: {e}") 
  

# @app.websocket("/ws/voice")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             # 1. קבלת מקטע האודיו מהלקוח (React)
#             audio_bytes = await websocket.receive_bytes()

#             #---------------------------------
#             print(f"---> DEBUG: Raw data received! Size: {len(audio_bytes)} bytes", flush=True)
#             #---------------------------------
            
          
#             # 2. STT (Deepgram) מול קריאה מקבילית
#             stt_data = await process_deepgram_stt(audio_bytes)
#             user_text = stt_data["text"]

#             # אם הלקוח שתק, אין טעם להמשיך
#             if not user_text or len(user_text.strip()) < 2:
#                 continue

#             # 3. ניתוח אקוסטי במקביל (משתמש במידע מה-STT)
#             acoustics = await analyze_acoustics(audio_bytes, stt_data)

#             # 4. הפעלת מנוע ה-LLM לקבלת JSON מורכב
#             llm_result = await process_llm_advanced(user_text, stt_data["sentiment"], acoustics)
#             ai_text = llm_result.get("response_to_user", "")

#         # 5. המרת התשובה לקול במקביל לשמירת הנתונים לארכיון
#             archive_data = {
#                 "user_text": user_text,
#                 "deepgram_metadata": stt_data,
#                 "acoustics": acoustics,
#                 "ai_analysis": llm_result.get("analysis", {})
#             }
            
#             ai_audio_bytes, _ = await asyncio.gather(
#                 process_tts_hebrew(ai_text),
#                 save_to_archive(archive_data)
#             )

#             # 6. שליחת האודיו המוכן חזרה ללקוח (מופיע פעם אחת בלבד!)
#             if ai_audio_bytes:
#                 await websocket.send_bytes(ai_audio_bytes)
            
#     except WebSocketDisconnect:
#         print("Client disconnected")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)





import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, TextField, IconButton, Fab, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

const NOTE_COLOR = '#fff9c4'; 
const ACCENT_PINK = '#e91e63';

const AgentNotes = () => {
  const [notes, setNotes] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [user, setUser] = useState<any>(null);

  // שימוש בפורט 8080 כפי שמופיע ב-application.properties
  const API_BASE = "http://localhost:8080/api/agent";

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
    if (savedUser.id) {
      setUser(savedUser);
      fetchNotes(savedUser.id);
    }
  }, []);

  const fetchNotes = async (userId: number) => {
    try {
      const res = await axios.get(`${API_BASE}/${userId}/notes`);
      setNotes(res.data);
    } catch (err) {
      console.error("שגיאה בטעינת פתקים:", err);
    }
  };

  const handleAddNote = async () => {
    if (!newNoteContent.trim() || !user) return;
    try {
      await axios.post(`${API_BASE}/${user.id}/add-note`, newNoteContent, {
        headers: { 'Content-Type': 'text/plain' }
      });
      setNewNoteContent('');
      setOpen(false);
      fetchNotes(user.id);
    } catch (err) {
      console.error("שגיאה בהוספת פתק:", err);
    }
  };

  const handleDeleteNote = async (id: number) => {
    try {
      await axios.delete(`${API_BASE}/delete-note/${id}`);
      fetchNotes(user.id);
    } catch (err) {
      console.error("שגיאה במחיקת פתק:", err);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 800, color: '#1e1e2d' }}>הפתקים שלי 📝</Typography>
      <Grid container spacing={3}>
        {notes.map((note) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={note.id}>
            <Paper elevation={3} sx={{ p: 3, bgcolor: NOTE_COLOR, minHeight: '150px', position: 'relative', transform: 'rotate(-1deg)' }}>
              <IconButton 
                size="small" 
                onClick={() => handleDeleteNote(note.id)}
                sx={{ position: 'absolute', top: 5, left: 5, color: 'rgba(0,0,0,0.2)' }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
              <Typography variant="body1" sx={{ mt: 1, textAlign: 'right' }}>{note.content}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
      <Fab color="primary" sx={{ position: 'fixed', bottom: 30, left: 30, bgcolor: ACCENT_PINK }} onClick={() => setOpen(true)}>
        <AddIcon />
      </Fab>
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle sx={{ textAlign: 'right' }}>הוספת פתק חדש</DialogTitle>
        <DialogContent>
          <TextField autoFocus multiline rows={4} fullWidth variant="outlined" value={newNoteContent} onChange={(e) => setNewNoteContent(e.target.value)} sx={{ mt: 1, direction: 'rtl' }} />
        </DialogContent>
        <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
          <Button onClick={() => setOpen(false)}>ביטול</Button>
          <Button onClick={handleAddNote} variant="contained" sx={{ bgcolor: ACCENT_PINK }}>שמור</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentNotes;
