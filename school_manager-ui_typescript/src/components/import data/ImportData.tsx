import React from 'react';
// import Store from '../../store';
import { observer } from 'mobx-react';
import Container from '../containers/Container';

interface Props {

}

const ImportData: React.FC<Props> = () => {
    return (
        <Container title='ייבוא נתונים מקובץ - גרסת פיתוח בלבד' >
        </Container>
    );
}

export default observer(ImportData);