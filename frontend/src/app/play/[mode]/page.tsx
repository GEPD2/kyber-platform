import { notFound } from "next/navigation";
import { PlayClient } from "@/components/PlayClient";
import { MODES, isMode } from "@/lib/types";

export const dynamicParams = false;

export function generateStaticParams() {
  return MODES.map((mode) => ({ mode }));
}

export default async function PlayPage({ params }: { params: Promise<{ mode: string }> }) {
  const { mode } = await params;
  if (!isMode(mode)) notFound();
  return <PlayClient mode={mode} />;
}
