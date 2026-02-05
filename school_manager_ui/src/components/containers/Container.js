import React from 'react';
import PropTypes from 'prop-types';
import ContainerHeader from './ContainerHeader';
import ContainerNavbar from './ContainerNavbar';
import '../../styles/containers/Container.css';

const Container = (props) => {
    return (
        <div id='containerPage' className='containerPage disableTextSelectionHighlighting' >
            <div style={{ display: 'flex', direction: 'rtl' }}>
                <div style={{ height: '100vh', minHeight: '100%', backgroundColor: '#c5c5c5' }} >
                    <h3 style={{ textAlign: 'center' }}>School Manager</h3>
                    <ContainerNavbar />
                </div>
                <div style={{ width: '100%', marginBottom: '10px' }}>
                    <ContainerHeader title={props.title} goBack={props.goBack} />
                    {/* showCart={props.showCart} */}
                    <div style={props.childrenStyle}>
                        {props.children}
                    </div>
                </div>
            </div>
        </div>
    )
}

Container.propTypes = {
    title: PropTypes.string.isRequired,
    // showCart: PropTypes.bool,
    children: PropTypes.any.isRequired,
    childrenStyle: PropTypes.any,
    goBack: PropTypes.bool,
}

export default Container;