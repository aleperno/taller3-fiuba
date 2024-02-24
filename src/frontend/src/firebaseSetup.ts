import { initializeApp } from 'firebase/app';
import { 
  getAuth,
  onAuthStateChanged, 
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  connectAuthEmulator
} from 'firebase/auth';

const dummyFirebaseConfig = {
    apiKey: "dummy-apiKey",
    authDomain: "dummy-authDomain.firebaseapp.com",
    projectId: "dummy-project-id",
    storageBucket: "dummy-authDomain.firebaseapp.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:7c7abae699b868b7f896ec",
    measurementId: "G-ABCDEFGHIJ"
  }; //this is where your firebase app values you copied will go


const readFirebaseConfig = () => {
  try {
    const config = require('./firebase-prod-config.json');
    return config 
  } catch (error) {
    console.log("Error reading firebase config file", error);
    throw new Error("Error reading firebase config file");
  }
};

const isDev = process.env.REACT_APP_APP_MODE === 'development';
console.log("Running in: ", process.env["REACT_APP_APP_MODE"])

const firebaseApp = isDev ? initializeApp(dummyFirebaseConfig) : initializeApp(readFirebaseConfig());

const auth = getAuth(firebaseApp);
if (isDev) {
  connectAuthEmulator(auth, "http://localhost:9099");
}

export default auth;