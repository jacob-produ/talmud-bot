import React from 'react';
import PropTypes from 'prop-types';

const SelectData = (props) => {
    return (
        <div style={{ display: 'flex', marginBottom: '5px' }}>
            <div style={{ marginLeft: '5px' }}>
                {props.titles.map((title, index) => <div key={index} style={{ marginTop: index > 0 && '5px' }}>{title}:</div>)}
            </div>
            {props.children}
        </div>
    )
}

SelectData.propTypes = {
    titles: PropTypes.arrayOf(PropTypes.string).isRequired,
    children: PropTypes.any.isRequired
}

export default SelectData;