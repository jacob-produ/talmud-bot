import React, { useState, useEffect } from 'react';
// import { useHistory } from 'react-router-dom';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import PaymentsBasketFilters from '../payment report/FinanceReportFilters';
import { FaSearch } from 'react-icons/fa';
import Table from '../Table';
import { Spin } from "react-loading-io";
import '../../styles/payment report/PaymentReport.css';
const fileDownload = require('js-file-download');

const StudentsBasket = (props) => {
    // const history = useHistory();
    const { receptionBasketStore } = props.rootStore;
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);

    useEffect(() => {
        receptionBasketStore.fetchReceptionBasketFilters().then(() => HandleCheckAll()).then(() => HandleSearchByCheckBox());

        window.onresize = (e) => {
            setWindowWidth(e.target.innerWidth);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    useEffect(() => {
        receptionBasketStore.afterLeftTableUpdate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [receptionBasketStore.leftTableReceptionBasket])

    const HandleOnChange = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex) => {
        receptionBasketStore.setReceptionBasketFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            receptionBasketStore.setReceptionBasketFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e =>
                e.checked = receptionBasketStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        receptionBasketStore.setReceptionBasketFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = false);
    }

    const HandleSearch = (tableIndex, e) => {
        receptionBasketStore.allReceptionBasket && receptionBasketStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e, tab, tableIndex, tableClass) => {
        if (receptionBasketStore.allReceptionBasket) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            receptionBasketStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        receptionBasketStore.fetchFilteredReceptionBasket(receptionBasketStore.receptionBasketFiltersToSend)
    }

    // const HandleSelectedLeftTableSelectedItem = (item) => {
    // }

    const HandlePrint = (onlyShown) => {
        receptionBasketStore.fetchPrint(onlyShown)
            .then(res => {
                if (res.ok) {
                    const header = res.headers.get('Content-Disposition');
                    if (header) {
                        HandleSearchByCheckBox();
                        const fileName = header.slice(header.indexOf('filename=') + 9, header.length - 1);
                        res.blob().then(file => fileDownload(file, fileName));
                    }
                }
            })
    }

    return (
        <Container title='סל תקבולים' childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className='paymentReportFiltersContainer' >
                <PaymentsBasketFilters data={receptionBasketStore.receptionBasketFilters}
                    onChange={HandleOnChange} />
                {receptionBasketStore.receptionBasketFilters.length > 0 && <div className='paymentReportFiltersResetButtonContainer' >
                    <div className='paymentReportFiltersResetButtonPosition' >
                        <input type='button' value='סמן הכל' className='paymentReportFiltersResetButton button' onClick={HandleCheckAll} />
                        <input type='button' value='נקה הכל' className='paymentReportFiltersResetButton button' style={{ margin: '0.5em 0' }} onClick={HandleUnCheckAll} />
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={HandleSearchByCheckBox}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                                חיפוש
                            </div>
                        </div>
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={HandleSearchByCheckBox}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                בצע רישום
                            </div>
                        </div>
                    </div>
                    <div className='paymentReportFiltersResetButtonPosition' style={{ marginRight: '50px' }} >
                        <input type='button' value='הדפס הכל' className='paymentReportFiltersResetButton button' onClick={() => HandlePrint()} />
                        <input type='button' value='הדפס מוצגים' className='paymentReportFiltersResetButton button' onClick={() => HandlePrint(true)} />
                    </div>
                </div>}
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh', fontSize: windowWidth <= 1600 ? '0.85em' : '0.8em',
                height: receptionBasketStore.leftTableHeight < receptionBasketStore.rightTableHeight ? receptionBasketStore.leftTableHeight : receptionBasketStore.rightTableHeight
            }} >
                <div style={{ height: receptionBasketStore.rightTableReceptionBasket.length < 10 && 'fit-content', marginRight: 'calc(5em + 5px)' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={receptionBasketStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={['שם', 'תאריך לשידור', 'יתרה כוללת', 'סמן להדפסה']}
                        rightTable
                        data={receptionBasketStore.rightTableReceptionBasket}
                        tableCheckbox={receptionBasketStore.rightTableCheckbox}
                        tableSelectedItems={receptionBasketStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => receptionBasketStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => receptionBasketStore.changeCheckbox(checked, item, 1)}
                        changePaymentMethod={(paymentMethod, item) => receptionBasketStore.changePaymentMethod(paymentMethod, item, 1)}
                        paymentMethods={receptionBasketStore.generalLists?.income_payment_methods}
                        noEdit
                        changeCheckDate={(date, item) => receptionBasketStore.changeCheckDate(date, item, 1)}
                        changeForMonth={(date, item) => receptionBasketStore.changeForMonth(date, item, 1)}
                        changeSum={(sum, item) => receptionBasketStore.changeCheckSum(sum, item, 1)}
                        delete={(item) => receptionBasketStore.delete(item, 1)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => receptionBasketStore.setRightTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: receptionBasketStore.leftTableHeight < receptionBasketStore.rightTableHeight && receptionBasketStore.leftTableHeight
                        }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${receptionBasketStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${receptionBasketStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>סניפים</div>
                            <div className={`paymentReportRightTableTab ${receptionBasketStore.selectedRightTableTab === 'student' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'student', 1, '.paymentReportRightTableTab')}>מנחים</div>
                        </div>
                        <div className='paymentReportRightTableSum' >שורת סיכום</div>
                        {!receptionBasketStore.allReceptionBasket && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: receptionBasketStore.leftTableReceptionBasket.length < 10 && 'fit-content', marginLeft: '4em' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={receptionBasketStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={['מזהה', 'שם מלא', 'נייד', 'כתובת', 'גיל', 'מועד לביצוע', 'רישום', 'שיטת מלגה', 'שיטת תשלום', 'זמן ביום', 'שיטת זכאות', 'דרגת זכאות']}
                        data={receptionBasketStore.leftTableReceptionBasket}
                        noFottTitle={['שם מלא']}
                        // tableCheckbox={receptionBasketStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => receptionBasketStore.changeCheckbox(checked, item, 0, index)}
                        // changeTableSelectedItems={(checked, index, item) => HandleSelectedLeftTableSelectedItem(item)}
                        changePaymentMethod={(paymentMethod, item, index) => receptionBasketStore.changePaymentMethod(paymentMethod, item, 0, index)}
                        paymentMethods={receptionBasketStore.generalLists?.income_payment_methods}
                        noEdit
                        changeCheckDate={(date, item, index) => receptionBasketStore.changeCheckDate(date, item, 0, index)}
                        changeForMonth={(date, item, index) => receptionBasketStore.changeForMonth(date, item, 0, index)}
                        changeSum={(sum, item, index) => receptionBasketStore.changeCheckSum(sum, item, 0, index)}
                        delete={(item) => receptionBasketStore.delete(item, 0)}
                        bankAccount={receptionBasketStore.bankAccount}
                        changeBankAccountId={(date, item, index) => receptionBasketStore.changeBankAccountId(date, item, 0, index)}
                        changeTrendCoordinatorId={(date, item, index) => receptionBasketStore.changeTrendCoordinatorId(date, item, 0, index)}
                        trendCoordinator={receptionBasketStore.trendCoordinator}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => receptionBasketStore.setLeftTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: receptionBasketStore.leftTableHeight > receptionBasketStore.rightTableHeight && receptionBasketStore.rightTableHeight
                        }} >
                        <div className='paymentReportTableTabsPosition' style={{ right: '100%' }}>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'donations', 0, '.paymentReportLeftTableTab')}>תלמידים</div>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'donations', 0, '.paymentReportLeftTableTab')}>עובדים</div>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'donations', 0, '.paymentReportLeftTableTab')}>ספקים</div>
                        </div>
                        {!receptionBasketStore.allReceptionBasket && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
        </Container>
    )
}

export default inject('rootStore')(observer(StudentsBasket));