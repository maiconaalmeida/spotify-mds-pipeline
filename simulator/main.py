#!/usr/bin/env python3
"""
Simple Spotify Data Producer - Brazilian Music
"""

import json
import time
import uuid
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

# Brazilian artists and songs
BRAZILIAN_MUSIC = [
    {"artist": "Marília Mendonça", "song": "Todo Mundo Vai Sofrer", "genre": "sertanejo"},
    {"artist": "Gusttavo Lima", "song": "Zé da Recaída", "genre": "sertanejo"},
    {"artist": "Anitta", "song": "Envolver", "genre": "funk"},
    {"artist": "João Gomes", "song": "Meu Pedaço de Pecado", "genre": "piseiro"},
    {"artist": "Ludmilla", "song": "Sou Má", "genre": "funk"},
    {"artist": "Jorge & Mateus", "song": "Propaganda", "genre": "sertanejo"},
    {"artist": "Henrique & Juliano", "song": "A Maior Saudade", "genre": "sertanejo"},
    {"artist": "Péricles", "song": "Melhor Eu Ir", "genre": "pagode"},
    {"artist": "Wesley Safadão", "song": "Camarote", "genre": "forró"},
    {"artist": "Zé Neto & Cristiano", "song": "Largado às Traças", "genre": "sertanejo"}
]

# Generate song IDs
for song in BRAZILIAN_MUSIC:
    song["song_id"] = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{song['artist']}::{song['song']}"))

# Kafka configuration
producer = KafkaProducer(
    bootstrap_servers=['localhost:29092'],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

def generate_event():
    """Generate a Spotify-like event."""
    song = random.choice(BRAZILIAN_MUSIC)
    user_id = f"user_{random.randint(1000, 9999)}"
    
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "song_id": song["song_id"],
        "song_name": song["song"],
        "artist_name": song["artist"],
        "genre": song["genre"],
        "event_type": random.choices(
            ["play", "pause", "skip", "save"], 
            weights=[0.7, 0.1, 0.15, 0.05]
        )[0],
        "device_type": random.choice(["mobile", "desktop", "web", "smart_speaker"]),
        "duration_played": random.randint(10000, 240000) if random.random() > 0.3 else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "region": random.choice(["sudeste", "nordeste", "sul", "norte", "centro_oeste"]),
        "premium_user": random.random() > 0.6
    }

if __name__ == "__main__":
    print("🎵 Starting Brazilian Spotify Data Producer...")
    print(f"📊 Using {len(BRAZILIAN_MUSIC)} Brazilian songs")
    
    try:
        while True:
            event = generate_event()
            producer.send('spotify-streams', event)
            
            print(f"📤 Sent: {event['event_type']} - {event['song_name']} by {event['artist_name']}")
            
            time.sleep(1)  # Send 1 event per second
            
    except KeyboardInterrupt:
        print("\n🛑 Producer stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        producer.close()