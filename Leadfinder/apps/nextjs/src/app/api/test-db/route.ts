import { NextResponse } from "next/server";
import { db } from "@saasfly/db";

export async function GET() {
  try {
    // Test database connection by counting customers
    const customerCount = await db
      .selectFrom("Customer")
      .select(db.fn.count("id").as("count"))
      .executeTakeFirst();
    
    console.log("[test-db] Customer count:", customerCount);
    
    return NextResponse.json({ 
      success: true, 
      message: "Database connection successful",
      customerCount: customerCount?.count || 0
    });
  } catch (error: any) {
    console.error("[test-db] Database connection error:", error);
    return NextResponse.json({ 
      success: false, 
      error: error?.message || "Database connection failed" 
    }, { status: 500 });
  }
} 