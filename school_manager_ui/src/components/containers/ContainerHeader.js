import React from 'react';
import PropTypes from 'prop-types';
import { useHistory } from 'react-router-dom';
import { FaShoppingCart } from 'react-icons/fa';
import { MdArrowBack } from 'react-icons/md';
import '../../styles/containers/ContainerHeader.css';

const ContainerHeader = (props) => {
    const history = useHistory();

    const HandleGoBack = () => {
        const location = history.location.pathname.split('/')[1];
        sessionStorage.setItem('reload', 'true');
        sessionStorage.setItem('route', `/${location}`);
        history.push(location);
    }

    const HandleClickCart = () => {
        sessionStorage.setItem('route', '/finance-report/payments-basket');
        history.push('/finance-report/payments-basket')
    }

    return (
        <div className='containerHeader'>
            {props.goBack && <div className='containerHeaderGoBack' onClick={HandleGoBack} >
                חזור
                <MdArrowBack size='1.5em' style={{ marginRight: '5px' }} />
            </div>}
            <div className='containerHeaderTitle' >
                {props.title}
            </div>
            {/* {props.showCart &&  */}
            {!history.location.pathname.includes('payments-basket') && <div className='containerHeaderCart' >
                <FaShoppingCart size='2em' onClick={HandleClickCart} />
            </div>}
        </div>
    )
}

ContainerHeader.propTypes = {
    title: PropTypes.string.isRequired,
    // showCart: PropTypes.bool,
    goBack: PropTypes.bool,
}

export default ContainerHeader;