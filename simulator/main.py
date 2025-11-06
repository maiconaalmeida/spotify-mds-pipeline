#!/usr/bin/env python3
"""
Spotify Data Simulator
=====================
Simula dados de streaming do Spotify em tempo real e envia para Kafka.
Gera dados realistas de usuários, músicas, artistas e reproduções.

Autor: Maicon Almeida
Data: 2024
"""

import json
import time
import random
import logging
from datetime import datetime, timedelta
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os
from dotenv import load_dotenv
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simulator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('spotify_simulator')

# Carregar variáveis de ambiente
load_dotenv()

class SpotifyDataSimulator:
    def __init__(self):
        """Inicializa o simulador de dados do Spotify."""
        self.fake = Faker('pt_BR')
        self.kafka_config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092').split(','),
            'topic': os.getenv('KAFKA_TOPIC', 'spotify-plays')
        }
        
        # Inicializar estruturas de dados
        self.users = []
        self.artists = []
        self.tracks = []
        self.devices = ['mobile', 'desktop', 'tablet', 'smart_speaker', 'car_system']
        
        # Configurações de simulação
        self.regions = [
            'southeast', 'south', 'northeast', 'north', 'midwest'
        ]
        
        # Estatísticas
        self.stats = {
            'messages_sent': 0,
            'errors': 0,
            'start_time': None
        }
        
        self.producer = None
        self._initialize_data()
        self._connect_kafka()
    
    def _initialize_data(self):
        """Inicializa dados base de usuários, artistas e músicas."""
        logger.info("Inicializando dados base...")
        
        # Gerar usuários
        for i in range(100):
            self.users.append({
                'user_id': f"user_{i:06d}",
                'name': self.fake.name(),
                'email': self.fake.email(),
                'region': random.choice(self.regions),
                'age': random.randint(18, 65),
                'premium': random.choice([True, False])
            })
        
        # Gerar artistas brasileiros (reais e fictícios)
        brazilian_artists = [
            'Anitta', 'Ludmilla', 'Maiara & Maraisa', 'Gusttavo Lima', 
            'Marília Mendonça', 'Jorge & Mateus', 'Henrique & Juliano',
            'Ivete Sangalo', 'Claudia Leitte', 'Luan Santana',
            'Wesley Safadão', 'Zé Neto & Cristiano', 'Diego & Victor Hugo',
            'Leo Santana', 'Alok', 'Vintage Culture', 'KVSH'
        ]
        
        for artist in brazilian_artists:
            self.artists.append({
                'artist_id': f"artist_{len(self.artists):06d}",
                'name': artist,
                'genre': random.choice(['sertanejo', 'funk', 'pop', 'pagode', 'eletrônica']),
                'popularity': random.randint(70, 100)
            })
        
        # Gerar mais artistas fictícios
        for i in range(50):
            self.artists.append({
                'artist_id': f"artist_{len(self.artists):06d}",
                'name': self.fake.name(),
                'genre': random.choice(['rock', 'mpb', 'samba', 'forró', 'rap', 'indie']),
                'popularity': random.randint(10, 95)
            })
        
        # Gerar músicas
        music_templates = [
            "{adjective} {noun}", "{} do Coração", "{} e {}",
            "Vida {}", "{} na {}", "{} de {}"
        ]
        
        adjectives = ['Amor', 'Saudade', 'Felicidade', 'Paixão', 'Dor', 'Vida', 'Noite', 'Dia']
        nouns = ['Verdadeiro', 'Perdido', 'Loucura', 'Destino', 'Fim', 'Começo']
        
        for artist in self.artists:
            num_tracks = random.randint(5, 20)
            for i in range(num_tracks):
                template = random.choice(music_templates)
                if template.count('{}') == 1:
                    track_name = template.format(random.choice(adjectives))
                elif template.count('{}') == 2:
                    track_name = template.format(random.choice(adjectives), random.choice(nouns))
                else:
                    track_name = template.format(adjective=random.choice(adjectives), noun=random.choice(nouns))
                
                self.tracks.append({
                    'track_id': f"track_{len(self.tracks):06d}",
                    'name': track_name,
                    'artist_id': artist['artist_id'],
                    'artist_name': artist['name'],
                    'duration_ms': random.randint(120000, 360000),  # 2-6 minutos
                    'explicit': random.choice([True, False]),
                    'danceability': round(random.uniform(0.3, 0.9), 3),
                    'energy': round(random.uniform(0.3, 0.95), 3),
                    'valence': round(random.uniform(0.2, 0.95), 3)  # positividade musical
                })
        
        logger.info(f"Dados base inicializados: {len(self.users)} usuários, {len(self.artists)} artistas, {len(self.tracks)} músicas")
    
    def _connect_kafka(self):
        """Conecta ao cluster Kafka."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_config['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                acks='all',
                retries=3,
                batch_size=16384,
                linger_ms=10
            )
            logger.info(f"Conectado ao Kafka em {self.kafka_config['bootstrap_servers']}")
        except KafkaError as e:
            logger.error(f"Erro ao conectar com Kafka: {e}")
            raise
    
    def generate_play_event(self):
        """Gera um evento de reprodução de música."""
        user = random.choice(self.users)
        track = random.choice(self.tracks)
        artist = next((a for a in self.artists if a['artist_id'] == track['artist_id']), None)
        
        # Timestamp atual com pequena variação
        event_time = datetime.now() - timedelta(seconds=random.randint(0, 300))
        
        # Determinar se a reprodução foi completa baseado na popularidade
        play_duration = track['duration_ms']
        if random.random() > 0.3:  # 70% das reproduções são completas
            play_duration = track['duration_ms']
        else:
            play_duration = random.randint(10000, track['duration_ms'] // 2)
        
        event = {
            'event_id': f"event_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'event_type': 'track_play',
            'user_id': user['user_id'],
            'user_region': user['region'],
            'user_premium': user['premium'],
            'track_id': track['track_id'],
            'track_name': track['name'],
            'artist_id': track['artist_id'],
            'artist_name': track['artist_name'],
            'genre': artist['genre'] if artist else 'unknown',
            'duration_ms': track['duration_ms'],
            'play_duration_ms': play_duration,
            'device_type': random.choice(self.devices),
            'timestamp': event_time.isoformat(),
            'explicit': track['explicit'],
            'audio_features': {
                'danceability': track['danceability'],
                'energy': track['energy'],
                'valence': track['valence']
            },
            'completed': play_duration >= track['duration_ms'] * 0.9
        }
        
        return event
    
    def send_to_kafka(self, event):
        """Envia evento para o Kafka."""
        try:
            future = self.producer.send(
                self.kafka_config['topic'], 
                value=event
            )
            # Forçar flush para garantir entrega
            self.producer.flush()
            self.stats['messages_sent'] += 1
            return True
        except KafkaError as e:
            logger.error(f"Erro ao enviar mensagem para Kafka: {e}")
            self.stats['errors'] += 1
            return False
    
    def print_stats(self):
        """Exibe estatísticas da simulação."""
        if self.stats['start_time']:
            elapsed = datetime.now() - self.stats['start_time']
            rate = self.stats['messages_sent'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
            
            logger.info(f"""
=== ESTATÍSTICAS DA SIMULAÇÃO ===
Tempo de execução: {elapsed}
Mensagens enviadas: {self.stats['messages_sent']}
Taxa de mensagens/segundo: {rate:.2f}
Erros: {self.stats['errors']}
Tópico Kafka: {self.kafka_config['topic']}
            """.strip())
    
    def run_continuous(self, rate_per_second=5, duration_minutes=None):
        """
        Executa a simulação continuamente.
        
        Args:
            rate_per_second: Eventos por segundo
            duration_minutes: Duração em minutos (None para executar indefinidamente)
        """
        logger.info(f"Iniciando simulação contínua - Taxa: {rate_per_second} eventos/segundo")
        self.stats['start_time'] = datetime.now()
        
        end_time = None
        if duration_minutes:
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            logger.info(f"Duração: {duration_minutes} minutos")
        
        interval = 1.0 / rate_per_second
        
        try:
            while True:
                if end_time and datetime.now() >= end_time:
                    logger.info("Tempo de simulação concluído")
                    break
                
                start_time = time.time()
                
                # Gerar e enviar evento
                event = self.generate_play_event()
                success = self.send_to_kafka(event)
                
                if success and self.stats['messages_sent'] % 100 == 0:
                    logger.info(f"Eventos enviados: {self.stats['messages_sent']} - Último: {event['track_name']} por {event['artist_name']}")
                
                # Controlar taxa
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Simulação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro na simulação: {e}")
        finally:
            self.print_stats()
            if self.producer:
                self.producer.close()
    
    def run_burst(self, num_events, rate_per_second=10):
        """
        Executa uma rajada de eventos.
        
        Args:
            num_events: Número total de eventos
            rate_per_second: Eventos por segundo
        """
        logger.info(f"Iniciando rajada de {num_events} eventos - Taxa: {rate_per_second}/segundo")
        self.stats['start_time'] = datetime.now()
        
        interval = 1.0 / rate_per_second
        
        for i in range(num_events):
            start_time = time.time()
            
            event = self.generate_play_event()
            success = self.send_to_kafka(event)
            
            if success and (i + 1) % 100 == 0:
                logger.info(f"Progresso: {i + 1}/{num_events} eventos")
            
            # Controlar taxa
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
        
        self.print_stats()
        if self.producer:
            self.producer.close()

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spotify Data Simulator')
    parser.add_argument('--mode', choices=['continuous', 'burst'], default='continuous',
                       help='Modo de operação: continuous ou burst')
    parser.add_argument('--rate', type=float, default=5,
                       help='Eventos por segundo (padrão: 5)')
    parser.add_argument('--duration', type=int,
                       help='Duração em minutos (apenas para modo continuous)')
    parser.add_argument('--events', type=int, default=1000,
                       help='Número de eventos (apenas para modo burst)')
    parser.add_argument('--verbose', action='store_true',
                       help='Log verboso')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        simulator = SpotifyDataSimulator()
        
        if args.mode == 'continuous':
            simulator.run_continuous(
                rate_per_second=args.rate,
                duration_minutes=args.duration
            )
        else:
            simulator.run_burst(
                num_events=args.events,
                rate_per_second=args.rate
            )
            
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()