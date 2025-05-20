import { AuthContextProps } from "react-oidc-context";
import cognitoConfig from "../config.json"

const signOutRedirect = () => {
    const clientId = cognitoConfig.client_id;
    const logoutUri = cognitoConfig.signOutConfig.logout_uri;
    const cognitoDomain = cognitoConfig.signOutConfig.cognitoDomain;
    window.location.href = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`;
};

export const signIn = (auth:AuthContextProps) => {
    auth.signinRedirect();
};

export const signOut = (auth:AuthContextProps) => {
    signOutRedirect();
    auth.removeUser();
}