"use client";
import { useState } from "react";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { Button } from "@saasfly/ui/button";

export function useFirebaseAuthModal() {
  const [open, setOpen] = useState(false);
  return {
    open,
    onOpen: () => setOpen(true),
    onClose: () => setOpen(false),
    setOpen,
  };
}

export function FirebaseAuthModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [tab, setTab] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value);
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value);

  const handlePostLogin = async (firebaseUser: import("firebase/auth").User) => {
    try {
      console.log("[auth-modal] Syncing user to database:", {
        uid: firebaseUser.uid,
        email: firebaseUser.email,
        name: firebaseUser.displayName,
      });
      
      // Call backend to sync user
      const response = await fetch("/api/user-sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          name: firebaseUser.displayName,
        }),
      });
      
      const result = await response.json();
      console.log("[auth-modal] User sync response:", result);
      
      if (!result.success) {
        console.error("[auth-modal] User sync failed:", result.error);
      }
    } catch (error) {
      console.error("[auth-modal] Error syncing user:", error);
    }
  };

  const handleGoogle = async () => {
    setLoading(true);
    setError(null);
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      await handlePostLogin(result.user);
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let userCredential;
      if (tab === 'login') {
        userCredential = await signInWithEmailAndPassword(auth, email, password);
      } else {
        userCredential = await createUserWithEmailAndPassword(auth, email, password);
      }
      await handlePostLogin(userCredential.user);
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center min-h-screen bg-black/60 backdrop-blur-sm">
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-xl p-8 w-full max-w-md relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">&times;</button>
        <div className="flex justify-center mb-6">
          <button
            className={`px-4 py-2 font-semibold rounded-t-lg ${tab === 'login' ? 'bg-blue-600 text-white' : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-200'}`}
            onClick={() => setTab('login')}
          >
            Login
          </button>
          <button
            className={`px-4 py-2 font-semibold rounded-t-lg ml-2 ${tab === 'signup' ? 'bg-blue-600 text-white' : 'bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-200'}`}
            onClick={() => setTab('signup')}
          >
            Signup
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={handleEmailChange}
            className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={handlePasswordChange}
            className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100"
            required
          />
          {error && <div className="text-red-500 text-sm">{error}</div>}
          {/* Button does not support 'loading' prop, so show spinner inside */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
                {tab === 'login' ? 'Logging in...' : 'Signing up...'}
              </span>
            ) : (
              tab === 'login' ? 'Login' : 'Signup'
            )}
          </Button>
        </form>
        <div className="mt-6 flex flex-col gap-2">
          <Button onClick={handleGoogle} className="w-full" variant="outline" disabled={loading}>
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>
                Continue with Google
              </span>
            ) : (
              'Continue with Google'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 