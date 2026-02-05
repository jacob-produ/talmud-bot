import React from 'react';

interface Props {
    headers: string[]
}

const Header: React.FC<Props> = ({ headers }) => {
    return (
        <thead style={{ backgroundColor: '#c5c5c5' }}>
            <tr>
                {headers.map((head) => <th key={head}
                    style={{
                        position: 'sticky', top: '-1px', border: '1px solid black', backgroundColor: '#c5c5c5',
                        boxShadow: 'inset 0px 0.5px 0px black, inset 0px -0.5px 0px black'
                    }}>
                    <div style={{ margin: '5px' }}>{head}</div>
                </th>)}
            </tr>
        </thead>
    );
}

export default Header;