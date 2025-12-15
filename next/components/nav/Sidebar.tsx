"use client"
import { ArrowLeftFromLine, ArrowRightFromLine, Database, Home } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export const routes = [
    {
        title: "Home",
        href: '/d',
        icon: <Home className="w-6 h-6" />
    },
    {
        title: "Datasets",
        href: "/d/datasets",
        icon: <Database className="w-6 h-6" />
    }
]

function Sidebar() {
    const [open, setOpen] = useState(false)
    return (
        <nav className={`flex flex-col justify-between h-screen max-w-[200px] bg-gray-100 animate transition-all ${open ? "w-md" : "w-12"}`}>
            <div>
                <div className="p-4">
                    <h1 className="text-2xl">{open && "Gutenpedia"}</h1>
                </div>
                <div>
                    {routes.map((route: Omit<SidebarLinkProps, "open">, index: number) => <SidebarLink title={route.title} href={route.href} icon={route.icon} key={index} open={open} />)}
                </div>
            </div>
            <div onClick={() => setOpen(!open)} className="hover:cursor-pointer flex flex-row w-full p-4 gap-2">
                {open ? <ArrowLeftFromLine /> : <ArrowRightFromLine />}{open && "Collapse"}
            </div>
        </nav>
    );
}

export default Sidebar;


type SidebarLinkProps = {
    title?: string
    href: string
    icon: React.ReactNode
    open: boolean
}
function SidebarLink({ title, href, icon, open }: SidebarLinkProps) {
    const path = usePathname()
    const active = path == href
    return (
        <Link href={href} className={`text-gray-800 flex flex-row w-full px-4 py-2 gap-2 text-sm leading-tight items-center rounded-sm ${active ? "font-semibold bg-gray-300" : ""}`}>{icon}{open && title}</Link>
    )

}