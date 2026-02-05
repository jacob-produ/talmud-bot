import React, { useEffect } from 'react';
// import { useHistory } from 'react-router-dom';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import FinanceReportFilters from '../payment report/FinanceReportFilters';
import { FaSearch } from 'react-icons/fa';
import { GrDocumentCsv } from 'react-icons/gr';
import Table from '../Table';
import { Spin } from "react-loading-io";
import { CSVLink } from 'react-csv';
import GoogleSheetsLink from '../UI/GoogleSheetsLink'
import '../../styles/payment report/PaymentReport.css';
const fileDownload = require('js-file-download');

const TransactionsReport = (props) => {
    // const history = useHistory();
    const { transactionsReportStore } = props.rootStore;
    console.log(transactionsReportStore);

    useEffect(() => {
        transactionsReportStore.fetchTransactionsReportFilters()
            .then(() => {
                const dateFrom = `${new Date().getFullYear()}-01-01`;
                const dateTo = `${new Date().toISOString().slice(0, 10)}`;
                transactionsReportStore.setDateFromTo(dateFrom, dateTo);
                transactionsReportStore.setTransactionsReportFiltersDateToSend(dateFrom.split('-').reverse().join('/'), 0);
                transactionsReportStore.setTransactionsReportFiltersDateToSend(dateTo.split('-').reverse().join('/'), 1);
            })
            .then(() => HandleCheckAll())
            .then(() => HandleSearchByCheckBox());
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    useEffect(() => {
        transactionsReportStore.afterLeftTableUpdate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [transactionsReportStore.leftTableCheckbox])

    const HandleOnChange = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex) => {
        transactionsReportStore.setTransactionsReportFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            transactionsReportStore.setTransactionsReportFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e =>
                e.checked = transactionsReportStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        transactionsReportStore.setTransactionsReportFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = false);
    }

    const HandleSelectedDateOption = (option) => {
        transactionsReportStore.setTransactionsReportFiltersDateSelectedOption(option.split(','));
    }

    const HandleSelectedDateFrom = (date) => {
        transactionsReportStore.setDateFromTo(date);
        transactionsReportStore.setTransactionsReportFiltersDateToSend(date.split('-').reverse().join('/'), 0);
    }

    const HandleSelectedDateTo = (date) => {
        transactionsReportStore.setDateFromTo(null, date);
        transactionsReportStore.setTransactionsReportFiltersDateToSend(date.split('-').reverse().join('/'), 1);
    }

    const HandleClearDate = () => {
        transactionsReportStore.setDateFromTo('', '');
        transactionsReportStore.setTransactionsReportFiltersDateToSend(null, null, 'clear');
    }

    const HandleSearch = (tableIndex, e) => {
        transactionsReportStore.allTransactionsReport && transactionsReportStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e, tab, tableIndex, tableClass) => {
        if (transactionsReportStore.allTransactionsReport) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            transactionsReportStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        let body = transactionsReportStore.transactionsReportFiltersToSend;

        const setDates = (data) => {
            data.checked[0] = data.checked[0] && data.checked[0] !== '' ? data.checked[0] : `01/01/${new Date().getFullYear()} 00:00`;
            data.checked[1] = data.checked[1] && data.checked[1] !== '' ? data.checked[1] : `${new Date().toISOString().slice(0, 10).split('-').reverse().join('/')} 23:59`;
            return data;
        }

        body.expense_filters = [...body.expense_filters.filter(data => data.name !== 'expense_date'),
        ...transactionsReportStore.transactionsReportFiltersDateToSend.expense_filters.map(expense => setDates(expense))];
        body.income_filters = [...body.income_filters.filter(data => data.name !== 'income_date'),
        ...transactionsReportStore.transactionsReportFiltersDateToSend.income_filters.map(income => setDates(income))];
        body.attribution_filters = [...body.attribution_filters];
        !sessionStorage.getItem('reload') ? transactionsReportStore.fetchFilteredTransactionsReport(body) : sessionStorage.removeItem('reload');
    }

    const HandleExpenseMessage = () => {
        setTimeout(() => {
            transactionsReportStore.changeExpenseMessage('');
        }, 5000);

        return <div style={{ position: 'absolute', left: '0', bottom: '-1.2em', whiteSpace: 'nowrap', marginLeft: '3px', fontSize: '1.1em' }}>{transactionsReportStore.expenseMessage}</div>
    }

    const HandleRestoreExpense = () => {
        const checkboxRestoreLength = transactionsReportStore.leftTableCheckbox.filter(data => data.checked).length;

        const HandleExeptRestoreExpense = () => {
            transactionsReportStore.fetchRestoreExpense()
                .then(() => {
                    HandleSearchByCheckBox();
                    HandleClosePopup();
                })
        }

        const HandleClosePopup = () => {
            transactionsReportStore.setShowPopup(false);
        }

        return <div id='popupContainer'>
            <div className='restorePopup'>
                <div> {`קיימים ${checkboxRestoreLength} שינויים`} </div>
                <div>האם לבצע שחזור?</div>
                <div style={{ display: 'flex', justifyContent: 'space-evenly', marginTop: '10px' }}>
                    <div className='button' style={{ padding: '3px' }} onClick={HandleExeptRestoreExpense}>אישור</div>
                    <div className='button' style={{ padding: '3px' }} onClick={HandleClosePopup}>ביטול</div>
                </div>
            </div>
        </div>
    }

    const HandleRawTable = () => {
        transactionsReportStore.fetchRawTable()
            .then(res => {
                if (res.ok) {
                    const header = res.headers.get('Content-Disposition');
                    if (header) {
                        const fileName = header.slice(header.indexOf('filename=') + 9, header.length - 1);
                        res.blob().then(file => fileDownload(file, fileName));
                    }
                }
            })
    }

    return (
        <Container title='דוח תנועות' childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className='paymentReportFiltersContainer' >
                <FinanceReportFilters data={transactionsReportStore.transactionsReportFilters}
                    onChange={HandleOnChange}
                    dateSelectOption={HandleSelectedDateOption}
                    dateFrom={transactionsReportStore.dateFrom}
                    dateTo={transactionsReportStore.dateTo}
                    onDateFrom={HandleSelectedDateFrom}
                    onDateTo={HandleSelectedDateTo}
                    cleanDate={HandleClearDate} />
                {transactionsReportStore.transactionsReportFilters.length > 0 && <div className='paymentReportFiltersResetButtonContainer' >
                    <div className='paymentReportFiltersResetButtonPosition' style={{ position: 'relative' }} >
                        <input type='button' value='סמן הכל' className='paymentReportFiltersResetButton button' onClick={HandleCheckAll} />
                        <input type='button' value='נקה הכל' className='paymentReportFiltersResetButton button' onClick={HandleUnCheckAll} />
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={() => transactionsReportStore.allTransactionsReport && HandleSearchByCheckBox()}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                                חיפוש
                            </div>
                        </div>
                        <div style={{ position: 'absolute', top: '110%', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 'max-content' }}>
                            {transactionsReportStore.expenseMessage?.trim() !== '' && HandleExpenseMessage()}
                            <div className='button' onClick={() => transactionsReportStore.allTransactionsReport && transactionsReportStore.setShowPopup(true)}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1em' }} >
                                בצע שחזור
                            </div>
                        </div>
                    </div>
                </div>}
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh',
                height: transactionsReportStore.leftTableHeight < transactionsReportStore.rightTableHeight ? transactionsReportStore.leftTableHeight : transactionsReportStore.rightTableHeight
            }} >
                <div style={{ height: transactionsReportStore.rightTableTransactionsReport.length < 10 && 'fit-content', marginRight: 'calc(5em + 5px)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' style={{ width: '50%' }} >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={transactionsReportStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <CSVLink filename={`${transactionsReportStore.selectedRightTableTab} ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={transactionsReportStore.rightTableTransactionsReportDownloadCSV}
                            headers={[
                                { label: 'שם', key: 'name' },
                                { label: 'יתרה', key: 'balance' },
                                { label: 'יתרה כוללת', key: 'balance_total' }
                            ]}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                        <GoogleSheetsLink 
                            data={transactionsReportStore.rightTableTransactionsReportDownloadCSV}
                            headers={[
                                { label: 'שם', key: 'name' },
                                { label: 'יתרה', key: 'balance' },
                                { label: 'יתרה כוללת', key: 'balance_total' }
                            ]}
                            store={transactionsReportStore}
                            table={ transactionsReportStore.selectedRightTableTab}
                            />
                    </div>
                    <Table header={['שם', 'יתרה', 'יתרה כוללת']}
                        rightTable
                        data={transactionsReportStore.rightTableTransactionsReport}
                        tableCheckbox={transactionsReportStore.rightTableCheckbox}
                        tableSelectedItems={transactionsReportStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => transactionsReportStore.allTransactionsReport && transactionsReportStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => transactionsReportStore.setRightTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => transactionsReportStore.setRightTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${transactionsReportStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${transactionsReportStore.selectedRightTableTab === 'branch' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'branch', 1, '.paymentReportRightTableTab')}>סנפים</div>
                            <div className={`paymentReportRightTableTab ${transactionsReportStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>מנחים</div>
                        </div>
                        {!transactionsReportStore.allTransactionsReport && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: transactionsReportStore.leftTableTransactionsReport.length < 10 && 'fit-content', marginLeft: '4em' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' style={{ width: '20%' }} >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={transactionsReportStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <div style={{ display: 'flex' }}>
                            <div style={{ textDecoration: 'underline', fontWeight: '500' }}>סוג תנועה:</div>
                            <label style={{ display: 'flex', marginRight: '3px' }}>
                                הוצאות
                                <input type='checkbox' checked={transactionsReportStore.checkExpense}
                                    onChange={e => transactionsReportStore.changeCheckBox('expense', e.target.checked)} />
                            </label>
                            <label style={{ display: 'flex', marginRight: '3px' }}>
                                הכנסות
                                <input type='checkbox' checked={transactionsReportStore.checkIncome}
                                    onChange={e => transactionsReportStore.changeCheckBox('income', e.target.checked)} />
                            </label>
                        </div>
                        <CSVLink style={{ marginRight: '1em' }} filename={`דוח תנועות ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={transactionsReportStore.leftTableTransactionsReportDownloadCSV}
                            headers={[
                                { label: 'שיוך', key: 'heb_attribution' },
                                { label: 'שם מלא', key: 'full_name' },
                                { label: 'מזהה', key: 'identity' },
                                { label: 'תאריך תנועה', key: 'transaction_date' },
                                { label: 'סטטוס תשלום', key: 'payment_status' },
                                { label: 'סכום', key: 'amount' },
                                { label: 'אמצעי', key: 'payment_method' },
                                { label: 'עבור חודש', key: 'for_month' },
                                { label: 'תאריך הדפסה', key: 'printing_date' }
                            ]}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                        <GoogleSheetsLink headers={[
                                { label: 'שיוך', key: 'heb_attribution' },
                                { label: 'שם מלא', key: 'full_name' },
                                { label: 'מזהה', key: 'identity' },
                                { label: 'תאריך תנועה', key: 'transaction_date' },
                                { label: 'סטטוס תשלום', key: 'payment_status' },
                                { label: 'סכום', key: 'amount' },
                                { label: 'אמצעי', key: 'payment_method' },
                                { label: 'עבור חודש', key: 'for_month' },
                                { label: 'תאריך הדפסה', key: 'printing_date' }
                            ]} data={transactionsReportStore.leftTableTransactionsReportDownloadCSV} store={transactionsReportStore}
                            table={ 'דוח תנועות' }
                            />
                        <input style={{ marginRight: '1em' }} type='button' value='יצא דוח הוצאות והכנסות' onClick={HandleRawTable} />
                    </div>
                    <Table header={['שיוך', 'שם מלא', 'מזהה', 'תאריך תנועה', 'סטטוס תשלום', 'סכום', 'אמצעי', 'עבור חודש', 'תאריך הדפסה', 'סמן לשחזור']}
                        noEdit
                        noFottTitle={['מזהה']}
                        data={transactionsReportStore.leftTableTransactionsReport}
                        tableCheckbox={transactionsReportStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => transactionsReportStore.setLeftTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => transactionsReportStore.setLeftTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }} >
                        {!transactionsReportStore.allTransactionsReport && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
            {transactionsReportStore.showPopup && <HandleRestoreExpense />}
        </Container>
    )
}

export default inject('rootStore')(observer(TransactionsReport));