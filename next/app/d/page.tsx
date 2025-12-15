import { auth } from "@/auth";
import SignOutButton from "@/components/auth/SignOutButton";

async function DashboardPage() {
    const session = await auth()
    const user = session?.user
    return (
        <div className="w-full h-full py-4 px-8">
            <div className="flex flex-col gap-2 max-w-xl">
                <h1 className="text-2xl">Welcome {user?.name}</h1>
                <p>Explore your dashboard or sign out</p>
                <div className="w-40 mt-4">
                    <SignOutButton />
                </div>
            </div>
        </div>
    );
}

export default DashboardPage;