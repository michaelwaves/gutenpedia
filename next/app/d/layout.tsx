import { auth } from "@/auth";
import { redirect } from "next/navigation";
import React from "react";

async function DashboardLayout({ children }: { children: React.ReactNode }) {
    const session = await auth()
    if (!session?.user) {
        redirect("/")
    }
    return (
        <div className="">
            {children}
        </div>
    );
}

export default DashboardLayout;