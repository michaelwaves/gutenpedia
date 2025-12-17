"use server"

import { signOut } from "@/auth"

export async function signOutServer() {
    await signOut()
}