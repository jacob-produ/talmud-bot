import React, { useEffect } from 'react';
import { inject, observer } from 'mobx-react';
import { useHistory } from 'react-router-dom';
import Container from '../containers/Container';
import TopDetails from './TopDetails';
import Table from '../Table';
import { Spin } from "react-loading-io";
import '../../styles/student/StudentDetails.css';

const StudentProfile = (props) => {
    const history = useHistory();
    const { studentStore } = props.rootStore;

    useEffect(() => {
        if (sessionStorage.getItem('student_id')) {
            studentStore.fetchStudentById(sessionStorage.getItem('student_id'))
        }
        else {
            sessionStorage.setItem('route', '/finance-report');
            history.push('/finance-report');
        }

        return () => {
            studentStore.resetDetails();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const HandleSelectedTableTab = (e, tab, tableIndex, tableClass) => {
        document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
        e.currentTarget.classList.add('selectedTab');
        studentStore.setSelectedTableTab(tab);
    }

    const HandleEditStudent = () => {
        studentStore.fetchSaveStudentDetails();
    }

    return (
        <Container title='כרטיס תלמיד' goBack childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <TopDetails
                allowEdit={studentStore.tableData !== null}
                student={studentStore.studentDetails}
                balance={studentStore.studentBalanceDetails}
                branch={studentStore.branchDetails}
                coordinator={studentStore.coordinatorDetails}
                institutionBranchCoordinator={studentStore.institutionBranchCoordinator}
                trendCoordinator={studentStore.trendCoordinator}
                generalLists={studentStore.generalLists}
                onChange={(target, param, value, changeAll, index) => studentStore.changeSelectedData(target, param, value, changeAll, index)} />
            <div style={{ display: 'flex', width: 'fit-content', marginRight: '20px' }}>
                <input className='button' type='button' value='הדפס צק' style={{ padding: '0.2em 0.5em', margin: '0 5px' }} onClick={() => { }} />
                <input className='button' type='button' value='הדפס מסב' style={{ padding: '0.2em 0.5em', margin: '0 5px' }} onClick={() => { }} />
                <input className='button' type='button' value='שמירה' disabled={!studentStore.editStudent} style={{ padding: '0.2em 0.5em', margin: '0 5px' }} onClick={HandleEditStudent} />
                <input className='button' type='button' value='מחיקה' title={studentStore.studentDetails?.deleted && 'התלמיד כבר מחוק'} disabled={studentStore.studentDetails?.deleted} style={{ padding: '0.2em 0.5em', margin: '0 5px' }} onClick={() => studentStore.fetchDeleteStudent()} />
            </div>
            <Table header={studentStore.selectedTableTab === 'course_enrollments' ?
                ['תאריך סיום קורס', 'תאריך התחלה קורס', 'סוג קורס', 'מוסד - סניף', 'חלק ביום', 'שם מנחה', 'זכאות מינימלית', 'שיטת זכאות', 'רמת זכאות', 'תאריך סיום מנחה', 'תאריך התחלה מנחה'] :
                ['הוצאה', 'הכנסה', 'מסלול', 'מנחה קבוצה', 'מוסד', 'חודש']}
                data={studentStore.tableData || []}
                style={{ hight: '100%' }}
                tableStyle={{ width: '100%' }}>
                <div style={{ position: 'absolute', display: 'flex', left: '1em', top: '-2.4em' }}>
                    <div className='studentDetailsTableTab' onClick={e => HandleSelectedTableTab(e, 'student', 0, '.studentDetailsTableTab')}>מבחנים</div>
                    <div className='studentDetailsTableTab' onClick={e => HandleSelectedTableTab(e, 'course_enrollments', 0, '.studentDetailsTableTab')}>היסטוריית מסלולים</div>
                    <div className='studentDetailsTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'payments', 0, '.studentDetailsTableTab')}>תשלומים</div>
                </div>
                {!studentStore.tableData && <div className='studentDetailsTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
            </Table>
        </Container>
    )
}

export default inject('rootStore')(observer(StudentProfile));