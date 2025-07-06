import "server-only";

import { cookies } from "next/headers";
import { createTRPCProxyClient, loggerLink, TRPCClientError } from "@trpc/client";

import { AppRouter } from "@saasfly/api";

import { transformer } from "./shared";
import { observable } from "@trpc/server/observable";
import { callProcedure } from "@trpc/server";
import { TRPCErrorResponse } from "@trpc/server/rpc";
import { cache } from "react";
import { appRouter } from "../../../../packages/api/src/root";

export const createTRPCContext = async (opts: {
  headers: Headers;
}) => {
  // Try to extract user ID from Authorization header (Firebase token)
  let userId: string | null = null;
  const authHeader = opts.headers.get("authorization");
  
  if (authHeader && authHeader.startsWith("Bearer ")) {
    const token = authHeader.substring(7);
    try {
      // TODO: Verify Firebase token on server side
      // For now, we'll use a simple approach - you can implement proper token verification later
      // This is a placeholder - in production, you should verify the Firebase token
      userId = "firebase-user-id"; // Placeholder
    } catch (error) {
      console.error("Failed to verify Firebase token:", error);
    }
  }

  return {
    userId,
    ...opts,
  };
};

/**
 * This wraps the `createTRPCContext` helper and provides the required context for the tRPC API when
 * handling a tRPC call from a React Server Component.
 */
const createContext = cache(async () => {
  return createTRPCContext({
    headers: new Headers({
      cookie: cookies().toString(),
      "x-trpc-source": "rsc",
    }),
  });
});

export const trpc = createTRPCProxyClient<AppRouter>({
  transformer,
  links: [
    loggerLink({
      enabled: (op) =>
        process.env.NODE_ENV === "development" ||
        (op.direction === "down" && op.result instanceof Error),
    }),
    /**
     * Custom RSC link that lets us invoke procedures without using http requests. Since Server
     * Components always run on the server, we can just call the procedure as a function.
     */
    () =>
      ({op}) =>
        observable((observer) => {
          createContext()
            .then((ctx) => {
              return callProcedure({
                procedures: appRouter._def.procedures,
                path: op.path,
                rawInput: op.input,
                ctx,
                type: op.type,
              });
            })
            .then((data) => {
              observer.next({result: {data}});
              observer.complete();
            })
            .catch((cause: TRPCErrorResponse) => {
              observer.error(TRPCClientError.from(cause));
            });
        }),
  ],
});
export {type RouterInputs, type RouterOutputs} from "@saasfly/api";
