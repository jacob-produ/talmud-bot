import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { FiCheckSquare, FiMinusSquare, FiTrash2, FiPlusSquare } from 'react-icons/fi';
import '../styles/Table.css';

const Table = (props) => {
    const [edit, setEdit] = useState(-1);
    const [editText, setEditText] = useState('');
    const [editTextTitle, setEditTextTitle] = useState('');
    const [newData, setNewData] = useState({});
    const [title, setTitle] = useState('');
    const [inputType, setInputType] = useState('');

    let incomeSum = 0;
    let expanseSum = 0;
    let balanceSum = 0;
    let balanceTotalSum = 0;
    let cashSum = 0;
    let commitmentSum = 0;
    let flowSum = 0;
    let monthlyFlowSum = 0;
    let lineOfCreditSum = 0;
    let loanSum = 0;
    let transactionAmountSum = 0;
    let expenseSum = 0;
    let expenseTotalSum = 0;
    let periodicSum = 0;
    let periodicTotalSum = 0;
    let totalChargedAmountSum = 0;

    const tableRef = useRef(null);

    const regNumber = /^\d+$/;

    useEffect(() => {
        props.tableHeight && tableRef.current && props.tableHeight(tableRef.current.scrollHeight);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [props.data])

    const ShowWithMinus = (item, data) => {
        return item && data && !isNaN(data) ? (data.toString().includes('-') ? `${Math.abs(data % 1 !== 0 ? data.toFixed(2) : data)}-` :
            `${Math.abs(data % 1 !== 0 ? data.toFixed(2) : data)}`) : ''
        // item ? (data < 0 ? `${Math.abs(data).toFixed(2)}-` : `${data}`) : '';
    }

    const convertIsoDate = (date) => {
        return date && new Date(date).toISOString().slice(0, 10).split('-').reverse().join('/');
    }

    const HandleTableData = (title, item, index) => {
        switch (title) {
            case 'מזהה':
                return <div style={{ whiteSpace: 'nowrap' }}>{item.identity}</div>;
            case 'שם':
                return item.name;
            case 'שם מלא':
                return item.full_name;
            case 'הכנסות':
                item && (incomeSum += parseFloat(item.income_sum));
                return ShowWithMinus(item, item?.income_sum);
            case 'הוצאות':
                item && (expanseSum += parseFloat(item.expense_sum));
                return ShowWithMinus(item, item?.expense_sum);
            case 'יתרה':
                item && (balanceSum += parseFloat(item.balance));
                return ShowWithMinus(item, item?.balance);
            case 'יתרה כוללת':
                item && (balanceTotalSum += parseFloat(item.balance_total));
                return item ? ShowWithMinus(item, item?.balance_total) : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'סמן להדפסה':
            case 'סמן לשחזור':
            case 'סמן לתשלום':
                return <div>
                    <input disabled={(title === 'סמן לשחזור' && (item?.amount >= 0 || item?.payment_status === 'טיוטה' || item?.payment_status === 'נפרע')) ||
                        (title === 'סמן לתשלום' && item.deleted)}
                        title={(title === 'סמן לשחזור' && (item?.deleted ? 'התלמיד כבר מחוק' : item?.amount >= 0 ? 'ניתן לשחזר רק הוצאות' :
                            (item?.payment_status === 'טיוטה' || item?.payment_status === 'נפרע') ? `לא ניתן לשחזר הוצאות עם סטטוס ${item?.payment_status}` : '')) ||
                            (title === 'סמן לתשלום' && item.deleted && 'התלמיד כבר מחוק') || ''}
                        type='checkbox' checked={item ? (props.tableCheckbox ? props.tableCheckbox[index].checked : item.is_printable) : false}
                        style={{
                            visibility: (!item || props.rightTable) && 'hidden', position: (item && props.rightTable) && 'absolute',
                            cursor: 'pointer'
                        }} onChange={e => props.changeCheckbox(e.target.checked, index, item)} />
                    {item && props.rightTable && <div style={{ display: 'flex', justifyContent: 'space-evenly' }}>
                        <FiMinusSquare size='1em' style={{ cursor: 'pointer' }} onClick={() => props.changeCheckbox(false, index, item)} />
                        <FiCheckSquare size='1em' style={{ cursor: 'pointer', color: item.all_selected && '#3BB2DC' }} onClick={() => props.changeCheckbox(true, index, item)} />
                    </div>}
                </div>;
            case 'הוצאה':
                return ShowWithMinus(item, item?.expense_amount);
            case 'הכנסה':
                return ShowWithMinus(item, item?.income_amount);
            case 'מסלול':
                return item.course_type;
            case 'מנחה קבוצה':
                return item.coordinator_name;
            case 'מוסד':
                return item.institution_name;
            case 'חודש':
                return item.date;
            case 'מספר חשבון':
                return item ? item.account_number : <div style={{ visibility: 'hidden' }}>0</div>;
            case 'מסגרת':
                item && (lineOfCreditSum += parseFloat(item.line_of_credit));
                return ShowWithMinus(item, item?.line_of_credit); //item ? (item.line_of_credit < 0 ? `${Math.abs(item.line_of_credit)}-` : item.line_of_credit) : '';
            case 'הלוואות':
                item && (loanSum += parseFloat(item.loan));
                return ShowWithMinus(item, item?.loan); //item ? (item.loan < 0 ? `${Math.abs(item.loan)}-` : item.loan) : '';
            case 'התחייבויות':
                item && (commitmentSum += parseFloat(item.commitment));
                return ShowWithMinus(item, item?.commitment); //item ? (item.commitment < 0 ? `${Math.abs(item.commitment)}-` : item.commitment) : '';
            case 'נזיל':
                item && (cashSum += parseFloat(item.cash));
                return ShowWithMinus(item, item?.cash); //item ? (item.cash < 0 ? `${Math.abs(item.cash)}-` : item.cash) : '';
            case 'תזרים':
                item && (flowSum += parseFloat(item.flow));
                return ShowWithMinus(item, item?.flow); //item ? (item.flow < 0 ? `${Math.abs(item.flow)}-` : item.flow) : '';
            case 'תזרים חודשי':
                item && (monthlyFlowSum += parseFloat(item.flow));
                return ShowWithMinus(item, item?.monthly_flow); //item ? (item.flow < 0 ? `${Math.abs(item.flow)}-` : item.flow) : '';
            case 'תאריך':
            case 'תאריך תנועה':
            case 'תאריך הדפסה':
                const date = title === 'תאריך' ? item.date : title === 'תאריך תנועה' ? item.transaction_date : item?.printing_date;
                return convertIsoDate(date);
            case 'יום ערך':
                return convertIsoDate(item.value_date);
            case 'סכום':
                if (item?.amount || item?.amount?.toString() === '-0' || item?.amount?.toString() === '0') {
                    transactionAmountSum += parseFloat(item.amount);
                    const amount = ShowWithMinus(item, item.amount)
                    return <div style={{ color: amount.includes('-') ? 'red' : 'green' }}>{amount}</div>;
                }
                if (item && props.allowEdit) {
                    // onBlur={e => { item.expense_sum !== e.target.value && props.changeSum(editText); setEdit(''); }}
                    transactionAmountSum += parseFloat(item.expense_sum);
                    return <div onClick={() => { setEdit(index); setEditTextTitle(title); setEditText(item.expense_sum); }}
                        style={{ cursor: 'text', border: item.show_error && (!item.expense_sum || item.expense_sum === 0) && '1px solid red' }} >
                        {edit === index && editTextTitle === title ? <input type='text' autoFocus value={editText}
                            style={{ width: '85%', fontSize: '1em' }} onChange={e => regNumber.test(e.target.value) && setEditText(e.target.value)}
                            onBlur={e => { item.expense_sum !== e.target.value && props.changeSum(editText, item, index); setEdit(''); }} /> :
                            ShowWithMinus(item, item?.expense_sum)}</div>;
                }
                item && (transactionAmountSum += parseFloat(item?.transaction_amount));
                return ShowWithMinus(item, item?.transaction_amount); //item ? (item.transaction_amount < 0 ? `${Math.abs(item.transaction_amount)}-` : item.transaction_amount) : '';
            case 'אסמכתה':
                return item.reference_number;
            case 'בצע קישור':
                return <FiPlusSquare size='1em' style={{ cursor: 'pointer', visibility: !item && 'hidden' }} onClick={() => props.makeLink(item)} />
            case 'צורת תשלום':
                return item && <select value={item.payment_method || item.method} style={{ borderColor: ((item.show_error && !item.payment_method) || (item.show_error && !item.method)) && 'red', fontSize: '1em', width: '100%', minWidth: '60px' }}
                    onChange={e => e.target.value !== '' && props.changePaymentMethod(e.target.value, item, index)} >
                    <option value='' hidden>בחר</option>
                    {props.paymentMethods && Object.keys(props.paymentMethods).map(res =>
                        <option key={res} value={props.paymentMethods[res]}>{props.paymentMethods[res]}</option>)}
                </select>
            case 'סכום לתשלום':
                if (item && props.allowEdit) {
                    return <div onClick={() => { setEdit(index); setEditTextTitle(title); setEditText(0); }} style={{ cursor: 'text' }} >
                        {edit === index && editTextTitle === title ? <input type='text' autoFocus value={editText}
                            style={{ width: '85%', fontSize: '1em' }} onChange={e => regNumber.test(e.target.value) && setEditText(e.target.value)}
                            onBlur={e => { 0 !== e.target.value && props.changeSum(editText, item, index); setEdit(''); }} /> : 0}</div>;
                }
                item && (expenseSum += parseFloat(item.expense_sum));
                return ShowWithMinus(item, item?.expense_sum);
            case 'סכום כולל':
                item && (expenseTotalSum += parseFloat(item.expense_sum_total));
                return ShowWithMinus(item, item?.expense_sum_total);
            case 'תאריך לשידור':
                if (props.noEdit)
                    return convertIsoDate(item.transmission_date);
                return item && <div onClick={() => { setEdit(index); setEditTextTitle(title); setEditText(item.transmission_date); }}
                    style={{ cursor: 'text', border: item.show_error && (!item.transmission_date || item.transmission_date === 0) && '1px solid red' }} >
                    {edit === index && editTextTitle === title ? <input type='date' autoFocus value={editText && editText.slice(0, 10)}
                        style={{ width: '95%', fontSize: '1em' }} onChange={e => setEditText(`${e.target.value} 00:00`)}
                        onBlur={e => {
                            item.transmission_date !== e.target.value && props.changeCheckDate(editText, item, index);
                            setEdit('');
                        }} /> :
                        item.transmission_date ? convertIsoDate(item.transmission_date) : 0}</div>;
            case 'עבור חודש':
                if (props.noEdit)
                    return convertIsoDate(item.for_month);
                return item && <div onClick={() => { setEdit(index); setEditTextTitle(title); setEditText(item.for_month); }}
                    style={{ cursor: 'text', border: item.show_error && !item.for_month && '1px solid red' }} >
                    {edit === index && editTextTitle === title ? <input type='date' autoFocus value={editText && editText.slice(0, 10)}
                        style={{ width: '95%', fontSize: '1em' }} onChange={e => setEditText(`${e.target.value} 00:00`)}
                        onBlur={e => {
                            item.for_month !== e.target.value &&
                                props.changeForMonth(editText, item, index); setEdit('');
                        }} /> :
                        item.for_month ? convertIsoDate(item.for_month) : 0}</div>;
            case 'סך עובדים':
                return item.employee_sum;
            case 'סך תלמידים':
                return item.student_sum;
            case 'סך הדפסות':
                return item && (item.print_employee_sum || item.print_student_sum || item.print_supplier_sum || 0);
            case 'חשבון בנק':
                return item && <select value={item.fk_bank_account_id} style={{ borderColor: item.show_error && !item.fk_bank_account_id && 'red', fontSize: '1em' }}
                    onChange={e => e.target.value !== '' && props.changeBankAccountId(e.target.value, item, index)} >
                    <option value='' hidden>בחר</option>
                    {props.bankAccount && props.bankAccount.map(res =>
                        <option key={res.id} value={res.id}>{res.account_number}</option>)}
                </select>
            case 'מנחה':
                return item && <select value={item.fk_trend_coordinator_id} style={{ borderColor: item.show_error && !item.fk_trend_coordinator_id && 'red', fontSize: '1em', width: '100%', minWidth: '60px' }}
                    onChange={e => e.target.value !== '' && props.changeTrendCoordinatorId(e.target.value, item, index)} >
                    <option value='' hidden>בחר</option>
                    {props.trendCoordinator && props.trendCoordinator.map(res =>
                        <option key={res.id} value={res.id}>{res.name}</option>)}
                </select>
            case 'תיאור':
                const description = item.transaction_description?.length > 29 ? `${item.transaction_description.slice(0, 30)}...` : item.transaction_description;
                return description;
            case 'שיוך':
                return item?.heb_attribution;
            case 'סטטוס תשלום':
                return item?.payment_status;
            case 'אמצעי':
                return item?.payment_method;
            case 'מספר תקבולים':
                item && (periodicSum += parseFloat(item.pr_num));
                return item ? ShowWithMinus(item, item?.pr_num) : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'סך תקבולים':
                item && (periodicTotalSum += parseFloat(item.pr_amount_sum));
                return item ? ShowWithMinus(item, item?.pr_amount_sum) : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'תאריך לחיוב':
                return convertIsoDate(item.charge_date);
            case 'הערות':
                return item.comment?.length > 15 ? item.comment.slice(0, 15) : item.comment;
            case 'סטטוס לתקבול':
                return item.periodic_reception_status;
            case 'סך כשלונות':
                return item ? item.num_failed_payment : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'סך הצלחות':
                return item ? item.num_success_payment : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'יתרת חיובים':
                return item ? item.charges_remainder : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'סה"כ סכום שנגבה':
                item && (totalChargedAmountSum += parseFloat(item.total_charged_amount));
                return item ? item.total_charged_amount : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'מספר חיובים':
                return item ? item.charges : <div style={{ visibility: !item && 'hidden' }}>0</div>;
            case 'תאריך ביטול הרשאה':
                return convertIsoDate(item.bank_permission_end_date);
            case 'תאריך קבלת הרשאה':
                return convertIsoDate(item.bank_permission_start_date);
            case 'תאריך אחרון':
                return convertIsoDate(item.last_charge_date);
            case 'תאריך סיום קורס':
                return convertIsoDate(item.end_date_course_enrollment);
            case 'תאריך התחלה קורס':
                return convertIsoDate(item.start_date_course_enrollment);
            case 'סוג קורס':
                return item.course_type;
            case 'מוסד - סניף':
                return '';
            case 'חלק ביום':
                return item.day_part;
            case 'שם מנחה':
                return '';
            case 'זכאות מינימלית':
                return item.eligibility_min;
            case 'שיטת זכאות':
                return item.eligibility_method;
            case 'רמת זכאות':
                return item.eligibility_level;
            case 'תאריך סיום מנחה':
                return convertIsoDate(item.end_date_trend_attribution);
            case 'תאריך התחלה מנחה':
                return convertIsoDate(item.start_date_trend_attribution);
            case 'סמן לאיחוד':
                return item && (item.merged_printing_number ?
                    <input type='button' value='פיצול תשלום' className='button' style={{ fontSize: '1em' }} onClick={() => props.splitPayment(item.merged_printing_number)} /> :
                    <input type='checkbox' checked={props.mergedCheckbox.includes(item.expense_id)} onChange={e => props.changeMergedCheckbox(e.target.checked, item.expense_id)} />)
            case 'איחוד תשלום':
                return item && item.merged_printing_number ? item.merged_printing_number : null;
            case '':
                return item && <FiTrash2 size='1.1em' style={{ cursor: 'pointer', color: 'red' }} onClick={() => props.delete(item)} />;
            default:
                break;
        }
    }

    const ShowSumWithMinus = (data) => {
        return !isNaN(data) ? (data < 0 ? `${Math.abs(data % 1 !== 0 ? data.toFixed(2) : data)}-` :
            `${Math.abs(data % 1 !== 0 ? data.toFixed(2) : data)}`) : 0;
    }

    const HandleTableFootData = (title) => {
        switch (title) {
            case 'שיוך':
            case 'מזהה':
            case 'שם':
            case 'שם מלא':
            case 'מספר חשבון':
            case 'תאריך':
                return props.noFottTitle?.includes(title) ? '' : `${props.data.filter(data => data !== '').length} רשומות`;
            case 'הכנסות':
                return ShowSumWithMinus(incomeSum);
            case 'הוצאות':
                return ShowSumWithMinus(expanseSum);
            case 'יתרה':
                return ShowSumWithMinus(balanceSum);
            case 'יתרה כוללת':
                return ShowSumWithMinus(balanceTotalSum);
            case 'מסגרת':
                return ShowSumWithMinus(lineOfCreditSum);
            case 'הלוואות':
                return ShowSumWithMinus(loanSum);
            case 'התחייבויות':
                return ShowSumWithMinus(commitmentSum);
            case 'נזיל':
                return ShowSumWithMinus(cashSum);
            case 'תזרים':
                return ShowSumWithMinus(flowSum);
            case 'תזרים חודשי':
                return ShowSumWithMinus(monthlyFlowSum);
            case 'סכום':
                return ShowSumWithMinus(transactionAmountSum);
            case 'סכום לתשלום':
                return !props.allowEdit && ShowSumWithMinus(expenseSum);
            case 'סכום כולל':
                return ShowSumWithMinus(expenseTotalSum);
            case 'מספר תקבולים':
                return ShowSumWithMinus(periodicSum);
            case 'סך תקבולים':
                return ShowSumWithMinus(periodicTotalSum);
            case 'סה"כ סכום שנגבה':
                return ShowSumWithMinus(totalChargedAmountSum);
            default:
                break;
        }
    }
    const {keys} = props
    useEffect(()=>{
        const tempObj = {}
        if(keys){
            
            keys.forEach(element => {
                tempObj[element] = null;
              });
              setNewData(tempObj)
        }
    },[keys])

    const newRowDataHandler = (e)=>{
        let tempData = {...newData}
        tempData[e.target.title]=e.target.value 
        setNewData(tempData)
    }
    useEffect(()=>{
        if(title==='bank_permission_end_date' || title==='bank_permission_start_date'||title==='charge_date'||title==='last_charge_date')setInputType('date')
        if(title==='amount' || title==='charges'||title==='charges_remainder'||title==='identity'||title==='num_failed_peyment'||title==='num_success_peyment'||title==='total_charged_amount')setInputType('number')
        setInputType('text')

    },[title])
    return (
        <div style={{ position: 'relative', margin: '1em', ...props.style }}>
            <table ref={tableRef} id='table' style={{ borderCollapse: 'collapse', ...props.tableStyle }} >
                <thead style={{ backgroundColor: '#c5c5c5' }}>
                    <tr >
                        {props.header.map((head, index) => <th key={head}
                            style={{
                                position: 'sticky', top: '-1px', border: '1px solid black', backgroundColor: '#c5c5c5',
                                boxShadow: 'inset 0px 0.5px 0px black, inset 0px -0.5px 0px black'
                            }}>
                            <div style={{ margin: '5px' }}>{head}</div>
                        </th>)}
                    </tr>
                </thead>
                <tbody className='wrapWord'>
                    {props.isAddingData &&  <tr >
                        {keys.map((head, index) => <th key={head}
                            style={{
                                top: '-1px', border: '1px solid black', backgroundColor: '#F7F7F7' }} >
                            
                            <input type={inputType} style={{ maxWidth: '68px',maxHeight:"100%", backgroundColor:'#F7F7F7',  outline: 'none', boxShadow: 'none',border:'none' }} title={head} onChange = {(e)=>newRowDataHandler(e)} onClick={(e)=>setTitle(e.target.title)}/>
                            
                            </th>)
                        }
                        <input type='button' value='שמור' style={{ position: 'absolute' }} size='5' onClick={()=>props.addingData(newData)}/>
                    </tr> }
                    {props.data.map((item, index) => <tr key={index} >{
                        props.header.map((title) => <td key={title} style={{
                            border: '1px solid black', cursor: item && title !== 'סמן לתשלום' && title !== 'צורת תשלום' && title !== '' &&
                                title !== 'סמן להדפסה' && title !== 'תאריך לשידור' && title !== 'עבור חודש' && (!props.allowEdit || title !== 'סכום') &&
                                (!props.allowEdit || title !== 'סכום לתשלום') && props.changeTableSelectedItems && 'pointer',
                            backgroundColor: item && props.tableSelectedItems && props.tableSelectedItems[index].checked && '#abcdef'
                        }}
                            onClick={() => item && title !== 'סמן לתשלום' && title !== 'צורת תשלום' && title !== 'סמן להדפסה' && title !== '' &&
                                title !== 'תאריך לשידור' && title !== 'עבור חודש' && (!props.allowEdit || title !== 'סכום') && (!props.allowEdit || title !== 'סכום לתשלום') &&
                                props.changeTableSelectedItems && props.changeTableSelectedItems(props.tableSelectedItems &&
                                    !props.tableSelectedItems[index].checked, index, item)}>
                            <div style={{
                                margin: '5px', maxWidth: '10em', wordBreak: 'break-word', color: item.deleted && 'gray'
                                // backgroundColor: props.tableSelectedItems && props.tableSelectedItems[index].checked && 'red'
                            }}>
                                {HandleTableData(title, item, index)}</div>
                        </td>)}
                    </tr>)}
                </tbody>
                {!props.withoutSum && <tfoot style={{ width: '100%', fontWeight: 'bold' }}>
                    <tr>
                        {props.header.map((title, index) => <td key={title} style={{ position: 'sticky', bottom: '-1px', backgroundColor: '#f7f7f7' }}>
                            <div style={{ margin: '5px' }}>{(!props.doNotSum || !props.doNotSum.includes(title)) && HandleTableFootData(title)}</div>
                            {index === 0 && <div style={{ backgroundColor: '#f7f7f7', position: 'absolute', right: '-5px', top: '0', width: '5px', height: '100%' }}></div>}
                        </td>)}
                    </tr>
                </tfoot>}
            </table>
            {props.children}
        </div>
    )
}

Table.propTypes = {
    header: PropTypes.arrayOf(PropTypes.string).isRequired,
    data: PropTypes.array,
    children: PropTypes.any,
    style: PropTypes.any,
    tableStyle: PropTypes.any,
    className: PropTypes.string,
    tableHeight: PropTypes.func,
    tableCheckbox: PropTypes.array,
    changeCheckbox: PropTypes.func,
    tableSelectedItems: PropTypes.array,
    changeTableSelectedItems: PropTypes.func,
    doNotSum: PropTypes.array,
    rightTable: PropTypes.bool,
    changePaymentMethod: PropTypes.func,
    paymentMethods: PropTypes.array,
    allowEdit: PropTypes.bool,
    changeCheckDate: PropTypes.func,
    changeSum: PropTypes.func,
}

export default Table;