import { NextRequest, NextResponse } from "next/server";
import { db, SubscriptionPlan } from "@saasfly/db";

export async function POST(req: NextRequest) {
  try {
    const { uid, name, email } = await req.json();
    console.log("[user-sync] Incoming:", { uid, name, email });
    
    if (!uid) {
      console.error("[user-sync] Missing uid");
      return NextResponse.json({ success: false, error: "Missing uid" }, { status: 400 });
    }

    // Check if customer exists
    const existing = await db
      .selectFrom("Customer")
      .selectAll()
      .where("authUserId", "=", uid)
      .executeTakeFirst();
    console.log("[user-sync] Existing customer:", existing);

    if (existing) {
      // Update name if changed
      await db
        .updateTable("Customer")
        .set({ name: name || existing.name })
        .where("authUserId", "=", uid)
        .execute();
      console.log("[user-sync] Updated customer", uid);
    } else {
      // Insert new customer
      await db
        .insertInto("Customer")
        .values({ 
          authUserId: uid, 
          name: name || email?.split('@')[0] || 'User', 
          plan: SubscriptionPlan.FREE 
        })
        .executeTakeFirst();
      console.log("[user-sync] Inserted new customer", uid);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[user-sync] Error:", error);
    return NextResponse.json({ success: false, error: error?.toString() });
  }
} 