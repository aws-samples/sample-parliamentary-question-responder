import { Outlet } from 'react-router-dom'
import { AppLayout } from '@cloudscape-design/components';
import Navigation from './Navigation';
import { useState } from 'react';
import Breadcrumbs from './Breadcrumbs';
import TopNav from './TopNav';
import { AuthContextProps } from 'react-oidc-context';

const Layout = (props : {home: boolean; auth: AuthContextProps}) => {

    const [navigationOpen, setNavigationOpen] = useState(true);

    return (
        <>
            <TopNav auth={props.auth}/>
            <AppLayout
                navigation={<Navigation />}
                headerVariant="high-contrast"
                content={<Outlet />}
                breadcrumbs={!props.home && <Breadcrumbs/>}
                navigationOpen={navigationOpen}
                onNavigationChange={(event) => setNavigationOpen(event.detail.open)}
                toolsHide
                disableContentPaddings
                maxContentWidth={Number.MAX_VALUE}
            />
        </>
    )
}

export default Layout;