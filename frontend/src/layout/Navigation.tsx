import { SideNavigation } from "@cloudscape-design/components";
import { useLocation, useNavigate } from "react-router-dom";

const Navigation = () => {

    const navigate = useNavigate();
    const location = useLocation()

    return (
        <SideNavigation 
            activeHref={location.pathname}
            onFollow={event => {
                if (!event.detail.external) {
                  event.preventDefault();
                  const href = event.detail.href
                  navigate(href)
                }
            }}
            items={[
                { 
                    type: "section-group", 
                    title: "Parliamentary Question Responder", 
                    items: [
                        { type: "link", text: "Find similar questions", href: "/similar" },
                        { type: "link", text: "Chat", href: "/suggest" },
                    ]
                }
            ]}
        />
    )
}

export default Navigation;