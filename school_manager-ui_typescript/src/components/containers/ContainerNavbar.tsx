import { useNavigate, useLocation } from 'react-router-dom';
import { Tabs, ITab } from './ContainerNavbarTabs';
import { GoPrimitiveDot } from "react-icons/go";

const ContainerNavbar = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const HandleChangePage = (tab: ITab) => {
        if (location.pathname === tab.location)
            navigate(tab.location, { replace: true });
        else {
            sessionStorage.setItem('route', tab.location);
            navigate(tab.location);
        }
    }

    return (
        <div className='container__navbar' >
            <h3 className='container__navbar__title' style={{ textAlign: 'center' }}>School Manager</h3>
            {Tabs.map(tab => <div key={tab.name} className='container__navbar__tab'
                data-selected={location.pathname.includes(tab.location)}
                data-under_tab={tab.underTab}
                onClick={() => HandleChangePage(tab)} >
                {tab.underTab && <GoPrimitiveDot size='0.8em' style={{ color: location.pathname.includes(tab.location) ? '#3BB2DC' : '', marginLeft: '3px' }} />}
                {tab.name}
            </div>)}
        </div>
    )
}

export default ContainerNavbar;