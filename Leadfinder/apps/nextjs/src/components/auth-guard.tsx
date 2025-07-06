"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useFirebaseAuth } from "./firebase-auth-provider";

interface AuthGuardProps {
  children: React.ReactNode;
  lang: string;
}

export function AuthGuard({ children, lang }: AuthGuardProps) {
  const { user, loading } = useFirebaseAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push(`/${lang}/login`);
    }
  }, [user, loading, router, lang]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return <>{children}</>;
} 