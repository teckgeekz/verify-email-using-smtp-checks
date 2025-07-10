"use client";

import React from "react";
import Link from "next/link";
import { useSelectedLayoutSegment } from "next/navigation";

import { cn } from "@saasfly/ui";
import { Button } from "@saasfly/ui/button";

import { MainNav } from "./main-nav";
import { useFirebaseAuthModal, FirebaseAuthModal } from "./firebase-auth-modal";
import useScroll from "~/hooks/use-scroll";
import type { MainNavItem } from "~/types";
import { useFirebaseAuth } from "./firebase-auth-provider";

interface NavBarProps {
  items?: MainNavItem[];
  children?: React.ReactNode;
  rightElements?: React.ReactNode;
  scroll?: boolean;
  params: {
    lang: string;
  };
  marketing: Record<string, string | object>;
  dropdown: Record<string, string>;
}

export function NavBar({
  items,
  children,
  rightElements,
  scroll = false,
  params: { lang },
  marketing,
  dropdown,
}: NavBarProps) {
  const scrolled = useScroll(50);
  const authModal = useFirebaseAuthModal();
  const segment = useSelectedLayoutSegment();
  const { user, loading, logout } = useFirebaseAuth();
  const [dropdownOpen, setDropdownOpen] = React.useState(false);

  const handleLogout = async () => {
    await logout();
    setDropdownOpen(false);
  };

  return (
    <header
      className={`sticky top-0 z-40 flex w-full justify-center border-border bg-background/60 backdrop-blur-xl transition-all ${
        scroll ? (scrolled ? "border-b" : "bg-background/0") : "border-b"
      }`}
    >
      <div className="container flex h-16 items-center justify-between py-4">
        <MainNav items={items} params={{ lang: `${lang}` }} marketing={marketing}>
          {children}
        </MainNav>

        <div className="flex items-center space-x-3">
          {items?.length ? (
            <nav className="hidden gap-6 md:flex">
              {items?.map((item, index) => (
                <Link
                  key={index}
                  href={item.disabled ? "#" : `/${lang}${item.href}`}
                  className={cn(
                    "flex items-center text-lg font-medium transition-colors hover:text-foreground/80 sm:text-sm",
                    item.href.startsWith(`/${segment}`)
                      ? "text-blue-500 font-semibold"
                      : "",
                    item.disabled && "cursor-not-allowed opacity-80",
                  )}
                >
                  {item.title}
                </Link>
              ))}
            </nav>
          ) : null}

          <div className="w-[1px] h-8 bg-accent"></div>

          {rightElements}


          {!user && !loading ? (
            <>
              <Button variant="outline" size="sm" onClick={authModal.onOpen}>
                {typeof marketing.login === "string"
                  ? marketing.login
                  : "Login"}
              </Button>
              <Button
                className="px-3 ml-2"
                variant="default"
                size="sm"
                onClick={authModal.onOpen}
              >
                {typeof marketing.signup === "string"
                  ? marketing.signup
                  : "Signup"}
              </Button>
              <FirebaseAuthModal open={authModal.open} onClose={authModal.onClose} />
            </>
          ) : user ? (
            <div className="ml-4 text-white flex items-center gap-2 relative select-none">
              <button
                className="flex items-center gap-2 focus:outline-none"
                onClick={() => setDropdownOpen((v) => !v)}
                aria-haspopup="true"
                aria-expanded={dropdownOpen}
              >
                {user.photoURL ? (
                  <img src={user.photoURL} alt="avatar" className="w-8 h-8 rounded-full object-cover bg-zinc-200" />
                ) : (
                  <span className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-bold uppercase">
                    {user.displayName ? user.displayName[0] : user.email ? user.email[0] : "U"}
                  </span>
                )}
                <span>{user.displayName || user.email}</span>
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
              </button>
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white dark:bg-zinc-900 rounded-lg shadow-lg py-2 z-50 border border-zinc-200 dark:border-zinc-700">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-zinc-700 dark:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                  >
                    Log out
                  </button>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
