import { auth } from "@/auth";
import SignInButton from "@/components/ui/auth/SignInButton";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await auth()
  if (session?.user) {
    redirect("/d")
  }
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <SignInButton />
    </div>
  );
}
