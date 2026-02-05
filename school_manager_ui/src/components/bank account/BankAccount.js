import React, { useEffect } from 'react';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import { FaSearch } from 'react-icons/fa';
import Table from '../Table';
import { Spin } from "react-loading-io";
import MakeLink from './MakeLinkPopUp';
import '../../styles/payment report/PaymentReport.css';

const BankAccount = (props) => {
    const { bankAccountStore } = props.rootStore;

    useEffect(() => {
        bankAccountStore.fetchBankAccount();
        bankAccountStore.fetchCurrentAccount();
        bankAccountStore.fetchTrendCoordinator();
        bankAccountStore.fetchStudens();
        bankAccountStore.fetchSuppliers();
        bankAccountStore.fetchDonators();

        return () => {
            bankAccountStore.setDateFromTo('', '');
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [])

    const HandleSearch = (tableIndex, e) => {
        ((bankAccountStore.allBankAccount && tableIndex === 1) || (bankAccountStore.allCurrentAccount && tableIndex === 0)) &&
            bankAccountStore.setTableSearch(tableIndex, e.target.value);
    }

    const HandleChangeCheckBox = (e, position) => {
        e && position ? bankAccountStore.changeCheckBoxFilter(e.target.checked, position) :
            Object.keys(bankAccountStore.checkBoxFilter).map(key => bankAccountStore.changeCheckBoxFilter(true, key));
    }

    return (
        <Container title='חשבונות בנק - עובר ושב' childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '15px' }} >
                <div style={{ marginLeft: '10px', whiteSpace: 'nowrap' }}>תאריך תנועה:</div>
                <input type='date' value={bankAccountStore.dateFrom} style={{ fontSize: '1em', marginLeft: '10px' }} onChange={e => bankAccountStore.setDateFromTo(e.target.value)} />
                <input type='date' value={bankAccountStore.dateTo} style={{ fontSize: '1em', marginLeft: '10px' }} onChange={e => bankAccountStore.setDateFromTo(null, e.target.value)} />
                <div style={{ color: 'blue', textDecoration: 'underline', cursor: 'pointer', marginLeft: '10px' }} onClick={() => bankAccountStore.setDateFromTo('', '')}>נקה</div>
                <div className='button' onClick={() => bankAccountStore.allCurrentAccount && bankAccountStore.fetchCurrentAccount()}
                    style={{ display: 'flex', padding: '0.2em 1em' }} >
                    <FaSearch style={{ marginLeft: '3px' }} size='1em' fill='black' />
                    חיפוש
                </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '15px' }}>
                <label style={{ cursor: 'pointer' }}>
                    <input className='checkboxFinanceReportFilter' type='checkbox'
                        checked={bankAccountStore.checkBoxFilter.linked} onChange={e => HandleChangeCheckBox(e, 'linked')} />
                    הצג מקושרים
                </label>
                <label style={{ cursor: 'pointer', marginRight: '10px' }}>
                    <input className='checkboxFinanceReportFilter' type='checkbox'
                        checked={bankAccountStore.checkBoxFilter.unlinked} onChange={e => HandleChangeCheckBox(e, 'unlinked')} />
                    הצג לא מקושרים
                </label>
                <div style={{ color: 'blue', textDecoration: 'underline', cursor: 'pointer', marginRight: '10px' }} onClick={HandleChangeCheckBox}>סמן הכל</div>
            </div>
            <div className='paymentReportTablesContainer' style={{
                maxHeight: '50vh',
                height: bankAccountStore.leftTableHeight < bankAccountStore.rightTableHeight ? bankAccountStore.leftTableHeight : bankAccountStore.rightTableHeight
            }} >
                <div style={{ height: bankAccountStore.rightTableBankAccount.length < 10 && 'fit-content', marginRight: 'calc(5em + 5px)' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={bankAccountStore.rightTableSearch} onChange={(e) => HandleSearch(1, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={['מספר חשבון', 'מוסד', 'מסגרת', 'הלוואות', 'התחייבויות', 'נזיל', 'תזרים', 'תזרים חודשי', 'יתרה']}
                        data={bankAccountStore.rightTableBankAccount}
                        tableSelectedItems={bankAccountStore.rightTableSelectedItems}
                        changeTableSelectedItems={(checked, index, item) => bankAccountStore.allCurrentAccount && bankAccountStore.setRightTableSelectedItems(checked, index, item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => bankAccountStore.setRightTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }}>
                        <div className='paymentReportTableTabsPosition' style={{ left: '100%' }}>
                            <div className={`paymentReportRightTableTab selectedTab ${bankAccountStore.selectedRightTableTab === 'institution' && 'selectedTab'}`} onClick={e => { }}>חשבונות</div>

                        </div>
                        <div className='paymentReportRightTableSum' >שורת סיכום</div>
                        {!bankAccountStore.allBankAccount && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
                <div style={{ height: bankAccountStore.leftTableBankAccount.length < 10 && 'fit-content' }}>
                    <div className='paymentReportTableSearchPosition' >
                        <input className='paymentReportTableSearchInput' type='text' placeholder='חיפוש'
                            value={bankAccountStore.leftTableSearch} onChange={(e) => HandleSearch(0, e)} />
                        <FaSearch className='paymentReportTableSearchIcon' size='1em' fill='black' />
                    </div>
                    <Table header={['תאריך', 'יום ערך', 'סכום', 'יתרה', 'אסמכתה', 'תיאור', 'בצע קישור']}
                        data={bankAccountStore.leftTableBankAccount}
                        doNotSum={['יתרה']}
                        makeLink={item => bankAccountStore.setMakeLink(item)}
                        style={{ height: 'calc(100% - 3em)' }}
                        tableHeight={height => bankAccountStore.setLeftTableHeight(height)}
                        tableStyle={{ display: 'block', overflow: 'auto', minHeight: '15em', height: '100%' }} >
                        {!bankAccountStore.allCurrentAccount && <div className='paymentReportTableSpin' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                    </Table>
                </div>
            </div>
            {bankAccountStore.makeLink && <MakeLink />}
        </Container>
    )
}

export default inject('rootStore')(observer(BankAccount));