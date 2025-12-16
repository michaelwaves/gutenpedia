import { auth } from "@/auth";
import Sidebar from "@/components/nav/Sidebar";
import { redirect } from "next/navigation";
import React from "react";

async function DashboardLayout({ children }: { children: React.ReactNode }) {
    const session = await auth()
    if (!session?.user) {
        redirect("/")
    }
    return (
        <div className="flex flex-row gap-2">
            <Sidebar />
            <div className="max-h-screen overflow-y-scroll w-full">
                {children}
            </div>
        </div>
    );
}

export default DashboardLayout;