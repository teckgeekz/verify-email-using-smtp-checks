import { getAuth, onAuthStateChanged } from "firebase/auth";

export interface User {
  id: string;
  name?: string | null;
  email?: string | null;
  image?: string | null;
  isAdmin?: boolean;
}

export const authOptions = {
  pages: {
    signIn: "/login",
  },
}

export async function getCurrentUser(): Promise<User | null> {
  // This function is called on the server side, so we can't use Firebase Auth directly
  // Instead, we'll return null and let the client-side handle authentication
  // TODO: Implement server-side Firebase token verification if needed
  return null;
}

// Client-side function to get current user
export function getCurrentUserClient(): Promise<User | null> {
  return new Promise((resolve) => {
    const auth = getAuth();
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      unsubscribe();
      if (firebaseUser) {
        resolve({
          id: firebaseUser.uid,
          name: firebaseUser.displayName,
          email: firebaseUser.email,
          image: firebaseUser.photoURL,
          isAdmin: false, // TODO: Check admin status from database
        });
      } else {
        resolve(null);
      }
    });
  });
}
