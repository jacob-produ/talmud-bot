import React from 'react';
import PropTypes from 'prop-types';

const DetailContainer = (props) => {
    return (
        <div style={{ position: 'relative', border: '1px solid black', width: '22%', height: '100%' }}>
            <div style={{ marginTop: '10px', marginRight: '3px', minWidth: 'fit-content' }}>
                {props.children}
            </div>
            <div style={{ position: 'absolute', border: '1px solid black', backgroundColor: '#fff', top: '-1em', ...props.titleStyle }}>{props.title}</div>
        </div>
    )
}

DetailContainer.propTypes = {
    children: PropTypes.any,
    title: PropTypes.string,
    titleStyle: PropTypes.any,
}

export default DetailContainer;