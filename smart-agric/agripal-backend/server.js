// server.js - Node.js + Express Backend for AgriPal
const express = require('express');
const mqtt = require('mqtt');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');

// ============================================
// CONFIGURATION
// ============================================
const PORT = 3001;

const MQTT_CONFIG = {
    protocol: 'mqtts',
    host: 'f3150d0d05ce46d0873bf1a69c56ff38.s1.eu.hivemq.cloud', // Update this
    port: 8883,
    username: 'Ayodeji',  // Update this
    password: 'cand4f694a@A',  // Update this
    clientId: `agripal_backend_${Math.random().toString(16).substr(2, 8)}`,
    clean: true,
    reconnectPeriod: 5000,
};

// ============================================
// INITIALIZE EXPRESS & SOCKET.IO
// ============================================
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: '*', // In production, specify your React app URL
        methods: ['GET', 'POST']
    }
});

app.use(cors());
app.use(express.json());

// ============================================
// IN-MEMORY DATA STORE
// ============================================
const sensorDataStore = {
    latest: new Map(),      // Latest reading per sensor
    history: new Map(),     // Historical readings (last 100 per sensor)
    maxHistorySize: 100
};

// Helper function to store sensor data
function storeSensorData(data) {
    const key = `${data.farm_id}_${data.device_id}`;

    // Store latest
    sensorDataStore.latest.set(key, {
        ...data,
        receivedAt: new Date().toISOString()
    });

    // Store in history
    if (!sensorDataStore.history.has(key)) {
        sensorDataStore.history.set(key, []);
    }
    const history = sensorDataStore.history.get(key);
    history.unshift({
        ...data,
        receivedAt: new Date().toISOString()
    });

    // Keep only last N readings
    if (history.length > sensorDataStore.maxHistorySize) {
        history.pop();
    }
}

// ============================================
// MQTT CLIENT SETUP
// ============================================
console.log('🚀 Starting AgriPal Backend Server...');
console.log(`📡 Connecting to MQTT Broker: ${MQTT_CONFIG.host}`);

const mqttClient = mqtt.connect(MQTT_CONFIG);

mqttClient.on('connect', () => {
    console.log('✅ Connected to HiveMQ!');

    // Subscribe to all AgriPal topics
    mqttClient.subscribe('agripal/#', (err) => {
        if (!err) {
            console.log('✅ Subscribed to agripal/# topics');
        } else {
            console.error('❌ Subscription error:', err);
        }
    });
});

mqttClient.on('message', (topic, message) => {
    try {
        const data = JSON.parse(message.toString());
        console.log(`📥 Received from ${topic}:`, {
            device_id: data.device_id,
            farm_id: data.farm_id,
            soil_moisture: data.soil_moisture,
            temperature: data.temperature,
            humidity: data.humidity
        });

        // Store in memory
        storeSensorData(data);

        // Broadcast to all connected Socket.IO clients
        io.emit('sensor-data', {
            topic,
            data: {
                ...data,
                receivedAt: new Date().toISOString()
            }
        });

        // Optional: Save to Supabase here
        // await saveToSupabase(data);

    } catch (error) {
        console.error('❌ Error parsing message:', error);
    }
});

mqttClient.on('error', (error) => {
    console.error('❌ MQTT Error:', error);
});

mqttClient.on('reconnect', () => {
    console.log('🔄 Reconnecting to MQTT Broker...');
});

mqttClient.on('close', () => {
    console.log('⚠️  MQTT connection closed');
});

// ============================================
// SOCKET.IO EVENTS
// ============================================
io.on('connection', (socket) => {
    console.log(`👤 Client connected: ${socket.id}`);

    // Send current data to newly connected client
    const latestData = Array.from(sensorDataStore.latest.values());
    socket.emit('initial-data', latestData);

    socket.on('disconnect', () => {
        console.log(`👤 Client disconnected: ${socket.id}`);
    });

    // Optional: Allow clients to request specific sensor data
    socket.on('request-sensor', (sensorId) => {
        const data = sensorDataStore.latest.get(sensorId);
        if (data) {
            socket.emit('sensor-data', { data });
        }
    });
});

// ============================================
// REST API ENDPOINTS
// ============================================

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        mqtt: mqttClient.connected ? 'connected' : 'disconnected',
        sensors: sensorDataStore.latest.size,
        timestamp: new Date().toISOString()
    });
});

// Get all latest sensor data
app.get('/api/sensors', (req, res) => {
    const sensors = Array.from(sensorDataStore.latest.values());
    res.json({
        success: true,
        count: sensors.length,
        data: sensors,
        timestamp: new Date().toISOString()
    });
});

// Get specific sensor (latest + history)
app.get('/api/sensors/:farmId/:deviceId', (req, res) => {
    const { farmId, deviceId } = req.params;
    const key = `${farmId}_${deviceId}`;

    const latest = sensorDataStore.latest.get(key);
    const history = sensorDataStore.history.get(key) || [];

    if (!latest) {
        return res.status(404).json({
            success: false,
            error: 'Sensor not found'
        });
    }

    res.json({
        success: true,
        latest,
        history,
        historyCount: history.length
    });
});

// Get only latest data for specific sensor
app.get('/api/sensors/:farmId/:deviceId/latest', (req, res) => {
    const { farmId, deviceId } = req.params;
    const key = `${farmId}_${deviceId}`;

    const data = sensorDataStore.latest.get(key);

    if (!data) {
        return res.status(404).json({
            success: false,
            error: 'Sensor not found'
        });
    }

    res.json({
        success: true,
        data
    });
});

// Get history for specific sensor
app.get('/api/sensors/:farmId/:deviceId/history', (req, res) => {
    const { farmId, deviceId } = req.params;
    const key = `${farmId}_${deviceId}`;
    const limit = parseInt(req.query.limit) || 100;

    const history = sensorDataStore.history.get(key) || [];

    res.json({
        success: true,
        count: history.length,
        data: history.slice(0, limit)
    });
});

// ============================================
// START SERVER
// ============================================
server.listen(PORT, () => {
    console.log(`\n✅ Server running on http://localhost:${PORT}`);
    console.log(`📊 API Endpoints:`);
    console.log(`   GET  /health`);
    console.log(`   GET  /api/sensors`);
    console.log(`   GET  /api/sensors/:farmId/:deviceId`);
    console.log(`   GET  /api/sensors/:farmId/:deviceId/latest`);
    console.log(`   GET  /api/sensors/:farmId/:deviceId/history`);
    console.log(`\n🔌 Socket.IO Events:`);
    console.log(`   sensor-data  - Real-time sensor updates`);
    console.log(`   initial-data - Initial data on connection`);
    console.log(`\n⏳ Waiting for sensor data from Raspberry Pi...\n`);
});

// ============================================
// GRACEFUL SHUTDOWN
// ============================================
process.on('SIGINT', () => {
    console.log('\n⏹  Shutting down gracefully...');
    mqttClient.end();
    server.close(() => {
        console.log('✅ Server closed');
        process.exit(0);
    });
});