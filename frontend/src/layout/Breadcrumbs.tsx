import { BreadcrumbGroup } from "@cloudscape-design/components";
import { useLocation, useNavigate } from "react-router-dom";

const Breadcrumbs = () => {
  const navigate = useNavigate();

  function createBreadCrumbsFromPathname(pathname: string) {
    const items:{text: string, href: string}[]= [];
    const slicedPathname = pathname.slice(1);

    const text = slicedPathname.charAt(0).toUpperCase() + slicedPathname.slice(1);

    items.push({ text: 'Parliamentary Question Responder', href: "/home" });
    items.push({ text: text, href: "/" + pathname });
    
    return items;
  }

  const items = createBreadCrumbsFromPathname(useLocation().pathname);

  function handleFollow(event:any) {
    const href = "/" + event.detail.href.split("/").slice(2).join("/");
    if (event.detail.external === true || typeof href === "undefined") {
      return;
    }
    event.preventDefault();

    navigate(href);
  }

  return <BreadcrumbGroup items={items} onFollow={handleFollow} />;
}

export default Breadcrumbs;