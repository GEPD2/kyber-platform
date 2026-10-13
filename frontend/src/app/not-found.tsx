import Link from "next/link";

export default function NotFound() {
  return (
    <div className="state">
      <p>404</p>
      <Link href="/" className="btn">ML-KEM Lab</Link>
    </div>
  );
}
