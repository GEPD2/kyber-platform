"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { isLoggedIn } from "./api";

/** Redirects to /login/ when no access token is stored. Returns true once allowed. */
export function useAuthGuard(): boolean {
  const router = useRouter();
  const [ok, setOk] = useState(false);
  useEffect(() => {
    if (isLoggedIn()) setOk(true);
    else router.replace("/login/");
  }, [router]);
  return ok;
}
