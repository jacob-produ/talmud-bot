import React from 'react';
import ContainerNavbar from './ContainerNavbar';
import ContainerHeader from './ContainerHeader';

interface Props {
    title: string,
    cartTo?: string,
    children: React.ReactNode,
    childrenClassName?: string,
    childrenStyle?: React.CSSProperties,
    goBack?: boolean
}

const Container: React.FC<Props> = (props) => {
    return (
        <div className='container' >
            <ContainerNavbar />
            <div className='container__body'>
                <ContainerHeader title={props.title} goBack={props.goBack} cartTo={props.cartTo} />
                <div className={props.childrenClassName} style={props.childrenStyle}>
                    {props.children}
                </div>
            </div>
        </div>
    )
}

export default Container;