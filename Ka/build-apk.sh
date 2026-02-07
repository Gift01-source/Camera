#!/bin/bash
# 📱 Build APK with Expo - Fastest Way!
# This script creates a standalone Android APK from React Native

set -e

echo "🚀 Building APK for AI Camera App..."
echo ""
echo "Prerequisites:"
echo "  ✓ Node.js installed (check: node -v)"
echo "  ✓ npm installed (check: npm -v)"
echo "  ✓ Expo account (free at https://expo.dev)"
echo ""
echo "Creating React Native project..."

# Create new Expo project
npx create-expo-app@latest camera-mobile

cd camera-mobile

# Copy main app code
cat > App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';

// CHANGE THIS TO YOUR IP ADDRESS
const API_URL = 'http://10.0.2.78:5000';

export default function App() {
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      // Fetch status
      const statusRes = await fetch(`${API_URL}/api/status`);
      const statusData = await statusRes.json();
      setStatus(statusData);

      // Fetch events
      const eventsRes = await fetch(`${API_URL}/api/events`);
      const eventsData = await eventsRes.json();
      setEvents(eventsData.slice(0, 10)); // Show last 10

      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setStatus({ error: error.message });
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#2196F3" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🎥 AI Camera</Text>
        <Text style={styles.subtitle}>Real-time Security & Analytics</Text>
      </View>

      {/* Status Card */}
      {status && !status.error ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>📊 System Status</Text>
          <View style={styles.statusRow}>
            <Text style={styles.label}>Status:</Text>
            <Text style={[styles.value, { color: status.status === 'running' ? '#4CAF50' : '#f44336' }]}>
              {status.status?.toUpperCase()}
            </Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.label}>FPS:</Text>
            <Text style={styles.value}>{status.fps || '0'}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.label}>Frames:</Text>
            <Text style={styles.value}>{status.frames_processed || '0'}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.label}>Time:</Text>
            <Text style={styles.value}>{new Date(status.timestamp).toLocaleTimeString()}</Text>
          </View>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.error}>❌ Cannot connect to API</Text>
          <Text style={styles.errorSubtext}>
            Make sure the server is running and IP is correct: {API_URL}
          </Text>
        </View>
      )}

      {/* Events */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🚨 Recent Events</Text>
        {events.length > 0 ? (
          events.map((event, index) => (
            <View key={index} style={styles.eventItem}>
              <View style={styles.eventHeader}>
                <Text style={styles.eventType}>{event.type}</Text>
                <Text style={[styles.severity, { backgroundColor: getSeverityColor(event.severity) }]}>
                  {event.severity}
                </Text>
              </View>
              <Text style={styles.eventTime}>{new Date(event.timestamp).toLocaleString()}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.noEvents}>No events recorded</Text>
        )}
      </View>

      {/* Refresh Button */}
      <TouchableOpacity style={styles.button} onPress={onRefresh}>
        <Text style={styles.buttonText}>🔄 Refresh Now</Text>
      </TouchableOpacity>

      {/* API Status */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>API: {API_URL}</Text>
        <Text style={styles.footerText}>Version: 1.0.0</Text>
      </View>
    </ScrollView>
  );
}

function getSeverityColor(severity) {
  const colors = {
    critical: '#f44336',
    high: '#ff9800',
    medium: '#2196F3',
    low: '#4CAF50',
  };
  return colors[severity] || '#999';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#1976D2',
    paddingVertical: 20,
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#e3f2fd',
    marginTop: 4,
  },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginBottom: 12,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#212121',
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    fontSize: 14,
    color: '#666',
  },
  value: {
    fontSize: 14,
    fontWeight: '600',
    color: '#212121',
  },
  eventItem: {
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
    paddingLeft: 12,
    paddingVertical: 8,
    marginBottom: 8,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  eventType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#212121',
  },
  severity: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  eventTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  noEvents: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
  },
  button: {
    backgroundColor: '#2196F3',
    marginHorizontal: 12,
    marginBottom: 12,
    paddingVertical: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  error: {
    fontSize: 14,
    color: '#f44336',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  errorSubtext: {
    fontSize: 12,
    color: '#999',
  },
  footer: {
    backgroundColor: '#f5f5f5',
    paddingVertical: 16,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
  },
});
EOF

echo "✅ Project created!"
echo ""
echo "📱 To build APK:"
echo ""
echo "1. Install EAS CLI:"
echo "   npm install -g eas-cli"
echo ""
echo "2. Login to Expo:"
echo "   eas login"
echo ""
echo "3. Build APK:"
echo "   cd camera-mobile"
echo "   eas build -p android --profile preview"
echo ""
echo "4. Download APK from: https://expo.dev/builds"
echo ""
echo "Done! 🎉"
