import { useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import firebase from "firebase/app";
import auth from "../firebaseSetup";
import { User } from 'firebase/auth'

interface Props {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<Props> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((firebaseUser) => {
      console.debug("Parece que hubo un logueo!",firebaseUser);
      setUser(firebaseUser);
    });


    return unsubscribe;
  }, []);

  return <AuthContext.Provider
    value={
      { currentUser: user, hasInitialized: (auth as unknown as { _isInitialized: boolean })._isInitialized }}
  >{children}</AuthContext.Provider>;
};