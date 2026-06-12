import base64, json, os
from http.server import BaseHTTPRequestHandler
from openai import OpenAI

MIMO_KEY = os.environ.get("MIMO_KEY", "")
CLIENT = OpenAI(api_key=sk-cpha9c00cnbs0ufyoap5gz16zx7qvf2n4jhcf8p3ooa4qyz4, base_url="https://api.xiaomimimo.com/v1")

VOICES = {
    "default": "mimo_default", "冰糖": "冰糖", "茉莉": "茉莉",
    "白桦": "白桦", "苏打": "苏打", "Mia": "Mia", "Chloe": "Chloe",
}

STYLES = {
    "无": "", "东北话": "东北话", "四川话": "四川话", "粤语": "粤语",
    "台湾腔": "台湾腔", "开心": "开心", "悄悄话": "悄悄话",
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/config"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            host = self.headers.get("Host", "")
            cfg = {
                "name": "MIMO TTS",
                "url": f"https://{host}/api/tts",
                "method": "POST",
                "body": "text={{encodeURIComponent(speakText)}}&speed={{speakSpeed}}",
                "contentType": "audio/mpeg"
            }
            self.wfile.write(json.dumps(cfg).encode())
        elif self.path == "/" or self.path == "/api/tts":
            self.send_response(200)
            self.end_headers()
            self.wfile.write("MIMO TTS OK".encode())

    def do_POST(self):
        if self.path != "/api/tts":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        params = {}
        for p in body.split("&"):
            if "=" in p:
                k, v = p.split("=", 1)
                params[k] = v

        text = params.get("text", "")
        voice_key = params.get("voice", "default")
        style_key = params.get("style", "无")
        fmt = params.get("format", "mp3")

        if not text.strip():
            self.send_response(400)
            self.end_headers()
            return

        voice = VOICES.get(voice_key, "mimo_default")
        style_label = STYLES.get(style_key, "")
        user_prompt = f"<style>{style_label}</style>语气自然一点" if style_label else "语气自然一点"

        try:
            resp = CLIENT.chat.completions.create(
                model="mimo-v2.5-tts",
                modalities=["text", "audio"],
                audio={"voice": voice, "format": fmt},
                messages=[
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": text},
                ],
            )
            audio = base64.b64decode(resp.choices[0].message.audio.data)
            ct = "audio/mpeg" if fmt == "mp3" else "audio/wav"
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(audio)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
