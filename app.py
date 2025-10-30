from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Use your existing logic from main.py (do NOT change main.py beyond the __main__ guard)
from main import get_sentiment, get_llm_reply, speak

app = FastAPI()

# Optional static mount if you later add assets (icons, css)


@app.get("/", response_class=HTMLResponse)
def index():
    # Single-page app: Chat UI + mic + fetch-based chatting (no reloads)
    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Clarity AI</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        :root{
          --bg1:#06a7b7; /* teal */
          --bg2:#81d742; /* green */
          --pill-border:rgba(255,255,255,0.85);
          --text:#ffffff;
          --bubble-user: rgba(255,255,255,0.15);
          --bubble-bot: rgba(0,0,0,0.15);
        }
        *{box-sizing:border-box}
        html,body{height:100%}
        body{
          margin:0;
          font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif;
          color:var(--text);
          background: linear-gradient(90deg, var(--bg1) 0%, var(--bg2) 100%);
          display:flex; flex-direction:column;
        }
        .wrap{ flex:1; display:flex; flex-direction:column; padding:24px; gap:16px; }
        .brand{ font-weight:800; font-size:22px; letter-spacing:.4px; }
        .chat{
          flex:1;
          width:min(900px, 92vw);
          margin:0 auto;
          padding:16px;
          border-radius:18px;
          border:2px solid var(--pill-border);
          backdrop-filter:saturate(140%) blur(2px);
          overflow-y:auto;
          max-height: calc(100vh - 210px);
        }
        .row{ display:flex; margin:10px 0; }
        .msg{
          padding:12px 14px;
          border-radius:14px;
          line-height:1.45;
          max-width:80%;
          white-space:pre-wrap;
          word-wrap:break-word;
        }
        .you{ margin-left:auto; background:var(--bubble-user); border:1px solid rgba(255,255,255,.35); }
        .bot{ margin-right:auto; background:var(--bubble-bot); border:1px solid rgba(0,0,0,.15); }
        .meta{ font-size:12px; opacity:.9; margin-top:8px }
        .composer{
          position:relative;
          width:min(900px, 92vw);
          margin:0 auto 18px auto;
          display:flex; align-items:center; gap:10px;
          padding:10px 12px 10px 18px;
          border-radius:999px;
          border:2px solid var(--pill-border);
          backdrop-filter:saturate(140%) blur(2px);
        }
        #user_text{
          flex:1; height:48px; border:none; outline:none;
          background:transparent; color:#fff; font-size:16px;
        }
        ::placeholder{ color:rgba(255,255,255,.85) }
        .btn{
          width:44px; height:44px; border-radius:999px;
          border:2px solid var(--pill-border);
          background:transparent; display:grid; place-items:center; cursor:pointer;
        }
        .btn:active{ transform:scale(.98) }
        .icon{ width:22px; height:22px; display:block }
        .status{ text-align:center; font-size:13px; opacity:.95; min-height:20px; }
        .loading{ opacity:.9; font-style:italic }
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="brand">Clarity AI</div>

        <div id="chat" class="chat" aria-live="polite" aria-label="Conversation"></div>

        <div class="composer">
          <input id="user_text" type="text" placeholder="What's on your mind?...." autocomplete="off">
          <button id="micBtn" class="btn" type="button" aria-label="Speak">
            <!-- Microphone icon -->
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10a7 7 0 0 1-14 0"></path>
              <path d="M12 17v6"></path>
              <path d="M8 23h8"></path>
            </svg>
          </button>
          <button id="sendBtn" class="btn" type="button" aria-label="Send">
            <!-- Send icon -->
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>

        <div id="status" class="status"></div>
      </div>

      <script>
        const chat   = document.getElementById('chat');
        const input  = document.getElementById('user_text');
        const send   = document.getElementById('sendBtn');
        const micBtn = document.getElementById('micBtn');
        const status = document.getElementById('status');

        // --- Chat rendering helpers ---
        function appendMessage(text, who='you', meta=''){
          const row = document.createElement('div');
          row.className = 'row';
          const bubble = document.createElement('div');
          bubble.className = 'msg ' + (who === 'you' ? 'you' : 'bot');
          bubble.textContent = text;
          row.appendChild(bubble);
          if (meta){
            const m = document.createElement('div');
            m.className = 'meta';
            m.textContent = meta;
            row.appendChild(m);
          }
          chat.appendChild(row);
          chat.scrollTop = chat.scrollHeight;
        }

        function setStatus(msg){ status.textContent = msg || ''; }
        function setLoading(on){
          if (on){ status.innerHTML = '<span class="loading">Thinking…</span>'; }
          else { status.textContent = ''; }
        }

        // --- Send message via fetch (no page reload) ---
        async function sendMessage(text){
          if (!text || !text.trim()) return;
          appendMessage(text.trim(), 'you');
          input.value = '';
          setLoading(true);

          try {
            const res = await fetch('/api/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ user_text: text.trim() })
            });

            if (!res.ok){
              const errTxt = await res.text();
              appendMessage('We hit a snag. ' + errTxt, 'bot');
              setLoading(false);
              return;
            }

            const data = await res.json();
            // data: { reply, sentiment, speak_note, error }
            if (data.error){
              appendMessage('Error: ' + data.error, 'bot');
            } else {
              let meta = data.sentiment ? ('Sentiment: ' + data.sentiment) : '';
              appendMessage(data.reply || '(no reply)', 'bot', meta);
              if (data.speak_note){
                appendMessage(data.speak_note, 'bot');
              }
            }
          } catch (e){
            appendMessage('Network error: ' + e, 'bot');
          } finally {
            setLoading(false);
          }
        }

        // --- UI bindings: Enter to send, click to send ---
        send.addEventListener('click', () => sendMessage(input.value));
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') { e.preventDefault(); sendMessage(input.value); }
        });

        // --- Mic (Web Speech API) ---
        let recognizing = false;
        let recognition;

        function supportsSpeech(){
          return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        }

        if (supportsSpeech()){
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          recognition = new SR();
          recognition.lang = 'en-US';
          recognition.interimResults = false;
          recognition.continuous = false;

          recognition.onstart = () => { recognizing = true; setStatus('Listening… speak now'); };
          recognition.onend   = () => { recognizing = false; setStatus(''); };
          recognition.onerror = (e) => { recognizing = false; setStatus('Mic error: ' + (e.error || 'unknown')); };
          recognition.onresult = (e) => {
            const transcript = Array.from(e.results).map(r => r[0].transcript).join(' ').trim();
            if (transcript) { sendMessage(transcript); }
            else { setStatus("I didn't catch that — try again."); }
          };

          micBtn.addEventListener('click', () => {
            if (!recognizing){
              try { recognition.start(); } catch(_) {}
            } else {
              recognition.stop();
            }
          });
        } else {
          micBtn.addEventListener('click', () => setStatus('Speech recognition not supported in this browser.'));
        }
      </script>
    </body>
    </html>
    """


@app.post("/api/chat", response_class=JSONResponse)
async def api_chat(payload: dict):
    """
    Accepts JSON: { "user_text": "..." }
    Returns JSON: { "reply": "...", "sentiment": "...", "speak_note": "...", "error": "..." }
    """
    try:
        user_text = (payload or {}).get("user_text", "")
    except Exception:
        user_text = ""

    # Guard: empty input
    if not user_text or not str(user_text).strip():
        return JSONResponse({"error": "Empty input. Please say or type something."}, status_code=400)

    try:
        # NLP + LLM
        sentiment = get_sentiment(user_text)
        reply = get_llm_reply(user_text, sentiment)

        # TTS playback on host machine; never crash request if audio fails
        speak_note = ""
        try:
            speak(str(reply))
        except Exception as audio_err:
            speak_note = f"🔇 Couldn’t play audio: {audio_err}"

        return JSONResponse({
            "reply": str(reply),
            "sentiment": str(sentiment),
            "speak_note": speak_note
        })

    except Exception as e:
        # Handle rate-limits or any other backend error gracefully
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    # Run with auto-reload for dev
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
