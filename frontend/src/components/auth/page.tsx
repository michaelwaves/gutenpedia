import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from 'jwt-decode'
function LoginPage() {
    return (
        <div>
            Login
            <GoogleLogin onSuccess={(res) => {
                console.log(res)
                console.log(jwtDecode(res.credential!))
            }}
                onError={() => alert("Login Failed!")}
            />
        </div>
    );
}

export default LoginPage;