import React, { useEffect,useState } from 'react';
import { observer } from 'mobx-react';
import Container from '../containers/Container';
import SelectData from './SelectData';
import { Spin } from "react-loading-io";
import Store from '../../store/RootStore';
import PopupTemplate from '../popup/PopupTemplate'
const fileDownload = require('js-file-download');



const UploadCSVFile = (props) => {
    const { uploadCSVFile } = Store;
    const [uploadData,setUploadData]=useState(null)
    const [popupIsShown,setPopupIsShown]=useState(false)
    const [googleSheetsToogle,setGoogleSheetsToogle]=useState(false)
    const [downloadJson,setDownloadJson]=useState(false)


    const regexNumber = /^\d+$/
    useEffect(() => {
        uploadCSVFile.callFetch();
        // eslint-disable-next-line
    }, [])

    useEffect(() => {
        console.log('useEffect');

        if(downloadJson){
        uploadCSVFile.sendData()
            .then(res => {
                console.log(downloadJson);

                    const newBlob = new Blob([JSON.stringify(res)], { type: 'application/json' });
                    const url = window.URL || window.webkitURL;
                    const link = document.createElement('a');
                    link.download = 'data.json';
                    link.href = url.createObjectURL(newBlob);
                    link.target = '_blank';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
            })
        }


    
    },[downloadJson])

    const HandleUploadCSV = () => {
        uploadCSVFile.sendData()
            .then(res => {
                const filteredData = res.filter(data=>data !==undefined)
                console.log(filteredData);
                setUploadData(filteredData)
                if(!googleSheetsToogle){

                    setPopupIsShown(true)
                }
            })
    }

    const Title = ({ title, template_from }) => {
        const HandleDownloadTemplate = () => {
            uploadCSVFile.fetchDownloadTemplate(template_from)
                .then(res => {
                    const header = res.headers.get('Content-Disposition');
                    if (header) {
                        const fileName = header.slice(header.indexOf('filename=') + 9, header.length - 1);
                        res.blob().then(file => fileDownload(file, fileName));
                    }
                })
        }

        return <div style={{ display: 'flex' }}>
            <div style={{ fontSize: '1.1em', fontWeight: 'bolder' }}>{title}</div>
            {template_from && <span style={{ marginRight: '10px', color: 'blue', cursor: 'pointer' }} onClick={HandleDownloadTemplate}>template</span>}
        </div>
    }


    const Label = ({ setFile, file, update, setUpdate, googleSheetsToggle,googleSheets,name }) => {
        return <div style={{ display: 'flex' }}>
            <label style={{ display: 'flex', cursor:!googleSheets?'pointer':'not-allowed',  width: 'fit-content',backgroundColor:!googleSheets?'none':'#858282'  }}>
                <input type='file' accept='.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'
                    style={{ display: 'none', backgroundColor:!googleSheets?'none':'#858282' }} disabled={uploadCSVFile.loader?uploadCSVFile.loader:googleSheets} cursor={!googleSheets?'pointer':'not-allowed'} value={e=> e.target.value} onClick={e => e.target.value=''} onChange={e => setFile(e.target.files[0] || null)} />
                <div style={{ display: 'flex', alignItem: 'center', paddingRight: '5px', border: '1px solid black', width: '20em', marginLeft: '5px', overflow: 'hidden' }}>{file?.name}</div>
                <div className='button paymentReportFiltersResetButton'
                    style={{ padding: '0.2em 0.5em',backgroundColor:!googleSheets?'none':'#858282',cursor:!googleSheets?'pointer':'not-allowed', disabled:googleSheets} }>
                    עיון
                </div>
            </label>
            <div style={{ display: 'flex', flexDirection:"column" }}>
            <label style={{ display: 'flex', alignItems: 'center',  marginRight: '5px' }}>
                <input type='checkbox' checked={!!update}  onChange={e => setUpdate && setUpdate(e.target.checked)} />
                עידכון
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', marginRight: '5px' }}>
                <input type='checkbox'  name={name} checked={googleSheets}  onChange={e => googleSheetsToggle(e.target.checked)} />
                Google Sheets
            </label>

            </div >
        </div>
    }

    const hidePopupHandler =()=>{
        setPopupIsShown(false)

    }
    return (
        <Container title='ייבוא נתונים מקובץ - גרסת פיתוח בלבד' >
            <div>
                {(popupIsShown || uploadCSVFile.loader) && <PopupTemplate  onClose = {hidePopupHandler}  data={uploadData} downloadJson={setDownloadJson}/>  }
                <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                    בחר את קבצי הנתונים אותם תרצה לייבא למערכת
                    <div>ולאחר מכן לחץ - שלח</div>
                </div>
                <div style={{ display: 'flex' }}>
                    <div style={{ width: '50%' }}>
                        {/* מוסדות וחשבונות בנק */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת מוסדות וחשבונות בנק' template_from='institution_bank_account' />
                            <Label name='institution_bank_account' setFile={file => uploadCSVFile.setInstitutionBankAccount(file)} file={uploadCSVFile.institutionBankAccount} googleSheets={uploadCSVFile.googleSheetsInstitutionBankAccount} googleSheetsToggle={uploadCSVFile.setGoogleSheetsInstitutionBankAccount} update={uploadCSVFile.institutionBankAccountUpdate} setUpdate={uploadCSVFile.setInstitutionBankAccountUpdate}/>
                            {uploadCSVFile.errorInstitutionBankAccount.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorInstitutionBankAccount}</div>}
                        </div>
                        {/* סניפים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת סניפים' template_from='branch' />
                            <Label name='branch' setFile={file => uploadCSVFile.setBranch(file)} file={uploadCSVFile.branch} googleSheetsToggle={uploadCSVFile.setGoogleSheetsBranch} googleSheets={uploadCSVFile.googleSheetsBranch} update={uploadCSVFile.branchUpdate} setUpdate={uploadCSVFile.setBranchUpdate}/>
                            {uploadCSVFile.errorBranch.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorBranch}</div>}
                        </div>
                        {/* מנחים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת מנחים' template_from='trend_coordinator' />
                            <Label name='trend_coordinator' setFile={file => uploadCSVFile.setTrendCoordinator(file)} file={uploadCSVFile.trendCoordinator} googleSheetsToggle={uploadCSVFile.setGoogleSheetsTrendCoordinator} googleSheets={uploadCSVFile.googleSheetsTrendCoordinator} update={uploadCSVFile.trendCoordinatorUpdate} setUpdate={uploadCSVFile.setTrendCoordinatorUpdate} />
                            {uploadCSVFile.errorTrendCoordinator.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorTrendCoordinator}</div>}
                        </div>
                        {/* הרשמה למסלולים ושיוכי מנחים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת הרשמה למסלולים ושיוכי מנחים' template_from='course_enrollment_trend_coordinator_attribution' />
                            <Label name='course_enrollment_trend_coordinator_attribution' setFile={file => uploadCSVFile.setCourseEnrollmentTrendCoordinatorAttribution(file)} file={uploadCSVFile.courseEnrollmentTrendCoordinatorAttribution} googleSheetsToggle={uploadCSVFile.setGoogleSheetsCourseEnrollmentTrendCoordinatorAttribution} googleSheets={uploadCSVFile.googleSheetsCourseEnrollmentTrendCoordinatorAttribution} update={uploadCSVFile.courseEnrollmentTrendCoordinatorAttributionUpdate} setUpdate={uploadCSVFile.setCourseEnrollmentTrendCoordinatorAttributionUpdate} />
                            {uploadCSVFile.errorCourseEnrollmentTrendCoordinatorAttribution.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorCourseEnrollmentTrendCoordinatorAttribution}</div>}
                        </div>
                        {/* נתוני תלמידים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני תלמידים' template_from='student' />
                            <Label name='student' setFile={file => uploadCSVFile.setStudents(file)} file={uploadCSVFile.students} googleSheetsToggle={uploadCSVFile.setGoogleSheetsStudents}   googleSheets={uploadCSVFile.googleSheetsStudents}  update={uploadCSVFile.studentsUpdate} setUpdate={uploadCSVFile.setStudentsUpdate}/>
                            {uploadCSVFile.errorStudents.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorStudents}</div>}
                        </div>
                        {/* הרשמה למסלולים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת הרשמה למסלולים' template_from='course_enrollment' />
                            <Label name='course_enrollment' setFile={file => uploadCSVFile.setCourseEnrollment(file)} file={uploadCSVFile.courseEnrollment} googleSheetsToggle={uploadCSVFile.setGoogleSheetsCourseEnrollment} googleSheets={uploadCSVFile.googleSheetsCourseEnrollment}  update={uploadCSVFile.courseEnrollmentUpdate} setUpdate={uploadCSVFile.setCourseEnrollmentUpdate}/>
                            {uploadCSVFile.errorCourseEnrollment.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorCourseEnrollment}</div>}
                        </div>
                        {/* נתוני ספקים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני ספקים' template_from='supplier' />
                            <Label name='supplier' setFile={file => uploadCSVFile.setSupplier(file)} file={uploadCSVFile.supplier} googleSheetsToggle={uploadCSVFile.setGoogleSheetsSupplier} googleSheets={uploadCSVFile.googleSheetsSupplier}  update={uploadCSVFile.supplierUpdate} setUpdate={uploadCSVFile.setSupplierUpdate}/>
                            {uploadCSVFile.errorSupplier.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorSupplier}</div>}
                        </div>
                        {/* תורמים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת תורמים' template_from='donator' />
                            <Label name='donator' setFile={file => uploadCSVFile.setDonator(file)} file={uploadCSVFile.donator} googleSheetsToggle={uploadCSVFile.setGoogleSheetsDonator} googleSheets={uploadCSVFile.googleSheetsDonator}  update={uploadCSVFile.donatorUpdate} setUpdate={uploadCSVFile.setDonatorUpdate} />
                            {uploadCSVFile.errorDonator.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorDonator}</div>}
                        </div>
                        {/* נתוני חשבונות בנק כלליים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני חשבונות בנק כלליים' template_from='general_bank_account' />
                            <SelectData titles={['שיוך']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.generalBanksAttribution} onChange={(e) => uploadCSVFile.setGeneralBanksAttribution(e.target.value)}>
                                        {uploadCSVFile.attributions.map(attribution => <option key={attribution} value={attribution}>{attribution}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='general_bank_account' setFile={file => uploadCSVFile.setGeneralBanks(file)} file={uploadCSVFile.generalBanks} googleSheetsToggle={uploadCSVFile.setGoogleSheetsGeneralBanks} googleSheets={uploadCSVFile.googleSheetsGeneralBanks}  update={uploadCSVFile.generalBanksUpdate} setUpdate={uploadCSVFile.setGeneralBanksUpdate}/>
                            {uploadCSVFile.errorGeneralBanks.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorGeneralBanks}</div>}
                        </div>
                        {/* הוראת קבע */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת הוראת קבע' template_from='periodic_reception' />
                            <SelectData titles={['חשבון בנק']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.periodicReceptionBankAccountNumber} onChange={(e) => uploadCSVFile.setPeriodicReceptionBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='periodic_reception' setFile={file => uploadCSVFile.setPeriodicReception(file)} file={uploadCSVFile.periodicReception} googleSheetsToggle={uploadCSVFile.setGoogleSheetsPeriodicReception} googleSheets={uploadCSVFile.googleSheetsPeriodicReception}  update={uploadCSVFile.periodicReceptionUpdate} setUpdate={uploadCSVFile.setPeriodicReceptionUpdate} />
                            {uploadCSVFile.errorPeriodicReception.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorPeriodicReception}</div>}
                        </div>
                        {/* פלטפורמות סליקה */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת פלטפורמות סליקה' template_from='clearing_platform' />
                            <SelectData titles={['מנחה']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.clearingPlatformTrendCoordinatorID} onChange={(e) => uploadCSVFile.setClearingPlatformTrendCoordinatorID(e.target.value)}>
                                        <option key={''} value={''} />
                                        {uploadCSVFile.trendCoordinators.map(trend => <option key={trend.id} value={trend.id}>{trend.name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='clearing_platform' setFile={file => uploadCSVFile.setClearingPlatform(file)} file={uploadCSVFile.clearingPlatform} googleSheetsToggle={uploadCSVFile.setGoogleSheetsClearingPlatform} googleSheets={uploadCSVFile.googleSheetsClearingPlatform}  update={uploadCSVFile.clearingPlatformUpdate} setUpdate={uploadCSVFile.setClearingPlatformUpdate} />
                            {uploadCSVFile.errorClearingPlatform.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorClearingPlatform}</div>}
                        </div>
                        {/* העלאת מסב גולמי */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת מס"ב גולמי' template_from='msv_scraping' />
                            <Label name='msv_scraping' setFile={file => uploadCSVFile.setMsvScrapingPlatform(file)} file={uploadCSVFile.msvScrapingPlatform} googleSheetsToggle={uploadCSVFile.setGoogleSheetsMsvScrapingPlatform} googleSheets={uploadCSVFile.googleSheetsMsvScrapingPlatform}  update={uploadCSVFile.msvScrapingPlatformUpdate} setUpdate={uploadCSVFile.setMsvScrapingPlatformUpdate} />
                            {uploadCSVFile.errorMsvScraping.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorMsvScraping}</div>}
                        </div>
                    </div>
                    <div style={{ width: '50%' }}>
                        {/* עובר ושב */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני עובר ושב' template_from='current_account' />
                            <SelectData titles={['חשבון בנק']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.currentAccountBankAccountNumber} onChange={(e) => uploadCSVFile.setCurrentAccountBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='current_account' setFile={file => uploadCSVFile.setCurrentAccount(file)} file={uploadCSVFile.currentAccount} googleSheetsToggle={uploadCSVFile.setGoogleSheetsCurrentAccount}  googleSheets={uploadCSVFile.googleSheetsCurrentAccount}  update={uploadCSVFile.currentAccountUpdate} setUpdate={uploadCSVFile.setCurrentAccountUpdate}/>
                            {uploadCSVFile.errorCurrentAccount.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorCurrentAccount}</div>}
                        </div>
                        {/* נתוני הכנסות משכר לימוד */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני הכנסות משכר לימוד' template_from='income'/>
                            <SelectData titles={['מזהה מקור הכנסה', 'שיטת תשלום', 'חשבון בנק', 'סטטוס הכנסה']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.studentsIncomesSourceID} onChange={(e) => uploadCSVFile.setStudentsIncomesSourceID(e.target.value)}>
                                        {uploadCSVFile.incomeSource.map(income => <option key={income.id} value={income.id}>{income.name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.studentsIncomesMethod} onChange={(e) => uploadCSVFile.setStudentsIncomesMethod(e.target.value)}>
                                        {uploadCSVFile.paymentMethods.map(payment => <option key={payment} value={payment}>{payment}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.studentsIncomesBankAccountNumber} onChange={(e) => uploadCSVFile.setStudentsIncomesBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.studentsPaymentStatus} onChange={(e) => uploadCSVFile.setStudentsPaymentStatus(e.target.value)}>
                                        {uploadCSVFile.paymentStatus.map(status => <option key={status} value={status}>{status}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='income' setFile={file => uploadCSVFile.setStudentsIncomes(file)} file={uploadCSVFile.studentsIncomes} googleSheetsToggle={uploadCSVFile.setGoogleSheetsStudentsIncomes} googleSheets={uploadCSVFile.googleSheetsStudentsIncomes}   update={uploadCSVFile.studentsIncomesUpdate} setUpdate={uploadCSVFile.setStudentsIncomesUpdate}/>
                            {uploadCSVFile.errorStudentsIncomes.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorStudentsIncomes}</div>}
                        </div>
                        {/* נתוני שגיאות הכנסות תלמידים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת שגיאות הכנסות תלמידים' template_from='payment_failure' />
                            <Label name='payment_failure' setFile={file => uploadCSVFile.setStudentsPaymentFailure(file)} file={uploadCSVFile.studentsPaymentFailure} googleSheetsToggle={uploadCSVFile.setGoogleSheetsStudentsPaymentFailure} googleSheets={uploadCSVFile.googleSheetsStudentsPaymentFailure}  update={uploadCSVFile.studentsPaymentFailureUpdate} setUpdate={uploadCSVFile.setStudentsPaymentFailureUpdate} />
                            {uploadCSVFile.errorStudentsPaymentFailure.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorStudentsPaymentFailure}</div>}
                        </div>
                        {/* דפי סליקה */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת דפי סליקה' template_from='clearing' />
                            <SelectData titles={['פלטפורמת סליקה']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.clearingPlatformID} onChange={(e) => uploadCSVFile.setClearingPlatformID(e.target.value)}>
                                        {uploadCSVFile.platforms.map(platform => <option key={platform.id} value={platform.id}>{platform.name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='clearing' setFile={file => uploadCSVFile.setClearing(file)} file={uploadCSVFile.clearing} googleSheetsToggle={uploadCSVFile.setGoogleSheetsClearing} googleSheets={uploadCSVFile.googleSheetsClearing}  update={uploadCSVFile.clearingUpdate} setUpdate={uploadCSVFile.setClearingUpdate}/>
                            {uploadCSVFile.errorClearing.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorClearing}</div>}
                        </div>
                        {/* ולידציית סליקת אשראי */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת ולידציית סליקת אשראי' template_from='clearing_validation' />
                            <Label name='clearing_validation'  setFile={file => uploadCSVFile.setClearingValidation(file)} file={uploadCSVFile.clearingValidation} googleSheetsToggle={uploadCSVFile.setGoogleSheetsClearingValidation} googleSheets={uploadCSVFile.googleSheetsClearingValidation}  update={uploadCSVFile.clearingValidationUpdate} setUpdate={uploadCSVFile.setClearingValidationUpdate} />
                            {uploadCSVFile.errorClearingValidation.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorClearingValidation}</div>}
                        </div>
                        {/* נתוני הוצאות מס"ב */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני הוצאות - מס"ב' template_from='msv' />
                            <SelectData titles={['שיוך', 'חשבון בנק', 'עבור חודש', 'תאריך שידור', 'מנחה']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.msvAttribution} onChange={(e) => uploadCSVFile.setMsvAttribution(e.target.value)}>
                                        {uploadCSVFile.attributions.map(attribution => attribution!=='donator'? <option key={attribution} value={attribution}>{attribution}</option>:null)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.msvBankAccountNumber} onChange={(e) => uploadCSVFile.setMsvBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                    <input type='date' style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.msvForDate} onChange={e => uploadCSVFile.setMsvForDate(e.target.value)} />
                                    <input type='date' style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.msvSendingDate} onChange={e => uploadCSVFile.setMsvSendingDate(e.target.value)} />
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.msvTrendCoordinator} onChange={(e) => uploadCSVFile.setMsvTrendCoordinator(e.target.value)}>
                                        {uploadCSVFile.trendCoordinators.map(trend => <option key={trend.id} value={trend.id}>{trend.name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='msv' setFile={file => uploadCSVFile.setMSV(file)} file={uploadCSVFile.msv} googleSheetsToggle={uploadCSVFile.setGoogleSheetsMSV}  googleSheets={uploadCSVFile.googleSheetsMSV}  update={uploadCSVFile.msvUpdate} setUpdate={uploadCSVFile.setMsvUpdate} />
                            {uploadCSVFile.errorMSV.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorMSV}</div>}
                        </div>
                        {/* נתוני הוצאות שיקים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני הוצאות - שיקים' template_from='check' />
                            <SelectData titles={['שיוך', 'חשבון בנק']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.checksAttribution} onChange={(e) => uploadCSVFile.setChecksAttribution(e.target.value)}>
                                        {uploadCSVFile.attributions.map(attribution => attribution!=='donator'? <option key={attribution} value={attribution}>{attribution}</option>:null)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.checksBankAccountNumber} onChange={(e) => uploadCSVFile.setChecksBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='check' setFile={file => uploadCSVFile.setChecks(file)} file={uploadCSVFile.checks} googleSheetsToggle={uploadCSVFile.setGoogleSheetsChecks} googleSheets={uploadCSVFile.googleSheetsChecks}  update={uploadCSVFile.checksUpdate} setUpdate={uploadCSVFile.setChecksUpdate}/>
                            {uploadCSVFile.errorChecks.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorChecks}</div>}
                        </div>
                        {/* חשבוניות */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת חשבוניות' />
                            <SelectData key='invoice' titles={['מוסד', 'מנחה', 'ספק', 'תאריך החשבונית', 'סכום', 'מספר החשבונית', 'יום אחרון לתשלום']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceInstitutionBranchCoordinator} onChange={(e) => uploadCSVFile.setInvoiceInstitutionBranchCoordinator(e.target.value)}>
                                        {uploadCSVFile.institutionBranchCoordinators.map(institution => <option key={institution.id} value={institution.identity}>{institution.identity} - {institution.name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceTrendCoordinator} onChange={(e) => uploadCSVFile.setInvoiceTrendCoordinator(e.target.value)}>
                                        {uploadCSVFile.trendCoordinators.map(trend => <option key={trend.id} value={trend.name}>{trend.name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceSupplier} onChange={(e) => uploadCSVFile.setInvoiceSupplier(e.target.value)}>
                                        {uploadCSVFile.suppliers.map(supplier => <option key={supplier.id} value={supplier.identity}>{supplier.identity} - {supplier.name}</option>)}
                                    </select>
                                    <input type='date' style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceDate} onChange={e => uploadCSVFile.setInvoiceDate(e.target.value)} />
                                    <input style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceSum}
                                        onChange={e => regexNumber.test(e.target.value) && uploadCSVFile.setInvoiceSum(e.target.value || '0')} />
                                    <input style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceNumber}
                                        onChange={e => uploadCSVFile.setInvoiceNumber(e.target.value)} />
                                    <input type='date' style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.invoiceLastDate} onChange={e => uploadCSVFile.setInvoiceLastDate(e.target.value)} />
                                </div>
                            </SelectData>
                            <Label name='invoice' setFile={file => uploadCSVFile.setInvoice(file)} file={uploadCSVFile.invoice} googleSheetsToggle={uploadCSVFile.setGoogleSheetsInvoice} googleSheets={uploadCSVFile.googleSheetsInvoice}  update={uploadCSVFile.invoiceUpdate} setUpdate={uploadCSVFile.setInvoiceUpdate} />
                            {uploadCSVFile.errorInvoice.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorInvoice}</div>}
                        </div>
                        {/* נתוני הוצאות ביטוח תלמידים */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני הוצאות ביטוח תלמידים' template_from='student_insurance' />
                            <SelectData titles={['חשבון בנק']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.studentInsuranceBankAccountNumber} onChange={(e) => uploadCSVFile.setStudentInsuranceBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                </div>
                            </SelectData>
                            <Label name='student_insurance' setFile={file => uploadCSVFile.setStudentInsurance(file)} file={uploadCSVFile.studentInsurance} googleSheetsToggle={uploadCSVFile.setGoogleSheetsStudentInsurance} googleSheets={uploadCSVFile.googleSheetsStudentInsurance}  update={uploadCSVFile.studentInsuranceUpdate} setUpdate={uploadCSVFile.setStudentsInsuranceUpdate}/>
                            {uploadCSVFile.errorStudentInsurance.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorStudentInsurance}</div>}
                        </div>
                        {/* נתוני טיוטות תשלום */}
                        <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                            <Title title='העלאת נתוני טיוטות תשלום' template_from='expense_draft' />
                            <SelectData titles={uploadCSVFile.expenseDraftAttribution === 'student' ?
                                ['שיוך', 'עבור חודש', 'מנחה', 'חשבון בנק', 'שיטת תשלום', 'סוג מילגה'] :
                                ['שיוך', 'עבור חודש', 'מנחה', 'חשבון בנק', 'שיטת תשלום']} >
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftAttribution} onChange={(e) => uploadCSVFile.setExpenseDraftAttribution(e.target.value)}>
                                        {uploadCSVFile.attributions.map(attribution =>attribution!=='donator'? <option key={attribution} value={attribution}>{attribution}</option>:null)}
                                    </select>
                                    <input type='date' style={{ marginTop: '5px', width: 'fit-content', height: '1em', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftForMonth} onChange={e => uploadCSVFile.setExpenseDraftForMonth(e.target.value)} />
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftTrendCoordinator} onChange={(e) => uploadCSVFile.setExpenseDraftTrendCoordinator(e.target.value)}>
                                        <option value=''>בחר מנחה (רשות)</option>
                                        {uploadCSVFile.trendCoordinators.map(trend => <option key={trend.id} value={trend.id}>{trend.name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftBankAccountNumber} onChange={(e) => uploadCSVFile.setExpenseDraftBankAccountNumber(e.target.value)}>
                                        {uploadCSVFile.bankAccounts.map(bank => <option key={bank.id} value={bank.account_number}>{bank.account_number} - {bank.institution_name}</option>)}
                                    </select>
                                    <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftPaymentMethod} onChange={(e) => uploadCSVFile.setExpenseDraftPaymentMethod(e.target.value)}>
                                        <option value=''>בחר שיטת תשלום (רשות)</option>
                                        {uploadCSVFile.paymentMethods.map(payment => <option key={payment} value={payment}>{payment}</option>)}
                                    </select>
                                    {uploadCSVFile.expenseDraftAttribution === 'student' &&
                                        <select style={{ marginTop: '5px', width: 'fit-content', fontSize: '1em', outline: 'none' }} value={uploadCSVFile.expenseDraftScholarshipType} onChange={(e) => uploadCSVFile.setExpenseDraftScholarshipType(e.target.value)}>
                                            {uploadCSVFile.scholarshipTypes.map(type => <option key={type} value={type}>{type}</option>)}
                                        </select>}
                                </div>
                            </SelectData>
                            <div style={{ display: 'flex' }}>
                                <Label name='expense_draft' setFile={file => uploadCSVFile.setExpenseDraft(file)} file={uploadCSVFile.expenseDraft} googleSheetsToggle={uploadCSVFile.setGoogleSheetsExpenseDraft} googleSheets={uploadCSVFile.googleSheetsExpenseDraft}  update={uploadCSVFile.expenseDraftFixedUpdate} setUpdate={uploadCSVFile.setExpenseDraftFixedUpdate}/>
                                <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', marginRight: '5px' }}>
                                    <input type='checkbox' checked={uploadCSVFile.expenseDraftFixed} onChange={e => uploadCSVFile.setExpenseDraftFixed(e.target.checked)} />
                                    fixed
                                </label>
                            </div>

                            {uploadCSVFile.errorExpenseDraft.trim() !== '' && <div style={{ color: 'red' }}>{uploadCSVFile.errorExpenseDraft}</div>}
                        </div>
                    </div>
                </div>


                <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start', width: 'fit-content', margin: '2em auto 0' }}>
                    <input disabled={uploadCSVFile.loader} className='button' type='button' value='שלח' style={{ padding: '0.2em 0.5em', fontSize: '1.1em' }} onClick={HandleUploadCSV} />
                </div>

            </div>
        </Container >
    )
}

export default observer(UploadCSVFile);