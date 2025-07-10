"use client";

import { useState, useRef } from "react";
import { flaskAPI, type BulkFinderResponse } from "~/lib/flask-api";
import { useFirebaseAuth } from "~/components/firebase-auth-provider";

import { Button } from "@saasfly/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@saasfly/ui/card";
import { Alert, AlertDescription } from "@saasfly/ui/alert";
import {
  Loader2,
  Upload,
  Download,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileSpreadsheet,
  Mail
} from "lucide-react";

export default function BulkFinderPage() {
  const { user, loading: authLoading } = useFirebaseAuth();
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<BulkFinderResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadLink, setDownloadLink] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      const response = await flaskAPI.bulkFindEmails(file);
      setResults(response.results);
      if (response.download_link) {
        setDownloadLink(response.download_link);
      }
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

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Bulk Email Finder</h1>
          <p className="text-lg text-muted-foreground mb-8">
            Authentication required to use bulk email finder
          </p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Sign In Required
            </CardTitle>
            <CardDescription>
              Please sign in to your account to use the bulk email finder feature.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Bulk email finder requires authentication to track usage and ensure fair usage limits.
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
        <h1 className="text-4xl font-bold mb-4">Bulk Email Finder</h1>
        <p className="text-lg text-muted-foreground">
          Upload a CSV or Excel file with <b>Full Name</b> and <b>Domain</b> columns (optional <b>Company</b>) to find and verify emails in bulk.
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
                Upload a CSV or Excel file with <b>Full Name</b> and <b>Domain</b> columns (optional <b>Company</b>).
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
                      Finding Emails...
                    </>
                  ) : (
                    "Find Emails"
                  )}
                </Button>
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </form>
            </CardContent>
          </Card>
        </div>
        {/* Results Section */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Results
              </CardTitle>
              <CardDescription>
                {results.length > 0 ? `${results.length} rows processed` : "Results will appear here after upload."}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {results.length > 0 ? (
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm border">
                      <thead>
                        <tr>
                          <th className="border px-2 py-1">Full Name</th>
                          <th className="border px-2 py-1">Company</th>
                          <th className="border px-2 py-1">Domain</th>
                          <th className="border px-2 py-1">Found Email</th>
                          <th className="border px-2 py-1">Valid</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.map((r, i) => (
                          <tr key={i}>
                            <td className="border px-2 py-1">{r.name}</td>
                            <td className="border px-2 py-1">{r.company || "-"}</td>
                            <td className="border px-2 py-1">{r.domain}</td>
                            <td className="border px-2 py-1">{r.emails && r.emails.length > 0 ? r.emails[0][0] : "Not Found"}</td>
                            <td className="border px-2 py-1 text-center">
                              {r.found ? (
                                <CheckCircle className="inline h-4 w-4 text-green-600" />
                              ) : (
                                <XCircle className="inline h-4 w-4 text-red-600" />
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {downloadLink && (
                    <Button variant="secondary" className="mt-4" onClick={handleDownload}>
                      <Download className="mr-2 h-4 w-4" />
                      Download Results
                    </Button>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No results yet.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 