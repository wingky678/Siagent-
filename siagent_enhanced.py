#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SiAgent Enhanced - AI Cerdas dengan Pembelajaran Mandiri 24/7
Sistem AI yang bisa belajar sendiri tanpa perlu dibuka/dijalankan manual
Dengan Web UI Modern dan Background Service

Author: Enhanced for Autonomous Robot Development  
Version: 3.0 Enhanced Autonomous
Compatible: All Python 3.7+ environments
"""

import json
import os
import re
import random
import time
import datetime
import sqlite3
import threading
import hashlib
import math
import sys
import signal
import subprocess
import schedule
import asyncio
import logging
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import atexit
import daemon
from daemon import pidfile

# Try import optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_ENABLED = True
except ImportError:
    print("⚠️ Web features disabled. Install: pip install requests beautifulsoup4 flask flask-socketio python-daemon schedule")
    WEB_ENABLED = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('siagent_enhanced.log'),
        logging.StreamHandler()
    ]
)

class EnhancedKnowledgeBase:
    """Enhanced Knowledge Base dengan kategorisasi dan indexing"""
    
    def __init__(self, db_path="siagent_enhanced.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__ + '.KnowledgeBase')
        self.init_database()
        
    def init_database(self):
        """Inisialisasi database dengan tabel yang lebih canggih"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel pengetahuan dengan kategorisasi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                confidence REAL DEFAULT 0.5,
                source TEXT,
                category TEXT,
                importance_score REAL DEFAULT 0.5,
                last_accessed DATETIME,
                access_count INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk tracking learning sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT,
                topic TEXT,
                facts_learned INTEGER,
                success_rate REAL,
                duration_seconds INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk autonomous learning tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS autonomous_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT,
                task_data TEXT,
                priority INTEGER DEFAULT 1,
                status TEXT DEFAULT 'pending',
                scheduled_time DATETIME,
                completed_time DATETIME,
                result TEXT
            )
        ''')
        
        # Index untuk performa
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_subject ON knowledge(subject)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON knowledge(confidence)')
        
        conn.commit()
        conn.close()
        self.logger.info("Enhanced database initialized")

class AutonomousLearningEngine:
    """Engine for autonomous 24/7 learning"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.logger = logging.getLogger(__name__ + '.AutonomousLearning')
        self.is_running = False
        self.learning_threads = []
        
        # Learning strategy configuration
        self.learning_strategies = {
            'web_exploration': {'weight': 0.4, 'interval': 1800},  # 30 menit
            'knowledge_synthesis': {'weight': 0.3, 'interval': 3600},  # 1 jam
            'pattern_recognition': {'weight': 0.2, 'interval': 7200},  # 2 jam
            'deep_reasoning': {'weight': 0.1, 'interval': 21600}  # 6 jam
        }
        
        # Topics yang akan dipelajari secara otomatis
        self.learning_topics = [
            'artificial intelligence', 'machine learning', 'robotics', 'automation',
            'computer vision', 'natural language processing', 'neural networks',
            'data science', 'programming', 'algorithms', 'sensors', 'actuators',
            'IoT', 'edge computing', 'quantum computing', 'blockchain',
            'scientific discoveries', 'technological innovations', 'research papers'
        ]
        
        self.current_focus = 'general'
        
    def start_autonomous_learning(self):
        """Start the autonomous learning system"""
        if self.is_running:
            return
            
        self.is_running = True
        self.logger.info("🚀 Starting autonomous learning system...")
        
        # Schedule different learning tasks
        schedule.every(30).minutes.do(self._web_exploration_task)
        schedule.every(1).hour.do(self._knowledge_synthesis_task)
        schedule.every(2).hours.do(self._pattern_recognition_task)
        schedule.every(6).hours.do(self._deep_reasoning_task)
        schedule.every(12).hours.do(self._learning_optimization_task)
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Start continuous learning thread
        continuous_thread = threading.Thread(target=self._continuous_learning_loop)
        continuous_thread.daemon = True
        continuous_thread.start()
        
        self.learning_threads = [scheduler_thread, continuous_thread]
        self.logger.info("✅ Autonomous learning system started")
    
    def _run_scheduler(self):
        """Run the scheduled tasks"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
    
    def _continuous_learning_loop(self):
        """Continuous learning loop that runs 24/7"""
        while self.is_running:
            try:
                # Select random topic based on current focus
                topic = self._select_learning_topic()
                
                # Perform learning task
                self._execute_learning_task(topic)
                
                # Wait before next iteration (random interval 5-15 minutes)
                wait_time = random.randint(300, 900)
                time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"Continuous learning error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _select_learning_topic(self):
        """Select topic for learning based on various factors"""
        # Check knowledge gaps
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM knowledge 
            GROUP BY category
            ORDER BY count ASC, avg_conf ASC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            # Focus on categories with less knowledge or low confidence
            weak_category = results[0][0] if results[0][0] else 'general'
            related_topics = [t for t in self.learning_topics if weak_category in t or 'ai' in weak_category.lower()]
            if related_topics:
                return random.choice(related_topics)
        
        return random.choice(self.learning_topics)
    
    def _execute_learning_task(self, topic):
        """Execute a learning task for given topic"""
        session_start = time.time()
        facts_learned = 0
        
        try:
            if WEB_ENABLED:
                # Web-based learning
                search_results = self._autonomous_web_search(topic)
                facts_learned = len(search_results)
                
                # Process and store knowledge
                for result in search_results:
                    self._process_and_store_fact(result, topic)
            
            # Generate synthetic knowledge through reasoning
            synthetic_facts = self._generate_synthetic_knowledge(topic)
            facts_learned += len(synthetic_facts)
            
            # Log learning session
            session_duration = int(time.time() - session_start)
            success_rate = min(1.0, facts_learned / 10.0)
            
            self._log_learning_session('autonomous', topic, facts_learned, success_rate, session_duration)
            self.logger.info(f"📚 Learned {facts_learned} facts about {topic}")
            
        except Exception as e:
            self.logger.error(f"Learning task error for {topic}: {e}")
    
    def _autonomous_web_search(self, topic):
        """Autonomous web search and knowledge extraction"""
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36'
            })
            
            # Wikipedia search
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '%20')}"
            response = session.get(wiki_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data:
                    return self._extract_facts_from_text(data['extract'], topic)
            
        except Exception as e:
            self.logger.error(f"Web search error: {e}")
        
        return []
    
    def _extract_facts_from_text(self, text, topic):
        """Extract facts from text using NLP patterns"""
        facts = []
        sentences = re.split(r'[.!?]+', text)
        
        patterns = [
            r'(\w+(?:\s+\w+)*)\s+(is|are|was|were)\s+([^,\.]+)',
            r'(\w+(?:\s+\w+)*)\s+(has|have|had)\s+([^,\.]+)',
            r'(\w+(?:\s+\w+)*)\s+(can|could|may|might)\s+([^,\.]+)',
            r'(\w+(?:\s+\w+)*)\s+(uses|used|utilizes)\s+([^,\.]+)',
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            for pattern in patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 3:
                        subject = match.group(1).strip()
                        predicate = match.group(2).strip()
                        obj = match.group(3).strip()
                        
                        # Filter out too generic subjects/objects
                        if len(subject) > 2 and len(obj) > 2:
                            facts.append({
                                'subject': subject,
                                'predicate': predicate,
                                'object': obj,
                                'source': 'autonomous_learning',
                                'category': topic,
                                'confidence': 0.7
                            })
        
        return facts[:5]  # Limit to prevent spam
    
    def _process_and_store_fact(self, fact, topic):
        """Process and store a learned fact"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Check if fact already exists
        cursor.execute('''
            SELECT id FROM knowledge 
            WHERE subject=? AND predicate=? AND object=?
        ''', (fact['subject'], fact['predicate'], fact['object']))
        
        if cursor.fetchone():
            # Update confidence if fact exists
            cursor.execute('''
                UPDATE knowledge 
                SET confidence = MIN(1.0, confidence + 0.1),
                    access_count = access_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE subject=? AND predicate=? AND object=?
            ''', (fact['subject'], fact['predicate'], fact['object']))
        else:
            # Insert new fact
            cursor.execute('''
                INSERT INTO knowledge 
                (subject, predicate, object, confidence, source, category, importance_score, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''', (fact['subject'], fact['predicate'], fact['object'], 
                  fact['confidence'], fact['source'], fact['category'], 
                  random.uniform(0.3, 0.8)))
        
        conn.commit()
        conn.close()
    
    def _generate_synthetic_knowledge(self, topic):
        """Generate synthetic knowledge through reasoning"""
        facts = []
        
        # Get related facts from knowledge base
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subject, predicate, object, confidence
            FROM knowledge 
            WHERE category=? OR subject LIKE ? OR object LIKE ?
            ORDER BY confidence DESC
            LIMIT 10
        ''', (topic, f'%{topic}%', f'%{topic}%'))
        
        related_facts = cursor.fetchall()
        conn.close()
        
        if len(related_facts) >= 2:
            # Generate inferences
            for i, fact1 in enumerate(related_facts):
                for fact2 in related_facts[i+1:]:
                    # Simple transitive inference
                    if fact1[2] == fact2[0]:  # object of fact1 == subject of fact2
                        synthetic_fact = {
                            'subject': fact1[0],
                            'predicate': 'relates_to',
                            'object': fact2[2],
                            'source': 'synthetic_reasoning',
                            'category': topic,
                            'confidence': min(fact1[3], fact2[3]) * 0.8
                        }
                        facts.append(synthetic_fact)
        
        return facts[:3]  # Limit synthetic facts
    
    def _web_exploration_task(self):
        """Scheduled web exploration task"""
        if not self.is_running:
            return
            
        topic = random.choice(self.learning_topics)
        self.logger.info(f"🌐 Web exploration task: {topic}")
        self._execute_learning_task(topic)
    
    def _knowledge_synthesis_task(self):
        """Scheduled knowledge synthesis task"""
        if not self.is_running:
            return
            
        self.logger.info("🧬 Running knowledge synthesis...")
        
        # Find knowledge gaps and contradictions
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Find low confidence facts that need reinforcement
        cursor.execute('''
            SELECT subject, predicate, object, confidence, category
            FROM knowledge 
            WHERE confidence < 0.6
            ORDER BY access_count DESC, confidence ASC
            LIMIT 5
        ''')
        
        weak_facts = cursor.fetchall()
        conn.close()
        
        for fact in weak_facts:
            topic = fact[4] if fact[4] else fact[0]
            self._execute_learning_task(topic)
    
    def _pattern_recognition_task(self):
        """Scheduled pattern recognition task"""
        if not self.is_running:
            return
            
        self.logger.info("🔍 Running pattern recognition...")
        self._analyze_knowledge_patterns()
    
    def _deep_reasoning_task(self):
        """Scheduled deep reasoning task"""
        if not self.is_running:
            return
            
        self.logger.info("🤔 Running deep reasoning...")
        self._perform_deep_reasoning()
    
    def _learning_optimization_task(self):
        """Optimize learning strategy based on results"""
        if not self.is_running:
            return
            
        self.logger.info("⚡ Optimizing learning strategy...")
        
        # Analyze learning session success rates
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, AVG(success_rate), COUNT(*)
            FROM learning_sessions
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY topic
            ORDER BY AVG(success_rate) DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if results:
            # Update topic priorities based on success rates
            successful_topics = [r[0] for r in results[:3]]
            self.learning_topics = successful_topics + self.learning_topics
            self.learning_topics = list(dict.fromkeys(self.learning_topics))  # Remove duplicates
    
    def _analyze_knowledge_patterns(self):
        """Analyze patterns in knowledge base"""
        # Implementation for pattern analysis
        pass
    
    def _perform_deep_reasoning(self):
        """Perform deep reasoning on existing knowledge"""
        # Implementation for deep reasoning
        pass
    
    def _log_learning_session(self, session_type, topic, facts_learned, success_rate, duration):
        """Log a learning session"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_sessions 
            (session_type, topic, facts_learned, success_rate, duration_seconds)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_type, topic, facts_learned, success_rate, duration))
        
        conn.commit()
        conn.close()
    
    def stop(self):
        """Stop autonomous learning"""
        self.is_running = False
        self.logger.info("🛑 Autonomous learning stopped")

class BackgroundService:
    """Service untuk menjalankan SiAgent di background"""
    
    def __init__(self):
        self.pid_file = '/tmp/siagent_enhanced.pid'
        self.log_file = 'siagent_background.log'
        self.is_daemon = False
        
    def start_as_daemon(self):
        """Start as background daemon service"""
        try:
            # Setup daemon context
            context = daemon.DaemonContext(
                pidfile=pidfile.TimeoutPIDLockFile(self.pid_file),
                stdout=open(self.log_file, 'a'),
                stderr=open(self.log_file, 'a')
            )
            
            with context:
                self.is_daemon = True
                self._run_background_service()
                
        except Exception as e:
            logging.error(f"Failed to start daemon: {e}")
            # Fallback to regular background thread
            self._start_background_thread()
    
    def _start_background_thread(self):
        """Fallback: start as background thread"""
        bg_thread = threading.Thread(target=self._run_background_service)
        bg_thread.daemon = True
        bg_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Background service stopped by user")
    
    def _run_background_service(self):
        """Run the main background service"""
        logging.info("🚀 Starting SiAgent background service...")
        
        try:
            # Initialize enhanced SiAgent
            agent = EnhancedSiAgent()
            agent.start_autonomous_mode()
            
            # Keep service running
            while True:
                time.sleep(3600)  # Check every hour
                
        except Exception as e:
            logging.error(f"Background service error: {e}")
    
    def stop_daemon(self):
        """Stop the daemon service"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            os.remove(self.pid_file)
            print("✅ SiAgent daemon stopped")
            
        except Exception as e:
            print(f"❌ Error stopping daemon: {e}")
    
    def is_running(self):
        """Check if daemon is running"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (FileNotFoundError, ProcessLookupError, ValueError):
            return False

class ModernWebUI:
    """Modern Web UI for SiAgent"""
    
    def __init__(self, agent):
        self.agent = agent
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'siagent_enhanced_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self._setup_routes()
        self._setup_socketio()
        
    def _setup_routes(self):
        """Setup web routes"""
        
        @self.app.route('/')
        def index():
            return render_template_string(self._get_html_template())
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.agent.get_comprehensive_status())
        
        @self.app.route('/api/knowledge')
        def get_knowledge():
            limit = request.args.get('limit', 50, type=int)
            knowledge = self.agent.get_recent_knowledge(limit)
            return jsonify(knowledge)
        
        @self.app.route('/api/learning_stats')
        def get_learning_stats():
            return jsonify(self.agent.get_learning_statistics())
    
    def _setup_socketio(self):
        """Setup Socket.IO events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            emit('status', {'msg': 'Connected to SiAgent Enhanced'})
        
        @self.socketio.on('send_message')
        def handle_message(data):
            message = data['message']
            response = self.agent.process_input(message)
            emit('bot_response', {'response': response})
        
        @self.socketio.on('get_stats')
        def handle_get_stats():
            stats = self.agent.get_comprehensive_status()
            emit('stats_update', stats)
    
    def _get_html_template(self):
        """Return modern HTML template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SiAgent Enhanced - AI with Autonomous Learning</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .card-header i {
            font-size: 1.5rem;
            margin-right: 10px;
            color: #667eea;
        }
        
        .card-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
            color: white;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            height: 500px;
            display: flex;
            flex-direction: column;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 15px;
            border-radius: 20px;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }
        
        .message.user {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
        }
        
        .message.bot {
            background: #e9ecef;
            color: #333;
        }
        
        .chat-input-container {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 15px;
            border: none;
            border-radius: 25px;
            background: #f8f9fa;
            font-size: 1rem;
            outline: none;
            transition: background 0.3s ease;
        }
        
        .chat-input:focus {
            background: #fff;
            box-shadow: 0 0 0 2px #667eea;
        }
        
        .send-btn {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s ease;
        }
        
        .send-btn:hover {
            transform: scale(1.05);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }
        
        .learning-activity {
            background: rgba(40, 167, 69, 0.1);
            border-left: 4px solid #28a745;
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
            100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
        }
        
        .chart-container {
            height: 300px;
            position: relative;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> SiAgent Enhanced</h1>
            <div class="subtitle">
                <span class="status-indicator"></span>
                Autonomous AI Learning 24/7
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-brain"></i>
                    <div class="card-title">Knowledge Base</div>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <span class="stat-number" id="total-knowledge">0</span>
                        <span class="stat-label">Total Facts</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="confidence-avg">0.0</span>
                        <span class="stat-label">Avg Confidence</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="categories">0</span>
                        <span class="stat-label">Categories</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="learning-sessions">0</span>
                        <span class="stat-label">Learning Sessions</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-chart-line"></i>
                    <div class="card-title">Learning Performance</div>
                </div>
                <div class="chart-container">
                    <canvas id="learningChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-cogs"></i>
                    <div class="card-title">Autonomous Learning Status</div>
                </div>
                <div id="learning-status">
                    <div class="learning-activity">
                        <strong>🌐 Web Exploration:</strong> <span id="web-status">Active</span>
                    </div>
                    <div class="learning-activity">
                        <strong>🧬 Knowledge Synthesis:</strong> <span id="synthesis-status">Active</span>
                    </div>
                    <div class="learning-activity">
                        <strong>🔍 Pattern Recognition:</strong> <span id="pattern-status">Active</span>
                    </div>
                    <div class="learning-activity">
                        <strong>🤔 Deep Reasoning:</strong> <span id="reasoning-status">Active</span>
                    </div>
                </div>
                <div style="margin-top: 15px;">
                    <strong>Current Focus:</strong> <span id="current-focus">General AI Research</span><br>
                    <strong>Next Learning Task:</strong> <span id="next-task">In 12 minutes</span><br>
                    <strong>Uptime:</strong> <span id="uptime">2h 34m</span>
                </div>
            </div>
            
            <div class="chat-container">
                <div class="card-header">
                    <i class="fas fa-comments"></i>
                    <div class="card-title">Chat with SiAgent</div>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="message bot">
                        <i class="fas fa-robot"></i> Hello! I'm SiAgent Enhanced. I'm continuously learning even when we're not chatting. Ask me anything!
                    </div>
                </div>
                <div class="chat-input-container">
                    <input type="text" class="chat-input" id="message-input" placeholder="Type your message..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="send-btn" onclick="sendMessage()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Chart for learning performance
        let learningChart;
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initializeChart();
            loadStats();
            setInterval(loadStats, 30000); // Update every 30 seconds
        });
        
        function initializeChart() {
            const ctx = document.getElementById('learningChart').getContext('2d');
            learningChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Facts Learned',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Confidence Score',
                        data: [],
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    }
                }
            });
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateDashboard(data);
                
                const learningResponse = await fetch('/api/learning_stats');
                const learningData = await learningResponse.json();
                
                updateChart(learningData);
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        function updateDashboard(data) {
            document.getElementById('total-knowledge').textContent = data.knowledge_count || 0;
            document.getElementById('confidence-avg').textContent = (data.avg_confidence || 0).toFixed(2);
            document.getElementById('categories').textContent = data.categories_count || 0;
            document.getElementById('learning-sessions').textContent = data.learning_sessions || 0;
            document.getElementById('current-focus').textContent = data.current_focus || 'General AI Research';
            document.getElementById('uptime').textContent = data.uptime || '0m';
        }
        
        function updateChart(data) {
            if (data.timeline && learningChart) {
                learningChart.data.labels = data.timeline.map(d => d.time);
                learningChart.data.datasets[0].data = data.timeline.map(d => d.facts_learned);
                learningChart.data.datasets[1].data = data.timeline.map(d => d.confidence * 100);
                learningChart.update();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessageToChat(message, 'user');
            
            // Send to server
            socket.emit('send_message', {message: message});
            
            // Clear input
            input.value = '';
        }
        
        function addMessageToChat(message, sender) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<i class="fas fa-user"></i> ${message}`;
            } else {
                messageDiv.innerHTML = `<i class="fas fa-robot"></i> ${message}`;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        // Socket.IO event handlers
        socket.on('bot_response', function(data) {
            addMessageToChat(data.response, 'bot');
        });
        
        socket.on('stats_update', function(data) {
            updateDashboard(data);
        });
        
        socket.on('learning_update', function(data) {
            // Update learning status indicators
            console.log('Learning update:', data);
        });
        
        // Auto-refresh learning status
        setInterval(function() {
            const statuses = ['web-status', 'synthesis-status', 'pattern-status', 'reasoning-status'];
            statuses.forEach(id => {
                const element = document.getElementById(id);
                if (Math.random() > 0.7) {
                    element.textContent = 'Working...';
                    element.style.color = '#ffc107';
                    setTimeout(() => {
                        element.textContent = 'Active';
                        element.style.color = '#28a745';
                    }, 2000);
                }
            });
        }, 15000);
        
        // Simulate next task countdown
        let nextTaskMinutes = 12;
        setInterval(function() {
            nextTaskMinutes--;
            if (nextTaskMinutes <= 0) {
                nextTaskMinutes = Math.floor(Math.random() * 30) + 5;
            }
            document.getElementById('next-task').textContent = `In ${nextTaskMinutes} minutes`;
        }, 60000);
    </script>
</body>
</html>
        '''
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the web server"""
        print(f"🌐 Starting SiAgent Enhanced Web UI at http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

class EnhancedSiAgent:
    """Enhanced SiAgent dengan autonomous learning dan UI modern"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.EnhancedSiAgent')
        self.logger.info("🚀 Initializing SiAgent Enhanced...")
        
        # Core components
        self.kb = EnhancedKnowledgeBase()
        self.autonomous_learning = AutonomousLearningEngine(self.kb)
        
        # System state
        self.start_time = time.time()
        self.is_autonomous_active = False
        
        # Performance metrics
        self.performance_metrics = {
            'total_interactions': 0,
            'successful_learnings': 0,
            'autonomous_sessions': 0,
            'uptime_hours': 0
        }
        
        # Load initial knowledge
        self._load_initial_knowledge()
        
        self.logger.info("✅ SiAgent Enhanced initialized successfully")
    
    def _load_initial_knowledge(self):
        """Load initial knowledge base"""
        initial_facts = [
            ("SiAgent Enhanced", "is", "autonomous learning AI system", 1.0, "ai_systems"),
            ("Machine Learning", "enables", "pattern recognition in data", 0.9, "ml"),
            ("Neural Networks", "mimic", "human brain structure", 0.9, "ml"),
            ("Robotics", "combines", "AI and mechanical engineering", 0.9, "robotics"),
            ("Autonomous Systems", "operate", "without human intervention", 0.9, "automation"),
            ("Deep Learning", "uses", "multiple layer neural networks", 0.9, "ml"),
            ("Computer Vision", "enables", "machines to see and interpret", 0.8, "ai_systems"),
            ("Natural Language Processing", "helps", "machines understand text", 0.8, "ai_systems"),
            ("Reinforcement Learning", "learns", "through trial and error", 0.8, "ml"),
            ("Internet of Things", "connects", "everyday devices to internet", 0.8, "technology")
        ]
        
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        for fact in initial_facts:
            cursor.execute('''
                INSERT OR IGNORE INTO knowledge 
                (subject, predicate, object, confidence, category, source, importance_score, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
            ''', (fact[0], fact[1], fact[2], fact[3], fact[4], "initial_load", 0.8))
        
        conn.commit()
        conn.close()
        
        self.logger.info("📚 Initial knowledge loaded")
    
    def start_autonomous_mode(self):
        """Start autonomous learning mode"""
        if not self.is_autonomous_active:
            self.autonomous_learning.start_autonomous_learning()
            self.is_autonomous_active = True
            self.logger.info("🤖 Autonomous mode activated")
    
    def stop_autonomous_mode(self):
        """Stop autonomous learning mode"""
        if self.is_autonomous_active:
            self.autonomous_learning.stop()
            self.is_autonomous_active = False
            self.logger.info("🛑 Autonomous mode deactivated")
    
    def process_input(self, user_input):
        """Process user input with enhanced capabilities"""
        self.performance_metrics['total_interactions'] += 1
        self.logger.info(f"📝 Processing input: {user_input}")
        
        # Analyze input type
        input_type = self._analyze_input_type(user_input)
        
        try:
            if input_type == "question":
                response = self._answer_question(user_input)
            elif input_type == "command":
                response = self._execute_command(user_input)
            elif input_type == "learning_material":
                response = self._learn_from_input(user_input)
            else:
                response = self._general_conversation(user_input)
            
            # Learn from interaction
            self._learn_from_interaction(user_input, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing input: {str(e)}"
            self.logger.error(error_msg)
            return "I encountered an error while processing your request. Let me learn from this and try again."
    
    def _analyze_input_type(self, text):
        """Analyze type of user input"""
        text_lower = text.lower()
        
        question_indicators = ['what', 'who', 'when', 'where', 'why', 'how', 'apa', 'siapa', 'kapan', 'dimana', 'mengapa', 'bagaimana']
        if any(word in text_lower for word in question_indicators) or text.endswith('?'):
            return "question"
        
        command_indicators = ['start', 'stop', 'show', 'analyze', 'learn', 'teach', 'pelajari', 'analisis', 'tampilkan']
        if any(word in text_lower for word in command_indicators):
            return "command"
        
        if len(text.split()) > 15:
            return "learning_material"
        
        return "conversation"
    
    def _answer_question(self, question):
        """Answer user questions using knowledge base"""
        keywords = self._extract_keywords(question)
        
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Search for relevant knowledge
        relevant_facts = []
        for keyword in keywords:
            cursor.execute('''
                SELECT subject, predicate, object, confidence, category
                FROM knowledge 
                WHERE subject LIKE ? OR object LIKE ? OR category LIKE ?
                ORDER BY confidence DESC, access_count DESC
                LIMIT 5
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            
            facts = cursor.fetchall()
            relevant_facts.extend(facts)
        
        conn.close()
        
        if relevant_facts:
            # Build response from top facts
            top_facts = sorted(set(relevant_facts), key=lambda x: x[3], reverse=True)[:3]
            
            response_parts = [f"Based on my knowledge about {', '.join(keywords)}:"]
            
            for fact in top_facts:
                confidence_indicator = "🟢" if fact[3] > 0.8 else "🟡" if fact[3] > 0.6 else "🔴"
                response_parts.append(f"{confidence_indicator} {fact[0]} {fact[1]} {fact[2]}")
            
            # Add learning note if confidence is low
            avg_confidence = sum(f[3] for f in top_facts) / len(top_facts)
            if avg_confidence < 0.7:
                response_parts.append("\n💡 I'm still learning about this topic. My autonomous learning system will continue to gather more information!")
            
            return "\n".join(response_parts)
        else:
            # No knowledge found - trigger autonomous learning
            if self.is_autonomous_active:
                # Add learning task for this topic
                topic = ' '.join(keywords) if keywords else question[:50]
                self.autonomous_learning._execute_learning_task(topic)
                return f"I don't have specific knowledge about this yet, but I've just started learning about '{topic}' autonomously. Ask me again in a few minutes!"
            else:
                return "I don't have information about this topic yet. You can start my autonomous learning mode to help me learn continuously!"
    
    def _execute_command(self, command):
        """Execute system commands"""
        cmd_lower = command.lower()
        
        if "start autonomous" in cmd_lower or "mulai otomatis" in cmd_lower:
            self.start_autonomous_mode()
            return "✅ Autonomous learning mode activated! I'm now learning 24/7 in the background."
        
        elif "stop autonomous" in cmd_lower or "hentikan otomatis" in cmd_lower:
            self.stop_autonomous_mode()
            return "⏸️ Autonomous learning mode paused. I'll wait for your commands."
        
        elif "status" in cmd_lower:
            return self._get_detailed_status()
        
        elif "learn" in cmd_lower or "pelajari" in cmd_lower:
            topic = self._extract_learning_topic(command)
            if topic:
                self.autonomous_learning._execute_learning_task(topic)
                return f"🎯 Started focused learning session on '{topic}'. Check back soon for new knowledge!"
        
        elif "analyze" in cmd_lower or "analisis" in cmd_lower:
            return self._analyze_knowledge_patterns()
        
        return "Command not recognized. Available commands: start autonomous, stop autonomous, status, learn [topic], analyze"
    
    def _learn_from_input(self, text):
        """Learn from user-provided text"""
        facts_learned = 0
        
        # Extract facts using NLP patterns
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Simple fact extraction patterns
            patterns = [
                r'(\w+(?:\s+\w+)*)\s+(is|are|was|were|adalah|ialah)\s+([^,\.]+)',
                r'(\w+(?:\s+\w+)*)\s+(has|have|had|memiliki|punya)\s+([^,\.]+)',
                r'(\w+(?:\s+\w+)*)\s+(can|could|may|might|dapat|bisa)\s+([^,\.]+)',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 3:
                        subject = match.group(1).strip()
                        predicate = match.group(2).strip()
                        obj = match.group(3).strip()
                        
                        # Store the fact
                        self._store_learned_fact(subject, predicate, obj, "user_input", "user_provided", 0.8)
                        facts_learned += 1
        
        return f"📚 Thank you! I learned {facts_learned} new facts from your input. This knowledge will help me answer future questions better!"
    
    def _general_conversation(self, text):
        """Handle general conversation"""
        positive_indicators = ['good', 'great', 'excellent', 'amazing', 'baik', 'bagus', 'hebat', 'terima kasih', 'thanks']
        negative_indicators = ['bad', 'poor', 'wrong', 'terrible', 'buruk', 'salah', 'jelek']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in positive_indicators):
            return "😊 Thank you! I'm glad I could help. My autonomous learning system is always working to improve my responses. Is there anything specific you'd like to know?"
        
        elif any(word in text_lower for word in negative_indicators):
            return "😔 I apologize if my response wasn't helpful. I'm constantly learning and improving. Could you help me understand what I got wrong so I can learn better?"
        
        elif "hello" in text_lower or "hi" in text_lower or "halo" in text_lower:
            autonomous_status = "active and learning continuously" if self.is_autonomous_active else "ready to activate"
            return f"👋 Hello! I'm SiAgent Enhanced. My autonomous learning system is currently {autonomous_status}. How can I help you today?"
        
        else:
            return "🤖 I understand you're sharing something with me. While I process natural conversation, I'm most helpful when you ask questions or give me specific topics to learn about. My autonomous learning system is always working to understand more!"
    
    def _extract_keywords(self, text):
        """Extract keywords from text"""
        # Simple keyword extraction
        stop_words = {'the', 'is', 'are', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                     'yang', 'dan', 'atau', 'di', 'pada', 'untuk', 'dari', 'dengan', 'oleh', 'adalah', 'apa', 'bagaimana'}
        
        words = re.findall(r'\w+', text.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:5]  # Limit to top 5 keywords
    
    def _extract_learning_topic(self, command):
        """Extract topic from learning command"""
        # Remove command words and get the topic
        command_words = ['learn', 'pelajari', 'study', 'research', 'analyze', 'analisis']
        words = command.split()
        
        topic_words = []
        found_command = False
        
        for word in words:
            if word.lower() in command_words:
                found_command = True
                continue
            if found_command:
                topic_words.append(word)
        
        return ' '.join(topic_words) if topic_words else None
    
    def _store_learned_fact(self, subject, predicate, obj, source, category, confidence):
        """Store a learned fact in the knowledge base"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge 
            (subject, predicate, object, confidence, source, category, importance_score, last_accessed, access_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1)
        ''', (subject, predicate, obj, confidence, source, category, random.uniform(0.5, 1.0)))
        
        conn.commit()
        conn.close()
    
    def _learn_from_interaction(self, user_input, response):
        """Learn from user interactions"""
        # Simple sentiment analysis and pattern learning
        interaction_data = {
            'input_length': len(user_input),
            'response_length': len(response),
            'timestamp': time.time(),
            'input_type': self._analyze_input_type(user_input)
        }
        
        # This could be expanded to learn user preferences, common questions, etc.
        self.logger.debug(f"Learning from interaction: {interaction_data}")
    
    def get_comprehensive_status(self):
        """Get comprehensive system status"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Get knowledge stats
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        knowledge_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(confidence) FROM knowledge')
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        cursor.execute('SELECT COUNT(DISTINCT category) FROM knowledge')
        categories_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM learning_sessions')
        learning_sessions = cursor.fetchone()[0]
        
        # Get recent learning activity
        cursor.execute('''
            SELECT COUNT(*) FROM learning_sessions 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        recent_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        uptime_seconds = time.time() - self.start_time
        uptime_str = self._format_uptime(uptime_seconds)
        
        return {
            'knowledge_count': knowledge_count,
            'avg_confidence': avg_confidence,
            'categories_count': categories_count,
            'learning_sessions': learning_sessions,
            'recent_sessions': recent_sessions,
            'autonomous_active': self.is_autonomous_active,
            'uptime': uptime_str,
            'current_focus': 'Autonomous Learning' if self.is_autonomous_active else 'Manual Mode',
            'performance_metrics': self.performance_metrics
        }
    
    def get_learning_statistics(self):
        """Get learning statistics for charts"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Get timeline data for the last 24 hours
        cursor.execute('''
            SELECT 
                strftime('%H:00', timestamp) as hour,
                SUM(facts_learned) as total_facts,
                AVG(success_rate) as avg_success
            FROM learning_sessions
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''')
        
        timeline_data = []
        for row in cursor.fetchall():
            timeline_data.append({
                'time': row[0],
                'facts_learned': row[1] or 0,
                'confidence': row[2] or 0.5
            })
        
        conn.close()
        
        return {
            'timeline': timeline_data,
            'total_autonomous_sessions': self.performance_metrics.get('autonomous_sessions', 0)
        }
    
    def get_recent_knowledge(self, limit=50):
        """Get recently learned knowledge"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subject, predicate, object, confidence, category, timestamp
            FROM knowledge
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        knowledge_list = []
        for row in cursor.fetchall():
            knowledge_list.append({
                'subject': row[0],
                'predicate': row[1],
                'object': row[2],
                'confidence': row[3],
                'category': row[4],
                'timestamp': row[5]
            })
        
        conn.close()
        return knowledge_list
    
    def _get_detailed_status(self):
        """Get detailed status for command line"""
        status = self.get_comprehensive_status()
        
        return f"""
🤖 SiAgent Enhanced Status Report
================================
📊 Knowledge Base:
   • Total Facts: {status['knowledge_count']}
   • Average Confidence: {status['avg_confidence']:.2f}
   • Categories: {status['categories_count']}
   
🎯 Learning Performance:
   • Total Learning Sessions: {status['learning_sessions']}
   • Recent Sessions (1h): {status['recent_sessions']}
   • Total Interactions: {status['performance_metrics']['total_interactions']}
   
🔄 Autonomous Learning:
   • Status: {'🟢 Active' if status['autonomous_active'] else '⭕ Inactive'}
   • Current Focus: {status['current_focus']}
   • Uptime: {status['uptime']}
   
💡 System is {'continuously learning in background' if status['autonomous_active'] else 'ready for autonomous activation'}
        """
    
    def _analyze_knowledge_patterns(self):
        """Analyze patterns in knowledge base"""
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        
        # Most common subjects
        cursor.execute('''
            SELECT subject, COUNT(*) as count
            FROM knowledge
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 5
        ''')
        
        top_subjects = cursor.fetchall()
        
        # Most common categories
        cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM knowledge
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        ''')
        
        top_categories = cursor.fetchall()
        
        conn.close()
        
        analysis = "📈 Knowledge Base Analysis:\n\n"
        
        analysis += "🏆 Top Subjects:\n"
        for subject, count in top_subjects:
            analysis += f"   • {subject}: {count} facts\n"
        
        analysis += "\n📂 Top Categories:\n"
        for category, count, avg_conf in top_categories:
            analysis += f"   • {category}: {count} facts (avg confidence: {avg_conf:.2f})\n"
        
        return analysis
    
    def _format_uptime(self, seconds):
        """Format uptime in human readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def shutdown(self):
        """Shutdown the system gracefully"""
        self.stop_autonomous_mode()
        self.logger.info("🛑 SiAgent Enhanced shutdown complete")

def main():
    """Main function untuk menjalankan SiAgent Enhanced"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SiAgent Enhanced - Autonomous Learning AI')
    parser.add_argument('--mode', choices=['chat', 'web', 'daemon', 'status'], 
                       default='web', help='Running mode')
    parser.add_argument('--host', default='127.0.0.1', help='Web server host')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    parser.add_argument('--daemon-action', choices=['start', 'stop', 'status'], 
                       help='Daemon action')
    
    args = parser.parse_args()
    
    if args.mode == 'daemon':