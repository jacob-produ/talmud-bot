import React from 'react';
// import Store from '../../store';
import { observer } from 'mobx-react';
import Container from '../containers/Container';

interface Props {

}

const BankAccount: React.FC<Props> = () => {
    return (
        // childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        <Container title='חשבונות בנק - עובר ושב' >
        </Container>
    );
}

export default observer(BankAccount);