"use client"
import { signOutServer } from "@/lib/actions/auth";
import { signOut, useSession } from "next-auth/react";
import { Button, buttonVariants } from "@/components/ui/button";
import Link from "next/link";

function SignOutButton() {

    const handleSignOut = () => {
        signOut().then(() => signOutServer())
    }

    const { data: session } = useSession()
    if (!session || session.user == null) {
        return <Link href="/" className={buttonVariants({ variant: "default" })}>Login</Link>
    }

    return (
        <Button onClick={handleSignOut} variant="destructive">Sign Out</Button>
    )
}

export default SignOutButton;