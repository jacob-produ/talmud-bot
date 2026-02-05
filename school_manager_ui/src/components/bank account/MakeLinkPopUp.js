import React, { useEffect } from 'react';
import { inject, observer } from 'mobx-react';
import { MdClose, MdNavigateBefore, MdNavigateNext } from 'react-icons/md';
import { BiShekel } from 'react-icons/bi';
import { Spin } from "react-loading-io";

const MakeLinkPopUp = (props) => {
    const { bankAccountStore } = props.rootStore;

    useEffect(() => {
        const makeLinkIndex = bankAccountStore.leftTableBankAccount.findIndex(makeLink => makeLink === bankAccountStore.makeLink);
        bankAccountStore.setIndex(makeLinkIndex);

        const rightBankAccount = bankAccountStore.rightTableBankAccount.find(bankAccount => bankAccount.id === bankAccountStore.makeLink.fk_bank_account_id);
        bankAccountStore.setRightBankAccount(rightBankAccount);
        // eslint-disable-next-line react-hooks/exhaustive-deps        
    }, [bankAccountStore.makeLink])

    const HandleClose = () => {
        if (!bankAccountStore.loader) {
            bankAccountStore.setMakeLink(null);
            ClearData();
        }
    }

    const HandleNext = () => {
        if (!bankAccountStore.loader && !!bankAccountStore.leftTableBankAccount[bankAccountStore.index + 1]) {
            bankAccountStore.setMakeLink(bankAccountStore.leftTableBankAccount[bankAccountStore.index + 1]);
            ClearData();
        }
    }

    const HandlePrev = () => {
        if (!bankAccountStore.loader && bankAccountStore.index > 0) {
            bankAccountStore.setMakeLink(bankAccountStore.leftTableBankAccount[bankAccountStore.index - 1]);
            ClearData();
        }
    }

    const ClearData = () => {
        bankAccountStore.setTrendCoordinator(null);
        bankAccountStore.setStudent(null);
        bankAccountStore.setSupplier(null);
        bankAccountStore.setMSV(null);
        bankAccountStore.setComment(null);
    }

    const ShowIncomeExpenseDetails = () => {

        const bank_account = bankAccountStore.makeLink.bank_account.length > 0 && bankAccountStore.makeLink.bank_account[0];
        const donator = bankAccountStore.ownDonator
        return bankAccountStore.makeLink.bank_account.length > 0 && <div>
            <div>{`שם בעל חשבון: ${bank_account.username} | מספר סניף: ${bank_account.branch_number} | מספר חשבון: ${bank_account.account_number} | מספר בנק:  ${bank_account.bank_number}`}</div>
            {donator && <div>{`שם התורם במערכת: ${donator.first_name} ${donator.last_name} | שם קבלה: ${donator.billing_name} | ת.ז: ${donator.identity}`}</div>}
        </div>
    }

    return (
        <div id='popupContainer'>
            <div className='makeLinkPopup' >
                <div className='makeLinkPopup__close' >
                    <MdClose size='1em' style={{ cursor: 'pointer' }} onClick={HandleClose} />
                </div>
                <div className='makeLinkPopup__header' >
                    <div className='makeLinkPopup__header__newAccount' onClick={HandlePrev} style={{ cursor: bankAccountStore.index === 0 ? 'not-allowed' : 'pointer', opacity: bankAccountStore.index === 0 && '0.4' }}>
                        <MdNavigateNext size='2em' /> הקודם
                    </div>
                    <div style={{ textDecoration: 'underline' }}>{bankAccountStore.rightBankAccount && `${bankAccountStore.rightBankAccount.institution_name}, חשבון בנק: ${bankAccountStore.rightBankAccount.account_number}`}</div>
                    <div className='makeLinkPopup__header__newAccount' onClick={HandleNext} style={{ cursor: !bankAccountStore.leftTableBankAccount[bankAccountStore.index + 1] ? 'not-allowed' : 'pointer', opacity: !bankAccountStore.leftTableBankAccount[bankAccountStore.index + 1] && '0.4' }}>
                        הבא <MdNavigateBefore size='2em' />
                    </div>
                </div>
                <div className='makeLinkPopup__details' >
                    <div>{bankAccountStore.makeLink.date.slice(0, 10).split('-').reverse().join('/')}</div>
                    <div style={{ textAlign: 'center' }}>
                        <div>תיאור: {bankAccountStore.makeLink.transaction_description}</div>
                        <div>אסמכתה: {bankAccountStore.makeLink.reference_number}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}><BiShekel size='1.1em' />{Math.abs(bankAccountStore.makeLink.transaction_amount)}{bankAccountStore.makeLink.transaction_amount < 0 ? '-' : ''}</div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-evenly' }}>
                    <ShowIncomeExpenseDetails />
                </div>
                <div className='makeLinkPopup__form' >

                    <div style={{ width: '17%' }}>
                        <div className='makeLinkPopup__form__label' >תורם</div>
                        <div>
                            <datalist id='donator-list' style={{ fontSize: '0.5em' }} >
                                {bankAccountStore.allDonators.map(donator =>
                                    <option key={donator.id} value={`${donator.first_name} ${donator.last_name} - ${donator.identity}`} style={{ fontSize: '0.5em' }} />)}
                            </datalist>
                            <input list='donator-list' className='makeLinkPopup__listInput' disabled={!bankAccountStore.makeLink.is_linked} placeholder='בחר תורם'
                                value={bankAccountStore.donator || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setDonator(e.target.value)} />
                        </div>
                    </div>

                    <div style={{ width: '17%' }}>
                        <div className='makeLinkPopup__form__label' >מנחה</div>
                        <div>
                            <datalist id='trends-list' style={{ fontSize: '0.5em' }} >
                                {bankAccountStore.allTrendCoordinator.map(trend =>
                                    <option key={trend.id} value={`${trend.name} - ${trend.id}`} style={{ fontSize: '0.5em' }} />)}
                            </datalist>
                            <input list='trends-list' className='makeLinkPopup__listInput' disabled={!bankAccountStore.makeLink.is_linked} placeholder='בחר מנחה'
                                value={bankAccountStore.trendCoordinator?.split(' - ')[0] || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setTrendCoordinator(e.target.value)} />
                        </div>
                    </div>
                    <div style={{ width: '17%' }}>
                        <div className='makeLinkPopup__form__label'>סטודנט</div>
                        <div>
                            <datalist id='students-list'>
                                {bankAccountStore.allStudents.map(student =>
                                    <option key={student.id} value={`${student.first_name} ${student.last_name} - ${student.identity}`} />)}
                            </datalist>
                            <input list='students-list' readOnly={bankAccountStore.allStudents?.length === 0} disabled={!bankAccountStore.makeLink.is_linked || bankAccountStore.existMsv || bankAccountStore.existSupplier} placeholder='בחר סטודנט'
                                className='makeLinkPopup__listInput' value={bankAccountStore.student || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setStudent(e.target.value)} />
                        </div>
                    </div>
                    <div style={{ width: '17%' }}>
                        <div className='makeLinkPopup__form__label'>ספק</div>
                        <div>
                            <datalist id='supplier-list'>
                                {bankAccountStore.allSuppliers.map(supplier =>
                                    <option key={supplier.id} value={`${supplier.name} - ${supplier.identity}`} />)}
                            </datalist>
                            <input list='supplier-list' readOnly={bankAccountStore.allSuppliers?.length === 0} disabled={!bankAccountStore.makeLink.is_linked || bankAccountStore.existMsv || bankAccountStore.existStudent} placeholder='בחר ספק'
                                className='makeLinkPopup__listInput' value={bankAccountStore.supplier || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setSupplier(e.target.value)} />
                        </div>
                    </div>
                    <div style={{ width: '17%' }}>
                        <div className='makeLinkPopup__form__label'>קובץ מס"ב</div>
                        <div>
                            <datalist id='msv-list'>
                                {bankAccountStore.allMSV && bankAccountStore.allMSV.map(msv =>
                                    <option key={msv.id} value={`${msv.amount} - ${msv.date} - ${msv.id}`} />)}
                            </datalist>
                            <input list='msv-list' readOnly={bankAccountStore.allMSV?.length === 0} placeholder='בחר קובץ מס"ב' className='makeLinkPopup__listInput' disabled={bankAccountStore.existStudent || bankAccountStore.existSupplier}
                                value={bankAccountStore.msv?.split(' - ')[0] || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setMSV(e.target.value)} />
                        </div>
                    </div>
                </div>
                {!bankAccountStore.makeLink.is_linked && <div style={{ textAlign: 'center' }}>רשומת העו"ש הנ"ל אינה מקושרת לשום רשומת הכנסה או הוצאה, לכן לא ניתן לשייכה למנחה, סטודנט או ספק.</div>}
                {(bankAccountStore.existMsv || bankAccountStore.existStudent || bankAccountStore.existSupplier) && <div style={{ textAlign: 'center' }}>הרשומה שיוכה {(bankAccountStore.existMsv && 'למס"ב') || (bankAccountStore.existStudent && 'לסטודנט') || (bankAccountStore.existSupplier && 'לספק')}, לכן לא ניתן לשייך את הרשומה {(bankAccountStore.existMsv && 'לסטודנט או ספק') || (bankAccountStore.existStudent && 'לספק או מס"ב') || (bankAccountStore.existSupplier && 'לסטודנט או ספק')}. הסר את השיוך הנ"ל אם ברצונך לבצע שינוי בשיוך</div>}
                <div style={{ display: 'flex', justifyContent: 'space-evenly', alignItems: 'center', marginTop: '50px' }}>
                    <textarea style={{ resize: 'none', width: '60%', height: '35vh' }} placeholder='הזן הערות' value={bankAccountStore.comment || ''} onChange={e => !bankAccountStore.loader && bankAccountStore.setComment(e.target.value)}>

                    </textarea>
                    <div className='makeLinkPopup__button__container' >
                        <div className='button makeLinkPopup__button' style={{ visibility: 'hidden' }}>הפקת קבלה</div>
                        <div className='button makeLinkPopup__button' style={{ marginTop: '20px' }} onClick={() => !bankAccountStore.loader && bankAccountStore.fetchSave()}>שמור</div>
                    </div>
                </div>
                {bankAccountStore.loader && <div className='makeLinkPopup__loader' ><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
            </div>
        </div >
    )
}

export default inject('rootStore')(observer(MakeLinkPopUp));