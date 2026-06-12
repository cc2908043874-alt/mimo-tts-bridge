import base64, json, os


def handler(event, context):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("MIMO_KEY", ""),
        base_url="https://api.xiaomimimo.com/v1",
    )

    path = event.get("path", "/").rstrip("/") or "/"

    # 首页测试
    if path == "/":
        return {"statusCode": 200, "body": "MIMO TTS OK"}

    # 返回阅读App配置
    if path == "/config":
        host = event.get("headers", {}).get("host", "")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "name": "MIMO TTS",
                    "url": f"https://{host}/tts",
                    "method": "POST",
                    "body": "text={{encodeURIComponent(speakText)}}&speed={{speakSpeed}}",
                    "contentType": "audio/mpeg",
                }
            ),
        }

    # TTS 合成
    if event.get("httpMethod", "GET") != "POST":
        return {"statusCode": 404}

    body = event.get("body", "")
    params = {}
    for p in body.split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v

    text = params.get("text", "")
    if not text.strip():
        return {"statusCode": 400}

    fmt = params.get("format", "mp3")
    voice_key = params.get("voice", "default")
    voice_map = {"default": "mimo_default", "冰糖": "冰糖", "茉莉": "茉莉", "白桦": "白桦", "苏打": "苏打", "Mia": "Mia"}
    voice = voice_map.get(voice_key, "mimo_default")

    try:
        resp = client.chat.completions.create(
            model="mimo-v2.5-tts",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": fmt},
            messages=[
                {"role": "user", "content": "语气自然一点"},
                {"role": "assistant", "content": text},
            ],
        )
        audio = base64.b64decode(resp.choices[0].message.audio.data)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "audio/mpeg" if fmt == "mp3" else "audio/wav"},
            "body": base64.b64encode(audio).decode(),
            "isBase64Encoded": True,
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
