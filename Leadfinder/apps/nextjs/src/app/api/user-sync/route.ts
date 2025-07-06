import { NextRequest, NextResponse } from "next/server";
import { db, SubscriptionPlan } from "@saasfly/db";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log("[user-sync] Full request body:", body);
    
    const { uid, name, email } = body;
    console.log("[user-sync] Extracted data:", { uid, name, email });
    
    if (!uid) {
      console.error("[user-sync] Missing uid in request");
      return NextResponse.json({ success: false, error: "Missing uid" }, { status: 400 });
    }

    // Check if customer exists
    const existing = await db
      .selectFrom("Customer")
      .selectAll()
      .where("authUserId", "=", uid)
      .executeTakeFirst();
    console.log("[user-sync] Existing customer query result:", existing);

    if (existing) {
      // Update name if changed
      const updateResult = await db
        .updateTable("Customer")
        .set({ 
          name: name || existing.name,
          updatedAt: new Date()
        })
        .where("authUserId", "=", uid)
        .execute();
      console.log("[user-sync] Updated customer", uid, "result:", updateResult);
    } else {
      // Insert new customer
      const insertResult = await db
        .insertInto("Customer")
        .values({ 
          authUserId: uid, 
          name: name || email?.split('@')[0] || 'User', 
          plan: SubscriptionPlan.FREE,
          createdAt: new Date(),
          updatedAt: new Date()
        })
        .executeTakeFirst();
      console.log("[user-sync] Inserted new customer", uid, "result:", insertResult);
    }

    // Verify the operation by fetching the customer
    const verification = await db
      .selectFrom("Customer")
      .selectAll()
      .where("authUserId", "=", uid)
      .executeTakeFirst();
    console.log("[user-sync] Verification query result:", verification);

    return NextResponse.json({ success: true, customer: verification });
  } catch (error: any) {
    console.error("[user-sync] Error details:", {
      message: error?.message,
      stack: error?.stack,
      name: error?.name
    });
    return NextResponse.json({ 
      success: false, 
      error: error?.toString(),
      details: error?.message 
    }, { status: 500 });
  }
} 