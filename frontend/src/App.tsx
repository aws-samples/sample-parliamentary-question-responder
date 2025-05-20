import { useAuth } from "react-oidc-context";
import AppRoutes from "./routing/AppRoutes";
import { signIn } from "./auth/auth";
import LandingPage from "./pages/LandingPage/LandingPage";
import { Button } from "@cloudscape-design/components";


const App = () => {
    const auth = useAuth();

    if (auth.isAuthenticated) return <AppRoutes auth={auth}/>

    if (auth.isLoading) return <br />

    return (
        <LandingPage 
            button={<Button variant="primary" onClick={() => signIn(auth)}>Sign In</Button>}
        />
    )

}

export default App;