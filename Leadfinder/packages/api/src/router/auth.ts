import { unstable_noStore as noStore } from "next/cache";

import { db } from "@saasfly/db";

import { createTRPCRouter, procedure } from "../trpc";

export const authRouter = createTRPCRouter({
  // TODO: Restore protectedProcedure and real user lookup after Firebase Auth integration
  mySubscription: procedure.query(async () => {
    noStore();
    // Return a mock subscription for now
    return {
      plan: "free",
      endsAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
    };
  }),
});
