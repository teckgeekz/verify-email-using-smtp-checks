"use client";

import * as React from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";

import { cn } from "@saasfly/ui";
import { buttonVariants } from "@saasfly/ui/button";
import * as Icons from "@saasfly/ui/icons";
import { Input } from "@saasfly/ui/input";
import { Label } from "@saasfly/ui/label";
import { toast } from "@saasfly/ui/use-toast";
import { useFirebaseAuth } from "./firebase-auth-provider";

type Dictionary = Record<string, string>;

interface UserAuthFormProps extends React.HTMLAttributes<HTMLDivElement> {
  lang: string;
  dict: Dictionary;
  disabled?: boolean;
}

const userAuthSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type FormData = z.infer<typeof userAuthSchema>;

export function UserAuthForm({
  className,
  lang,
  dict,
  disabled,
  ...props
}: UserAuthFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(userAuthSchema),
  });
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [isSignUp, setIsSignUp] = React.useState<boolean>(false);
  const searchParams = useSearchParams();
  const router = useRouter();
  const { signIn, signUp } = useFirebaseAuth();

  async function onSubmit(data: FormData) {
    setIsLoading(true);

    try {
      if (isSignUp) {
        await signUp(data.email.toLowerCase(), data.password);
        toast({
          title: "Account created successfully!",
          description: "You can now sign in with your new account.",
        });
        setIsSignUp(false);
      } else {
        await signIn(data.email.toLowerCase(), data.password);
        const callbackUrl = searchParams?.get("from") ?? `/${lang}/dashboard`;
        router.push(callbackUrl);
        toast({
          title: "Signed in successfully!",
          description: "Welcome back!",
        });
      }
    } catch (error: any) {
      console.error("Authentication error:", error);
      toast({
        title: "Authentication failed",
        description: error.message || "Please check your credentials and try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-2">
          <div className="grid gap-1">
            <Label className="sr-only" htmlFor="email">
              Email
            </Label>
            <Input
              id="email"
              placeholder="name@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading || disabled}
              {...register("email")}
            />
            {errors?.email && (
              <p className="px-1 text-xs text-red-600">
                {errors.email.message}
              </p>
            )}
          </div>
          <div className="grid gap-1">
            <Label className="sr-only" htmlFor="password">
              Password
            </Label>
            <Input
              id="password"
              placeholder="Enter your password"
              type="password"
              autoComplete="current-password"
              disabled={isLoading || disabled}
              {...register("password")}
            />
            {errors?.password && (
              <p className="px-1 text-xs text-red-600">
                {errors.password.message}
              </p>
            )}
          </div>
          <button className={cn(buttonVariants())} disabled={isLoading}>
            {isLoading && (
              <Icons.Spinner className="mr-2 h-4 w-4 animate-spin" />
            )}
            {isSignUp ? "Create Account" : "Sign In"}
          </button>
        </div>
      </form>
      <div className="text-center">
        <button
          type="button"
          className="text-sm text-muted-foreground hover:text-foreground"
          onClick={() => setIsSignUp(!isSignUp)}
          disabled={isLoading}
        >
          {isSignUp ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
        </button>
      </div>
    </div>
  );
}
