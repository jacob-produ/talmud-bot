import React from 'react';
// import Store from '../../store';
import { observer } from 'mobx-react';
import Container from '../containers/Container';

interface Props {

}

const TransactionsReport: React.FC<Props> = () => {
    return (
        // childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        <Container title='דוח תנועות' >
        </Container>
    );
}

export default observer(TransactionsReport);