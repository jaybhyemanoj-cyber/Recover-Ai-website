import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCDVzvrQYOjZktQhW0zU-Yzc8bB6kRQwyc",
  authDomain: "sarthak-18e43.firebaseapp.com",
  projectId: "sarthak-18e43",
  storageBucket: "sarthak-18e43.firebasestorage.app",
  messagingSenderId: "897434846837",
  appId: "1:897434846837:web:82c631ec60c95c8e995a3c"
};

// Initialize Firebase SDK
export const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
