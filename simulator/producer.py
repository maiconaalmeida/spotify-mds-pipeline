#!/usr/bin/env python3
"""
Spotify Data Producer - Brazilian Music Focus

Professional Kafka producer that generates realistic Spotify streaming data
with Brazilian artists and comprehensive event tracking.

Features:
- Brazilian music catalog with popular artists
- Realistic user behavior simulation
- Comprehensive event tracking
- Configurable throughput and patterns
- Error handling and retry logic
- Metrics and monitoring
- Graceful shutdown handling
"""

import os
import json
import time
import uuid
import random
import logging
import signal
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import boto3
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# ---------- Enums and Data Classes ----------
class EventType(Enum):
    PLAY = "play"
    PAUSE = "pause"
    SKIP = "skip"
    SAVE = "save"
    SHARE = "share"
    ADD_TO_PLAYLIST = "add_to_playlist"
    COMPLETE = "complete"

class DeviceType(Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    WEB = "web"
    SMART_SPEAKER = "smart_speaker"
    CAR = "car"

class Region(Enum):
    SUDESTE = "sudeste"
    NORDESTE = "nordeste"
    SUL = "sul"
    NORTE = "norte"
    CENTRO_OESTE = "centro_oeste"

@dataclass
class Song:
    """Represents a song with Brazilian music data."""
    song_id: str
    title: str
    artist: str
    genre: str
    duration_ms: int
    popularity: int
    release_year: int
    explicit: bool

@dataclass
class SpotifyEvent:
    """Represents a Spotify streaming event."""
    event_id: str
    user_id: str
    session_id: str
    song_id: str
    song_title: str
    artist_name: str
    event_type: str
    device_type: str
    timestamp: str
    duration_played: Optional[int] = None
    region: Optional[str] = None
    city: Optional[str] = None
    user_agent: Optional[str] = None
    premium_user: Optional[bool] = None
    shuffle_mode: Optional[bool] = None
    volume_level: Optional[int] = None

@dataclass
class ProducerConfig:
    """Configuration for the Spotify data producer."""
    # Kafka Configuration
    kafka_bootstrap_servers: str
    kafka_topic: str
    kafka_client_id: str
    
    # Producer Behavior
    user_count: int
    event_interval_ms: int
    batch_size: int
    max_events: Optional[int] = None
    
    # Data Configuration
    enable_brazilian_artists: bool = True
    enable_regional_distribution: bool = True
    enable_user_behavior_patterns: bool = True

# ---------- Brazilian Music Catalog ----------
class BrazilianMusicCatalog:
    """Catalog of Brazilian artists and songs with realistic data."""
    
    GENRES = [
        "sertanejo", "funk", "mpb", "forró", "samba", "pagode",
        "bossa_nova", "axé", "brega", "arrocha", "piseiro"
    ]
    
    BRAZILIAN_ARTISTS = [
        # Sertanejo
        {"name": "Marília Mendonça", "genre": "sertanejo", "popularity": 95},
        {"name": "Gusttavo Lima", "genre": "sertanejo", "popularity": 92},
        {"name": "Jorge & Mateus", "genre": "sertanejo", "popularity": 90},
        {"name": "Henrique & Juliano", "genre": "sertanejo", "popularity": 93},
        {"name": "Maiara & Maraisa", "genre": "sertanejo", "popularity": 88},
        
        # Funk
        {"name": "Anitta", "genre": "funk", "popularity": 96},
        {"name": "Ludmilla", "genre": "funk", "popularity": 89},
        {"name": "MC Kevin", "genre": "funk", "popularity": 85},
        {"name": "MC Ryan SP", "genre": "funk", "popularity": 87},
        {"name": "Pocah", "genre": "funk", "popularity": 82},
        
        # MPB
        {"name": "Seu Jorge", "genre": "mpb", "popularity": 88},
        {"name": "Caetano Veloso", "genre": "mpb", "popularity": 90},
        {"name": "Gilberto Gil", "genre": "mpb", "popularity": 89},
        {"name": "Maria Bethânia", "genre": "mpb", "popularity": 87},
        {"name": "Jorge Vercillo", "genre": "mpb", "popularity": 83},
        
        # Forró/Piseiro
        {"name": "Wesley Safadão", "genre": "forró", "popularity": 91},
        {"name": "João Gomes", "genre": "piseiro", "popularity": 89},
        {"name": "Zé Vaqueiro", "genre": "piseiro", "popularity": 86},
        {"name": "Tarcísio do Acordeon", "genre": "forró", "popularity": 84},
        
        # Samba/Pagode
        {"name": "Thiaguinho", "genre": "pagode", "popularity": 88},
        {"name": "Péricles", "genre": "pagode", "popularity": 90},
        {"name": "Ferrugem", "genre": "pagode", "popularity": 85},
        {"name": "Grupo Revelação", "genre": "samba", "popularity": 83},
    ]
    
    # Song templates for each artist
    SONG_TEMPLATES = {
        "Marília Mendonça": [
            "Todo Mundo Vai Sofrer", "Infiel", "Ciumeira", "Supera", "Graveto"
        ],
        "Gusttavo Lima": [
            "Zé da Recaída", "Balada", "Cem Mil", "Apelido Carinhoso", "Diz Pra Mim"
        ],
        "Anitta": [
            "Envolver", "Girl From Rio", "Used to Be", "Movimento da Sanfoninha", "Vai Malandra"
        ],
        "João Gomes": [
            "Meu Pedaço de Pecado", "Dono do Seu Beijo", "Esse B.O é Meu", "Cleane", "Aquele Nosso Contrato"
        ],
        "Thiaguinho": [
            "A Semente", "Falta Você", "Vamo Que Vamo", "Só Vem", "Amor de Verdade"
        ]
    }
    
    @classmethod
    def get_random_song(cls) -> Song:
        """Generate a random Brazilian song with realistic data."""
        artist = random.choice(cls.BRAZILIAN_ARTISTS)
        artist_name = artist["name"]
        
        # Get song title or generate one
        if artist_name in cls.SONG_TEMPLATES:
            title = random.choice(cls.SONG_TEMPLATES[artist_name])
        else:
            title = f"{random.choice(['Vai', 'Meu', 'Quem', 'Só', 'Agora'])} {random.choice(['Coração', 'Amor', 'Vida', 'Destino', 'Fim'])}"
        
        # Generate song ID
        name_for_uuid = f"{artist_name}::{title}"
        song_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, name_for_uuid))
        
        return Song(
            song_id=song_id,
            title=title,
            artist=artist_name,
            genre=artist["genre"],
            duration_ms=random.randint(180000, 240000),  # 3-4 minutes
            popularity=artist["popularity"] + random.randint(-5, 5),
            release_year=random.randint(2015, 2024),
            explicit=random.choices([True, False], weights=[0.3, 0.7])[0]
        )

# ---------- Main Producer Class ----------
class SpotifyDataProducer:
    """Professional Spotify data producer with Brazilian music focus."""
    
    def __init__(self, config: ProducerConfig):
        self.config = config
        self.producer = None
        self.fake = Faker('pt_BR')
        self.music_catalog = BrazilianMusicCatalog()
        self.metrics = {
            'events_produced': 0,
            'errors_encountered': 0,
            'start_time': datetime.now(timezone.utc),
            'last_event_time': None
        }
        
        # Generate stable user base
        self.user_ids = [str(uuid.uuid4()) for _ in range(config.user_count)]
        self.user_sessions = {}  # user_id -> session_id
        self.user_preferences = self._generate_user_preferences()
        
        self.is_running = True
        self.setup_logging()
        self.setup_signal_handlers()
    
    def setup_logging(self):
        """Configure logging for the producer."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('spotify_producer.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _generate_user_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Generate user preferences for more realistic behavior."""
        preferences = {}
        for user_id in self.user_ids:
            preferences[user_id] = {
                'favorite_genres': random.sample(self.music_catalog.GENRES, 2),
                'premium_user': random.choices([True, False], weights=[0.4, 0.6])[0],
                'preferred_device': random.choice(list(DeviceType)).value,
                'region': random.choice(list(Region)).value,
                'activity_level': random.randint(1, 10)  # 1 = casual, 10 = power user
            }
        return preferences
    
    def _get_user_session(self, user_id: str) -> str:
        """Get or create session ID for user."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = str(uuid.uuid4())
        return self.user_sessions[user_id]
    
    def _get_brazilian_city(self, region: str) -> str:
        """Get realistic Brazilian city for region."""
        cities_by_region = {
            Region.SUDESTE.value: ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Campinas"],
            Region.NORDESTE.value: ["Salvador", "Fortaleza", "Recife", "Natal"],
            Region.SUL.value: ["Porto Alegre", "Curitiba", "Florianópolis", "Joinville"],
            Region.NORTE.value: ["Manaus", "Belém", "Porto Velho", "Macapá"],
            Region.CENTRO_OESTE.value: ["Brasília", "Goiânia", "Cuiabá", "Campo Grande"]
        }
        return random.choice(cities_by_region.get(region, ["São Paulo"]))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((KafkaError, NoBrokersAvailable))
    )
    def initialize_producer(self) -> bool:
        """Initialize Kafka producer with error handling."""
        try:
            self.logger.info("Initializing Kafka producer...")
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                client_id=self.config.kafka_client_id,
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10,
                compression_type='gzip'
            )
            
            # Test connection
            self.producer.flush(timeout=10)
            self.logger.info("✅ Kafka producer initialized successfully")
            return True
            
        except (KafkaError, NoBrokersAvailable) as e:
            self.logger.error(f"❌ Failed to initialize Kafka producer: {e}")
            return False
    
    def generate_event(self) -> SpotifyEvent:
        """Generate a realistic Spotify streaming event."""
        user_id = random.choice(self.user_ids)
        user_prefs = self.user_preferences[user_id]
        
        # Get song (prefer user's favorite genres)
        if random.random() < 0.7:  # 70% chance to play preferred genre
            preferred_genres = user_prefs['favorite_genres']
            # Filter artists by preferred genres
            suitable_artists = [
                artist for artist in self.music_catalog.BRAZILIAN_ARTISTS 
                if artist['genre'] in preferred_genres
            ]
            if suitable_artists:
                artist = random.choice(suitable_artists)
                # Simplified - in real implementation, we'd have songs per artist
                song = self.music_catalog.get_random_song()
            else:
                song = self.music_catalog.get_random_song()
        else:
            song = self.music_catalog.get_random_song()
        
        # Determine event type with realistic distribution
        event_weights = [0.6, 0.1, 0.15, 0.05, 0.05, 0.03, 0.02]  # play, pause, skip, etc.
        event_type = random.choices(list(EventType), weights=event_weights)[0].value
        
        # Generate event
        event = SpotifyEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=self._get_user_session(user_id),
            song_id=song.song_id,
            song_title=song.title,
            artist_name=song.artist,
            event_type=event_type,
            device_type=user_prefs['preferred_device'],
            timestamp=datetime.now(timezone.utc).isoformat(),
            region=user_prefs['region'],
            city=self._get_brazilian_city(user_prefs['region']),
            premium_user=user_prefs['premium_user'],
            shuffle_mode=random.choices([True, False], weights=[0.3, 0.7])[0],
            volume_level=random.randint(20, 100)
        )
        
        # Add duration for play events
        if event_type == EventType.PLAY.value:
            event.duration_played = random.randint(10000, song.duration_ms)
        
        return event
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    def send_event(self, event: SpotifyEvent) -> bool:
        """Send event to Kafka with error handling."""
        try:
            future = self.producer.send(
                self.config.kafka_topic,
                value=asdict(event)
            )
            
            # Optional: wait for acknowledgment
            # future.get(timeout=10)
            
            self.metrics['events_produced'] += 1
            self.metrics['last_event_time'] = datetime.now(timezone.utc)
            return True
            
        except KafkaError as e:
            self.logger.error(f"❌ Failed to send event to Kafka: {e}")
            self.metrics['errors_encountered'] += 1
            return False
    
    def log_metrics(self):
        """Log production metrics."""
        runtime = datetime.now(timezone.utc) - self.metrics['start_time']
        events_per_second = self.metrics['events_produced'] / runtime.total_seconds()
        
        self.logger.info(
            f"📊 Producer Metrics - Events: {self.metrics['events_produced']:,} | "
            f"Errors: {self.metrics['errors_encountered']} | "
            f"Rate: {events_per_second:.2f} events/sec | "
            f"Runtime: {runtime}"
        )
    
    def run(self):
        """Main producer loop."""
        self.logger.info("🚀 Starting Spotify Data Producer (Brazilian Edition)...")
        
        if not self.initialize_producer():
            self.logger.error("❌ Failed to initialize producer. Exiting.")
            sys.exit(1)
        
        self.logger.info(f"🎵 Using {len(self.music_catalog.BRAZILIAN_ARTISTS)} Brazilian artists")
        self.logger.info(f"👥 Simulating {len(self.user_ids)} users")
        self.logger.info(f"📤 Target rate: {1000/self.config.event_interval_ms:.2f} events/sec")
        
        event_count = 0
        
        try:
            while self.is_running:
                # Check if we've reached max events
                if (self.config.max_events and 
                    event_count >= self.config.max_events):
                    self.logger.info(f"✅ Reached maximum events ({self.config.max_events}). Shutting down.")
                    break
                
                # Generate and send event
                event = self.generate_event()
                if self.send_event(event):
                    self.logger.debug(
                        f"🎵 {event.event_type.upper()} - {event.song_title} by {event.artist_name} | "
                        f"User: {event.user_id[:8]}... | Device: {event.device_type}"
                    )
                
                event_count += 1
                
                # Log metrics periodically
                if event_count % 100 == 0:
                    self.log_metrics()
                
                # Sleep to control rate
                time.sleep(self.config.event_interval_ms / 1000.0)
                
        except Exception as e:
            self.logger.error(f"❌ Unexpected error in producer loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown procedure."""
        self.logger.info("🛑 Shutting down Spotify Data Producer...")
        
        if self.producer:
            self.logger.info("📤 Flushing remaining messages...")
            self.producer.flush(timeout=10)
            self.producer.close()
        
        self.log_metrics()
        self.logger.info("✅ Spotify Data Producer shutdown complete")

def load_config() -> ProducerConfig:
    """Load configuration from environment variables."""
    load_dotenv()
    
    return ProducerConfig(
        # Kafka Configuration
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"),
        kafka_topic=os.getenv("KAFKA_TOPIC_SPOTIFY_STREAMS", "spotify-streams"),
        kafka_client_id=os.getenv("KAFKA_CLIENT_ID", "spotify-brazil-producer"),
        
        # Producer Behavior
        user_count=int(os.getenv("USER_COUNT", "50")),
        event_interval_ms=int(os.getenv("EVENT_INTERVAL_MS", "500")),
        batch_size=int(os.getenv("BATCH_SIZE", "100")),
        max_events=int(os.getenv("MAX_EVENTS", "0")) or None,
        
        # Data Configuration
        enable_brazilian_artists=os.getenv("ENABLE_BRAZILIAN_ARTISTS", "true").lower() == "true",
        enable_regional_distribution=os.getenv("ENABLE_REGIONAL_DISTRIBUTION", "true").lower() == "true",
        enable_user_behavior_patterns=os.getenv("ENABLE_USER_BEHAVIOR_PATTERNS", "true").lower() == "true"
    )

if __name__ == "__main__":
    config = load_config()
    producer = SpotifyDataProducer(config)
    producer.run()