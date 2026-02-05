import React from 'react';
// import Store from '../../store';
import { observer } from 'mobx-react';
import Container from '../../containers/Container';

interface Props {

}

const ReceptionBasket: React.FC<Props> = () => {
    return (
        // childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        <Container title='סל תקבולים' goBack >
        </Container>
    );
}

export default observer(ReceptionBasket);