import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { colors } from '../src/theme/colors';

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: colors.background
          },
          headerTintColor: colors.cyan,
          headerTitleStyle: {
            fontWeight: '800'
          },
          contentStyle: {
            backgroundColor: colors.background
          }
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="route-planner" options={{ title: 'Route Options' }} />
        <Stack.Screen name="navigation" options={{ headerShown: false }} />
        <Stack.Screen name="copilot" options={{ title: 'AI Copilot' }} />
        <Stack.Screen name="destinations" options={{ title: 'Destinations' }} />
        <Stack.Screen name="itinerary" options={{ title: 'Journey Itinerary' }} />
        <Stack.Screen name="saved-places" options={{ title: 'Saved Places' }} />
        <Stack.Screen name="settings" options={{ title: 'Settings' }} />
        <Stack.Screen name="onboarding" options={{ headerShown: false }} />
      </Stack>
    </SafeAreaProvider>
  );
}
