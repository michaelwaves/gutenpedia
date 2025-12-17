
import { signIn } from "@/auth"
import Image from "next/image"
import { Button } from "../ui/button";
import GoogleLogo from "@/public/google_logo.png";
function SignInButton() {
    return (
        <form
            action={async () => {
                "use server"
                await signIn("google", {
                    redirectTo: "/d"
                })
            }}
        >
            <Button type="submit" variant="outline">Sign in with Google  <Image src={GoogleLogo} alt="Google Logo" height={20} width={20} /></Button>
        </form>
    );
}

export default SignInButton;
