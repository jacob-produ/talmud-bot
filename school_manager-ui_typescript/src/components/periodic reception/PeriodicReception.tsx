import React, { useEffect } from 'react';
import Store from '../../store';
import { observer } from 'mobx-react';
import { FaSearch } from 'react-icons/fa';
import { ClipLoader } from "react-spinners";
import Container from '../containers/Container';
import Filters from '../filters/Filters';
import Table from '../table/Table';

interface Props {

}

const PeriodicReception: React.FC<Props> = () => {
    const { periodicReceptionStore } = Store;

    useEffect(() => {
        periodicReceptionStore.fetchPeriodicReceptionFilters()
            .then(() => {
                const dateFrom = `${new Date().getFullYear()}-01-01`;
                const dateTo = `${new Date().toISOString().slice(0, 10)}`;
                periodicReceptionStore.setDateFromTo(dateFrom, dateTo);
                periodicReceptionStore.setPeriodicReceptionFiltersDateToSend(dateFrom.split('-').reverse().join('/'), 0);
                periodicReceptionStore.setPeriodicReceptionFiltersDateToSend(dateTo.split('-').reverse().join('/'), 1);
            })
            .then(() => HandleCheckAll())
            .then(() => HandleSearchByCheckBox());
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    useEffect(() => {
        periodicReceptionStore.afterLeftTableUpdate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [periodicReceptionStore.leftTableCheckbox])

    const HandleOnChange = (titleName: string, name: string, checked: string, titleIndex: number, filterIndex: number, checkboxIndex: number) => {
        periodicReceptionStore.setPeriodicReceptionFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            periodicReceptionStore.setPeriodicReceptionFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) =>
                e.checked = periodicReceptionStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        periodicReceptionStore.setPeriodicReceptionFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach((e: any) => e.checked = false);
    }

    const HandleSelectedDateOption = (option: any) => {
        periodicReceptionStore.setPeriodicReceptionFiltersDateSelectedOption(option.split(','));
    }

    const HandleSelectedDateFrom = (date: string) => {
        periodicReceptionStore.setDateFromTo(date);
        periodicReceptionStore.setPeriodicReceptionFiltersDateToSend(date.split('-').reverse().join('/'), 0);
    }

    const HandleSelectedDateTo = (date: string) => {
        periodicReceptionStore.setDateFromTo(null, date);
        periodicReceptionStore.setPeriodicReceptionFiltersDateToSend(date.split('-').reverse().join('/'), 1);
    }

    const HandleClearDate = () => {
        periodicReceptionStore.setDateFromTo('', '');
        periodicReceptionStore.setPeriodicReceptionFiltersDateToSend(null, null, 'clear');
    }

    const HandleSearch = (tableIndex: number, e: any) => {
        periodicReceptionStore.allPeriodicReception && periodicReceptionStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e: any, tab: string, tableIndex: number, tableClass: string) => {
        if (periodicReceptionStore.allPeriodicReception) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            periodicReceptionStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        let body = periodicReceptionStore.periodicReceptionFiltersToSend;

        const setDates = (data: any) => {
            data.checked[0] = data.checked[0] && data.checked[0] !== '' ? data.checked[0] : `01/01/${new Date().getFullYear()} 00:00`;
            data.checked[1] = data.checked[1] && data.checked[1] !== '' ? data.checked[1] : `${new Date().toISOString().slice(0, 10).split('-').reverse().join('/')} 23:59`;
            return data;
        }

        body.pr_filters = [...body.pr_filters.filter((data: any) => data.name !== 'pr_filters'),
        ...periodicReceptionStore.periodicReceptionFiltersDateToSend.pr_filters.map((expense: any) => setDates(expense))];
        !sessionStorage.getItem('reload') ? periodicReceptionStore.fetchFilteredPeriodicReception(body) : sessionStorage.removeItem('reload');
    }

    return (
        <Container title='מצבת תקבולים מחזוריים' childrenClassName='periodic_reception' cartTo='/periodic-reception/reception-basket'>
            <div className='paymentReportFiltersContainer' >
                <Filters data={periodicReceptionStore.periodicReceptionFilters}
                    onChange={HandleOnChange}
                    dateSelectOption={HandleSelectedDateOption}
                    dateFrom={periodicReceptionStore.dateFrom}
                    dateTo={periodicReceptionStore.dateTo}
                    onDateFrom={HandleSelectedDateFrom}
                    onDateTo={HandleSelectedDateTo}
                    cleanDate={HandleClearDate} />
                {periodicReceptionStore.periodicReceptionFilters.length > 0 && <div className='paymentReportFiltersResetButtonContainer' >
                    <div className='paymentReportFiltersResetButtonPosition' style={{ position: 'relative' }} >
                        <input type='button' value='סמן הכל' className='paymentReportFiltersResetButton button' onClick={HandleCheckAll} />
                        <input type='button' value='נקה הכל' className='paymentReportFiltersResetButton button' onClick={HandleUnCheckAll} />
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={() => periodicReceptionStore.allPeriodicReception && HandleSearchByCheckBox()}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                                חיפוש
                            </div>
                        </div>
                    </div>
                </div>}
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh',
                height: periodicReceptionStore.leftTableHeight < periodicReceptionStore.rightTableHeight ? periodicReceptionStore.leftTableHeight : periodicReceptionStore.rightTableHeight
            }} >
                <div style={{ height: periodicReceptionStore.rightTablePeriodicReception.length < 10 ? 'fit-content' : 'auto', marginRight: 'calc(5em + 5px)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <div className='paymentReportTableSearchPosition' style={{ width: '50%' }} >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={periodicReceptionStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                    </div>
                    <Table header={['שם', 'מספר תקבולים', 'סך תקבולים']}
                        rightTable
                        data={periodicReceptionStore.rightTablePeriodicReception}
                        tableCheckbox={periodicReceptionStore.rightTableCheckbox}
                        tableSelectedItems={periodicReceptionStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => periodicReceptionStore.allPeriodicReception && periodicReceptionStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => periodicReceptionStore.setRightTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => periodicReceptionStore.setRightTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${periodicReceptionStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${periodicReceptionStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>מנחים</div>
                            <div className={`paymentReportRightTableTab ${periodicReceptionStore.selectedRightTableTab === 'student' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'student', 1, '.paymentReportRightTableTab')}>תלמידים</div>
                            <div className={`paymentReportRightTableTab ${periodicReceptionStore.selectedRightTableTab === 'donator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'donator', 1, '.paymentReportRightTableTab')}>תורמים</div>
                        </div>
                        {!periodicReceptionStore.allPeriodicReception && <div className='paymentReportTableSpin' ><ClipLoader loading size='2.5em' color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: periodicReceptionStore.leftTablePeriodicReception.length < 10 ? 'fit-content' : 'auto', marginLeft: '4em' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '-1em' }}>
                        <input type='button' value='הוספת תקבול מחזורי' style={{ marginRight: '1em' }} />
                        <div className='paymentReportTableSearchPosition' style={{ width: '20%' }} >
                            <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                                value={periodicReceptionStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                            <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                        </div>
                    </div>
                    <Table header={['שם מלא', 'מזהה', 'תאריך לחיוב', 'הערות', 'סטטוס לתקבול', 'סכום', 'אמצעי', 'סך כשלונות', 'סך הצלחות', 'יתרת חיובים', 'סה"כ סכום שנגבה', 'מספר חיובים', 'תאריך ביטול הרשאה', 'תאריך קבלת הרשאה', 'תאריך אחרון']}
                        noEdit
                        noFottTitle={['מזהה']}
                        data={periodicReceptionStore.leftTablePeriodicReception}
                        tableCheckbox={periodicReceptionStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => periodicReceptionStore.setLeftTableCheckbox(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => periodicReceptionStore.setLeftTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }} >
                        {!periodicReceptionStore.allPeriodicReception && <div className='paymentReportTableSpin' ><ClipLoader loading size='2.5em' color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
        </Container>
    );
}

export default observer(PeriodicReception);