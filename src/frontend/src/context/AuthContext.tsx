import React from "react";

import {User} from 'firebase/auth'

console.log("En AuthContext.tsx")

export const AuthContext = React.createContext<{currentUser:User|null, hasInitialized:boolean} | null>(null);