import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const TopDetails = (props) => {
    const { student, balance, branch, coordinator, allowEdit } = props;

    // #region new Change
    // eslint-disable-next-line no-unused-vars
    const [newStudent, setNewStudent] = useState(null);
    // eslint-disable-next-line no-unused-vars
    const [newBranch, setNewBranch] = useState(null);
    // eslint-disable-next-line no-unused-vars
    const [newCoordinator, setNewCoordinator] = useState(null);
    // #endregion

    // const [change, setChange] = useState(0);

    useEffect(() => {
        setNewStudent(student);
        setNewBranch(branch);
        setNewCoordinator(coordinator);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // #region Edit Student Details
    // const [studentName, setStudentName] = useState(false);
    const [studentFirstName, setStudentFirstName] = useState(false);
    const [studentLastName, setStudentLastName] = useState(false);
    const [studentID, setStudentID] = useState(false);
    const [studentIdType, setStudentIdType] = useState(false);
    const [studentPhone, setStudentPhone] = useState(false);
    const [studentAnotherPhone, setStudentAnotherPhone] = useState(false);
    const [studentCountry, setStudentCountry] = useState(false);
    const [studentAddress, setStudentAddress] = useState(false);
    const [studentBirthDate, setStudentBirthDate] = useState(false);
    // #endregion

    // #region Edit Course Details
    const [branchInstitution, setBranchInstitution] = useState(false);
    const [branchSymbol, setBranchSymbol] = useState(false);
    const [coordinatorName, setCoordinatorName] = useState(false);
    const [studentCourseType, setStudentCourseType] = useState(false);
    const [studentEligibilityLevel, setStudentEligibilityLevel] = useState(false);
    const [studentStartDate, setStudentStartDate] = useState(false);
    const [studentEndDate, setStudentEndDate] = useState(false);
    // #endregion

    // #region Edit Bank Details
    // const [studentBank, setStudentBank] = useState(false);
    const [studentBankBankNumber, setStudentBankBankNumber] = useState(false);
    const [studentBankBranchNumber, setStudentBankBranchNumber] = useState(false);
    const [studentBankAccountNumber, setStudentBankAccountNumber] = useState(false);
    // const [studentBankAnother, setStudentBankAnother] = useState(false);
    const [studentBankAnotherBankNumber, setStudentBankAnotherBankNumber] = useState(false);
    const [studentBankAnotherBranchNumber, setStudentBankAnotherBranchNumber] = useState(false);
    const [studentBankAnotherAccountNumber, setStudentBankAnotherAccountNumber] = useState(false);
    const [studentPaymentMethod, setStudentPaymentMethod] = useState(false);
    // #endregion

    const DetailContainer = (props) => {
        return <div style={{ position: 'relative', border: '1px solid black', width: '22%' }}>
            <div style={{ marginTop: '9px', marginBottom: '3px', marginRight: '3px' }}>
                {props.children}
            </div>
            <div style={{ position: 'absolute', border: '1px solid black', backgroundColor: '#fff', left: '-1em', top: '-1em', ...props.titleStyle }}>{props.title}</div>
        </div>
    }

    const HandleOnChange = (e, target, param, date, moreParam, changeAll, index) => {
        const value = date ? new Date(e.target.value).toISOString() : e.target.value;
        // const value = date ? e.target.value.split('-').reverse().join('/') : e.target.value;
        const splitParams = param.split('.');

        splitParams[0] === 'bank' && student.bank.length === 0 && setNewStudent(student[splitParams[0]] = new Array(2).fill({ bank_number: '', branch_number: '', account_number: '' }));

        target === 'student' && setNewStudent(changeAll ? changeAll : splitParams.length > 1 ?
            (index ? student[splitParams[0]][index - 1][splitParams[1]] = value : student[splitParams[0]][splitParams[1]] = value) :
            (index ? student[splitParams[0]][index - 1] = value : student[splitParams[0]] = value));
        target === 'branch' && setNewBranch(changeAll ? changeAll : splitParams.length > 1 ?
            (index ? branch[splitParams[0]][index - 1][splitParams[1]] = value : branch[splitParams[0]][splitParams[1]] = value) :
            (index ? branch[splitParams[0]][index - 1] = value : branch[splitParams[0]] = value));
        target === 'coordinator' && setNewCoordinator(changeAll ? changeAll : splitParams.length > 1 ?
            (index ? coordinator[splitParams[0]][index - 1][splitParams[1]] = value : coordinator[splitParams[0]][splitParams[1]] = value) :
            (index ? coordinator[splitParams[0]][index - 1] = value : coordinator[splitParams[0]] = value));

        props.onChange(target, splitParams, value, changeAll, index);
        moreParam && moreParam.map(change => props.onChange(change['target'], change['param'].split('.'),
            (date ? change['value'].split('-').reverse().join('/') : change['value'])));
    }

    // const HandleBankDetails = (index) => {
    //     return <div style={{ display: 'flex' }}>
    //         <input onClick={() => setChange(1)} autoFocus={change === 1} onBlur={() => setChange(0)}
    //             type='text' maxLength='5' placeholder='מספר בנק' value={(student.bank.length > 0 && student.bank[index].bank_number) || ''}
    //             onChange={e => HandleOnChange(e, 'student', 'bank.bank_number', null, null, null, index + 1)} />
    //         <input onClick={() => setChange(2)} autoFocus={change === 2} onBlur={() => setChange(0)}
    //             type='text' maxLength='5' placeholder='מספר סניף' value={(student.bank.length > 0 && student.bank[index].branch_number) || ''}
    //             onChange={e => HandleOnChange(e, 'student', 'bank.branch_number', null, null, null, index + 1)} />
    //         <input onClick={() => setChange(3)} autoFocus={change === 3} onBlur={() => setChange(0)}
    //             type='text' maxLength='15' placeholder='מספר חשבון' value={(student.bank.length > 0 && student.bank[index].account_number) || ''}
    //             onChange={e => HandleOnChange(e, 'student', 'bank.account_number', null, null, null, index + 1)} />
    //     </div>
    // }

    return (
        <div className='studentDetails'>
            <DetailContainer title='פרטים אישיים' titleStyle={{ left: '35%' }}>
                {/* <div className='studentDetailsData' onClick={() => allowEdit && setStudentName(true)} onBlur={() => setStudentName(false)}>
                    שם: {student && (studentName ? <div style={{ display: 'flex' }}>
                        <input onClick={() => setChange(1)} autoFocus={change === 1} onBlur={() => setChange(0)} type='text'
                            placeholder='פרטי' value={student.first_name || ''} onChange={e => HandleOnChange(e, 'student', 'first_name')} />
                        <input onClick={() => setChange(2)} autoFocus={change === 2} onBlur={() => setChange(0)} type='text'
                            placeholder='משפחה' value={student.last_name || ''} onChange={e => HandleOnChange(e, 'student', 'last_name')} />
                    </div> : `${student.first_name} ${student.last_name}`)}</div> */}
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentFirstName(true)} onBlur={() => setStudentFirstName(false)}>
                    שם פרטי: {student && (studentFirstName ? <input autoFocus type='text' value={student.first_name || ''}
                        onChange={e => HandleOnChange(e, 'student', 'first_name')} /> : student.first_name)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentLastName(true)} onBlur={() => setStudentLastName(false)}>
                    שם משפחה: {student && (studentLastName ? <input autoFocus type='text' value={student.last_name || ''}
                        onChange={e => HandleOnChange(e, 'student', 'last_name')} /> : student.last_name)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentID(true)} onBlur={() => setStudentID(false)}>
                    מספר זיהוי: {student && (studentID ? <input autoFocus type='text' value={student.identity || ''}
                        onChange={e => HandleOnChange(e, 'student', 'identity')} /> : student.identity)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentIdType(true)} onBlur={() => setStudentIdType(false)}>
                    סוג זיהוי: {student && (studentIdType ? <input autoFocus type='text' value={student.identity_type || ''}
                        onChange={e => HandleOnChange(e, 'student', 'identity_type')} /> : student.identity_type)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentPhone(true)} onBlur={() => setStudentPhone(false)}>
                    טלפון: {student && (studentPhone ? <input autoFocus type='text' value={student.main_phone_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'main_phone_number')} /> : student.main_phone_number)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentAnotherPhone(true)} onBlur={() => setStudentAnotherPhone(false)}>
                    טלפון נוסף: {student && (studentAnotherPhone ? <input autoFocus type='text' value={student.secondary_phone_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'secondary_phone_number')} /> : student.secondary_phone_number)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentCountry(true)} onBlur={() => setStudentCountry(false)}>
                    מדינה: {student && (studentCountry ? <input autoFocus type='text' value={student.state || ''}
                        onChange={e => HandleOnChange(e, 'student', 'state')} /> : student.state)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentAddress(true)} onBlur={() => setStudentAddress(false)}>
                    כתובת: {student && (studentAddress ? <input autoFocus type='text' value={student.address || ''}
                        onChange={e => HandleOnChange(e, 'student', 'address')} /> : student.address)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBirthDate(true)} onBlur={() => setStudentBirthDate(false)}>
                    תאריך לידה: {student && (studentBirthDate ? <input autoFocus type='date' value={(student.birth_date && student.birth_date.split('/').reverse().join('-')) || ''}
                        onChange={e => HandleOnChange(e, 'student', 'birth_date', true)} /> : student.birth_date?.slice(0, 10).split('-').reverse().join('/'))}</div>
            </DetailContainer>
            <DetailContainer title='פרטי מסלול' titleStyle={{ left: '35%' }}>
                <div className='studentDetailsData' onClick={() => allowEdit && setBranchInstitution(true)} onBlur={() => setBranchInstitution(false)}>
                    מוסד: {branch && branch.institution && (branchInstitution ? <select autoFocus value={branch.institution.identity || ''}
                        onChange={e => HandleOnChange(e, 'branch', 'institution.identity', false,
                            [{ target: 'branch', param: 'institution.name', value: props.institutionBranchCoordinator[e.target.value]['name'] },
                            { target: 'branch', param: 'symbol', value: Object.keys(props.institutionBranchCoordinator[e.target.value]['branches'])[0] }])}>
                        {props.institutionBranchCoordinator && Object.values(props.institutionBranchCoordinator).map(res =>
                            <option key={res.identity} value={res.identity}>{`${res.name} - ${res.identity}`}</option>)}
                    </select>
                        : `${branch.institution.name} ${branch.institution.identity}`)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setBranchSymbol(true)} onBlur={() => setBranchSymbol(false)}>
                    סניף: {branch && (branchSymbol ? <select autoFocus value={branch.symbol || ''}
                        onChange={e => HandleOnChange(e, 'branch', 'symbol')}>
                        {props.institutionBranchCoordinator && branch.institution && branch.institution.identity &&
                            Object.keys(props.institutionBranchCoordinator[branch.institution.identity]['branches']).map(res =>
                                <option key={res} value={res}>{res}</option>)}
                    </select> : branch.symbol)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setCoordinatorName(true)} onBlur={() => setCoordinatorName(false)}>
                    מנחה קבוצה: {coordinator && (coordinatorName ? <select autoFocus value={coordinator.id || ''}
                        onChange={e => HandleOnChange(e, 'coordinator', 'id', false,
                            [{ target: 'student', param: 'fk_trend_coordinator_id', value: parseInt(e.target.value) }],
                            props.trendCoordinator.find(res => res.id === parseInt(e.target.value)))} >
                        {props.trendCoordinator && props.trendCoordinator.map(res =>
                            <option key={res.id} value={res.id}>{res.name}</option>)} </select> : coordinator.name)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentCourseType(true)} onBlur={() => setStudentCourseType(false)}>
                    מסלול: {student && props.generalLists && (studentCourseType ? <select autoFocus value={student.course_type || ''}
                        onChange={e => HandleOnChange(e, 'student', 'course_type')} >
                        {props.generalLists.course_types && Object.keys(props.generalLists.course_types).map(res =>
                            <option key={res} value={res}>{props.generalLists.course_types[res]}</option>)}
                    </select> : props.generalLists.course_types[student.course_type])}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentEligibilityLevel(true)} onBlur={() => setStudentEligibilityLevel(false)}>
                    דרגת זכאות: {student && (studentEligibilityLevel ? <input autoFocus type='text' value={student.eligibility_level || ''}
                        onChange={e => HandleOnChange(e, 'student', 'eligibility_level')} /> : student.eligibility_level)}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentStartDate(true)} onBlur={() => setStudentStartDate(false)}>
                    תאריך הצטרפות: {student && (studentStartDate ? <input autoFocus type='date' value={(student.start_date && student.start_date.split('/').reverse().join('-')) || ''}
                        onChange={e => HandleOnChange(e, 'student', 'start_date', true)} /> : student.start_date?.slice(0, 10).split('-').reverse().join('/'))}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentEndDate(true)} onBlur={() => setStudentEndDate(false)}>
                    תאריך סיום: {student && (studentEndDate ? <input autoFocus type='date' value={(student.end_date && student.end_date.split('/').reverse().join('-')) || ''}
                        onChange={e => HandleOnChange(e, 'student', 'end_date', true)} /> : student.end_date?.slice(0, 10).split('-').reverse().join('/'))}</div>
            </DetailContainer>
            <DetailContainer title='פרטי בנק' titleStyle={{ left: '45%' }}>
                {/* <div className='studentDetailsData' onClick={() => allowEdit && setStudentBank(true)} onBlur={() => setStudentBank(false)}>
                    פרטי בנק: {student && student.bank && student.bank.length > 0 ?
                        (studentBank ? HandleBankDetails(0) :
                            `${student.bank[0].bank_number}, ${student.bank[0].branch_number}, ${student.bank[0].account_number}`) :
                        studentBank && HandleBankDetails(0)}</div> */}
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankBankNumber(true)} onBlur={() => setStudentBankBankNumber(false)}>
                    מספר בנק: {student && student.bank && student.bank.length > 0 ? (studentBankBankNumber ? <input autoFocus type='text' value={student.bank[0]?.bank_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.bank_number', null, null, null, 1)} /> : student.bank[0]?.bank_number) :
                        studentBankBankNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[0]?.bank_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.bank_number', null, null, null, 1)} />}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankBranchNumber(true)} onBlur={() => setStudentBankBranchNumber(false)}>
                    מספר סניף: {student && student.bank && student.bank.length > 0 ? (studentBankBranchNumber ? <input autoFocus type='text' value={student.bank[0]?.branch_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.branch_number', null, null, null, 1)} /> : student.bank[0]?.branch_number) :
                        studentBankBranchNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[0]?.branch_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.branch_number', null, null, null, 1)} />}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankAccountNumber(true)} onBlur={() => setStudentBankAccountNumber(false)}>
                    מספר חשבון: {student && student.bank && student.bank.length > 0 ? (studentBankAccountNumber ? <input autoFocus type='text' value={student.bank[0]?.account_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.account_number', null, null, null, 1)} /> : student.bank[0]?.account_number) :
                        studentBankAccountNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[0]?.account_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.account_number', null, null, null, 1)} />}</div>
                {/* <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankAnother(true)} onBlur={() => setStudentBankAnother(false)}>
                    בנק נוסף: {student && student.bank && student.bank.length > 1 ?
                        (studentBankAnother ? HandleBankDetails(1) :
                            `${student.bank[1].bank_number}, ${student.bank[1].branch_number}, ${student.bank[1].account_number}`) :
                        studentBankAnother && HandleBankDetails(1)}</div> */}
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankAnotherBankNumber(true)} onBlur={() => setStudentBankAnotherBankNumber(false)}>
                    מספר בנק נוסף: {student && student.bank && student.bank.length > 0 ? (studentBankAnotherBankNumber ? <input autoFocus type='text' value={student.bank[1]?.bank_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.bank_number', null, null, null, 2)} /> : student.bank[1]?.bank_number) :
                        studentBankAnotherBankNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[1]?.bank_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.bank_number', null, null, null, 2)} />}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankAnotherBranchNumber(true)} onBlur={() => setStudentBankAnotherBranchNumber(false)}>
                    מספר סניף נוסף: {student && student.bank && student.bank.length > 0 ? (studentBankAnotherBranchNumber ? <input autoFocus type='text' value={student.bank[1].branch_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.branch_number', null, null, null, 2)} /> : student.bank[1]?.branch_number) :
                        studentBankAnotherBranchNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[1]?.branch_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.branch_number', null, null, null, 2)} />}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentBankAnotherAccountNumber(true)} onBlur={() => setStudentBankAnotherAccountNumber(false)}>
                    מספר חשבון נוסף: {student && student.bank && student.bank.length > 0 ? (studentBankAnotherAccountNumber ? <input autoFocus type='text' value={student.bank[1]?.account_number || ''}
                        onChange={e => HandleOnChange(e, 'student', 'bank.account_number', null, null, null, 2)} /> : student.bank[1]?.account_number) :
                        studentBankAnotherAccountNumber && <input autoFocus type='text' value={(student.banks?.length > 0 && student.bank[1]?.account_number) || ''}
                            onChange={e => HandleOnChange(e, 'student', 'bank.account_number', null, null, null, 2)} />}</div>
                <div className='studentDetailsData' onClick={() => allowEdit && setStudentPaymentMethod(true)} onBlur={() => setStudentPaymentMethod(false)}>
                    שיטת תשלום מלגות: {student && props.generalLists && (studentPaymentMethod ? <select autoFocus value={student.payment_method || ''}
                        onChange={e => HandleOnChange(e, 'student', 'payment_method')} >
                        {props.generalLists.expense_payment_methods && Object.keys(props.generalLists.expense_payment_methods).map(res =>
                            <option key={res} value={res}>{props.generalLists.expense_payment_methods[res]}</option>)}
                    </select> : props.generalLists.expense_payment_methods[student.payment_method])}</div>
            </DetailContainer>
            <DetailContainer title='מאזנים' titleStyle={{ left: '40%' }}>
                <div>הכנסות שנתיות: {balance ? (balance.yearly_income >= 0 ? balance.yearly_income : `${Math.abs(balance.yearly_income)}-`) : 0}</div>
                <div>הוצאות שנתיות: {balance ? (balance.yearly_expense >= 0 ? balance.yearly_expense : `${Math.abs(balance.yearly_expense)}-`) : 0}</div>
                <div>מאזן חודשי: {balance ? (balance.monthly_balance >= 0 ? balance.monthly_balance : `${Math.abs(balance.monthly_balance)}-`) : 0}</div>
                <div>מאזן שנתי: {balance ? (balance.yearly_balance >= 0 ? balance.yearly_balance : `${Math.abs(balance.yearly_balance)}-`) : 0}</div>
                <div>מאזן מצטבר: { }</div>
                <div>מאזן קבוצה מצטבר: { }</div>
                <div>מאזן מוסד מצטבר: { }</div>
            </DetailContainer>
        </div>
    )
}

TopDetails.propTypes = {
    student: PropTypes.any,
    balance: PropTypes.any,
    branch: PropTypes.any,
    coordinator: PropTypes.any,
    onChange: PropTypes.func,
}

export default TopDetails;