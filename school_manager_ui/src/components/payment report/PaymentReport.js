import React, { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import FinanceReportFilters from './FinanceReportFilters';
import { FaSearch } from 'react-icons/fa';
import { GrDocumentCsv } from 'react-icons/gr';
import Table from '../Table';
import { Spin } from "react-loading-io";
import { CSVLink } from 'react-csv';
import GoogleSheetsLink from '../UI/GoogleSheetsLink'

import '../../styles/payment report/PaymentReport.css';

const PaymentReport = (props) => {
    const history = useHistory();
    const { paymentReportStore } = props.rootStore;

    useEffect(() => {
        paymentReportStore.fetchFinanceReportFilters()
            .then(() => {
                const dateFrom = `${new Date().getFullYear()}-01-01`;
                const dateTo = `${new Date().toISOString().slice(0, 10)}`;
                paymentReportStore.setDateFromTo(dateFrom, dateTo);
                paymentReportStore.setFinanceReportFiltersDateToSend(dateFrom.split('-').reverse().join('/'), 0);
                paymentReportStore.setFinanceReportFiltersDateToSend(dateTo.split('-').reverse().join('/'), 1);
            })
            .then(() => HandleCheckAll())
            .then(() => HandleSearchByCheckBox());
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    useEffect(() => {
        paymentReportStore.afterLeftTableUpdate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [paymentReportStore.leftTableCheckbox])

    const HandleOnChange = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex) => {
        paymentReportStore.setFinanceReportFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            paymentReportStore.setFinanceReportFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e =>
                e.checked = paymentReportStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        paymentReportStore.setFinanceReportFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = false);
    }

    const HandleSelectedDateOption = (option) => {
        paymentReportStore.setFinanceReportFiltersDateSelectedOption(option.split(','));
    }

    const HandleSelectedDateFrom = (date) => {
        paymentReportStore.setDateFromTo(date);
        paymentReportStore.setFinanceReportFiltersDateToSend(date.split('-').reverse().join('/'), 0);
    }

    const HandleSelectedDateTo = (date) => {
        paymentReportStore.setDateFromTo(null, date);
        paymentReportStore.setFinanceReportFiltersDateToSend(date.split('-').reverse().join('/'), 1);
    }

    const HandleClearDate = () => {
        paymentReportStore.setDateFromTo('', '');
        paymentReportStore.setFinanceReportFiltersDateToSend(null, null, 'clear');
    }

    const HandleSearch = (tableIndex, e) => {
        paymentReportStore.allFinanceReport && paymentReportStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e, tab, tableIndex, tableClass) => {
        if (paymentReportStore.allFinanceReport) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            paymentReportStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        let body = paymentReportStore.financeReportFiltersToSend;
        const setDate = (data) => {
            data.checked[0] = data.checked[0] !== '' ? data.checked[0] : `01/01/${new Date().getFullYear()} 00:00`;
            data.checked[1] = data.checked[1] !== '' ? data.checked[1] : `${new Date().toISOString().slice(0, 10).split('-').reverse().join('/')} 23:59`;
            return data;
        }

        body.expense_filters = [...body.expense_filters,
        ...paymentReportStore.financeReportFiltersDateToSend.expense_filters.map(expense => setDate(expense))];
        body.income_filters = [...body.income_filters,
        ...paymentReportStore.financeReportFiltersDateToSend.income_filters.map(income => setDate(income))];
        body.student_filters = [...body.student_filters,
        ...paymentReportStore.financeReportFiltersDateToSend.student_filters.map(student => setDate(student))];
        !sessionStorage.getItem('reload') ? paymentReportStore.fetchFilteredFinanceReport(body) : sessionStorage.removeItem('reload');
    }

    const HandleSelectedLeftTableSelectedItem = (item) => {
        if (paymentReportStore.selectedLeftTableTab === 'student') {
            sessionStorage.setItem('student_id', item.attribution_id);
            history.push('/finance-report/student-profile');
            sessionStorage.setItem('route', '/finance-report/student-profile');
        }
    }

    const HandleExpenseMessage = () => {
        setTimeout(() => {
            paymentReportStore.changeExpenseMessage('');
        }, 5000);

        return <div style={{ position: 'absolute', left: '100%', whiteSpace: 'nowrap', marginLeft: '3px', fontSize: '1.1em' }}>{paymentReportStore.expenseMessage}</div>
    }

    console.log(paymentReportStore.financeReportFilters);
    return (
        <Container title='דוח תשלומים ותקבולים - הפקת תשלומים' childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className='paymentReportFiltersContainer' >
                <FinanceReportFilters data={paymentReportStore.financeReportFilters}
                    onChange={HandleOnChange}
                    dateSelectOption={HandleSelectedDateOption}
                    dateFrom={paymentReportStore.dateFrom}
                    dateTo={paymentReportStore.dateTo}
                    onDateFrom={HandleSelectedDateFrom}
                    onDateTo={HandleSelectedDateTo}
                    cleanDate={HandleClearDate} />
                {paymentReportStore.financeReportFilters.length > 0 && <div className='paymentReportFiltersResetButtonContainer' >
                    <div className='paymentReportFiltersResetButtonPosition' style={{ position: 'relative' }} >
                        <input type='button' value='סמן הכל' className='paymentReportFiltersResetButton button' onClick={HandleCheckAll} />
                        <input type='button' value='נקה הכל' className='paymentReportFiltersResetButton button' onClick={HandleUnCheckAll} />
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={() => paymentReportStore.allFinanceReport && HandleSearchByCheckBox()}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                                חיפוש
                            </div>
                        </div>
                        <div style={{ position: 'absolute', top: '110%', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 'max-content' }}>
                            {paymentReportStore.expenseMessage.trim() !== '' && HandleExpenseMessage()}
                            <div className='button' onClick={() => paymentReportStore.allFinanceReport && paymentReportStore.fetchExpense()}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1em' }} >
                                בצע תשלום
                            </div>
                        </div>
                    </div>
                </div>}
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh',
                height: paymentReportStore.leftTableHeight < paymentReportStore.rightTableHeight ? paymentReportStore.leftTableHeight : paymentReportStore.rightTableHeight
            }} >
                <div style={{ height: paymentReportStore.rightTableFinanceReport.length < 10 && 'fit-content', marginRight: 'calc(5em + 5px)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={paymentReportStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <CSVLink filename={`${paymentReportStore.selectedRightTableTab} ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={paymentReportStore.rightTableFinanceReportDownloadCSV}
                            headers={[
                                { label: 'שם', key: 'name' },
                                { label: 'הכנסות', key: 'income_sum' },
                                { label: 'הוצאות', key: 'expense_sum' },
                                { label: 'יתרה', key: 'balance' },
                                { label: 'יתרה כוללת', key: 'balance_total' }
                            ]}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                        <GoogleSheetsLink headers={{
                                  'name' :'שם',
                                   'income_sum':'הכנסות',
                                  'expense_sum':'הוצאות',
                                   'balance':'יתרה',
                                  'balance_total':'יתרה כוללת'
                        }}
                             data={paymentReportStore.rightTableFinanceReportDownloadCSV} 
                             store={paymentReportStore}
                             table={paymentReportStore.selectedRightTableTab}
                             />
                             
                    </div>
                    <Table header={['שם', 'הכנסות', 'הוצאות', 'יתרה', 'יתרה כוללת', 'סמן לתשלום']}
                        rightTable
                        data={paymentReportStore.rightTableFinanceReport}
                        tableCheckbox={paymentReportStore.rightTableCheckbox}
                        tableSelectedItems={paymentReportStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => paymentReportStore.allFinanceReport && paymentReportStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => paymentReportStore.setRightTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => paymentReportStore.setRightTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: paymentReportStore.leftTableHeight < paymentReportStore.rightTableHeight && paymentReportStore.leftTableHeight
                        }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${paymentReportStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${paymentReportStore.selectedRightTableTab === 'branch' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'branch', 1, '.paymentReportRightTableTab')}>סנפים</div>
                            <div className={`paymentReportRightTableTab ${paymentReportStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>מנחים</div>
                        </div>
                        <div className='paymentReportRightTableSum' >שורת סיכום</div>
                        {!paymentReportStore.allFinanceReport && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: paymentReportStore.leftTableFinanceReport.length < 10 && 'fit-content', marginLeft: '4em' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={paymentReportStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <CSVLink filename={`${paymentReportStore.selectedLeftTableTab} ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={paymentReportStore.leftTableFinanceReportDownloadCSV}
                            headers={[
                                { label: 'מזהה', key: 'identity' },
                                { label: 'שם מלא', key: 'full_name' },
                                { label: 'הכנסות', key: 'income_sum' },
                                { label: 'הוצאות', key: 'expense_sum' },
                                { label: 'יתרה', key: 'balance' },
                                { label: 'יתרה כוללת', key: 'balance_total' }
                            ]}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                        <GoogleSheetsLink headers={{
                            'identity':'מזהה' ,
                            'full_name':'שם מלא' ,
                            'income_sum':'הכנסות' ,
                            'expense_sum':'הוצאות' ,
                            'balance':'יתרה' ,
                            'balance_total':'יתרה כוללת' }
                            } 
                            data={paymentReportStore.leftTableFinanceReportDownloadCSV} 
                            store={paymentReportStore}
                            table={paymentReportStore.selectedLeftTableTab}
                            />
                    </div>
                    <Table header={['מזהה', 'שם מלא', 'הכנסות', 'הוצאות', 'יתרה', 'יתרה כוללת', 'סמן לתשלום']}
                        data={paymentReportStore.leftTableFinanceReport}
                        noFottTitle={['שם מלא']}
                        tableCheckbox={paymentReportStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => paymentReportStore.setLeftTableCheckbox(checked, index, item)}
                        changeTableSelectedItems={(checked, index, item) => paymentReportStore.allFinanceReport && HandleSelectedLeftTableSelectedItem(item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => paymentReportStore.setLeftTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: paymentReportStore.leftTableHeight > paymentReportStore.rightTableHeight && paymentReportStore.rightTableHeight
                        }} >
                        <div className='paymentReportTableTabsPosition' style={{ right: '100%' }}>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'student', 0, '.paymentReportLeftTableTab')}>תלמידים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'employee', 0, '.paymentReportLeftTableTab')}>עובדים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'supplier', 0, '.paymentReportLeftTableTab')}>ספקים</div>
                        </div>
                        {!paymentReportStore.allFinanceReport && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
        </Container>
    )
}

export default inject('rootStore')(observer(PaymentReport));