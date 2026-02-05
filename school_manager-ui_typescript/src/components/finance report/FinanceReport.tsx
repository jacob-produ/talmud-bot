import React, { useEffect } from 'react';
import Store from '../../store';
import { observer } from 'mobx-react';
import { useNavigate } from 'react-router-dom';
import { FaSearch } from 'react-icons/fa';
import { GrDocumentCsv } from 'react-icons/gr';
import { CSVLink } from 'react-csv';
import { ClipLoader } from "react-spinners";
import Container from '../containers/Container';
import Filters from '../filters/Filters';
import Table from '../table/Table';

interface Props {

}

const FinanceReport: React.FC<Props> = () => {
    const { financeReportStore } = Store;
    const navigate = useNavigate();

    useEffect(() => {
        financeReportStore.fetchFinanceReportFilters().then(() => {
            const dateFrom = `${new Date().getFullYear()}-01-01`;
            const dateTo = `${new Date().toISOString().slice(0, 10)}`;
            financeReportStore.setDateFromTo(dateFrom, dateTo);
            financeReportStore.setFinanceReportFiltersDateToSend(dateFrom.split('-').reverse().join('/'), 0);
            financeReportStore.setFinanceReportFiltersDateToSend(dateTo.split('-').reverse().join('/'), 1);
        })
            .then(() => HandleCheckAll())
            .then(() => HandleSearchByCheckBox())
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            financeReportStore.setFinanceReportFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) =>
                e.checked = financeReportStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        financeReportStore.setFinanceReportFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) => e.checked = false);
    }

    const HandleFiltersOnChange = (titleName: string, name: string, checked: string, titleIndex: number, filterIndex: number, checkboxIndex: number) => {
        financeReportStore.setFinanceReportFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleFiltersSelectedDateOption = (option: any) => {
        financeReportStore.setFinanceReportFiltersDateSelectedOption(option.split(','));
    }

    const HandleFiltersSelectedDateFrom = (date: string) => {
        financeReportStore.setDateFromTo(date);
        financeReportStore.setFinanceReportFiltersDateToSend(date.split('-').reverse().join('/'), 0);
    }

    const HandleFiltersSelectedDateTo = (date: string) => {
        financeReportStore.setDateFromTo(null, date);
        financeReportStore.setFinanceReportFiltersDateToSend(date.split('-').reverse().join('/'), 1);
    }

    const HandleFiltersClearDate = () => {
        financeReportStore.setDateFromTo('', '');
        financeReportStore.setFinanceReportFiltersDateToSend(null, null, 'clear');
    }

    const HandleSearch = (tableIndex: number, e: any) => {
        financeReportStore.allFinanceReport && financeReportStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e: any, tab: string, tableIndex: number, tableClass: string) => {
        if (financeReportStore.allFinanceReport) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            financeReportStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        let body = financeReportStore.financeReportFiltersToSend;
        const setDate = (data: any) => {
            data.checked[0] = data.checked[0] !== '' ? data.checked[0] : `01/01/${new Date().getFullYear()} 00:00`;
            data.checked[1] = data.checked[1] !== '' ? data.checked[1] : `${new Date().toISOString().slice(0, 10).split('-').reverse().join('/')} 23:59`;
            return data;
        }

        body.expense_filters = [...body.expense_filters,
        ...financeReportStore.financeReportFiltersDateToSend.expense_filters.map((expense: any) => setDate(expense))];
        body.income_filters = [...body.income_filters,
        ...financeReportStore.financeReportFiltersDateToSend.income_filters.map((income: any) => setDate(income))];
        body.student_filters = [...body.student_filters,
        ...financeReportStore.financeReportFiltersDateToSend.student_filters.map((student: any) => setDate(student))];
        !sessionStorage.getItem('reload') ? financeReportStore.fetchFilteredFinanceReport(body) : sessionStorage.removeItem('reload');
    }

    const HandleSelectedLeftTableSelectedItem = (item: any) => {
        if (financeReportStore.selectedLeftTableTab === 'student') {
            sessionStorage.setItem('student_id', item.attribution_id);
            navigate('/finance-report/student-profile');
            sessionStorage.setItem('route', '/finance-report/student-profile');
        }
    }

    const HandleExpenseMessage = () => {
        setTimeout(() => {
            financeReportStore.changeExpenseMessage('');
        }, 5000);

        return <div style={{ position: 'absolute', left: '100%', whiteSpace: 'nowrap', marginLeft: '3px', fontSize: '1.1em' }}>{financeReportStore.expenseMessage}</div>
    }

    return (
        // childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
        <Container title='דוח תשלומים ותקבולים - הפקת תשלומים' childrenClassName='finance_report' cartTo='/finance-report/payments-basket'>
            <div className='finance_report__filters'>
                <Filters data={financeReportStore.financeReportFilters}
                    onChange={HandleFiltersOnChange}
                    dateSelectOption={HandleFiltersSelectedDateOption}
                    dateFrom={financeReportStore.dateFrom}
                    dateTo={financeReportStore.dateTo}
                    onDateFrom={HandleFiltersSelectedDateFrom}
                    onDateTo={HandleFiltersSelectedDateTo}
                    cleanDate={HandleFiltersClearDate} />
                <div>
                    {financeReportStore.financeReportFilters.length > 0 && <div className='finance_report__filters__inputs' >
                        <div className='finance_report__filters__inputs__checkbox_button' onClick={HandleCheckAll} >סמן הכל</div>
                        <div className='finance_report__filters__inputs__checkbox_button' onClick={HandleUnCheckAll} >נקה הכל</div>
                        <div className='finance_report__filters__inputs__checkbox_button__search' onClick={() => financeReportStore.allFinanceReport && HandleSearchByCheckBox()} >
                            <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                            חיפוש
                        </div>
                        <div className='finance_report__filters__inputs__checkbox_button__payment' onClick={() => financeReportStore.allFinanceReport && financeReportStore.fetchExpense()} >בצע תשלום</div>
                        <div className='finance_report__filters__inputs__error_message' >{financeReportStore.expenseMessage.trim() !== '' && HandleExpenseMessage()}</div>
                    </div>}
                </div>
            </div>

            <div className='finance_report__tables' style={{
                height: financeReportStore.leftTableHeight < financeReportStore.rightTableHeight ? financeReportStore.leftTableHeight : financeReportStore.rightTableHeight
            }} >
                <div style={{ height: financeReportStore.rightTableFinanceReport.length < 10 ? 'fit-content' : 'auto', marginRight: 'calc(5em + 5px)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={financeReportStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <CSVLink filename={`${financeReportStore.selectedRightTableTab} ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={financeReportStore.rightTableFinanceReportDownloadCSV}
                            headers={financeReportStore.rightTableCSV_data}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                    </div>
                    <Table header={['שם', 'הכנסות', 'הוצאות', 'יתרה', 'יתרה כוללת', 'סמן לתשלום']}
                        rightTable
                        data={financeReportStore.rightTableFinanceReport}
                        tableCheckbox={financeReportStore.rightTableCheckbox}
                        tableSelectedItems={financeReportStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => financeReportStore.allFinanceReport && financeReportStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => financeReportStore.setRightTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => financeReportStore.setRightTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: financeReportStore.leftTableHeight < financeReportStore.rightTableHeight && financeReportStore.leftTableHeight
                        }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${financeReportStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${financeReportStore.selectedRightTableTab === 'branch' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'branch', 1, '.paymentReportRightTableTab')}>סנפים</div>
                            <div className={`paymentReportRightTableTab ${financeReportStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>מנחים</div>
                        </div>
                        <div className='paymentReportRightTableSum' >שורת סיכום</div>
                        {!financeReportStore.allFinanceReport && <div className='paymentReportTableSpin' ><ClipLoader loading size='2.5em' color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: financeReportStore.leftTableFinanceReport.length < 10 ? 'fit-content' : 'auto', marginLeft: '4em' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={financeReportStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                        <CSVLink filename={`${financeReportStore.selectedLeftTableTab} ${new Date().toISOString().slice(0, 10)}.csv`}
                            data={financeReportStore.leftTableFinanceReportDownloadCSV}
                            headers={financeReportStore.leftTableCSV_data}>
                            <GrDocumentCsv size='1.3em' title='הורדה' style={{ cursor: 'pointer' }} />
                        </CSVLink>
                    </div>
                    <Table header={['מזהה', 'שם מלא', 'הכנסות', 'הוצאות', 'יתרה', 'יתרה כוללת', 'סמן לתשלום']}
                        data={financeReportStore.leftTableFinanceReport}
                        noFottTitle={['שם מלא']}
                        tableCheckbox={financeReportStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => financeReportStore.setLeftTableCheckbox(checked, index, item)}
                        changeTableSelectedItems={(checked, index, item) => financeReportStore.allFinanceReport && HandleSelectedLeftTableSelectedItem(item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => financeReportStore.setLeftTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: financeReportStore.leftTableHeight > financeReportStore.rightTableHeight && financeReportStore.rightTableHeight
                        }} >
                        <div className='paymentReportTableTabsPosition' style={{ right: '100%' }}>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'student', 0, '.paymentReportLeftTableTab')}>תלמידים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'employee', 0, '.paymentReportLeftTableTab')}>עובדים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'supplier', 0, '.paymentReportLeftTableTab')}>ספקים</div>
                        </div>
                        {!financeReportStore.allFinanceReport && <div className='paymentReportTableSpin' ><ClipLoader loading size='2.5em' color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
        </Container>
    );
}

export default observer(FinanceReport);