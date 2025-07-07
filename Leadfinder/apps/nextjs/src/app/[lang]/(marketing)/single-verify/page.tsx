"use client";

import { useState } from "react";
import { flaskAPI, type SingleVerifyResponse } from "~/lib/flask-api";

import { Button } from "@saasfly/ui/button";
import { Input } from "@saasfly/ui/input";
import { Label } from "@saasfly/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@saasfly/ui/card";
import { Alert, AlertDescription } from "@saasfly/ui/alert";
import { Loader2, Mail, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function SingleVerifyPage() {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState<SingleVerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await flaskAPI.verifySingleEmail({ email });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Single Email Verification</h1>
        <p className="text-lg text-muted-foreground">
          Verify if an email address is valid and deliverable
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Verify Email Address
          </CardTitle>
          <CardDescription>
            Enter an email address to check if it's valid and can receive emails
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="john.doe@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Verifying Email...
                </>
              ) : (
                "Verify Email"
              )}
            </Button>
          </form>

          {error && (
            <Alert className="mt-4" variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <div className="mt-6 p-4 border rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-sm font-medium">Email Address</Label>
                  <p className="font-mono text-sm text-muted-foreground">{result.email}</p>
                </div>
                <div className="flex items-center gap-2">
                  {result.status ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm font-medium text-green-600">Valid</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-5 w-5 text-red-600" />
                      <span className="text-sm font-medium text-red-600">Invalid</span>
                    </>
                  )}
                </div>
              </div>
              
              <div className="mt-3">
                <Label className="text-sm font-medium">Status</Label>
                <p className="text-sm text-muted-foreground">
                  {result.status 
                    ? "This email address is valid and can receive emails."
                    : "This email address is invalid or cannot receive emails."
                  }
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="mt-8 text-center">
        <p className="text-sm text-muted-foreground">
          Need to verify multiple emails? Try our{" "}
          <a href="/bulk-verify" className="text-blue-600 hover:underline">
            Bulk Email Verification
          </a>{" "}
          tool.
        </p>
      </div>
    </div>
  );
} 