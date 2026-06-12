import json


def handler(event, context):
    host = event.get("headers", {}).get("host", "")
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "name": "MIMO TTS",
                "url": f"https://{host}/.netlify/functions/tts",
                "method": "POST",
                "body": "text={{encodeURIComponent(speakText)}}&speed={{speakSpeed}}",
                "contentType": "audio/mpeg",
            }
        ),
    }
