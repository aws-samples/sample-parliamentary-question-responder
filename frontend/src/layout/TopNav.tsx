import { TopNavigation } from "@cloudscape-design/components";
import { signOut } from "../auth/auth";
import { AuthContextProps } from "react-oidc-context";

const TopNav = (props: {auth: AuthContextProps}) => {

    const auth = props.auth;

    return (
        <TopNavigation
            identity={{
                title: "Parliamentary Question Responder",
                href: "/",
            }}
            utilities={[
                {
                    type: "menu-dropdown",
                    text: auth.user?.profile.email,
                    iconName: "user-profile",
                    items: [{
                        id: "signout",
                        text: "Sign Out",
                    }],
                    onItemClick: () => signOut(auth)
                }
            ]}
            i18nStrings={{
                overflowMenuTriggerText: "More",
                overflowMenuTitleText: "All",
            }}
        />
    )
    
}

export default TopNav;