// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBnLNMylTO8bGoO6X-XXdtJ9dTAKOf3LaI",
  authDomain: "renaultcup-4a1d2.firebaseapp.com",
  projectId: "renaultcup-4a1d2",
  storageBucket: "renaultcup-4a1d2.firebasestorage.app",
  messagingSenderId: "1031158605901",
  appId: "1:1031158605901:web:2c7f08ec7c34bb33585404",
  measurementId: "G-67C71NFEQ5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);