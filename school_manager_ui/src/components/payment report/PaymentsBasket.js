import React, { useState, useEffect } from 'react';
// import { useHistory } from 'react-router-dom';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import PaymentsBasketFilters from './FinanceReportFilters';
import { FaSearch } from 'react-icons/fa';
import Table from '../Table';
import { Spin } from "react-loading-io";
import '../../styles/payment report/PaymentReport.css';
const fileDownload = require('js-file-download');

const PaymentsBasket = (props) => {
    // const history = useHistory();
    const { paymentsBasketStore } = props.rootStore;
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);
    const [checkConsolidation, setCheckConsolidation] = useState('');

    useEffect(() => {
        paymentsBasketStore.fetchPaymentsBasketFilters().then(() => HandleCheckAll()).then(() => HandleSearchByCheckBox());

        window.onresize = (e) => {
            setWindowWidth(e.target.innerWidth);
        }

        return () => {
            paymentsBasketStore.changeMergedCheckbox(null, null, true);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    useEffect(() => {
        paymentsBasketStore.afterLeftTableUpdate();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [paymentsBasketStore.leftTablePaymentsBasket])

    const HandleOnChange = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex) => {
        paymentsBasketStore.setPaymentsBasketFiltersToSend(titleName, name, checked, titleIndex, filterIndex, checkboxIndex);
    }

    const HandleCheckAll = () => {
        if (!sessionStorage.getItem('reload')) {
            paymentsBasketStore.setPaymentsBasketFiltersToSend(null, null, null, null, null, null, 'checkAll');
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = true);
        }
        else {
            document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e =>
                e.checked = paymentsBasketStore.checkedFilters[e.getAttribute('title_index') - 1][e.getAttribute('filter_index')][e.getAttribute('checkbox_index')]);
        }
    }

    const HandleUnCheckAll = () => {
        paymentsBasketStore.setPaymentsBasketFiltersToSend(null, null, null, null, null, null, 'unCheckAll');
        document.querySelectorAll('.checkboxFinanceReportFilter').forEach(e => e.checked = false);
    }

    const HandleSearch = (tableIndex, e) => {
        paymentsBasketStore.allPaymentsBasket && paymentsBasketStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleSelectedTableTab = (e, tab, tableIndex, tableClass) => {
        if (paymentsBasketStore.allPaymentsBasket) {
            document.querySelectorAll(tableClass).forEach(e => e.classList.remove('selectedTab'));
            e.currentTarget.classList.add('selectedTab');
            paymentsBasketStore.setSelectedTableTab(tableIndex, tab);
        }
    }

    const HandleSearchByCheckBox = () => {
        paymentsBasketStore.fetchFilteredPaymentsBasket(paymentsBasketStore.paymentsBasketFiltersToSend)
    }

    // const HandleSelectedLeftTableSelectedItem = (item) => {
    // }

    const HandlePrint = (onlyShown) => {
        paymentsBasketStore.fetchPrint(onlyShown,checkConsolidation)
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

    const checkConsolidationHandle = (e)=>{
        setCheckConsolidation(e.target.value)
    }
    return (
        <Container title='סל תשלומים' goBack childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div className='paymentReportFiltersContainer' >
                <PaymentsBasketFilters data={paymentsBasketStore.paymentsBasketFilters}
                    onChange={HandleOnChange} />
                {paymentsBasketStore.paymentsBasketFilters.length > 0 && <div className='paymentReportFiltersResetButtonContainer' >
                    <div className='paymentReportFiltersResetButtonPosition' >
                        <input type='button' value='סמן הכל' className='paymentReportFiltersResetButton button' onClick={HandleCheckAll} />
                        <input type='button' value='נקה הכל' className='paymentReportFiltersResetButton button' onClick={HandleUnCheckAll} />
                        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '6em' }}>
                            <div className='button' onClick={HandleSearchByCheckBox}
                                style={{ display: 'flex', width: '100%', padding: '0.5em 1em', fontSize: '1.1em' }} >
                                <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                                חיפוש
                            </div>
                        </div>
                    </div>
                    <div className='paymentReportFiltersResetButtonPosition' style={{ marginRight: '50px' }} >
                        <select  style={{width:'100%' }} value={checkConsolidation} onChange={checkConsolidationHandle} >
                            <option value="" selected disabled>קיבוץ שיקים</option>
                            <option value="trend_coordinator">מנחה</option>
                            <option value="branch">סניף</option>
                        </select>
                        <input type='button' value='הדפס הכל' className='paymentReportFiltersResetButton button' onClick={() => HandlePrint()} style={{width:'100%' }}/>
                        <input type='button' value='הדפס מוצגים' className='paymentReportFiltersResetButton button' onClick={() => HandlePrint(true)} style={{width:'100%' }} />
                        <input type='button' value='בצע איחוד' className='paymentReportFiltersResetButton button' onClick={() => paymentsBasketStore.fetchMerge()} style={{width:'100%' }}/>
                    </div>

                </div>}
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh', fontSize: windowWidth <= 1600 ? '0.85em' : '0.8em',
                height: paymentsBasketStore.leftTableHeight < paymentsBasketStore.rightTableHeight ? paymentsBasketStore.leftTableHeight : paymentsBasketStore.rightTableHeight
            }} >
                <div style={{ height: paymentsBasketStore.rightTablePaymentsBasket.length < 10 && 'fit-content', marginRight: 'calc(5em + 5px)' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={paymentsBasketStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={paymentsBasketStore.selectedRightTableTab === 'institution' ?
                        (windowWidth > 1600 ? ['שם', 'סך עובדים', 'סך תלמידים', 'סך הדפסות', 'צורת תשלום', 'עבור חודש', 'תאריך לשידור', 'סכום לתשלום', 'סכום כולל', 'יתרה כוללת', 'סמן להדפסה', ''] :
                            ['שם', 'צורת תשלום', 'עבור חודש', 'תאריך לשידור', 'סכום לתשלום', 'סכום כולל', 'יתרה כוללת', 'סמן להדפסה', '']) :
                        (windowWidth > 1600 ? ['שם', 'סך תלמידים', 'סך הדפסות', 'צורת תשלום', 'עבור חודש', 'תאריך לשידור', 'סכום לתשלום', 'סכום כולל', 'יתרה כוללת', 'סמן להדפסה', ''] :
                            ['שם', 'צורת תשלום', 'עבור חודש', 'תאריך לשידור', 'סכום לתשלום', 'סכום כולל', 'יתרה כוללת', 'סמן להדפסה', ''])}
                        rightTable
                        data={paymentsBasketStore.rightTablePaymentsBasket}
                        tableCheckbox={paymentsBasketStore.rightTableCheckbox}
                        tableSelectedItems={paymentsBasketStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => paymentsBasketStore.setRightTableSelectedItems(checked, index, item)}
                        changeCheckbox={(checked, index, item) => paymentsBasketStore.changeCheckbox(checked, item, 1)}
                        changePaymentMethod={(paymentMethod, item) => paymentsBasketStore.changePaymentMethod(paymentMethod, item, 1)}
                        paymentMethods={paymentsBasketStore.generalLists?.expense_payment_methods}
                        allowEdit
                        changeCheckDate={(date, item) => paymentsBasketStore.changeCheckDate(date, item, 1)}
                        changeForMonth={(date, item) => paymentsBasketStore.changeForMonth(date, item, 1)}
                        changeSum={(sum, item) => paymentsBasketStore.changeCheckSum(sum, item, 1)}
                        delete={(item) => paymentsBasketStore.delete(item, 1)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => paymentsBasketStore.setRightTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: paymentsBasketStore.leftTableHeight < paymentsBasketStore.rightTableHeight && paymentsBasketStore.leftTableHeight
                        }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab ${paymentsBasketStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'institution', 1, '.paymentReportRightTableTab')}>מוסדות</div>
                            <div className={`paymentReportRightTableTab ${paymentsBasketStore.selectedRightTableTab === 'branch' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'branch', 1, '.paymentReportRightTableTab')}>סנפים</div>
                            <div className={`paymentReportRightTableTab ${paymentsBasketStore.selectedRightTableTab === 'trend_coordinator' && 'selectedTab'}`} onClick={e => HandleSelectedTableTab(e, 'trend_coordinator', 1, '.paymentReportRightTableTab')}>מנחים</div>
                        </div>
                        <div className='paymentReportRightTableSum' >שורת סיכום</div>
                        {!paymentsBasketStore.allPaymentsBasket && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: paymentsBasketStore.leftTablePaymentsBasket.length < 10 && 'fit-content', marginLeft: '4em' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={paymentsBasketStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={['מזהה', 'שם מלא', 'סכום', 'צורת תשלום', 'עבור חודש', 'תאריך לשידור', 'יתרה כוללת', 'חשבון בנק', 'מנחה', 'סמן להדפסה', 'איחוד תשלום', 'סמן לאיחוד', '']}
                        data={paymentsBasketStore.leftTablePaymentsBasket}
                        noFottTitle={['שם מלא']}
                        // tableCheckbox={paymentsBasketStore.leftTableCheckbox}
                        changeCheckbox={(checked, index, item) => paymentsBasketStore.changeCheckbox(checked, item, 0, index)}
                        mergedCheckbox={paymentsBasketStore.mergedCheckbox}
                        changeMergedCheckbox={(checked, id) => paymentsBasketStore.changeMergedCheckbox(checked, id)}
                        splitPayment={(merged_number) => paymentsBasketStore.fetchSplit(merged_number)}
                        // changeTableSelectedItems={(checked, index, item) => HandleSelectedLeftTableSelectedItem(item)}
                        changePaymentMethod={(paymentMethod, item, index) => paymentsBasketStore.changePaymentMethod(paymentMethod, item, 0, index)}
                        paymentMethods={paymentsBasketStore.generalLists?.expense_payment_methods}
                        allowEdit
                        changeCheckDate={(date, item, index) => paymentsBasketStore.changeCheckDate(date, item, 0, index)}
                        changeForMonth={(date, item, index) => paymentsBasketStore.changeForMonth(date, item, 0, index)}
                        changeSum={(sum, item, index) => paymentsBasketStore.changeCheckSum(sum, item, 0, index)}
                        delete={(item) => paymentsBasketStore.delete(item, 0)}
                        bankAccount={paymentsBasketStore.bankAccount}
                        changeBankAccountId={(date, item, index) => paymentsBasketStore.changeBankAccountId(date, item, 0, index)}
                        changeTrendCoordinatorId={(date, item, index) => paymentsBasketStore.changeTrendCoordinatorId(date, item, 0, index)}
                        trendCoordinator={paymentsBasketStore.trendCoordinator}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => paymentsBasketStore.setLeftTableHeight(height)}
                        tableStyle={{
                            display: 'block', overflow: 'auto', minHeight: '15em', height: '100%'
                            // height: paymentsBasketStore.leftTableHeight > paymentsBasketStore.rightTableHeight && paymentsBasketStore.rightTableHeight
                        }} >
                        <div className='paymentReportTableTabsPosition' style={{ right: '100%' }}>
                            <div className='paymentReportLeftTableTab selectedTab' onClick={e => HandleSelectedTableTab(e, 'student', 0, '.paymentReportLeftTableTab')}>תלמידים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'employee', 0, '.paymentReportLeftTableTab')}>עובדים</div>
                            <div className='paymentReportLeftTableTab' onClick={e => HandleSelectedTableTab(e, 'supplier', 0, '.paymentReportLeftTableTab')}>ספקים</div>
                        </div>
                        {!paymentsBasketStore.allPaymentsBasket && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
        </Container>
    )
}

export default inject('rootStore')(observer(PaymentsBasket));