import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from 'jwt-decode'
import { useNavigate } from "react-router-dom";
function LoginPage() {
    const navigate = useNavigate()
    return (
        <div className="flex flex-col gap-2 items-center">
            Login
            <GoogleLogin onSuccess={(res) => {
                console.log(res)
                console.log(jwtDecode(res.credential!))
                navigate('/d')
            }}
                onError={() => alert("Login Failed!")}
            />
        </div>
    );
}

export default LoginPage;