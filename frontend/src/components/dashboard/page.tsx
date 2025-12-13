import { googleLogout } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import { Button } from "../ui/button";

function DashboardPage() {
    const navigate = useNavigate()
    function handleLogout() {
        console.log("logged out!")
        googleLogout()
        navigate("/")
    }
    return (
        <div className="flex flex-col gap-2 items-center">
            Dashboard
            <Button variant={"destructive"}
                onClick={handleLogout}
                className="bg-red-500"
            > Log Out </Button>
        </div>
    );
}

export default DashboardPage;