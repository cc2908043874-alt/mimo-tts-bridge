import base64
import json
import os

MIMO_KEY = os.environ.get("MIMO_KEY", "")


def handler(event, context):
    """Netlify Python function handler"""
    from openai import OpenAI

    client = OpenAI(api_key=MIMO_KEY, base_url="https://api.xiaomimimo.com/v1")

    path = event.get("path", "/")
    http_method = event.get("httpMethod", "GET")

    # /config 接口：返回阅读App配置
    if path == "/config":
        host = event.get("headers", {}).get("host", "")
        cfg = {
            "name": "MIMO TTS",
            "url": f"https://{host}/tts",
            "method": "POST",
            "body": "text={{encodeURIComponent(speakText)}}&speed={{speakSpeed}}",
            "contentType": "audio/mpeg",
        }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(cfg),
        }

    # / 首页
    if path == "/":
        return {
            "statusCode": 200,
            "body": "✅ MIMO TTS Bridge is running",
        }

    # /tts 接口
    if path == "/tts" and http_method == "POST":
        body = event.get("body", "")
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
            return {"statusCode": 400, "body": "empty text"}

        voice = {
            "default": "mimo_default",
            "冰糖": "冰糖",
            "茉莉": "茉莉",
            "白桦": "白桦",
            "苏打": "苏打",
            "Mia": "Mia",
        }.get(voice_key, "mimo_default")

        style_label = {
            "无": "",
            "东北话": "东北话",
            "四川话": "四川话",
            "粤语": "粤语",
            "台湾腔": "台湾腔",
            "开心": "开心",
            "悄悄话": "悄悄话",
        }.get(style_key, "")

        user_prompt = (
            f"<style>{style_label}</style>语气自然一点"
            if style_label
            else "语气自然一点"
        )

        try:
            resp = client.chat.completions.create(
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
            return {
                "statusCode": 200,
                "headers": {"Content-Type": ct},
                "body": base64.b64encode(audio).decode(),
                "isBase64Encoded": True,
            }
        except Exception as e:
            return {"statusCode": 500, "body": str(e)}

    return {"statusCode": 404, "body": "not found"}
