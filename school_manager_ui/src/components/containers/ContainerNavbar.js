import React from 'react';
import { useHistory } from 'react-router-dom';
import { GoPrimitiveDot } from "react-icons/go";
import '../../styles/containers/ContainerNavbar.css';

const ContainerNavbar = (props) => {
    const history = useHistory();

    const tabs = [
        {
            name: 'דו"ח פיננסי',
            location: '/finance-report',
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'סל תשלומים',
            location: '/finance-report/payments-basket',
            underTab: true,
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'מצבת תקבולים',
            location: '/periodic-reception',
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'סל תקבולים',
            location: '/periodic-reception/reception-basket',
            underTab: true,
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'מצבת תלמידים',
            location: '/students-reception',
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'סל רישום תלמידים',
            location: '/students-reception/students-basket',
            underTab: true,
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'דו"ח תנועות',
            location: '/transactions-report',
            // icon: require('../../assets/images/lab.png')
        },
        {
            name: 'ייבוא נתונים מקובץ',
            location: '/import-data',
            // icon: require('../../assets/images/heart.png')
        },
        {
            name: 'חשבונות בנק - עובר ושב',
            location: '/bank-account',
            // icon: require('../../assets/images/heart.png')
        },
        {
            name: 'הפקת טופס',
            location: '/student-form',
            // icon: require('../../assets/images/heart.png')
        },
        {
            name: 'תלמוד',
            location: '/talmud',
            // icon: require('../../assets/images/heart.png')
        }
    ]

    const HandleChangePage = (tab) => {
        if (history.location.pathname === tab.location)
            history.replace(tab.location)
        else {
            sessionStorage.setItem('route', tab.location);
            history.push(tab.location);
        }
    }

    return (tabs.map(tab => <div key={tab.name} className='navbarTab'>
        <div className='navbarTabName'
            style={{
                color: history.location.pathname.includes(tab.location) && '#3BB2DC', marginRight: tab.underTab && '10px',
                minWidth: tab.underTab && '0'
            }}
            onClick={() => HandleChangePage(tab)} >
            {tab.underTab && <GoPrimitiveDot size='0.8em' style={{ color: history.location.pathname.includes(tab.location) && '#3BB2DC', marginLeft: '3px' }} />}
            {/* <img src={tab.icon} alt='' className={`navbarTabNameIcon ${history.location.pathname.includes(tab.location) && 'selectedNavbarTab'}`} /> */}
            {tab.name}
        </div>
    </div>)
    )
}

export default ContainerNavbar;