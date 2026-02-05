import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaShoppingCart } from 'react-icons/fa';
import { MdArrowBack } from 'react-icons/md';

interface Props {
    title: string,
    cartTo?: string,
    goBack?: boolean
}

const ContainerHeader: React.FC<Props> = (props) => {
    const navigate = useNavigate();
    const location = useLocation();

    const HandleGoBack = () => {
        const back_location = location.pathname.split('/')[1];
        sessionStorage.setItem('reload', 'true');
        sessionStorage.setItem('route', `/${back_location}`);
        navigate(back_location);
    }

    const HandleClickCart = () => {
        sessionStorage.setItem('route', props.cartTo || '');
        navigate(props.cartTo || '')
    }

    return (
        <div className='container__header'>
            {props.goBack && <div className='container__header__go_back' onClick={HandleGoBack} >
                חזור
                <MdArrowBack size='1.5em' className='container__header__go_back__icon' />
            </div>}
            <div className='container__header__title' >
                {props.title}
            </div>
            {props.cartTo && <div className='container__header__cart' >
                <FaShoppingCart size='2em' onClick={HandleClickCart} />
            </div>}
            {/* {!location.pathname.includes('payments-basket') && <div className='container__header__cart' >
                 <FaShoppingCart size='2em' onClick={HandleClickCart} />
             </div>} */}
        </div>
    )
}

export default ContainerHeader;