"use client";

import { useState, useRef, useEffect } from "react";
import { flaskAPI, type BulkVerifyResponse, type BulkVerifyUsage } from "~/lib/flask-api";
import { useFirebaseAuth } from "~/components/firebase-auth-provider";

import { Button } from "@saasfly/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@saasfly/ui/card";
import { Alert, AlertDescription } from "@saasfly/ui/alert";
import { 
  Loader2, 
  Mail, 
  Upload, 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  FileSpreadsheet,
  Info
} from "lucide-react";

export default function BulkVerifyPage() {
  const { user, loading: authLoading } = useFirebaseAuth();
  const [file, setFile] = useState<File | null>(null);
  const [usage, setUsage] = useState<BulkVerifyUsage | null>(null);
  const [results, setResults] = useState<BulkVerifyResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadLink, setDownloadLink] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load usage on component mount when user is authenticated
  useEffect(() => {
    if (user && !authLoading) {
      loadUsage();
    }
  }, [user, authLoading]);

  const loadUsage = async () => {
    try {
      const usageData = await flaskAPI.getBulkVerifyUsage();
      setUsage(usageData);
    } catch (err) {
      console.error("Failed to load usage:", err);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ];
      
      if (!validTypes.includes(selectedFile.type)) {
        setError("Please select a valid CSV or Excel file");
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError(null);
    setResults([]);
    setDownloadLink(null);

    try {
      const response = await flaskAPI.bulkVerifyEmails(file);
      setResults(response.results);
      if (response.download_link) {
        setDownloadLink(response.download_link);
      }
      
      // Reload usage after successful verification
      await loadUsage();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!downloadLink) return;
    
    try {
      const filename = downloadLink.split('/').pop();
      if (!filename) return;
      
      const blob = await flaskAPI.downloadFile(filename);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError("Failed to download file");
    }
  };

  const validEmails = results.filter(r => r.status).length;
  const invalidEmails = results.filter(r => !r.status).length;

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication required message
  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Bulk Email Verification</h1>
          <p className="text-lg text-muted-foreground mb-8">
            Authentication required to use bulk email verification
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Sign In Required
            </CardTitle>
            <CardDescription>
              Please sign in to your account to use the bulk email verification feature.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Bulk email verification requires authentication to track usage and ensure fair usage limits.
            </p>
            <Button className="w-full" onClick={() => window.location.href = '/login'}>
              Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Bulk Email Verification</h1>
        <p className="text-lg text-muted-foreground">
          Upload a CSV or Excel file with email addresses to verify them in bulk
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload File
              </CardTitle>
              <CardDescription>
                Upload a CSV or Excel file with an "Email" column
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full h-32 border-dashed"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <FileSpreadsheet className="h-8 w-8 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {file ? file.name : "Click to select file"}
                      </span>
                    </div>
                  </Button>
                </div>

                <Button type="submit" className="w-full" disabled={loading || !file}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Verifying Emails...
                    </>
                  ) : (
                    "Verify Emails"
                  )}
                </Button>
              </form>

              {error && (
                <Alert className="mt-4" variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Usage Information */}
          {usage && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Usage Limit
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Used</span>
                    <span>{usage.used_rows} / {usage.row_limit}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${(usage.used_rows / usage.row_limit) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    You can verify up to {usage.row_limit} emails per month
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Download Section */}
          {downloadLink && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Download Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button onClick={handleDownload} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Verified Emails
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          {results.length > 0 && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mail className="h-5 w-5" />
                    Verification Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{validEmails}</div>
                      <div className="text-sm text-muted-foreground">Valid Emails</div>
                    </div>
                    <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">{invalidEmails}</div>
                      <div className="text-sm text-muted-foreground">Invalid Emails</div>
                    </div>
                  </div>

                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {results.slice(0, 10).map((result, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-2 border rounded text-sm"
                      >
                        <span className="font-mono truncate">{result.email}</span>
                        <div className="flex items-center gap-1">
                          {result.status ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                        </div>
                      </div>
                    ))}
                    {results.length > 10 && (
                      <p className="text-sm text-muted-foreground text-center">
                        ... and {results.length - 10} more results
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-muted-foreground">
          Need to verify just one email? Try our{" "}
          <a href="/single-verify" className="text-blue-600 hover:underline">
            Single Email Verification
          </a>{" "}
          tool.
        </p>
      </div>
    </div>
  );
} 